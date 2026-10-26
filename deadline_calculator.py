"""Draft procedural deadline arithmetic. Legal rules and holidays require Egyptian-lawyer review."""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_RULES = ROOT / "data" / "deadline_rules.draft.json"
DEFAULT_HOLIDAYS = ROOT / "data" / "deadline_holidays.draft.json"
WEEKDAYS_AR = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
WEEKEND_DEFAULT = (4, 5)
MAX_EXTENSION_DAYS = 31
DISCLAIMER = ("أداة حساب تجريبية وليست استشارة قانونية. لا تعتمد على النتيجة قبل مراجعة محامٍ مصري "
              "لنوع الميعاد وبدايته وقواعد حسابه والعطلات والاستثناءات المنطبقة.")
UNITS = {"days", "months", "years"}


class DeadlineError(ValueError):
    pass


class UnverifiedRuleError(DeadlineError):
    pass


def add_months(day: dt.date, months: int) -> dt.date:
    index = day.year * 12 + day.month - 1 + months
    year, month0 = divmod(index, 12)
    month = month0 + 1
    return dt.date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def load_rules(path: Path = DEFAULT_RULES) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DeadlineError("could not read valid rules JSON") from exc
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise DeadlineError("rules file must contain a rules array")
    result = {}
    for rule in data["rules"]:
        if not isinstance(rule, dict) or not all(k in rule for k in ("id", "label_ar", "amount", "unit")):
            raise DeadlineError("each rule must include id, label_ar, amount, and unit")
        if not isinstance(rule["id"], str) or not rule["id"].strip() or rule["id"] in result:
            raise DeadlineError("rule IDs must be unique non-empty strings")
        if isinstance(rule["amount"], bool) or not isinstance(rule["amount"], int) or not 1 <= rule["amount"] <= 3650:
            raise DeadlineError("rule period must be a positive integer no greater than 3650")
        if rule["unit"] not in UNITS:
            raise DeadlineError("rule unit must be days, months, or years")
        result[rule["id"]] = rule
    return result


def load_holidays(path: Path = DEFAULT_HOLIDAYS, years=()) -> tuple[dict, set]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("fixed_holidays", []), list):
            raise DeadlineError("holiday file must contain a fixed_holidays array")
        holidays = {}
        for item in data.get("fixed_holidays", []):
            month, day, name = item["month"], item["day"], item["name_ar"]
            if isinstance(month, bool) or isinstance(day, bool) or not isinstance(month, int) or not isinstance(day, int) or not isinstance(name, str) or not name.strip():
                raise DeadlineError("invalid fixed holiday entry")
            for year in years:
                try:
                    holidays[dt.date(year, month, day)] = name
                except ValueError:
                    if month != 2 or day != 29:
                        raise DeadlineError("invalid fixed holiday date")
        for item in data.get("dated_holidays", []):
            if not isinstance(item, dict) or not isinstance(item.get("name_ar"), str):
                raise DeadlineError("invalid dated holiday entry")
            holidays[dt.date.fromisoformat(item["date"])] = item["name_ar"]
        complete = set(data.get("complete_years", []))
        if any(isinstance(y, bool) or not isinstance(y, int) or not 1900 <= y <= 2200 for y in complete):
            raise DeadlineError("complete_holiday_years contains an invalid year")
        return holidays, complete
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if isinstance(exc, DeadlineError):
            raise
        raise DeadlineError("could not read valid holiday data") from exc


def _is_verified(rule: dict) -> bool:
    if rule.get("verified") is not True:
        return False
    reviewer = rule.get("verified_by")
    source = rule.get("source_article")
    if not isinstance(reviewer, str) or not reviewer.strip():
        return False
    if not isinstance(source, str) or not source.strip():
        return False
    try:
        verified_on = dt.date.fromisoformat(rule.get("verified_on", ""))
    except (TypeError, ValueError):
        return False
    return verified_on.isoformat() == rule.get("verified_on")


def compute_deadline(trigger: dt.date, amount: int, unit: str, *, rule_id=None,
                     verified_rule=False, allow_unverified=False,
                     non_working_weekdays=WEEKEND_DEFAULT, holidays=None,
                     complete_holiday_years=frozenset(), distance_days=0,
                     extend_if_non_working=True, today=None) -> dict:
    if isinstance(trigger, dt.datetime) or not isinstance(trigger, dt.date):
        raise DeadlineError("trigger must be a date, not a datetime")
    if today is not None and (isinstance(today, dt.datetime) or not isinstance(today, dt.date)):
        raise DeadlineError("today must be a date")
    if unit not in UNITS:
        raise DeadlineError("unit must be days, months, or years")
    if isinstance(amount, bool) or not isinstance(amount, int) or not 1 <= amount <= 3650:
        raise DeadlineError("amount must be a positive integer no greater than 3650")
    if isinstance(distance_days, bool) or not isinstance(distance_days, int) or not 0 <= distance_days <= 365:
        raise DeadlineError("distance_days must be an integer between 0 and 365")
    if not isinstance(extend_if_non_working, bool):
        raise DeadlineError("extend_if_non_working must be boolean")
    try:
        weekend = tuple(non_working_weekdays)
    except TypeError as exc:
        raise DeadlineError("non-working weekdays must be a collection of weekday numbers") from exc
    if any(isinstance(d, bool) or not isinstance(d, int) or d not in range(7) for d in weekend):
        raise DeadlineError("weekday numbers must be integers from 0 to 6")
    if len(set(weekend)) != len(weekend):
        raise DeadlineError("weekday numbers must not repeat")
    if not verified_rule and not allow_unverified:
        raise UnverifiedRuleError("rule is unverified; refusing to calculate without explicit override")
    holidays = holidays or {}
    warnings = []
    if not verified_rule:
        warnings.append("القاعدة مسودة غير معتمدة؛ لا تعتمد على النتيجة.")
    if unit == "days":
        raw_end = trigger + dt.timedelta(days=amount)
    elif unit == "months":
        raw_end = add_months(trigger, amount)
    else:
        raw_end = add_months(trigger, amount * 12)
    end = raw_end + dt.timedelta(days=distance_days)
    steps = [f"تاريخ الواقعة: {trigger.isoformat()} ({WEEKDAYS_AR[trigger.weekday()]})؛ لا يُحسب يوم الواقعة وفق اصطلاح المسودة.",
             f"نهاية المدة الحسابية قبل الإضافات: {raw_end.isoformat()}."]
    if distance_days:
        steps.append(f"إضافة {distance_days} يومًا كمدة مسافة مدخلة يدويًا: {end.isoformat()}.")
    extensions = []
    if extend_if_non_working:
        for _ in range(MAX_EXTENSION_DAYS + 1):
            if end.weekday() not in weekend and end not in holidays:
                break
            reason = f"عطلة رسمية: {holidays[end]}" if end in holidays else "عطلة أسبوعية"
            nxt = end + dt.timedelta(days=1)
            extensions.append({"from": end.isoformat(), "reason": reason, "to": nxt.isoformat()})
            steps.append(f"{end.isoformat()} يوم غير عامل ({reason})؛ يمتد الحساب إلى {nxt.isoformat()}.")
            end = nxt
        else:
            raise DeadlineError("too many consecutive non-working days; check the holiday list")
    if end.year not in complete_holiday_years:
        warnings.append(f"قائمة عطلات سنة {end.year} غير مكتملة؛ لا تشمل بالضرورة الأعياد المتغيرة أو قرارات نقل العطلات.")
    steps.append(f"نهاية الحساب الحالية: {end.isoformat()} ({WEEKDAYS_AR[end.weekday()]}).")
    remaining = (end - today).days if today else None
    if remaining is not None and remaining < 0:
        warnings.append("قد يكون الميعاد قد انقضى وفق هذا الحساب غير المعتمد.")
    return {
        "rule_id": rule_id, "trigger_date": trigger.isoformat(), "amount": amount, "unit": unit,
        "raw_end": raw_end.isoformat(), "final_due": end.isoformat(),
        "final_due_weekday_ar": WEEKDAYS_AR[end.weekday()], "extensions": extensions,
        "days_remaining": remaining, "verified_rule": bool(verified_rule), "steps_ar": steps,
        "warnings": warnings, "disclaimer": DISCLAIMER,
    }


def compute_from_rule(rule: dict, trigger: dt.date, **kwargs) -> dict:
    verified = _is_verified(rule)
    return compute_deadline(trigger, rule["amount"], rule["unit"], rule_id=rule["id"],
                            verified_rule=verified, **kwargs)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rule")
    parser.add_argument("--from", dest="trigger", required=True, help="trigger date YYYY-MM-DD")
    parser.add_argument("--distance-days", type=int, default=0)
    parser.add_argument("--rules-file", default=str(DEFAULT_RULES))
    parser.add_argument("--holidays-file", default=str(DEFAULT_HOLIDAYS))
    parser.add_argument("--weekend", default="4,5", help="non-working weekdays; Monday=0")
    parser.add_argument("--allow-unverified", action="store_true")
    parser.add_argument("--today", help="today YYYY-MM-DD")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        trigger = dt.date.fromisoformat(args.trigger)
        today = dt.date.fromisoformat(args.today) if args.today else None
        weekend = tuple(int(x.strip()) for x in args.weekend.split(",") if x.strip())
        holidays, complete = load_holidays(Path(args.holidays_file), range(trigger.year, min(2201, trigger.year + 13)))
        rules = load_rules(Path(args.rules_file))
        if not args.rule or args.rule not in rules:
            raise DeadlineError("select a known --rule from the unverified draft rules file")
        result = compute_from_rule(rules[args.rule], trigger, allow_unverified=args.allow_unverified,
                                   non_working_weekdays=weekend, holidays=holidays,
                                   complete_holiday_years=complete, distance_days=args.distance_days, today=today)
    except (ValueError, DeadlineError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n".join(result["steps_ar"]))
        for warning in result["warnings"]:
            print("تنبيه: " + warning)
        print(DISCLAIMER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
