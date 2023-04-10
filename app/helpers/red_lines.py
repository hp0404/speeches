# -*- coding: utf-8 -*-
"""This module red-lines text classifier."""
import typing
from pathlib import Path

import spacy

from app.schemas import RedLines

Prediction = typing.Dict[str, float]
DEFAULT_MODEL = Path(__file__).resolve().parent / "assets" / "red-lines"


class RedLinesClassifier:
    """This class is used for classifying red-lines statements
    using pre-trained textcat model."""

    def __init__(self, model: typing.Union[spacy.language.Language, None] = None):
        self.nlp = model if model is not None else spacy.load(DEFAULT_MODEL)
        self._lang = self.nlp.meta["lang"]
        self._name = self.nlp.meta["name"]
        self._version = self.nlp.meta["version"]
        try:
            self._f_score: typing.Optional[float] = self.nlp.meta["performance"][
                "cats_macro_f"
            ]
            self._model_type: typing.Optional[str] = "textcat_multilabel"
        except KeyError:
            self._f_score = None
            self._model_type = None

    @classmethod
    def load(
        cls, model: typing.Union[spacy.language.Language, None] = None
    ) -> "RedLinesClassifier":
        """A class method that returns an instance of the RedLinesClassifier
        with a pre-trained spaCy model."""
        return RedLinesClassifier(model=model)

    def predict(self, text: str) -> Prediction:
        """Given a text, return the predicted categories using the spaCy model."""
        return self.nlp(text).cats

    def store(self, text: str) -> RedLines:
        """Given a text, return red line prediction with model's metadata."""
        prediction = self.predict(text)["red line"]
        return RedLines(
            model_language=self._lang,
            model_name=self._name,
            model_type=self._model_type,
            model_version=self._version,
            model_performance=self._f_score,
            prediction=prediction,
        )
