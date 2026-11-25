import unittest
from tools.source_match_evidence import load_source_match_evidence

class SourceMatchEvidenceAdapterTests(unittest.TestCase):
    def test_bad_ids_fail_closed(self):
        self.assertIsNone(load_source_match_evidence(None, True, "source"))
        self.assertIsNone(load_source_match_evidence(None, 1, " source"))

if __name__ == "__main__":
    unittest.main()
