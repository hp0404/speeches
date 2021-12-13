# -*- coding: utf-8 -*-
from typing import Optional
from datetime import datetime, date

from pydantic import HttpUrl
from sqlmodel import Field, SQLModel


class SchemaBase(SQLModel):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
        nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Speeches(SchemaBase, table=True):
    title: str
    text: str
    date: date
    URL: HttpUrl
    category: Optional[str] = Field(default=None) 
