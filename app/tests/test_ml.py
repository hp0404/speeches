from pathlib import Path

import pytest

from app.ml import create_pipeline

patterns_directory = (
    Path(__file__).resolve().parent.parent.parent / "assets" / "patterns"
)


def test_create_pipeline():
    """Making sure the pipeline works out of the box."""
    ml = create_pipeline()
    assert ml is not None


@pytest.mark.parametrize("model", ["blank", "en", "invalid_name"])
def test_create_pipeline_model_failure(model):
    """Raising error on invalid model name."""
    with pytest.raises(OSError):
        ml = create_pipeline(model=model)


def test_create_pipeline_patterns_dir():
    """Making sure that internal build_phrase_matcher method can
    handle directory input."""
    ml = create_pipeline(patterns=patterns_directory)
    assert ml is not None


def test_create_pipeline_patterns_file():
    """Making sure that internal build_phrase_matcher method can
    handle file input."""
    ml = create_pipeline(patterns=patterns_directory / "matcher.json")
    assert ml is not None


def test_create_pipeline_patterns_raise():
    """Making sure that internal build_phrase_matcher method can
    hande invalid string input."""
    with pytest.raises(ValueError):
        ml = create_pipeline(patterns="match all noun-phrases please")
