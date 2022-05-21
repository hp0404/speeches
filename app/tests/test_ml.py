from pathlib import Path

import pytest

from app.ml import create_pipeline

patterns_directory = (
    Path(__file__).resolve().parent.parent.parent / "assets" / "patterns"
)


def test_create_pipeline():
    """Successful initialization of ML's create_pipeline
    with default values."""
    ml = create_pipeline()
    assert ml is not None


def test_create_pipeline_patterns_dir():
    """Successful initialization: interal build_phrase_matcher method
    can handle directory input."""
    ml = create_pipeline(patterns=patterns_directory)
    assert ml is not None


def test_create_pipeline_patterns_file():
    """Successful initialization: interal build_phrase_matcher method
    can handle file input."""
    ml = create_pipeline(patterns=patterns_directory / "matcher.json")
    assert ml is not None


def test_create_pipeline_patterns_raise():
    """Failed initialization: raising ValueError on invalid patterns input."""
    with pytest.raises(ValueError):
        create_pipeline(patterns="match all noun-phrases please")


@pytest.mark.parametrize("model", ["blank", "en", "invalid_name"])
def test_create_pipeline_model_failure(model):
    """Failed initialization: raising OSError on invalid model name."""
    with pytest.raises(OSError):
        create_pipeline(model=model)
