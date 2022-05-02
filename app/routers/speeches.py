# -*- coding: utf-8 -*-
import uuid
import typing
import collections

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.ml import feature_extractor
from app.auth import auth_request
from app.models import ParsedText, Metadata, Texts, Features, SpeechesRespose
from app.database import get_session

router = APIRouter(prefix="/speeches", tags=["speeches"])


@router.get("/", include_in_schema=False)
def read_speeches(
    offset: int = 0,
    limit: int = 5,
    session: Session = Depends(get_session),
    auth: bool = Depends(auth_request),
) -> typing.List[Metadata]:
    query = (
        select(Metadata)
        .order_by(Metadata.date.desc(), Metadata.created_at)
        .offset(offset)
        .limit(limit)
    )
    return session.exec(query).all()


@router.post("/", include_in_schema=False)
def create_speeches(
    payload: ParsedText,
    session: Session = Depends(get_session),
    auth: bool = Depends(auth_request),
) -> typing.Dict[str, bool]:
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


@router.get("/{id}", response_model=SpeechesRespose)
def read_speech_by_id(
    id: uuid.UUID,
    include_features: bool = False,
    session: Session = Depends(get_session),
    auth: bool = Depends(auth_request),
):
    if not include_features:
        doc = select(Metadata, Texts).join(Texts).where(Metadata.id == id)
        result = session.exec(doc).all()
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        for metadata, texts in result:
            return SpeechesRespose(
                id=metadata.id,
                title=metadata.title,
                text=texts.text,
                date=metadata.date,
                created_at=metadata.created_at,
                URL=metadata.URL,
                features=None,
            )
    doc = (
        select(Metadata, Texts, Features)
        .join(Texts)
        .join(Features, Metadata.id == Features.document_id)
        .where(Metadata.id == id)
    )
    result = session.exec(doc).all()
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")

    seen = set()
    storage = collections.defaultdict(list)
    for metadata, texts, features in result:
        if metadata.id not in seen:
            storage["id"] = metadata.id
            storage["title"] = metadata.title
            storage["text"] = texts.text
            storage["date"] = metadata.date
            storage["created_at"] = metadata.created_at
            storage["URL"] = metadata.URL
        storage["features"].append(features)
    return SpeechesRespose(**storage)
