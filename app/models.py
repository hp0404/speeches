# -*- coding: utf-8 -*-
import uuid
import typing
import datetime

from pydantic import HttpUrl
from sqlmodel import Field, SQLModel
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


class Input(SQLModel):
    title: str
    text: str
    date: datetime.date
    URL: HttpUrl
    category: typing.Optional[str] = Field(default=None)


class Metadata(SQLModel, table=True):
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


class Texts(SQLModel, table=True):
    id: typing.Optional[uuid.UUID] = Field(
        primary_key=True,
        index=True,
        nullable=False,
        default=None,
        foreign_key="metadata.id",
    )
    text: str = Field(index=False)


class Features(SQLModel, table=True):
    feature_id: typing.Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True
    )
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
    location: typing.List[int] = Field(
        sa_column=Column(postgresql.ARRAY(Integer()))
    )
