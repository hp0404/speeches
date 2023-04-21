# -*- coding: utf-8 -*-
"""This module contains /documents/ router."""
import typing

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from app.crud.crud_html import create_html_processor
from app.db.database import get_session

router = APIRouter(prefix="/upload", tags=["ETL pipeline"])


@router.post("/", response_model=typing.Dict[str, int])
def upload_html(file: UploadFile, session: Session = Depends(get_session)):
    """Uploads new documents."""
    html_contents = file.file.read()
    document = create_html_processor(html_contents)
    document.create(session)
    return {"status": 201}
