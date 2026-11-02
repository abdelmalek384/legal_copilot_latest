"""Draft procedural deadline arithmetic. Legal rules and holidays require Egyptian-lawyer review."""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

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
    if isinstance(months, bool) or not isinstance(months, int):
        raise DeadlineError("months must be an integer")
    index = day.year * 12 + day.month - 1 + months
    year, month0 = divmod(index, 12)
    month = month0 + 1
    try:
        return dt.date(year, month, min(day.day, calendar.monthrange(year, month)[1]))
    except (ValueError, OverflowError) as exc:
        raise DeadlineError("month arithmetic produced a date outside the supported range") from exc


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
        if not isinstance(rule["label_ar"], str) or not rule["label_ar"].strip():
            raise DeadlineError("rule label_ar must be a non-empty string")
        if isinstance(rule["amount"], bool) or not isinstance(rule["amount"], int) or not 1 <= rule["amount"] <= 3650:
            raise DeadlineError("rule period must be a positive integer no greater than 3650")
        if not isinstance(rule["unit"], str) or rule["unit"] not in UNITS:
            raise DeadlineError("rule unit must be days, months, or years")
        if "verified" in rule and not isinstance(rule["verified"], bool):
            raise DeadlineError("rule verified field must be boolean")
        result[rule["id"]] = rule
    return result


def load_holidays(path: Path = DEFAULT_HOLIDAYS, years=()) -> tuple[dict, set]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DeadlineError("could not read valid holiday data") from exc
    if not isinstance(data, dict):
        raise DeadlineError("holiday file must be a JSON object")
    fixed = data.get("fixed_holidays", [])
    dated = data.get("dated_holidays", [])
    complete_raw = data.get("complete_years", [])
    if not isinstance(fixed, list) or not isinstance(dated, list) or not isinstance(complete_raw, list):
        raise DeadlineError("holiday arrays and complete_years must be lists")

    # Validate fixed dates even when no target years were supplied.
    for item in fixed:
        if not isinstance(item, dict):
            raise DeadlineError("invalid fixed holiday entry")
        month, day, name = item.get("month"), item.get("day"), item.get("name_ar")
        if (isinstance(month, bool) or not isinstance(month, int) or
                isinstance(day, bool) or not isinstance(day, int) or
                not isinstance(name, str) or not name.strip()):
            raise DeadlineError("invalid fixed holiday entry")
        if not 1 <= month <= 12 or not 1 <= day <= 31:
            raise DeadlineError("invalid fixed holiday date")
        # Use leap year 2000 to validate month/day combinations including Feb 29.
        try:
            dt.date(2000, month, day)
        except ValueError as exc:
            raise DeadlineError("invalid fixed holiday date") from exc

    holidays = {}
    try:
        for item in fixed:
            for year in years:
                try:
                    holidays[dt.date(year, item["month"], item["day"])] = item["name_ar"]
                except ValueError:
                    # February 29 is valid only in leap years.
                    if not (item["month"] == 2 and item["day"] == 29):
                        raise
        for item in dated:
            if not isinstance(item, dict):
                raise DeadlineError("invalid dated holiday entry")
            name, date_text = item.get("name_ar"), item.get("date")
            if not isinstance(name, str) or not name.strip() or not isinstance(date_text, str):
                raise DeadlineError("invalid dated holiday entry")
            parsed = dt.date.fromisoformat(date_text)
            if parsed.isoformat() != date_text:
                raise DeadlineError("holiday date must use YYYY-MM-DD")
            if parsed in holidays and holidays[parsed] != name:
                raise DeadlineError("conflicting names for the same holiday date")
            holidays[parsed] = name
    except (ValueError, TypeError, KeyError) as exc:
        if isinstance(exc, DeadlineError):
            raise
        raise DeadlineError("invalid holiday date or year") from exc

    if any(isinstance(y, bool) or not isinstance(y, int) or not 1900 <= y <= 2200 for y in complete_raw):
        raise DeadlineError("complete_years contains an invalid year")
    complete = set(complete_raw)
    return holidays, complete


def _is_verified(rule: dict) -> bool:
    """Require explicit counsel review metadata; this still cannot prove it is genuine."""
    if rule.get("verified") is not True:
        return False
    reviewer = rule.get("verified_by")
    reviewer_role = rule.get("verified_by_role")
    source = rule.get("source_article")
    evidence_url = rule.get("review_evidence_url")
    if not isinstance(reviewer, str) or not reviewer.strip():
        return False
    if not isinstance(reviewer_role, str) or reviewer_role not in {"egyptian_lawyer", "qualified_egyptian_counsel"}:
        return False
    if not isinstance(source, str) or not source.strip():
        return False
    if not isinstance(evidence_url, str) or not evidence_url.strip():
        return False
    try:
        parsed = urlsplit(evidence_url.strip())
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            return False
        _ = parsed.port
    except (TypeError, ValueError):
        return False
    try:
        verified_on_text = rule.get("verified_on", "")
        verified_on = dt.date.fromisoformat(verified_on_text)
    except (TypeError, ValueError):
        return False
    return verified_on.isoformat() == verified_on_text and verified_on <= dt.date.today()


def _compute_deadline_internal(trigger: dt.date, amount: int, unit: str, *, rule_id=None,
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
    if holidays is not None and not isinstance(holidays, dict):
        raise DeadlineError("holidays must be a date-to-name mapping")
    holidays = holidays or {}
    for day, name in holidays.items():
        if not isinstance(day, dt.date) or isinstance(day, dt.datetime) or not isinstance(name, str) or not name.strip():
            raise DeadlineError("invalid holiday mapping entry")
    if not isinstance(complete_holiday_years, (set, frozenset, list, tuple)):
        raise DeadlineError("complete holiday years must be a collection of years")
    if any(isinstance(y, bool) or not isinstance(y, int) or not 1900 <= y <= 2200 for y in complete_holiday_years):
        raise DeadlineError("complete holiday years contains an invalid year")

    warnings = []
    if not verified_rule:
        warnings.append("القاعدة مسودة غير معتمدة؛ لا تعتمد على النتيجة.")
    try:
        if unit == "days":
            raw_end = trigger + dt.timedelta(days=amount)
        elif unit == "months":
            raw_end = add_months(trigger, amount)
        else:
            raw_end = add_months(trigger, amount * 12)
        end = raw_end + dt.timedelta(days=distance_days)
    except (OverflowError, ValueError) as exc:
        raise DeadlineError("calculated date is outside the supported range") from exc
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


def compute_deadline(trigger: dt.date, amount: int, unit: str, *, rule_id=None,
                     allow_unverified=False, non_working_weekdays=WEEKEND_DEFAULT,
                     holidays=None, complete_holiday_years=frozenset(), distance_days=0,
                     extend_if_non_working=True, today=None) -> dict:
    """Calculate raw arithmetic only; verified status is derived from a reviewed rule."""
    return _compute_deadline_internal(
        trigger, amount, unit, rule_id=rule_id, verified_rule=False,
        allow_unverified=allow_unverified, non_working_weekdays=non_working_weekdays,
        holidays=holidays, complete_holiday_years=complete_holiday_years,
        distance_days=distance_days, extend_if_non_working=extend_if_non_working, today=today,
    )


def compute_from_rule(rule: dict, trigger: dt.date, **kwargs) -> dict:
    if not isinstance(rule, dict) or not all(k in rule for k in ("id", "amount", "unit")):
        raise DeadlineError("rule must be an object with id, amount, and unit")
    verified = _is_verified(rule)
    return _compute_deadline_internal(trigger, rule["amount"], rule["unit"], rule_id=rule["id"],
                                      verified_rule=verified, **kwargs)


def rule_catalog(path: Path = DEFAULT_RULES) -> dict:
    """Return safe display metadata for the deadline-rule selector."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DeadlineError("could not read valid rules JSON") from exc
    rules = load_rules(path)
    return {
        "status": raw.get("status", "unknown") if isinstance(raw, dict) else "unknown",
        "warning": raw.get("warning", "") if isinstance(raw, dict) else "",
        "rules": [
            {
                "id": rule["id"],
                "label_ar": rule["label_ar"],
                "amount": rule["amount"],
                "unit": rule["unit"],
                "verified": _is_verified(rule),
                "starts_from_ar": rule.get("starts_from_ar"),
                "source_article": rule.get("source_article"),
                "review_status": "verified" if _is_verified(rule) else "draft_unverified",
            }
            for rule in rules.values()
        ],
    }


def estimate_rule_deadline(rule_id: str, trigger: dt.date, *, distance_days: int = 0,
                           today: dt.date | None = None,
                           rules_path: Path = DEFAULT_RULES,
                           holidays_path: Path = DEFAULT_HOLIDAYS,
                           additional_dated_holidays: list[dict] | None = None) -> dict:
    """Build a non-authoritative preview from a selected rule and draft holiday calendar.

    The UI may explicitly preview unverified rules, but the returned warning and
    verified_rule flag must remain visible. This helper never creates a case deadline.
    """
    if not isinstance(rule_id, str) or not rule_id.strip():
        raise DeadlineError("a rule ID is required")
    rules = load_rules(rules_path)
    rule = rules.get(rule_id)
    if rule is None:
        raise DeadlineError("unknown deadline rule")
    if isinstance(trigger, dt.datetime) or not isinstance(trigger, dt.date):
        raise DeadlineError("trigger must be a calendar date")
    holidays, complete = load_holidays(
        holidays_path, range(trigger.year, min(2201, trigger.year + 13))
    )
    if additional_dated_holidays is not None:
        if not isinstance(additional_dated_holidays, list):
            raise DeadlineError("additional dated holidays must be a list")
        for item in additional_dated_holidays:
            if not isinstance(item, dict):
                raise DeadlineError("invalid firm holiday entry")
            date_text, name = item.get("date"), item.get("name_ar")
            if not isinstance(date_text, str) or not isinstance(name, str) or not name.strip():
                raise DeadlineError("invalid firm holiday entry")
            try:
                parsed = dt.date.fromisoformat(date_text)
            except ValueError as exc:
                raise DeadlineError("invalid firm holiday date") from exc
            if parsed.isoformat() != date_text:
                raise DeadlineError("firm holiday date must use YYYY-MM-DD")
            holidays[parsed] = name.strip()
    result = compute_from_rule(
        rule, trigger, allow_unverified=True, holidays=holidays,
        complete_holiday_years=complete, distance_days=distance_days, today=today,
    )
    result["rule_label_ar"] = rule["label_ar"]
    result["rule_catalog_status"] = rule_catalog(rules_path)["status"]
    result["rule_source_article"] = rule.get("source_article")
    result["starts_from_ar"] = rule.get("starts_from_ar")
    result["calculation_assumptions_ar"] = [
        "تاريخ البداية المدخل افتراض يحتاج إلى تأكيد المحامي من واقع الإعلان أو الحكم أو الواقعة؛ الأداة لا تستنتج تاريخ بدء الميعاد.",
        "في حساب الأيام، لا يدخل يوم الواقعة المدخل في عدد الأيام؛ أما قواعد الشهور والسنوات فتستخدم مقابلة التاريخ مع ضبط نهاية الشهر.",
        "تضاف أيام المسافة المدخلة يدوياً قبل فحص العطلات.",
        "يفترض الحساب الجمعة والسبت يومي عطلة أسبوعية، ويمدد النهاية إذا وافقت عطلة مسجلة؛ يجب التحقق من القاعدة القانونية والاستثناءات الخاصة.",
        "تقويم العطلات جزئي وغير معتمد ولا يشمل بالضرورة العطلات المتغيرة أو قرارات نقل العطلات.",
    ]
    try:
        holiday_data = json.loads(Path(holidays_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DeadlineError("could not read valid holiday data") from exc
    holiday_status = holiday_data.get("status", "unknown") if isinstance(holiday_data, dict) else "unknown"
    result["holiday_calendar_status"] = holiday_status
    if holiday_status != "verified":
        result["warnings"].append("تقويم العطلات غير مكتمل أو غير معتمد؛ قد لا تشمل النتيجة جميع العطلات.")
    return result


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
