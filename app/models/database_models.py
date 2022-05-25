# -*- coding: utf-8 -*-
"""This module contains SQLModel's models."""
import datetime
import typing
import uuid

from pydantic import HttpUrl
from sqlalchemy import Column, Integer
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel

__all__ = ["Features", "Metadata", "Texts", "custom_uuid"]


def custom_uuid() -> uuid.UUID:
    """Generates UUID without leading zeros."""
    # Note: Work around UUIDs with leading zeros:
    # https://github.com/tiangolo/sqlmodel/issues/25
    val = uuid.uuid4()
    while val.hex[0] == "0":
        val = uuid.uuid4()  # pragma: no cover
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
