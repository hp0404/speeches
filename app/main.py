# -*- coding: utf-8 -*-
from typing import List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from app.auth import auth_request
from app.models import Input, Extra, Texts
from app.database import engine
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/speeches/")
def read_speeches(offset: int = 0, limit: int = 5, auth: bool = Depends(auth_request)):
    with Session(engine) as session:
        statement = (
            select(Extra)
            .order_by(Extra.date.desc(), Extra.created_at)
            .offset(offset)
            .limit(limit)
        )
        speeches = session.exec(statement).all()
        return speeches


@app.post("/speeches/")
def create_speeches(payload: Input, auth: bool = Depends(auth_request)):
    with Session(engine) as session:
        metadata = Extra(
            title=payload.title,
            date=payload.date,
            URL=payload.URL,
            category=payload.category
        )
        texts = Texts(
            text_id=metadata.id,
            text=payload.text
        )
        session.add(metadata)
        session.add(texts)
        session.commit()
        session.refresh(metadata)
        session.refresh(texts)
        return payload
