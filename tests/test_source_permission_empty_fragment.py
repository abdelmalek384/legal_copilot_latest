"""Regression tests for ambiguous source-permission URL delimiters."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_source_permission_register",
    ROOT / "tools" / "validate_source_permission_register.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_empty_fragment_delimiter_is_rejected():
    assert not MODULE._https_url("https://example.gov/law.pdf#")
    assert not MODULE._https_url("https://example.gov/law.pdf#page=")
    assert MODULE._https_url("https://example.gov/law.pdf")
    assert MODULE._https_url("https://example.gov/law.pdf?reference=%23")


def test_empty_userinfo_and_fragment_delimiter_are_rejected_together():
    assert not MODULE._https_url("https://@example.gov/law.pdf#")
