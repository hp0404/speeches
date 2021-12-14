# -*- coding: utf-8 -*-
import uuid
import datetime
from typing import Optional

from pydantic import HttpUrl
from sqlmodel import Field, SQLModel


def custom_uuid() -> uuid.UUID:
    # Note: Work around UUIDs with leading zeros: https://github.com/tiangolo/sqlmodel/issues/25
    val = uuid.uuid4()
    while val.hex[0] == "0":
        val = uuid.uuid4()
    return val


class SchemaBase(SQLModel):
    id: uuid.UUID = Field(
        primary_key=True,
        index=True,
        nullable=False,
        default_factory=custom_uuid,
    )
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, 
        index=False
    )


class Speeches(SchemaBase, table=True):
    title: str = Field(index=False)
    text: str = Field(index=False)
    date: datetime.date = Field(index=False)
    URL: HttpUrl = Field(index=False)
    category: Optional[str] = Field(default=None, index=False) 
