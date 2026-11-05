"""Optional fail-closed lexical claim-support screen for generated legal answers.

This is a conservative heuristic, not semantic entailment or lawyer review. It is
disabled unless LEGAL_CLAIM_SUPPORT_CHECK=1 is explicitly configured.
"""
import os
import re


_ENGLISH_NO_EXPIRY = re.compile(
    r"\b(?:never\s+(?:expires?|ends?|lapses?)|does\s+not\s+expire|"
    r"doesn't\s+expire|no\s+limitation\s+period|not\s+subject\s+to\s+limitation)\b",
    re.IGNORECASE,
)
_ARABIC_NO_EXPIRY = re.compile(
    r"(?:لا\s+(?:يسقط|يتقادم|ينقضي|تنقضي)|بلا\s+تقادم|دون\s+تقادم)"
    r"(?:\s+(?:ابدا|مطلقا|نهائيا))?"
)
_ENGLISH_FINITE_PERIOD = re.compile(
    r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|twenty|thirty|forty|"
    r"fifty|sixty|ninety|hundred)\s*[- ]?"
    r"(?:year|years|month|months|week|weeks|day|days)\b",
    re.IGNORECASE,
)
_ARABIC_FINITE_PERIOD = re.compile(
    r"(?:\d+|واحد|واحدة|اثنين|اثنتين|ثلاث|ثلاثة|اربع|اربعة|خمس|خمسة|"
    r"ست|ستة|سبع|سبعة|ثمان|ثمانية|تسع|تسعة|عشر|عشرة)"
    r"\s*(?:سنه|سنوات|شهر|اشهر|اسبوع|اسابيع|يوم|ايام)"
)
_GENERIC_TERMS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "but", "if", "then", "this", "that", "these", "those",
    "it", "its", "of", "in", "on", "at", "by", "for", "from", "to",
    "as", "under", "with", "without", "must", "may", "shall", "should",
    "يكون", "تكون", "كان", "كانت", "هو", "هي", "من", "على", "في", "الى",
    "عن", "مع", "هذا", "هذه", "ذلك", "وفقا", "بموجب", "حيث", "يجوز",
    "يجب", "يحق", "يلتزم", "يستحق",
}


_ENGLISH_MODAL_PATTERNS = {
    "permission": re.compile(
        r"\b(?:may(?!\s+not)|is permitted to|are permitted to|"
        r"is allowed to|are allowed to|can)\b",
        re.IGNORECASE,
    ),
    # Exclude negated forms from the positive class so "must not" cannot
    # simultaneously count as an obligation and a prohibition.
    "obligation": re.compile(
        r"\b(?:must(?!\s+not)|shall(?!\s+not)|"
        r"(?<!not )required to|is required to|are required to)\b",
        re.IGNORECASE,
    ),
    "prohibition": re.compile(
        r"\b(?:may not|must not|shall not|is prohibited from|cannot|"
        r"is not permitted to|are not permitted to|not permitted to|"
        r"is not allowed to|are not allowed to|not allowed to)\b",
        re.IGNORECASE,
    ),
    "non_obligation": re.compile(
        r"\b(?:not required to|need not|is not obliged to|are not obliged to|"
        r"is not obligated to|are not obligated to)\b",
        re.IGNORECASE,
    ),
}
_ARABIC_MODAL_PATTERNS = {
    "permission": re.compile(r"(?<!لا )(?:يجوز|يحق|يسمح)"),
    "obligation": re.compile(r"(?<!لا )(?:يجب|يلتزم|يتعين)"),
    "prohibition": re.compile(r"(?:لا يجوز|لا يحق|لا يسمح|يحظر|يمتنع عن)"),
    "non_obligation": re.compile(r"(?:لا يجب|لا يلتزم|لا يتعين|ليس ملزما|غير ملزم)"),
}


def _modal_classes(text, patterns):
    """Return explicit modality classes for one language; absence is unknown."""
    return {
        label for label, pattern in patterns.items()
        if pattern.search(text)
    }


def _has_modal_mismatch(claim, evidence):
    """Compare explicit, conflicting modality classes only within one language."""
    conflicts = {
        ("permission", "prohibition"),
        ("prohibition", "permission"),
        ("permission", "obligation"),
        ("obligation", "permission"),
        ("obligation", "prohibition"),
        ("prohibition", "obligation"),
        ("obligation", "non_obligation"),
        ("non_obligation", "obligation"),
    }
    for patterns in (_ENGLISH_MODAL_PATTERNS, _ARABIC_MODAL_PATTERNS):
        claim_classes = _modal_classes(claim, patterns)
        evidence_classes = _modal_classes(evidence, patterns)
        if any((claim_class, evidence_class) in conflicts
               for claim_class in claim_classes
               for evidence_class in evidence_classes):
            return True
    return False


_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_NUMBER_WORDS = {
    "zero": 0, "one": 1, "first": 1, "two": 2, "second": 2,
    "three": 3, "third": 3, "four": 4, "five": 5, "fifth": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "eighteen": 18, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100,
    "صفر": 0, "واحد": 1, "واحدة": 1, "واحده": 1,
    "اثنين": 2, "اثنتين": 2, "اثنان": 2, "اثنتان": 2,
    "ثلاث": 3, "ثلاثة": 3, "ثلاثه": 3, "اربع": 4, "أربع": 4,
    "اربعة": 4, "أربعة": 4, "خمس": 5, "خمسة": 5, "خمسه": 5,
    "ست": 6, "ستة": 6, "سته": 6, "سبع": 7, "سبعة": 7,
    "سبعه": 7, "ثمان": 8, "ثمانية": 8, "ثمانيه": 8,
    "تسع": 9, "تسعة": 9, "تسعه": 9, "عشر": 10, "عشرة": 10,
    "عشره": 10, "عشرين": 20, "ثلاثين": 30, "اربعين": 40,
    "أربعين": 40, "خمسين": 50, "ستين": 60, "سبعين": 70,
    "ثمانين": 80, "تسعين": 90, "مئة": 100, "مائة": 100,
}
_NUMERIC_UNITS = {
    "year": "year", "years": "year", "سنة": "year", "سنوات": "year",
    "month": "month", "months": "month", "شهر": "month",
    "أشهر": "month", "اشهر": "month", "شهور": "month",
    "week": "week", "weeks": "week", "أسبوع": "week",
    "اسبوع": "week", "أسابيع": "week", "اسابيع": "week",
    "day": "day", "days": "day", "يوم": "day", "أيام": "day", "ايام": "day",
    "hour": "hour", "hours": "hour", "ساعة": "hour", "ساعات": "hour",
    "minute": "minute", "minutes": "minute", "دقيقة": "minute", "دقائق": "minute",
    "percent": "percent", "percentage": "percent", "بالمئة": "percent",
    "percent": "percent", "unit": "unit", "units": "unit",
    "وحدة": "unit", "وحدات": "unit", "egp": "currency",
    "pound": "currency", "pounds": "currency", "جنيه": "currency",
    "جنيهات": "currency",
}
_CURRENCY_PREFIXES = {"egp", "pound", "pounds", "جنيه", "جنيهات"}


def _numeric_markers(text):
    """Extract numeric values and optional units, including common Arabic/English words."""
    value = str(text or "").translate(_ARABIC_DIGITS).lower()
    parts = re.findall(r"[a-z]+|[0-9]+(?:[.,][0-9]+)?|[\u0600-\u06ff]+", value)
    values = set()
    markers = set()
    for index, part in enumerate(parts):
        if re.fullmatch(r"[0-9]+(?:[.,][0-9]+)?", part):
            number = str(float(part.replace(",", "."))).rstrip("0").rstrip(".")
        elif part in _NUMBER_WORDS:
            number = str(_NUMBER_WORDS[part])
        else:
            continue
        values.add(number)
        unit = None
        if index + 1 < len(parts):
            unit = _NUMERIC_UNITS.get(parts[index + 1])
        if unit is None and index > 0:
            unit = _NUMERIC_UNITS.get(parts[index - 1])
        markers.add((number, unit))
    return values, markers


def _has_unsupported_numbers(claim, evidence):
    claim_values, claim_markers = _numeric_markers(claim)
    evidence_values, evidence_markers = _numeric_markers(evidence)
    if not claim_values.issubset(evidence_values):
        return True
    for number, unit in claim_markers:
        if unit is not None and (number, unit) not in evidence_markers:
            return True
    return False


_QUALIFIER_PATTERNS = {
    "universal": (r"\b(?:all|every|each|any)\b", r"(?:^|\s)(?:لكل|كل|جميع|كافة)(?:\s|$)"),
    "always": (r"\balways\b", r"(?:^|\s)دائما(?:\s|$)"),
    "never": (r"\bnever\b", r"(?:^|\s)(?:ابدا|أبدا)(?:\s|$)"),
    "perpetual": (r"\b(?:forever|unlimited|without\s+limit)\b", r"(?:بلا|دون)\s+(?:حدود|نهاية)"),
    "exclusive": (r"\b(?:only|solely|exclusively)\b", r"(?:^|\s)(?:فقط|حصرا)(?:\s|$)"),
    "automatic": (r"\bautomatically\b", r"(?:^|\s)تلقائيا(?:\s|$)"),
    "guaranteed": (r"\bguarantee(?:s|d)?\b", r"(?:^|\s)مضمون(?:ة)?(?:\s|$)"),
    "no_exception": (r"\b(?:without\s+exception|no\s+exceptions)\b", r"(?:بلا|دون)\s+استثناء"),
}


def _has_unsupported_qualifiers(claim, evidence):
    for patterns in _QUALIFIER_PATTERNS.values():
        claim_has = any(re.search(pattern, claim) for pattern in patterns)
        evidence_has = any(re.search(pattern, evidence) for pattern in patterns)
        if claim_has and not evidence_has:
            return True
    return False


_REVERSAL_GROUPS = (
    (
        (r"\b(?:increase|increases|increased|go\s+up|goes\s+up|rise|rises|rose)\b",),
        (r"\b(?:decrease|decreases|decreased|go\s+down|goes\s+down|fall|falls|fell)\b",),
    ),
    ((r"\b(?:before|prior\s+to|earlier)\b",), (r"\b(?:after|following|later)\b",)),
    ((r"\b(?:include|includes|included)\b",), (r"\b(?:exclude|excludes|excluded)\b",)),
    ((r"\bvalid\b",), (r"\b(?:invalid|void)\b",)),
    ((r"(?<!non-)\brenewable\b",), (r"\bnon-renewable\b|\bnot\s+renewable\b",)),
    ((r"\b(?:accept|accepts|accepted)\b",), (r"\b(?:reject|rejects|rejected|deny|denies)\b",)),
    ((r"(?<!not\s)\bpayable\b",), (r"\b(?:not\s+payable|nonpayable)\b",)),
    ((r"\bmaximum\b",), (r"\bminimum\b",)),
    ((r"\b(?:applies|apply|applied)\b",), (r"\b(?:does\s+not\s+apply|not\s+applicable)\b",)),
    ((r"(?:^|\s)(?:تزيد|يزيد|زيادة)(?:\s|$)",), (r"(?:^|\s)(?:تنقص|ينقص|انخفاض)(?:\s|$)",)),
    ((r"(?:^|\s)قبل(?:\s|$)",), (r"(?:^|\s)بعد(?:\s|$)",)),
    ((r"(?:^|\s)(?:يشمل|يشملون|تضم)(?:\s|$)",), (r"(?:^|\s)(?:يستثني|تستثني|يستبعد)(?:\s|$)",)),
    ((r"(?:^|\s)(?:صحيح|سليم)(?:\s|$)",), (r"(?:^|\s)(?:باطل|غير\s+صحيح)(?:\s|$)",)),
    ((r"(?:^|\s)(?:يقبل|تقبل|قبول)(?:\s|$)",), (r"(?:^|\s)(?:يرفض|ترفض|رفض)(?:\s|$)",)),
)


def _canonicalize_coverage_text(text):
    """Normalize a small set of faithful lexical paraphrases before coverage scoring."""
    return re.sub(
        r"\b(?:goes\s+up|go\s+up|rises?|rose|increases?|increased)\b",
        "increase",
        text,
    )


def _has_reversal_mismatch(claim, evidence):
    for positive_patterns, negative_patterns in _REVERSAL_GROUPS:
        claim_positive = any(re.search(pattern, claim) for pattern in positive_patterns)
        claim_negative = any(re.search(pattern, claim) for pattern in negative_patterns)
        evidence_positive = any(re.search(pattern, evidence) for pattern in positive_patterns)
        evidence_negative = any(re.search(pattern, evidence) for pattern in negative_patterns)
        if claim_positive and evidence_negative and not claim_negative:
            return True
        if claim_negative and evidence_positive and not claim_positive:
            return True
    return False


def claim_support_enabled():
    """Opt in explicitly; default remains off until evaluated on reviewed answers."""
    return os.environ.get("LEGAL_CLAIM_SUPPORT_CHECK", "").strip() == "1"


def _sentences(answer, mask_code):
    visible = mask_code(answer) if callable(mask_code) else answer
    for raw_line in visible.splitlines():
        line = raw_line.strip()
        if (not line or re.match(r"^#{1,6}\s+", line)
                or re.fullmatch(r"[-*_]{3,}", line)
                or re.fullmatch(r"\*\*[^*]{1,100}[:：]\*\*", line)):
            continue
        if line.endswith((":", "：")) and len(line) <= 100:
            continue
        for sentence in re.split(r"(?<=[.!?؟])\s+", line):
            sentence = re.sub(r"^(?:[-*+]\s+|\d+[.)]\s+|>\s*)", "", sentence).strip()
            if sentence:
                yield sentence


def has_unsupported_claims(answer, hits, tokens_fn, norm_fn, mask_code=None):
    """Return True if a cited factual sentence is contradicted or weakly supported.

    Every citation must resolve. A finite limitation period in the source directly
    conflicts with an unqualified 'never expires' claim. Remaining content words
    must have at least 65% lexical coverage in the cited passages. This intentionally
    prefers false refusals over silently accepting unsupported factual wording.
    """
    if not isinstance(answer, str) or not answer.strip() or not isinstance(hits, (list, tuple)):
        return True

    for sentence in _sentences(answer, mask_code):
        cited = {int(value) for value in re.findall(r"\[(\d+)\]", sentence)}
        if not cited:
            continue  # Missing citations are handled by the existing citation guard.
        if any(index < 1 or index > len(hits) for index in cited):
            return True

        evidence = " ".join(
            str(hits[index - 1].get("text") or "") for index in cited
            if isinstance(hits[index - 1], dict)
        )
        if not evidence.strip():
            return True

        claim = re.sub(r"\[\d+\]", " ", sentence)
        # Negation is legally material: compare raw text before Arabic normalization
        # can remove particles such as "لا" and invert the obligation.
        if _has_modal_mismatch(claim, evidence):
            return True
        normalized_claim = norm_fn(claim)
        normalized_evidence = norm_fn(evidence)
        if _has_modal_mismatch(normalized_claim, normalized_evidence):
            return True
        if _has_unsupported_numbers(normalized_claim, normalized_evidence):
            return True
        if _has_unsupported_qualifiers(normalized_claim, normalized_evidence):
            return True
        if _has_reversal_mismatch(normalized_claim, normalized_evidence):
            return True

        claim_says_no_expiry = bool(
            _ENGLISH_NO_EXPIRY.search(normalized_claim)
            or _ARABIC_NO_EXPIRY.search(normalized_claim)
        )
        source_has_finite_period = bool(
            _ENGLISH_FINITE_PERIOD.search(normalized_evidence)
            or _ARABIC_FINITE_PERIOD.search(normalized_evidence)
        )
        source_mentions_limitation = bool(re.search(
            r"\b(?:limitation|prescription|time[- ]bar|expiry|expiration)\b|"
            r"(?:تقادم|سقوط|انقضاء)",
            normalized_evidence,
        ))
        if claim_says_no_expiry and source_has_finite_period and source_mentions_limitation:
            return True

        claim_terms = set(tokens_fn(_canonicalize_coverage_text(normalized_claim))) - _GENERIC_TERMS
        if not claim_terms:
            continue
        evidence_terms = set(tokens_fn(_canonicalize_coverage_text(normalized_evidence)))
        coverage = len(claim_terms & evidence_terms) / len(claim_terms)
        if coverage < 0.65:
            return True

    return False
