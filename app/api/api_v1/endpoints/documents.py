# -*- coding: utf-8 -*-
"""This module contains /documents/ router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, desc, select

from app.db import get_session
from app.models import Metadata

router = APIRouter(prefix="/documents", tags=["ETL pipeline"])


@router.get("/latest")
def get_latest_urls(
    offset: int = 0, limit: int = 10, session: Session = Depends(get_session)
):
    query = (
        select(Metadata.url, Metadata.created_at)
        .order_by(desc(Metadata.date), Metadata.created_at)
        .offset(offset)
        .limit(limit)
    )
    return session.exec(query).all()


@router.delete("/{id}")
def delete_document_by_id(id: int, session: Session = Depends(get_session)):
    """Deletes all related entries (parent and its children) by id."""
    data = session.get(Metadata, id)
    if not data:
        raise HTTPException(status_code=404, detail="Document not found")
    session.delete(data)
    session.commit()
    return {"detail": f"deleted id={id}"}


@router.get("/{id}", response_model_exclude_none=True)
def read_document_by_id(
    id: int,
    include_themes: bool = False,
    include_text: bool = False,
    session: Session = Depends(get_session),
):
    """Reads documents.

    Note: the response might also include text or features fields
    depending on the include_features parameter.
    """
    metadata = session.get(Metadata, id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    metadata_as_dict = metadata.dict()
    if include_themes:
        metadata_as_dict["themes"] = metadata.themes
    if include_text:
        metadata_as_dict["sentences"] = metadata.sentences
    return metadata_as_dict
