import os
import pytest


def test_env_defaults():
    assert os.getenv("ENABLE_HEADLESS") in (None, "true", "false")


@pytest.mark.skipif(__import__("importlib").import_module("importlib").util.find_spec("easyocr") is None, reason="easyocr not installed")
def test_easyocr_available():
    import easyocr
    assert hasattr(easyocr, "Reader")
