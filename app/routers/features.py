# -*- coding: utf-8 -*-
"""This module contains /features/ router."""
import uuid
import typing

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.ml import feature_extractor
from app.models import custom_uuid
from app.models import Features, FeaturesTypes, FeaturesPayload, ResponseFeatures
from app.database import get_session

router = APIRouter(prefix="/features", tags=["features"])


@router.post("/", response_model=typing.List[ResponseFeatures])
def extract_features_from_text(data: FeaturesPayload):
    """Runs feature extraction pipeline without writing to the database."""
    features = []
    data_stream = [(data.text, custom_uuid())]
    for feature in feature_extractor.stream(data_stream):
        features.append(feature)
    if not features:
        raise HTTPException(status_code=404, detail="Features not found")
    return features


@router.get("/{document_id}", response_model=typing.List[Features])
def read_features_by_document(
    document_id: uuid.UUID,
    feature_type: typing.Optional[FeaturesTypes] = None,
    offset: int = 0,
    limit: int = 25,
    session: Session = Depends(get_session),
):
    """Reads features of a given document."""
    doc = select(Features).where(Features.document_id == document_id)
    if feature_type is not None:
        doc = doc.where(Features.feature_type == feature_type)
    features = session.exec(doc.offset(offset).limit(limit)).all()
    if not features:
        raise HTTPException(status_code=404, detail="Features not found")
    return features
