# -*- coding: utf-8 -*-
"""This module red-lines text classifier."""
import typing

import torch
from numpy import argmax
from transformers import (  # type: ignore
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from app.schemas import Sentiment

Prediction = typing.List[float]
DEFAULT_TOKENIZER = "sismetanin/xlm_roberta_large-ru-sentiment-rusentiment"
DEFAULT_MODEL = "sismetanin/xlm_roberta_large-ru-sentiment-rusentiment"
DEFAULT_SENTIMENT_LABELS = {
    0: "negative",
    1: "neutral",
    2: "positive",
    3: "speech act",
    4: "skip",
}


class SentimentScorer:
    """This class is used for sentiment scoring using pre-trained sentiment model."""

    def __init__(
        self,
        tokenizer: str = DEFAULT_TOKENIZER,
        model: str = DEFAULT_MODEL,
        sentiment_labels: typing.Dict[int, str] = DEFAULT_SENTIMENT_LABELS,
    ) -> None:
        self._tokenizer_name = tokenizer
        self._model_name = model
        self._sentiment_labels = sentiment_labels
        self.tokenizer = AutoTokenizer.from_pretrained(self._tokenizer_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self._model_name
        )

    def get_sentiment_scores(self, text: str) -> Prediction:
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, padding=True
        )
        outputs = self.model(**inputs)
        scores = torch.softmax(outputs.logits, dim=1).tolist()[0]
        return scores

    def predict(self, text: str) -> Sentiment:
        scores = self.get_sentiment_scores(text)
        best_score_idx = argmax(scores)
        best_score_explained = self._sentiment_labels[int(best_score_idx)]
        return Sentiment(
            prediction=max(scores),
            prediction_label=best_score_explained,
            tokenizer_name=self._tokenizer_name,
            model_name=self._model_name,
        )
