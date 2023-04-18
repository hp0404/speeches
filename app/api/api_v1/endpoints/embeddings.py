# -*- coding: utf-8 -*-
"""This module contains /embeddings router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import get_session
from app.models import Embeddings as database_model
from app.schemas import Embeddings as response_model

router = APIRouter(prefix="/embeddings", tags=["NLP pipeline"])


@router.get("/{id}", response_model=response_model)
def read_prediction(id: int, session: Session = Depends(get_session)):
    data = session.get(database_model, id)
    if not data:
        raise HTTPException(status_code=404, detail="Vector not found")
    return data
