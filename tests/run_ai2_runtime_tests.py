"""Run the separate-runtime regression suite without AI-1 answer-generation coverage."""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


TEST_FILE = pathlib.Path(__file__).with_name("test_app_separate_database_runtime.py")
SPEC = importlib.util.spec_from_file_location("ai2_separate_runtime_tests", TEST_FILE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load separate-runtime regression module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SUITE = unittest.defaultTestLoader.loadTestsFromTestCase(
    MODULE.SeparateDatabaseApplicationTests
)
AI1_ONLY_TEST = "test_uploaded_matter_prompt_injection_reaches_model_only_as_untrusted_json"
FOCUSED_SUITE = unittest.TestSuite(
    test for test in SUITE if not test.id().endswith(AI1_ONLY_TEST)
)
RESULT = unittest.TextTestRunner(verbosity=2).run(FOCUSED_SUITE)
sys.exit(0 if RESULT.wasSuccessful() else 1)
