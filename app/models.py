# -*- coding: utf-8 -*-
"""This module contains SQLModel's models."""
import datetime
import enum
import typing
import uuid

from pydantic import HttpUrl
from sqlalchemy import Column, Integer
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel


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
    # one-to-many
    features: typing.List["Features"] = Relationship(
        back_populates="meta",
        sa_relationship_kwargs={
            "primaryjoin": "Metadata.id==Features.document_id",
            "cascade": "all,delete,delete-orphan",
        },
    )
    # one-to-one
    text: "Texts" = Relationship(
        back_populates="meta",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all,delete,delete-orphan",
        },
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
        back_populates="text", sa_relationship_kwargs={"uselist": False}
    )


class ResponseFeatures(SQLModel):
    """Response Feature model without document & feature ids."""

    feature_type: str
    feature_label: str
    match: str
    match_normalized: str

    # array workaround
    # https://github.com/tiangolo/sqlmodel/issues/178#issuecomment-1044569342
    location: typing.List[int] = Field(sa_column=Column(postgresql.ARRAY(Integer())))


class Features(ResponseFeatures, table=True):
    """public.features schema."""

    feature_id: typing.Optional[int] = Field(default=None, primary_key=True, index=True)
    document_id: typing.Optional[uuid.UUID] = Field(
        nullable=False,
        default=None,
        foreign_key="metadata.id",
    )
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


# /speeches/
class ResponseMetadata(SQLModel):
    """Metadata response model."""

    id: uuid.UUID
    created_at: datetime.datetime
    date: datetime.date
    title: str
    URL: HttpUrl


class ResponseMTF(ResponseMetadata):
    """Metadata with joined text and features."""

    text: str
    # using Optional to levearage response_model_exclude_none
    # to just omit 'features' fields from the response
    # when features were not requested
    features: typing.Optional[typing.List[Features]] = None


# /features/
class FeaturesTypes(str, enum.Enum):
    """Expected feature types."""

    NE = "NE"
    NP = "NP"


class FeaturesPayload(SQLModel):
    """Input fields that POST /features/ endpoint expects."""

    text: str
