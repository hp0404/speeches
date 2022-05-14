# -*- coding: utf-8 -*-
"""This module contains /features/ router."""
import uuid
import typing

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.ml import feature_extractor
from app.models import custom_uuid
from app.models import Features, FeatureTypes, FeaturePayload, FeatureResponse
from app.database import get_session

router = APIRouter(prefix="/features", tags=["features"])


@router.post("/", response_model=FeatureResponse)
def extract_features_from_text(data: FeaturePayload) -> FeatureResponse:
    """Runs feature extraction pipeline without writing to the database."""
    features = []
    data_stream = [(data.text, custom_uuid())]
    for fid, feature in enumerate(feature_extractor.stream(data_stream), start=1):
        feature["feature_id"] = str(fid)
        features.append(feature)
    if not features:
        raise HTTPException(status_code=404, detail="Features not found")
    return FeatureResponse(successful=True, features=features)


@router.get("/{document_id}", response_model=typing.List[Features])
def read_features_by_document(
    document_id: uuid.UUID,
    feature_type: typing.Optional[FeatureTypes] = None,
    offset: int = 0,
    limit: int = 25,
    session: Session = Depends(get_session),
) -> typing.List[Features]:
    """Reads features of a given document."""
    doc = select(Features).where(Features.document_id == document_id)
    if feature_type is not None:
        doc = doc.where(Features.feature_type == feature_type)
    features = session.exec(doc.offset(offset).limit(limit)).all()
    if not features:
        raise HTTPException(status_code=404, detail="Document not found")
    return features
