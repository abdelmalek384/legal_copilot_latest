"""Data-driven, conservative Arabic legal retrieval hints.

All expansions are retrieval-only: they never rewrite source text, establish legal
equivalence, or count as legal evidence. Original query tokens always remain first.
"""
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path


_LEXICON_PATH = Path(__file__).resolve().parents[1] / "data" / "arabic_legal_lexicon.json"


def _reject_duplicate_json_keys(pairs):
    """Reject ambiguous alias definitions instead of silently keeping the last one."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Arabic legal lexicon contains duplicate JSON key: {key}")
        result[key] = value
    return result


@lru_cache(maxsize=1)
def _load_lexicon():
    with _LEXICON_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle, object_pairs_hook=_reject_duplicate_json_keys)
    if not isinstance(payload, dict):
        raise ValueError("Arabic legal lexicon must be a JSON object")
    for section in ("phrase_aliases", "token_aliases"):
        entries = payload.get(section, {})
        if not isinstance(entries, dict):
            raise ValueError(f"{section} must be an object")
        for key, values in entries.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"{section} contains an empty key")
            if not isinstance(values, list) or not all(
                isinstance(value, str) and value.strip() for value in values
            ):
                raise ValueError(f"{section}[{key!r}] must be a list of non-empty strings")
    return payload


def orthographic_variants(token):
    """Return only the original token and its common ة/ه spelling counterpart."""
    if not isinstance(token, str) or not token:
        return ()
    variants = [token]
    if token.endswith("ة") and len(token) >= 4:
        variants.append(token[:-1] + "ه")
    elif token.endswith("ه") and len(token) >= 4:
        variants.append(token[:-1] + "ة")
    # Common hamza-seat spelling alternatives (e.g. مسؤول/مسئول, شؤون/شئون).
    if "ؤ" in token:
        variants.append(token.replace("ؤ", "ئ"))
    elif "ئ" in token:
        variants.append(token.replace("ئ", "ؤ"))
    return tuple(dict.fromkeys(variants))


def _is_negated_at(normalized_query, start):
    """Recognize nearby Arabic negators without treating discourse ما/لا as negation."""
    prefix = unicodedata.normalize("NFKC", normalized_query[:start])
    prefix = re.sub(r"[\u0640\u064b-\u065f\u0670]", "", prefix)
    prefix = re.split(r"[.!?؟؛,،;]|\b(?:لكن|ولكن|بل|إنما|بس)\b", prefix)[-1]
    # These common discourse expressions contain negator-looking words but are not negation.
    prefix = re.sub(r"(?:^|\s)(?:لا\s+سيما|ليس\s+فقط|لا\s+شك)\s+", " ", prefix)
    if re.search(
        r"(?:^|\s)(?:مش|مفيش|مافيش|معنديش|ماعنديش|لا|ليس|ليست|لست|لم|لن|"
        r"غير|بدون|بلا|دون|بغير)\s+(?:\S+\s+){0,5}$",
        prefix,
    ):
        return True
    # Standalone ما is ambiguous: in "ما هي الإجازة؟" it is interrogative,
    # while in "ما عنديش إجازة" / "ما حصلش على إجازة" it is negative.
    return bool(re.search(
        r"(?:^|\s)ما\s+(?:عند\w*|فيش|حصل\w*|استحق\w*|قدر\w*|طلب\w*)"
        r"\s+(?:\S+\s+){0,2}$",
        prefix,
    ) or re.search(
        # Egyptian circumfix negation: ما + verb ending in ش (e.g. ما دفعش الأجر).
        r"(?:^|\s)ما\s+\S+ش\s+(?:\S+\s+){0,2}$",
        prefix,
    ))


def _phrase_occurrences(normalized_query, normalized_phrase):
    if not normalized_phrase:
        return []
    pattern = r"(?<!\w)" + re.escape(normalized_phrase) + r"(?!\w)"
    return list(re.finditer(pattern, normalized_query))


def _positive_occurrence_starts(normalized_query, normalized_phrase):
    return [
        match.start() for match in _phrase_occurrences(normalized_query, normalized_phrase)
        if not _is_negated_at(normalized_query, match.start())
    ]


def expand_lexicon_hints(
    query, existing_tokens, tokens_fn, norm_fn, limit=48,
    phrase_aliases=None, token_aliases=None,
):
    """Append positive-occurrence legal hints and narrow spelling variants.

    Original query terms are retained. Negated occurrences do not contribute
    positive aliases; a separate positive occurrence in the same query still does.
    """
    payload = _load_lexicon()
    expanded = list(existing_tokens)
    normalized_query = norm_fn(query)

    phrase_sources = []
    if isinstance(phrase_aliases, dict):
        phrase_sources.append(phrase_aliases)
    phrase_sources.append(payload.get("phrase_aliases", {}))
    for phrases in phrase_sources:
        for phrase, aliases in phrases.items():
            if _positive_occurrence_starts(normalized_query, norm_fn(phrase)):
                expanded.extend(tokens_fn(" ".join(aliases)))

    current = set(expanded)
    token_sources = []
    if isinstance(token_aliases, dict):
        token_sources.append(token_aliases)
    token_sources.append(payload.get("token_aliases", {}))
    for aliases_by_token in token_sources:
        for token, aliases in aliases_by_token.items():
            token_terms = tokens_fn(token)
            if not token_terms or not any(term in current for term in token_terms):
                continue
            normalized_token = norm_fn(token)
            if len(token_terms) > 1:
                starts = _positive_occurrence_starts(normalized_query, normalized_token)
            else:
                starts = [
                    match.start()
                    for match in re.finditer(r"\w+", normalized_query)
                    if set(token_terms).intersection(tokens_fn(match.group()))
                    and not _is_negated_at(normalized_query, match.start())
                ]
            if starts:
                expanded.extend(tokens_fn(" ".join(aliases)))
        current = set(expanded)

    # Existing stem() already handles common clitics and plural suffixes.
    # Only add ة/ه orthographic counterparts here; avoid broad root guessing.
    for token in tuple(expanded):
        expanded.extend(orthographic_variants(token))

    return list(dict.fromkeys(expanded))[:max(1, int(limit))]
