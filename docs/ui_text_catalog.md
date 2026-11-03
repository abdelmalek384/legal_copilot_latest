# UI text extraction catalog

`static/i18n/ui_text_pairs.csv` is a reviewable extraction of literal Arabic/English pairs passed to `uiText(ar, en)` in `static/index.html`.

- It is a translation handoff/catalog, not a runtime replacement. The UI continues to use its existing `uiText` helper.
- Repeated pairs appear once with an `occurrences` count.
- Dynamic expressions are intentionally skipped; they need a human-authored translation rather than an inferred string.
- No legal content, user data, or secrets are extracted.

Regenerate after editing UI copy:

```bash
python tools/extract_ui_text_catalog.py
python tools/extract_ui_text_catalog.py --check
python tests/test_ui_text_catalog.py
```
