"""Optional fail-closed lexical claim-support screen for generated legal answers.

This is a conservative heuristic, not semantic entailment or lawyer review. It is
disabled unless LEGAL_CLAIM_SUPPORT_CHECK=1 is explicitly configured.
"""
import os
import re


_ENGLISH_NO_EXPIRY = re.compile(
    r"\b(?:never\s+(?:expires?|ends?|lapses?)|does\s+not\s+expire|"
    r"doesn't\s+expire|no\s+limitation\s+period|not\s+subject\s+to\s+limitation|"
    r"immune\s+from\s+limitation|cannot\s+be\s+time[- ]barred)\b",
    re.IGNORECASE,
)
_ARABIC_NO_EXPIRY = re.compile(
    r"(?:لا\s+(?:يسقط|يتقادم|ينقضي|تنقضي|يخضع|تخضع)|"
    r"بلا\s+تقادم|دون\s+تقادم|غير\s+(?:خاضع|خاضعة|قابل|قابلة)\s+للتقادم)"
    r"(?:\s+(?:ابدا|مطلقا|نهائيا))?"
)
_ENGLISH_FINITE_PERIOD = re.compile(
    r"\b(?:\d+(?:[.,]\d+)?|zero|one|two|three|four|five|six|seven|eight|"
    r"nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|"
    r"ninety|hundred|thousand)(?:[- ](?:one|two|three|four|five|six|seven|"
    r"eight|nine))?\s*(?:year|years|month|months|week|weeks|day|days)\b",
    re.IGNORECASE,
)
_ARABIC_FINITE_PERIOD = re.compile(
    # Dual-form units are complete duration expressions on their own (e.g. سنتين).
    # Other quantities require an explicit unit. Arabic-letter boundaries prevent
    # matching a number/unit fragment embedded inside a longer word.
    r"(?<![\u0621-\u064A])(?:سنتين|سنتان|عامين|عامان|شهرين|اسبوعين|يومين|"
    r"(?:\d+(?:[.,]\d+)?|واحد|واحدة|احد|احدى|اثنين|اثنتين|ثلاث|ثلاثة|"
    r"اربع|اربعة|خمس|خمسة|ست|ستة|سبع|سبعة|ثمان|ثمانية|تسع|تسعة|عشر|"
    r"عشرة|احد عشر|احدى عشرة|اثنا عشر|اثنتا عشرة|ثلاثة عشر|ثلاث عشر|"
    r"اربعة عشر|اربع عشر|خمسة عشر|خمس عشر|ستة عشر|ست عشر|سبعة عشر|"
    r"سبع عشر|ثمانية عشر|ثمان عشر|تسعة عشر|تسع عشر|عشرون|عشرين|"
    r"ثلاثون|ثلاثين|اربعون|اربعين|خمسون|خمسين|ستون|ستين|سبعون|سبعين|"
    r"ثمانون|ثمانين|تسعون|تسعين|مائه|مئة|ميه)"
    r"\s*(?:سنه|سنوات|سنين|عام|عاما|اعوام|اعواما|شهر|شهرا|شهور|اشهر|"
    r"اسبوع|اسبوعا|اسابيع|يوم|يوما|ايام))(?![\u0621-\u064A])"
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
