# -*- coding: utf-8 -*-
"""This module contains /speeches/ router."""
import uuid
import typing

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, desc, select

from app.ml import feature_extractor
from app.models import ParsedText, Metadata, Texts, Features, SpeechesResponse
from app.database import get_session

router = APIRouter(prefix="/speeches", tags=["speeches"])


@router.get("/", include_in_schema=False, response_model=typing.List[Metadata])
def read_speeches(
    offset: int = 0,
    limit: int = 5,
    session: Session = Depends(get_session),
) -> typing.List[Metadata]:
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
) -> typing.Dict[str, bool]:
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
    texts = Texts(id=metadata.id, text=payload.text)
    session.add(metadata)
    session.add(texts)
    session.commit()
    session.refresh(metadata)
    session.refresh(texts)

    data_tuples = [(payload.text, metadata.id)]
    for feature in feature_extractor.stream(data_tuples):
        found_feature = Features(**feature)
        session.add(found_feature)
    session.commit()
    return {"ok": True}


@router.get("/{id}", response_model=SpeechesResponse)
def read_speech_by_id(
    id: uuid.UUID,  # pylint: disable=redefined-builtin,invalid-name
    include_features: bool = False,
    session: Session = Depends(get_session),
) -> SpeechesResponse:
    """Reads speeches."""

    metadata = session.get(Metadata, id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Document not found")

    texts = session.get(Texts, id)
    assert texts is not None, "Text not found, something went wrong."

    if include_features:
        features = session.exec(
            select(Features).where(Features.document_id == id)
        ).all()
    else:
        features = None

    return SpeechesResponse(
        id=metadata.id,
        title=metadata.title,
        text=texts.text,
        date=metadata.date,
        created_at=metadata.created_at,
        URL=metadata.URL,
        features=features,
    )
