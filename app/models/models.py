# -*- coding: utf-8 -*-
"""This module contains SQLModel's models."""
import datetime
import typing

from pydantic import HttpUrl
from sqlalchemy import Column, Float, Integer
from sqlalchemy.dialects import postgresql
from sqlmodel import JSON, Field, Relationship, SQLModel

from app.schemas import FakeJSON


class Exports(SQLModel, table=True):
    id: typing.Optional[int] = Field(primary_key=True, default=None)
    html_contents: bytes
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    # Relationship
    # one-to-one
    meta: "Metadata" = Relationship(back_populates="raw_export")


class Metadata(SQLModel, table=True):
    __tablename__: typing.ClassVar[str] = "documents_metadata"
    id: typing.Optional[int] = Field(
        default=None, primary_key=True, index=True, foreign_key="exports.id"
    )
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    title: str
    date: datetime.date
    url: HttpUrl
    # Relationship
    # one-to-one
    raw_export: Exports = Relationship(
        back_populates="meta",
        sa_relationship_kwargs={
            "uselist": False,
            "single_parent": True,
            "cascade": "all,delete,delete-orphan",
        },
    )
    # one-to-many
    themes: typing.List["Themes"] = Relationship(
        back_populates="meta",
        sa_relationship_kwargs={
            "primaryjoin": "Metadata.id==Themes.document_id",
            "cascade": "all,delete,delete-orphan",
        },
    )
    # one-to-many
    sentences: typing.List["Sentences"] = Relationship(
        back_populates="meta",
        sa_relationship_kwargs={
            "primaryjoin": "Metadata.id==Sentences.document_id",
            "cascade": "all,delete,delete-orphan",
        },
    )


class Themes(SQLModel, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    document_id: typing.Optional[int] = Field(
        default=None, foreign_key="documents_metadata.id"
    )
    category: str
    theme: str

    # Relationship
    meta: Metadata = Relationship(back_populates="themes")


class Sentences(SQLModel, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    document_id: typing.Optional[int] = Field(
        default=None, foreign_key="documents_metadata.id"
    )
    paragraph_id: int
    sentence_id: int
    speaker: typing.Optional[str] = Field(default=None)
    text: str
    text_lemmatized: str

    # Relationship
    meta: Metadata = Relationship(back_populates="sentences")
    phrases: typing.List["ExtractedFeatures"] = Relationship(
        back_populates="sentences",
        sa_relationship_kwargs={
            "primaryjoin": "Sentences.id==ExtractedFeatures.sentence_id",
            "cascade": "all,delete,delete-orphan",
        },
    )
    textstats: "TextStatistics" = Relationship(
        back_populates="sentences",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all,delete,delete-orphan",
        },
    )
    redlines: "RedLines" = Relationship(
        back_populates="sentences",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all,delete,delete-orphan",
        },
    )
    embeddings: "Embeddings" = Relationship(
        back_populates="sentences",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all,delete,delete-orphan",
        },
    )
    sentiments: "Sentiment" = Relationship(
        back_populates="sentences",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all,delete,delete-orphan",
        },
    )


class ExtractedFeatures(SQLModel, table=True):
    __tablename__: typing.ClassVar[str] = "extracted_features"
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    sentence_id: typing.Optional[int] = Field(default=None, foreign_key="sentences.id")
    entity_type: str
    label: str
    match: str
    match_processed: str
    span_location: typing.List[int] = Field(
        sa_column=Column(postgresql.ARRAY(Integer())), nullable=False
    )
    # Relationship
    sentences: Sentences = Relationship(back_populates="phrases")


class TextStatistics(SQLModel, table=True):
    __tablename__: typing.ClassVar[str] = "text_statistics"
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    sentence_id: typing.Optional[int] = Field(default=None, foreign_key="sentences.id")

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
    # morph
    morphology: FakeJSON = Field(sa_column=Column(JSON), default={"all": "true"})

    # Relationship
    sentences: Sentences = Relationship(back_populates="textstats")

    class Config:
        arbitrary_types_allowed = True


class RedLines(SQLModel, table=True):
    __tablename__: typing.ClassVar[str] = "red_lines"
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    sentence_id: typing.Optional[int] = Field(default=None, foreign_key="sentences.id")

    model_language: str
    model_name: str
    model_type: typing.Optional[str] = Field(default=None)
    model_version: str
    model_performance: typing.Optional[float] = Field(default=None)

    prediction: float
    predicted_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    # Relationship
    sentences: Sentences = Relationship(back_populates="redlines")


class Embeddings(SQLModel, table=True):
    __tablename__: typing.ClassVar[str] = "embeddings"
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    sentence_id: typing.Optional[int] = Field(default=None, foreign_key="sentences.id")

    model_language: str
    model_name: str
    vector: typing.List[float] = Field(
        sa_column=Column(postgresql.ARRAY(Float())), nullable=False
    )

    # Relationship
    sentences: Sentences = Relationship(back_populates="embeddings")


class Sentiment(SQLModel, table=True):
    __tablename__: typing.ClassVar[str] = "sentiments"
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    sentence_id: typing.Optional[int] = Field(default=None, foreign_key="sentences.id")

    model_name: str
    tokenizer_name: str

    prediction: float
    prediction_label: str

    predicted_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    # Relationship
    sentences: Sentences = Relationship(back_populates="sentiments")
