# -*- coding: utf-8 -*-
"""This module contains SQLModel's models."""
import enum
import uuid
import typing
import datetime

from pydantic import HttpUrl
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Integer
from sqlalchemy.dialects import postgresql


def custom_uuid() -> uuid.UUID:
    """Generate UUID without leading zeros."""
    # Note: Work around UUIDs with leading zeros:
    # https://github.com/tiangolo/sqlmodel/issues/25
    val = uuid.uuid4()
    while val.hex[0] == "0":
        val = uuid.uuid4()
    return val

# SQLModel tables
class Metadata(SQLModel, table=True):
    """public.metadata schema."""

    id: uuid.UUID = Field(
        primary_key=True,
        index=True,
        nullable=False,
        default_factory=custom_uuid,
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, index=False
    )
    title: str
    date: datetime.date
    URL: HttpUrl
    category: typing.Optional[str] = Field(default=None)
    
    # Relationship
    features: typing.List["Features"] = Relationship(
        back_populates="meta",
        sa_relationship_kwargs={
            "primaryjoin": "Metadata.id==Features.document_id", 
        }
    )
    text: "Texts" = Relationship(
        back_populates="meta",
        # one-to-one relationship 
        sa_relationship_kwargs={"uselist": False}
    )


class Texts(SQLModel, table=True):
    """public.texts schema."""

    id: typing.Optional[uuid.UUID] = Field(
        primary_key=True,
        index=True,
        nullable=False,
        default=None,
        foreign_key="metadata.id",
    )
    text: str = Field(index=False)
    
    # Relationship
    meta: Metadata = Relationship(
        back_populates="text",
        sa_relationship_kwargs={"uselist": False}
    )


class Features(SQLModel, table=True):
    """public.features schema."""

    feature_id: typing.Optional[int] = Field(default=None, primary_key=True, index=True)
    document_id: typing.Optional[uuid.UUID] = Field(
        nullable=False,
        default=None,
        foreign_key="metadata.id",
    )
    feature_type: str
    feature_label: str
    match: str
    match_normalized: str

    # array workaround
    # https://github.com/tiangolo/sqlmodel/issues/178#issuecomment-1044569342
    location: typing.List[int] = Field(sa_column=Column(postgresql.ARRAY(Integer())))

    # Relationship
    meta: Metadata = Relationship(back_populates="features")


# SQLModels
class ParsedText(SQLModel):
    """Input fields that POST /speeches/ endpoint expects."""

    title: str
    text: str
    date: datetime.date
    URL: HttpUrl
    category: typing.Optional[str] = Field(default=None)

# Speeches
# read_speeches
class ResponseMeta(SQLModel):
    """Metadata response model."""
    id: uuid.UUID
    created_at: datetime.datetime
    date: datetime.date
    title: str
    URL: HttpUrl

class ResponseMT(ResponseMeta):
    """Metadata + text response model."""
    # extras
    # defining text as str as opposed to Texts
    # because I only care about Texts.text field
    text: str

class ResponseMTF(ResponseMeta):
    """Metadata with joined text and features."""
    text: str
    # using Optional to levearage response_model_exclude_none
    # to just omit 'features' fields from the response
    # when features were not requested
    features: typing.Optional[typing.List[Features]] = None
