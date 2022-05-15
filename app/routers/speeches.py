# -*- coding: utf-8 -*-
"""This module contains /speeches/ router."""
import uuid
import typing

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, desc, select

from app.ml import feature_extractor
from app.models import ParsedText, Metadata, Texts, Features, ResponseMeta, ResponseMTF
from app.database import get_session

router = APIRouter(prefix="/speeches", tags=["speeches"])


@router.get("/", include_in_schema=False, response_model=typing.List[ResponseMeta])
def read_speeches(
    offset: int = 0,
    limit: int = 5,
    session: Session = Depends(get_session),
):
    """Queries the latest entries of the metadata table."""
    query = (
        select(Metadata)
        .order_by(desc(Metadata.date), Metadata.created_at)
        .offset(offset)
        .limit(limit)
    )
    return session.exec(query).all()


@router.post("/", include_in_schema=False, response_model=typing.Dict[str, bool])
def create_speeches(
    payload: ParsedText,
    session: Session = Depends(get_session),
):
    """Creates speeches.

    It does so by moving payload fields to corresponding tables and
    calling the ML worflow. This is a hidden endpoint that is only
    exposed to the cronjob."""
    metadata = Metadata(
        title=payload.title,
        date=payload.date,
        URL=payload.URL,
        category=payload.category,
    )
    metadata.text = Texts(text=payload.text)

    data_tuples = [(payload.text, metadata.id)]
    for feature in feature_extractor.stream(data_tuples):
        metadata.features.append(Features(**feature))
    session.add(metadata)
    session.commit()
    return {"ok": True}


@router.get("/{id}", response_model=ResponseMTF, response_model_exclude_none=True)
def read_speech_by_id(
    id: uuid.UUID,  # pylint: disable=redefined-builtin,invalid-name
    include_features: bool = False,
    session: Session = Depends(get_session),
):
    """Reads speeches."""
    metadata = session.get(Metadata, id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")
    metadata_as_dict = metadata.dict()
    metadata_as_dict["text"] = metadata.text.text
    if include_features:
        metadata_as_dict["features"] = metadata.features
    return ResponseMTF(**metadata_as_dict)
