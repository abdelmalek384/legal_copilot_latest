# Legal answer citation grounding

The answer validator requires each non-heading claim sentence to contain an inline source citation. Numeric claims about common durations, monetary amounts, and percentages are additionally checked against the passage text of the sources cited on that same sentence.

This prevents a cited duration or amount in one part of an answer from being treated as support for an unrelated claim that cites a different source elsewhere.

## Limitations

- This is a narrow lexical check for quantities and units covered by the application's vocabulary, including common English/Arabic number words, additive Arabic conjunction compounds such as «خمسة وعشرون» and «مائة وخمسون», and percentage symbols. It remains non-exhaustive for multiplier constructions, uncommon inflections, OCR variants, and every legal proposition.
- It does not verify that the cited source is legally relevant to the claim, that all exceptions were retrieved, or that a statutory interpretation is correct.
- The legal corpus still needs complete provenance, permitted reuse, version/effective-date review, and qualified Egyptian-lawyer approval before any source is labelled verified.
- A benchmark question is scoreable only with a qualified Egyptian-counsel reviewer role, a non-future review date, an HTTPS review-evidence URL without credentials/query/fragments, and a reviewer ID/name matching the private approved reviewer registry. Registry approval is an auditable human assertion, not independent proof of a license.
- If citation or quantity validation fails, the application should abstain from generating the answer and show the retrieved sources instead.
- Release evaluation still requires an adequately sized lawyer-approved benchmark spanning the supported practice areas.
