"""Conservative parsing for explicit statute references in article lookups.

This module does not establish legal validity. It only prevents an exact article
number fallback from crossing instruments when the question identifies a law.
"""
import re
import unicodedata


def _normalize_digits(value: str) -> str:
    output = []
    for character in unicodedata.normalize("NFKC", value):
        try:
            output.append(str(unicodedata.digit(character)))
        except (TypeError, ValueError):
            output.append(character)
    return "".join(output)


def _normalized_words(value: str) -> str:
    value = _normalize_digits(value).casefold()
    value = "".join(
        character for character in value
        if unicodedata.category(character) not in {"Mn", "Me"}
    )
    return value.replace("\u0640", "")


def extract_statute_reference(question: object) -> tuple[str, str] | None:
    """Return (instrument number, year) only for an explicit law reference."""
    if not isinstance(question, str) or not question.strip():
        return None
    normalized = _normalized_words(question)
    match = re.search(
        r"(?<!\w)(?:law|القانون|قانون)\s*"
        r"(?:(?:no\.?|number|رقم)\s*)?"
        r"(\d{1,4})\s*(?:of|لسنة|/)\s*(\d{4})(?!\d)",
        normalized,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1), match.group(2)


def statute_title_matches(title: object, reference: object) -> bool:
    """Match a parsed law number/year against an official registry title."""
    if not isinstance(title, str) or not title.strip():
        return False
    if (not isinstance(reference, tuple) or len(reference) != 2
            or not all(isinstance(part, str) and part.isdigit() for part in reference)):
        return False
    normalized = _normalized_words(title)
    if not re.search(r"(?<!\w)(?:law|القانون|قانون)(?!\w)", normalized, re.IGNORECASE):
        return False
    number, year = reference
    return bool(
        re.search(rf"(?<!\d){re.escape(number)}(?!\d)", normalized)
        and re.search(rf"(?<!\d){re.escape(year)}(?!\d)", normalized)
    )
