import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.research_inspector import (
    STATUS_METADATA_ONLY, STATUS_REVIEW, STATUS_USER_SUPPLIED, STATUS_VERIFIED,
    _valid_review_evidence_url, citation_text, research_memo,
    source_permission_evidence_ready, source_status, has_current_review_evidence,
)


def valid_source():
    return {
        "text": "Exact quoted passage.",
        "article": "12",
        "requested_as_of": "2026-10-24",
        "scope": "verified_corpus",
        "provenance": {
            "status": "registry_linked",
            "official_title": "Test instrument",
            "document_type": "law",
            "law_number": "10",
            "law_year": 2020,
            "version_label": "consolidated-2025",
            "source_url": "https://example.gov/law",
            "original_sha256": "a" * 64,
            "review_status": "verified",
            "legal_status": "in_force",
            "authenticity_verified": True,
            "status_verified": True,
            "amendment_history_verified": True,
            "collection_permission": "allowed",
            "commercial_reuse_permission": "allowed",
            "source_permission_evidence": "license ref",
            "permission_evidence": "version permission ref",
            "source_permission_register_match": True,
            "source_permission_register_collection_permission": "allowed",
            "source_permission_register_commercial_reuse_permission": "allowed",
            "permission_evidence_url": "https://example.gov/rights/collection",
            "commercial_reuse_evidence_url": "https://example.gov/rights/commercial",
            "terms_checked_on": "2026-10-20",
            "commercial_terms_checked_on": "2026-10-20",
            "effective_date": "2020-01-01",
            "repeal_date": None,
            "review_evidence": [
                {"review_event_id": i, "review_type": kind, "outcome": "pass",
                 "evidence_url": "https://example.gov/review", "reviewer": "Reviewer",
                 "notes": ("[qualified_egyptian_counsel_attested:user_id=42] reviewed" if kind == "lawyer_approval" else "reviewed"),
                 "reviewed_at": "2026-10-24 10:00:00"}
                for i, kind in enumerate((
                    "source_authenticity", "extraction_quality", "legal_status",
                    "amendment_history", "licensing", "lawyer_approval",
                ), start=1)
            ],
        },
    }


class ResearchInspectorTests(unittest.TestCase):
    def test_only_all_explicit_gates_yield_verified_operative_status(self):
        source = valid_source()
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_VERIFIED)
        for key, value in (
            ("status_verified", False),
            ("authenticity_verified", False),
            ("amendment_history_verified", False),
            ("commercial_reuse_permission", "unknown"),
            ("source_permission_evidence", ""),
            ("permission_evidence", ""),
            ("source_permission_register_match", False),
            ("source_permission_register_collection_permission", "unknown"),
            ("source_permission_register_commercial_reuse_permission", "unknown"),
            ("permission_evidence_url", None),
            ("commercial_reuse_evidence_url", None),
            ("terms_checked_on", None),
            ("commercial_terms_checked_on", None),
            ("review_status", "pending_lawyer_review"),
            ("legal_status", "under_review"),
        ):
            candidate = valid_source()
            candidate["provenance"][key] = value
            self.assertEqual(source_status(candidate, "2026-10-24"), STATUS_REVIEW, key)

    def test_malformed_review_type_and_document_type_fail_closed_without_crashing(self):
        for value in ([], {}, 7, None):
            source = valid_source()
            source["provenance"]["review_evidence"][0]["review_type"] = value
            self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW, repr(value))

        for value in ([], {}, 7, None, " "):
            source = valid_source()
            source["provenance"]["document_type"] = value
            self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW, repr(value))

    def test_verified_status_requires_https_source_and_original_file_hash(self):
        source = valid_source()
        source["provenance"].pop("original_sha256")
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

        for value in ("not-a-hash", "a" * 63, "g" * 64, None):
            source = valid_source()
            source["provenance"]["original_sha256"] = value
            self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW, repr(value))

        for value in ("http://example.gov/law", "javascript:alert(1)", "", None):
            source = valid_source()
            source["provenance"]["source_url"] = value
            self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW, repr(value))

        source = valid_source()
        source["provenance"]["official_title"] = " "
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_all_evidence_urls_reject_ambiguous_https_forms(self):
        invalid_urls = (
            " https://example.gov/evidence",
            "https://example.gov/evidence ",
            "https://example.gov/path with spaces",
            "https://user:secret@example.gov/evidence",
            "https://@example.gov/evidence",
            "https://example.gov:not-a-port/evidence",
            "https://example.gov:99999/evidence",
            "https://example.gov:0/evidence",
            "https://example.gov:/evidence",
            "https://example.gov/\tunsafe",
            None,
            "",
        )
        for value in invalid_urls:
            with self.subTest(value=value):
                self.assertFalse(_valid_review_evidence_url(value))
                source = valid_source()
                source["provenance"]["source_url"] = value
                self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

                source = valid_source()
                source["provenance"]["review_evidence"][0]["evidence_url"] = value
                self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

                source = valid_source()
                source["provenance"]["permission_evidence_url"] = value
                self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

                source = valid_source()
                source["provenance"]["commercial_reuse_evidence_url"] = value
                self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_lawyer_approval_requires_explicit_counsel_attestation_marker(self):
        source = valid_source()
        approval = next(
            item for item in source["provenance"]["review_evidence"]
            if item["review_type"] == "lawyer_approval"
        )
        approval["notes"] = "Reviewed by an ordinary platform reviewer"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)
        approval["notes"] = "[qualified_egyptian_counsel_attested:user_id=42] reviewed"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_VERIFIED)
        approval["notes"] = "[qualified_egyptian_counsel_attested:user_id=0] reviewed"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_all_latest_review_types_are_required_for_verified_status(self):
        source = valid_source()
        source["provenance"]["review_evidence"] = [
            e for e in source["provenance"]["review_evidence"] if e["review_type"] != "licensing"
        ]
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

        source = valid_source()
        source["provenance"]["review_evidence"].append({
            "review_event_id": 99, "review_type": "lawyer_approval", "outcome": "fail",
            "evidence_url": "https://example.gov/review", "reviewer": "Reviewer",
            "reviewed_at": "2026-10-25 10:00:00",
        })
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_review_evidence_requires_https_and_reviewer_identity(self):
        source = valid_source()
        source["provenance"]["review_evidence"][0]["evidence_url"] = "http://example.gov/review"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)
        source = valid_source()
        source["provenance"]["review_evidence"][0]["reviewer"] = " "
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_every_current_review_event_requires_nonempty_notes(self):
        source = valid_source()
        self.assertTrue(has_current_review_evidence(source["provenance"]))
        source["provenance"]["review_evidence"][0]["notes"] = " "
        self.assertFalse(has_current_review_evidence(source["provenance"]))
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_source_permission_evidence_ready_requires_central_register_and_urls(self):
        source = valid_source()
        provenance = source["provenance"]
        self.assertTrue(source_permission_evidence_ready(provenance))
        for field, value in (
            ("source_permission_register_match", False),
            ("source_permission_register_collection_permission", "unknown"),
            ("source_permission_register_commercial_reuse_permission", "unknown"),
            ("permission_evidence_url", "http://example.gov/rights"),
            ("commercial_reuse_evidence_url", None),
            ("terms_checked_on", None),
            ("commercial_terms_checked_on", "2999-01-01"),
            ("collection_permission", "unknown"),
            ("commercial_reuse_permission", "unknown"),
            ("source_permission_evidence", ""),
        ):
            with self.subTest(field=field):
                candidate = dict(provenance)
                candidate[field] = value
                self.assertFalse(source_permission_evidence_ready(candidate))

    def test_current_permission_review_dates_do_not_override_historical_legal_as_of_date(self):
        source = valid_source()
        self.assertEqual(source_status(source, "2020-01-01"), STATUS_VERIFIED)
        source["provenance"]["terms_checked_on"] = "2999-01-01"
        self.assertEqual(source_status(source, "2030-01-01"), STATUS_REVIEW)

    def test_future_or_repealed_version_is_not_labelled_current(self):
        source = valid_source()
        source["provenance"]["effective_date"] = "2027-01-01"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)
        source = valid_source()
        source["provenance"]["repeal_date"] = "2026-10-01"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_metadata_only_and_firm_document_statuses_are_separate(self):
        self.assertEqual(source_status({"text": "", "provenance": {}}, "2026-10-24"), STATUS_METADATA_ONLY)
        source = valid_source()
        source["scope"] = "firm_documents"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_USER_SUPPLIED)
        source = valid_source()
        source["provenance"]["document_type"] = "commentary"
        self.assertEqual(source_status(source, "2026-10-24"), "secondary_copy")

    def test_matter_linked_source_is_never_labelled_as_verified_law(self):
        source = valid_source()
        source["case_id"] = 123
        # Even malformed/mis-set corpus scope must not promote firm evidence.
        source["scope"] = "verified_corpus"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_USER_SUPPLIED)

    def test_matter_linked_source_status_does_not_depend_on_as_of_date(self):
        source = valid_source()
        source["case_id"] = 123
        self.assertEqual(source_status(source, "2026-02-30"), STATUS_USER_SUPPLIED)
        source = valid_source()
        source["scope"] = "firm_documents"
        self.assertEqual(source_status(source, "not-a-date"), STATUS_USER_SUPPLIED)

    def test_unknown_or_missing_scope_never_inherits_verified_status(self):
        for scope in (None, "", "metadata_only", "future_scope", [], {}):
            source = valid_source()
            if scope is None:
                source.pop("scope")
            else:
                source["scope"] = scope
            self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW, repr(scope))

    def test_citation_does_not_invent_today_when_as_of_is_missing(self):
        source = valid_source()
        source.pop("requested_as_of")
        self.assertIn("as of unknown", citation_text(source))

    def test_citation_uses_only_recorded_pin_cite_and_metadata(self):
        citation = citation_text(valid_source(), "2026-10-24")
        self.assertIn("Test instrument", citation)
        self.assertIn("No. 10/2020", citation)
        self.assertIn("Article 12", citation)
        source = valid_source()
        source["page"] = "17"
        self.assertIn("Page 17", citation_text(source, "2026-10-24"))
        self.assertIn("as of 2026-10-24", citation)
        self.assertIn("https://example.gov/law", citation)
        self.assertNotIn("page", citation.lower())

    def test_memo_preserves_exact_passage_and_no_source_caveat(self):
        source = valid_source()
        memo = research_memo("What is the rule?", {"answer": "Answer [1]", "sources": [source], "requested_as_of": "2026-10-24", "scope": "verified_corpus"})
        self.assertIn("Exact passage (verbatim):\nExact quoted passage.", memo)
        self.assertIn("As of: 2026-10-24", memo)
        empty = research_memo("Question", {"answer": None, "sources": [], "requested_as_of": "2026-10-24"})
        self.assertIn("No source records were returned; the search scope was not recorded.", empty)
        self.assertIn("not evidence that no applicable law exists", empty)

    def test_malformed_as_of_and_provenance_dates_fail_closed(self):
        source = valid_source()
        self.assertEqual(source_status(source, "2026-02-30"), STATUS_REVIEW)
        self.assertEqual(source_status(source, "not-a-date"), STATUS_REVIEW)
        source = valid_source()
        source["provenance"]["effective_date"] = "2026-02-30"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)
        source = valid_source()
        source["provenance"]["effective_date"] = "2026/01/01"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)
        source = valid_source()
        source["provenance"]["repeal_date"] = "not-a-date"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_malformed_nested_shapes_do_not_crash_memo_or_status(self):
        self.assertEqual(source_status({"text": "passage", "provenance": []}, "2026-10-24"), STATUS_REVIEW)
        self.assertEqual(source_status(None, "2026-10-24"), STATUS_METADATA_ONLY)
        self.assertIn("Unresolved citation", citation_text(None, "2026-10-24"))
        memo = research_memo("Question", {
            "answer": "Answer", "sources": [None, {"text": "passage", "provenance": []}],
            "requested_as_of": "2026-10-24",
        })
        self.assertIn("malformed source record", memo)
        self.assertIn("Status: outdated_or_under_review", memo)
        malformed_sources = research_memo("Question", {"sources": "not-a-list"})
        self.assertIn("Source data was malformed", malformed_sources)

    def test_memo_does_not_invent_as_of_date_when_missing_or_invalid(self):
        for value in (None, "2026-02-31", "not-a-date", 20261026):
            result = {"scope": "verified_corpus", "sources": [valid_source()]}
            if value is not None:
                result["requested_as_of"] = value
            memo = research_memo("Question", result)
            self.assertIn("As of: unknown", memo, repr(value))
            self.assertIn("search as-of date was not recorded", memo, repr(value))
            self.assertNotIn("As of: 2026-10-26", memo, repr(value))

    def test_missing_memo_scope_is_not_defaulted_to_verified_corpus(self):
        memo = research_memo("Question", {"sources": []})
        self.assertIn("Search scope: unknown", memo)
        self.assertNotIn("Search scope: verified_corpus", memo)

    def test_empty_memo_message_does_not_overstate_metadata_only_search(self):
        metadata = research_memo("Question", {"sources": [], "scope": "metadata_only"})
        self.assertIn("No matching source-catalog metadata was returned", metadata)
        self.assertIn("this search did not retrieve legal text", metadata)
        self.assertNotIn("No relevant verified passage was returned", metadata)

        firm = research_memo("Question", {"sources": [], "scope": "firm_documents"})
        self.assertIn("No relevant passage was returned from the selected matter documents", firm)

        verified = research_memo("Question", {"sources": [], "scope": "verified_corpus"})
        self.assertIn("No relevant verified passage was returned by this verified-corpus search", verified)
        self.assertIn("not evidence that no applicable law exists", verified)

    def test_non_string_passages_are_not_presented_as_verbatim_text(self):
        for malformed in (["not exact source text"], {"text": "not exact source text"}, 123):
            source = valid_source()
            source["text"] = malformed
            self.assertEqual(source_status(source, "2026-10-24"), STATUS_METADATA_ONLY)
            memo = research_memo("Question", {
                "sources": [source], "requested_as_of": "2026-10-24", "scope": "verified_corpus"
            })
            self.assertIn("(No passage text recorded; metadata-only result.)", memo)
            self.assertNotIn("not exact source text", memo)

    def test_malformed_or_future_review_timestamps_fail_closed(self):
        for value in ("not-a-date", "2026-02-30T12:00:00Z", "2999-01-01T00:00:00Z"):
            source = valid_source()
            source["provenance"]["review_evidence"][0]["reviewed_at"] = value
            self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW, value)

    def test_review_event_ids_must_be_positive_integers(self):
        for value in (0, -1, True, 1.5):
            source = valid_source()
            source["provenance"]["review_evidence"][0]["review_event_id"] = value
            self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW, repr(value))

    def test_boolean_verification_flags_do_not_accept_float_one(self):
        source = valid_source()
        source["provenance"]["status_verified"] = 1.0
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)


if __name__ == "__main__":
    unittest.main()
