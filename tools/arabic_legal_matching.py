"""Data-driven, conservative Arabic legal retrieval hints.

All expansions are retrieval-only: they never rewrite source text, establish legal
equivalence, or count as legal evidence. Original query tokens always remain first.
"""
import json
import re
from functools import lru_cache
from pathlib import Path


_LEXICON_PATH = Path(__file__).resolve().parents[1] / "data" / "arabic_legal_lexicon.json"


@lru_cache(maxsize=1)
def _load_lexicon():
    with _LEXICON_PATH.open(encoding="utf-8") as handle:
        payload = json.load(handle)
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
    return tuple(dict.fromkeys(variants))


def expand_lexicon_hints(query, existing_tokens, tokens_fn, norm_fn, limit=48):
    """Append exact-phrase, token-alias and narrow spelling hints to existing tokens."""
    payload = _load_lexicon()
    expanded = list(existing_tokens)
    normalized_query = norm_fn(query)

    def is_negated_at(start):
        # Avoid positive legal-intent hints when a colloquial negator governs
        # the matched phrase/token, e.g. "مش عايز إجازة".
        prefix = normalized_query[:start]
        return bool(re.search(r"(?:^|\s)(?:مش|ما)\s+(?:\S+\s+){0,2}$", prefix))

    for phrase, aliases in payload.get("phrase_aliases", {}).items():
        normalized_phrase = norm_fn(phrase)
        if not normalized_phrase:
            continue
        for match in re.finditer(
            r"(?<!\w)" + re.escape(normalized_phrase) + r"(?!\w)",
            normalized_query,
        ):
            if not is_negated_at(match.start()):
                expanded.extend(tokens_fn(" ".join(aliases)))
                break

    current = set(expanded)
    for token, aliases in payload.get("token_aliases", {}).items():
        token_terms = tokens_fn(token)
        if not token_terms:
            continue
        normalized_token = norm_fn(token)
        occurrences = [
            match.start()
            for match in re.finditer(
                r"(?<!\w)" + re.escape(normalized_token) + r"(?!\w)",
                normalized_query,
            )
        ] if normalized_token else []
        if any(term in current for term in token_terms) and (
            not occurrences or any(not is_negated_at(start) for start in occurrences)
        ):
            expanded.extend(tokens_fn(" ".join(aliases)))

    # Existing stem() already handles common clitics and plural suffixes.
    # Only add ة/ه orthographic counterparts here; avoid broad root guessing.
    for token in tuple(expanded):
        expanded.extend(orthographic_variants(token))

    return list(dict.fromkeys(expanded))[:max(1, int(limit))]
