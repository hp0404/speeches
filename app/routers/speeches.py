# -*- coding: utf-8 -*-
"""This module contains /speeches/ router."""
import typing
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, desc, select

from app.database import get_session
from app.ml import feature_extractor
from app.models import (
    Features,
    Metadata,
    ParsedText,
    ResponseMetadata,
    ResponseMTF,
    Texts,
)

router = APIRouter(prefix="/speeches", tags=["speeches"])


@router.get("/", include_in_schema=False, response_model=typing.List[ResponseMetadata])
def read_speeches(
    offset: int = 0, limit: int = 5, session: Session = Depends(get_session)
):
    """Queries the latest entries of the metadata table."""
    query = (
        select(Metadata)
        .order_by(desc(Metadata.date), Metadata.created_at)
        .offset(offset)
        .limit(limit)
    )
    return session.exec(query).all()


@router.post("/", include_in_schema=False, response_model=typing.Dict[str, str])
def create_speeches(payload: ParsedText, session: Session = Depends(get_session)):
    """Creates new entries.

    Note: It does so by moving payload fields to corresponding tables and
    calling the ML worflow; this is a hidden endpoint that is only
    exposed to the cronjob.
    """
    metadata = Metadata(
        title=payload.title,
        date=payload.date,
        URL=payload.URL,
        category=payload.category,
    )
    metadata.text = Texts(text=payload.text)

    data_tuples = [(payload.text, metadata.id)]
    for feature in feature_extractor.stream(data_tuples):
        found_feature = Features(**feature)
        metadata.features.append(found_feature)  # pylint: disable=no-member
    session.add(metadata)
    session.commit()
    return {"id": str(metadata.id)}


@router.delete("/{id}")
def delete_speech_by_id(
    id: uuid.UUID,  # pylint: disable=redefined-builtin,invalid-name
    session: Session = Depends(get_session),
):
    """Deletes all related entries (parent and its children) by id."""
    data = session.get(Metadata, id)
    if not data:
        raise HTTPException(status_code=404, detail="Document not found")
    session.delete(data)
    session.commit()
    return {"detail": f"deleted id={id}"}


@router.get("/{id}", response_model=ResponseMTF, response_model_exclude_none=True)
def read_speech_by_id(
    id: uuid.UUID,  # pylint: disable=redefined-builtin,invalid-name
    include_features: bool = False,
    session: Session = Depends(get_session),
):
    """Reads speeches.

    Note: the response might also include text or features fields
    depending on the include_features parameter.
    """
    metadata = session.get(Metadata, id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    metadata_as_dict = metadata.dict()
    metadata_as_dict["text"] = metadata.text.text
    if include_features:
        metadata_as_dict["features"] = metadata.features
    return metadata_as_dict
