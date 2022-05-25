# -*- coding: utf-8 -*-
"""This module contains SQLModel's models."""
import datetime
import enum
import typing
import uuid

from pydantic import HttpUrl
from sqlalchemy import Column, Integer
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel

from app.models.database_models import Features

__all__ = [
    "FeaturesPayload",
    "FeaturesTypes",
    "ParsedText",
    "ResponseFeatures",
    "ResponseMTF",
    "ResponseMetadata",
]


class ResponseFeatures(SQLModel):
    """Response Feature model without document & feature ids.

    Note: it is also used as a response model for a generic POST request.
    """

    feature_type: str
    feature_label: str
    match: str
    match_normalized: str

    # array workaround
    # https://github.com/tiangolo/sqlmodel/issues/178#issuecomment-1044569342
    location: typing.List[int] = Field(sa_column=Column(postgresql.ARRAY(Integer())))


class ParsedText(SQLModel):
    """Payload that POST /speeches/ endpoint expects."""

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
    # to omit 'features' fields from the response data
    # when features were not requested
    features: typing.Optional[typing.List[Features]] = None


# /features/
class FeaturesTypes(str, enum.Enum):
    """Expected feature types.

    Note: might be changed in the future as it is only
    a hint for a documentation reader -- the features
    table columns are not of ENUM type so the values
    might be different.
    """

    NE = "NE"
    NP = "NP"


class FeaturesPayload(SQLModel):
    """Payload that POST /features/ endpoint expects."""

    text: str
