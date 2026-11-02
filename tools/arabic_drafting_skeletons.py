"""Arabic RTL drafting skeletons.

These are headings and case-data labels only, not legal advice or generated
pleadings. A lawyer must supply and review all substantive content.
"""
from __future__ import annotations

from collections.abc import Mapping


DRAFT_WARNING_AR = (
    "مسودة هيكلية فقط — يلزم استكمال الوقائع والأسانيد والطلبات ومراجعتها "
    "من محامٍ قبل الاستخدام أو التقديم."
)

_CASE_FIELDS = (
    ("court", "المحكمة"),
    ("circuit", "الدائرة"),
    ("case_number", "رقم الدعوى"),
    ("case_year", "السنة"),
    ("client", "الموكل"),
    ("opposing_party", "الخصم"),
    ("title", "موضوع الملف"),
)


def _case_value(record: Mapping[str, object], key: str) -> str:
    value = record.get(key)
    if value is None:
        return "يُستكمل"
    # Case metadata is plain text. Collapse control characters/newlines so a
    # stored label cannot inject additional document sections.
    text = " ".join(str(value).split()).strip()
    return text[:240] if text else "يُستكمل"


def build_arabic_skeleton(
    case_record: Mapping[str, object], document_type: str = "memorandum"
) -> str:
    """Return a heading-only Arabic memorandum or pleading skeleton."""
    if not isinstance(case_record, Mapping):
        raise TypeError("Case record must be a mapping")
    if document_type == "memorandum":
        title = "مذكرة"
        headings = (
            "أولاً: موجز الوقائع",
            "ثانياً: المسائل محل البحث",
            "ثالثاً: الأسانيد القانونية",
            "رابعاً: أوجه الدفاع والرد",
            "خامساً: الطلبات",
            "المستندات والمرفقات",
        )
    elif document_type == "pleading":
        title = "صحيفة دعوى"
        headings = (
            "أولاً: الوقائع",
            "ثانياً: الأساس القانوني",
            "ثالثاً: الطلبات",
            "المستندات المؤيدة",
        )
    else:
        raise ValueError("Unsupported Arabic drafting skeleton type")

    lines = [DRAFT_WARNING_AR, title, ""]
    for key, label in _CASE_FIELDS:
        lines.append(f"{label}: {_case_value(case_record, key)}")
    lines.extend(("", *headings, "", "اسم المحامي وتوقيعه: يُستكمل"))
    return "\n".join(lines)
