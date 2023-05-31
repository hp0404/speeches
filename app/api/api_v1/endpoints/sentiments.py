# -*- coding: utf-8 -*-
"""This module contains /sentiment router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.crud.crud_html import sentiment
from app.db.database import get_session
from app.models import Sentiment as database_model
from app.schemas import Sentiment as response_model

router = APIRouter(prefix="/sentiment", tags=["NLP pipeline"])


@router.post("/predict", response_model=response_model)
def predict_text(text: str):
    return sentiment.predict(text)


@router.get("/{id}", response_model=response_model)
def read_prediction(id: int, session: Session = Depends(get_session)):
    data = session.get(database_model, id)
    if not data:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return data
