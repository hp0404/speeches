# -*- coding: utf-8 -*-
"""This module contains SQLModel's models."""
import datetime
import typing

from pydantic import HttpUrl
from sqlmodel import SQLModel

FakeJSON = typing.Dict[str, typing.Any]


class TextStatisticsJSON(SQLModel):
    # basic
    n_chars: int
    n_letters: int
    n_words: int
    n_long_words: int
    n_complex_words: int
    n_simple_words: int
    n_unique_words: int
    n_syllables: int
    n_monosyllable_words: int
    n_polysyllable_words: int
    # readability
    automated_readability_index: float
    coleman_liau_index: float
    flesch_kincaid_grade: float
    flesch_reading_easy: float
    lix: float
    smog_index: float
    # diversity
    ttr: float
    rttr: float
    cttr: float
    sttr: float
    mttr: float
    dttr: float
    mattr: float
    msttr: float
    mtld: float
    mamtld: float
    hdd: float
    simpson_index: float
    hapax_index: float
    morphology: FakeJSON


class Sentence(SQLModel):
    document_id: int
    paragraph_id: int
    sentence_id: int
    speaker: typing.Optional[str] = None
    text: str
    text_lemmatized: str


class Theme(SQLModel):
    category: str
    theme: str


class Document(SQLModel):
    id: int
    title: str
    date: datetime.date
    url: HttpUrl
    sentences: typing.List[Sentence]
    themes: typing.Optional[typing.List[Theme]] = None


class RedLines(SQLModel):
    model_language: str
    model_name: str
    model_type: typing.Optional[str] = None
    model_version: str
    model_performance: typing.Optional[str] = None

    prediction: float


class Embeddings(SQLModel):
    model_language: str
    model_name: str
    vector: typing.List[float]


class Sentiment(SQLModel):
    model_name: str
    tokenizer_name: str
    prediction: float
    prediction_label: str
