# -*- coding: utf-8 -*-
"""This module contains SQLModel's models."""
import datetime
import typing

from pydantic import HttpUrl
from sqlmodel import SQLModel

FakeJSON = typing.Dict[str, typing.Any]


class TextStatisticsJSON(SQLModel):
    basic: FakeJSON
    readability: FakeJSON
    diversity: FakeJSON
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
