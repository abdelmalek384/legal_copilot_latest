"""Build a conservative, lawyer-editable Arabic legal draft from structured case data.

This tool formats supplied material; it does not research law or determine legal merits.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.output_path_safety import ensure_output_paths_safe

DRAFT_TYPES = {
    "defense_memo": ("مذكرة دفاع", "مذكرة بدفاع"),
    "statement_of_claim": ("صحيفة دعوى", "صحيفة دعوى"),
}
ALLOWED_PERMISSION_STATES = {"allowed", "allowed_limited"}

def _text(value: Any, placeholder: str) -> str:
    if value is None or not str(value).strip():
        return f"【{placeholder}】"
    return str(value).strip()

def _items(values: Any, placeholder: str) -> list[str]:
    if not isinstance(values, list):
        return [f"【{placeholder}】"]
    clean = [str(v).strip() for v in values if str(v).strip()]
    return clean or [f"【{placeholder}】"]

def _source_usable(source: dict[str, Any], as_of: date) -> bool:
    """Require explicit recorded review, status, dates, and permission evidence."""
    if source.get("lawyer_approved") is not True:
        return False
    if (source.get("legal_status") != "in_force"
            or source.get("status_verified") is not True
            or source.get("authenticity_verified") is not True):
        return False
    if source.get("permission_status") not in ALLOWED_PERMISSION_STATES:
        return False
    try:
        effective = date.fromisoformat(str(source["effective_date"]))
        reviewed = date.fromisoformat(str(source["reviewed_at"]))
    except (KeyError, TypeError, ValueError):
        return False
    if effective > as_of or reviewed > as_of:
        return False
    repeal_value = source.get("repeal_date")
    if repeal_value:
        try:
            if as_of >= date.fromisoformat(str(repeal_value)):
                return False
        except ValueError:
            return False
    if not str(source.get("title", "")).strip() or not str(source.get("citation", "")).strip():
        return False
    if not str(source.get("permission_evidence", "")).strip():
        return False
    source_url = source.get("url")
    if (not isinstance(source_url, str) or not source_url or source_url != source_url.strip()
            or "\\" in source_url
            or any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in source_url)):
        return False
    try:
        parsed_url = urlsplit(source_url)
        port = parsed_url.port
    except (TypeError, ValueError):
        return False
    if (parsed_url.scheme.lower() != "https" or not parsed_url.hostname
            or parsed_url.username is not None or parsed_url.password is not None
            or parsed_url.query or parsed_url.fragment or parsed_url.netloc.endswith(":")
            or (port is not None and not 1 <= port <= 65535)):
        return False
    return True

def render_draft(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be an object")
    kind = payload.get("draft_type")
    if kind not in DRAFT_TYPES:
        raise ValueError("draft_type must be defense_memo or statement_of_claim")
    try:
        as_of = date.fromisoformat(str(payload["as_of_date"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("as_of_date must be an ISO date (YYYY-MM-DD)") from exc
    case = payload.get("case") if isinstance(payload.get("case"), dict) else {}
    facts = _items(payload.get("facts"), "تُستكمل الوقائع من المحامي")
    arguments = _items(payload.get("lawyer_arguments"), "يُضاف وجه الدفاع أو أساس الطلب بمعرفة المحامي")
    requests = _items(payload.get("requests"), "تُحدد الطلبات الختامية بمعرفة المحامي")
    missing = _items(payload.get("missing_information"), "لا توجد عناصر إضافية مسجلة؛ راجع اكتمال البيانات قبل الاعتماد")
    sources = payload.get("sources", [])
    if not isinstance(sources, list):
        sources = []
    usable = [s for s in sources if isinstance(s, dict) and _source_usable(s, as_of)]
    title, opening = DRAFT_TYPES[kind]
    lines = [
        f"# {title}", "",
        f"**تاريخ إعداد المسودة:** {date.today().isoformat()}",
        f"**التاريخ القانوني المطلوب التحقق منه:** {as_of.isoformat()}", "",
        "> **مسودة عمل غير معتمدة للإيداع.** لم تُجرَ مراجعة قانونية مستقلة. راجع الوقائع والمستندات والاختصاص والمواعيد والطلبات والمصادر قبل الاستخدام. لا تعتبر هذه المسودة رأيًا قانونيًا نهائيًا.",
        "", "## بيانات القضية",
        f"- المحكمة/الدائرة: {_text(case.get('court'), 'تُحدد المحكمة والدائرة')}",
        f"- رقم الدعوى والسنة: {_text(case.get('case_number'), 'يُستكمل رقم الدعوى والسنة')}",
        f"- المدعي: {_text(case.get('claimant'), 'تُستكمل بيانات المدعي')}",
        f"- المدعى عليه: {_text(case.get('respondent'), 'تُستكمل بيانات المدعى عليه')}",
        f"- صفة مقدم المسودة: {_text(case.get('drafted_for'), 'تُحدد صفة الطرف الذي تُعد المسودة لصالحه')}",
        "", f"## {opening}", "", "تحريرًا في: 【تُستكمل المدينة والتاريخ】", "",
        "### أولًا: الوقائع والمعلومات المقدمة",
    ]
    lines.extend(f"{i}. {fact}" for i, fact in enumerate(facts, 1))
    lines += ["", "### ثانيًا: أوجه الدفاع/الأساس القانوني المقترح"]
    lines.extend(f"{i}. {argument}" for i, argument in enumerate(arguments, 1))
    lines += ["", "### ثالثًا: المصادر القانونية المصرح باستخدامها والمراجعة"]
    if usable:
        for i, source in enumerate(usable, 1):
            lines.append(
                f"- [S{i}] {_text(source.get('title'), 'عنوان المصدر غير متاح')} — "
                f"{_text(source.get('citation'), 'بيانات الإحالة غير مكتملة')}; "
                f"راجع في {source['reviewed_at']}; الرابط: {_text(source.get('url'), 'يُضاف رابط المصدر')}"
            )
    else:
        lines.append(
            "لم تُقدَّم مصادر تستوفي جميع شروط المراجعة المسجلة والحالة القانونية والتاريخ والإذن. "
            "لا تضف أرقام مواد أو أحكامًا قضائية بالتخمين؛ أدخل مصادر موثقة وراجعها قبل الاعتماد."
        )
    lines += ["", "### رابعًا: الطلبات", ""]
    lines.extend(f"{i}. {request}" for i, request in enumerate(requests, 1))
    lines += ["", "### خامسًا: معلومات ومستندات يلزم استكمالها أو التحقق منها", ""]
    lines.extend(f"- [ ] {item}" for item in missing)
    lines += [
        "", "### قائمة مراجعة المحامي قبل الاعتماد",
        "- [ ] مطابقة كل واقعة مع مستند أو إقرار أو مصدرها، وتصحيح أي تناقض.",
        "- [ ] التحقق من الاختصاص والصفة والمصلحة والإجراءات والمواعيد من مصدر موثوق وحديث.",
        "- [ ] فتح كل مصدر والتحقق من النص والإحالة والنطاق الزمني؛ وجود المصدر هنا لا يثبت صحة الحجة.",
        "- [ ] حذف أي طلب أو حجة غير معتمدة من المحامي، واستكمال البيانات بين الأقواس.",
        "- [ ] اعتماد النسخة النهائية من محامٍ مسؤول قبل التوقيع أو الإيداع.",
        "", "_تم إنشاء الهيكل آليًا من البيانات المقدمة فقط؛ لم تُنشأ وقائع أو مواد قانونية أو سوابق قضائية جديدة._", ""
    ]
    return "\n".join(lines)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to a structured JSON input file")
    parser.add_argument("-o", "--output", type=Path, help="Output Markdown path (default: stdout)")
    args = parser.parse_args(argv)
    try:
        if args.output:
            ensure_output_paths_safe([args.output], [args.input])
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = render_draft(payload)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(result, encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    if not args.output:
        print(result)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
