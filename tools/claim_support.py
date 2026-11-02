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
    "permission": re.compile(r"\b(?:may(?!\s+not)|is permitted to|are permitted to|can)\b", re.IGNORECASE),
    "obligation": re.compile(r"\b(?:must|shall|required to|is required to)\b", re.IGNORECASE),
    "prohibition": re.compile(r"\b(?:may not|must not|shall not|is prohibited from|cannot)\b", re.IGNORECASE),
}
_ARABIC_MODAL_PATTERNS = {
    "permission": re.compile(r"(?<!لا )(?:يجوز|يحق)"),
    "obligation": re.compile(r"(?:يجب|يلتزم|يتعين)"),
    "prohibition": re.compile(r"(?:لا يجوز|يحظر|يمتنع عن)"),
}


def _modal_classes(text, patterns):
    """Return explicit modality classes for one language; absence is unknown."""
    return {
        label for label, pattern in patterns.items()
        if pattern.search(text)
    }


_EXPLICIT_POLARITY_PAIRS = (
    # Each pair is (negative form, positive form). Keep these deliberately narrow:
    # the checker should reject clear reversals, not infer unstated legal meaning.
    (
        re.compile(r"\b(?:may\s+not|cannot|is\s+not\s+permitted\s+to|are\s+not\s+permitted\s+to)\b", re.IGNORECASE),
        re.compile(r"\b(?:may(?!\s+not)|can|is\s+permitted\s+to|are\s+permitted\s+to)\b", re.IGNORECASE),
    ),
    (
        re.compile(r"\bmust\s+not\b", re.IGNORECASE),
        re.compile(r"\bmust\b(?!\s+not)", re.IGNORECASE),
    ),
    (
        re.compile(r"\bshall\s+not\b", re.IGNORECASE),
        re.compile(r"\bshall\b(?!\s+not)", re.IGNORECASE),
    ),
    (
        re.compile(r"لا\s+يجوز"),
        re.compile(r"(?<!لا\s)يجوز"),
    ),
    (
        re.compile(r"لا\s+يحق"),
        re.compile(r"(?<!لا\s)يحق"),
    ),
)


def _has_explicit_polarity_mismatch(claim, evidence):
    """Reject an explicit positive/negative reversal of the same modal predicate."""
    for negative, positive in _EXPLICIT_POLARITY_PAIRS:
        claim_negative = bool(negative.search(claim))
        claim_positive = bool(positive.search(claim))
        evidence_negative = bool(negative.search(evidence))
        evidence_positive = bool(positive.search(evidence))
        # Mixed or absent polarity is ambiguous; leave it to other safeguards.
        if claim_negative and not claim_positive and evidence_positive and not evidence_negative:
            return True
        if claim_positive and not claim_negative and evidence_negative and not evidence_positive:
            return True
    return False


def _has_modal_mismatch(claim, evidence):
    """Compare explicit modality only within the same language."""
    for patterns in (_ENGLISH_MODAL_PATTERNS, _ARABIC_MODAL_PATTERNS):
        claim_classes = _modal_classes(claim, patterns)
        evidence_classes = _modal_classes(evidence, patterns)
        if claim_classes and evidence_classes and claim_classes.isdisjoint(evidence_classes):
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
        normalized_claim = norm_fn(claim)
        normalized_evidence = norm_fn(evidence)
        if _has_modal_mismatch(normalized_claim, normalized_evidence):
            return True
        if _has_explicit_polarity_mismatch(normalized_claim, normalized_evidence):
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

        claim_terms = set(tokens_fn(claim)) - _GENERIC_TERMS
        if not claim_terms:
            continue
        evidence_terms = set(tokens_fn(evidence))
        coverage = len(claim_terms & evidence_terms) / len(claim_terms)
        if coverage < 0.65:
            return True

    return False
