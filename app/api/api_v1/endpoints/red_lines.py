# -*- coding: utf-8 -*-
"""This module contains /classification router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.crud.crud_html import classifier
from app.db.database import get_session
from app.models import RedLines as database_model
from app.schemas import RedLines as response_model

router = APIRouter(prefix="/classifier", tags=["NLP pipeline"])


@router.post("/predict", response_model=response_model)
def predict_text(text: str):
    return classifier.store(text)


@router.get("/{id}", response_model=response_model)
def read_prediction(id: int, session: Session = Depends(get_session)):
    data = session.get(database_model, id)
    if not data:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return data
