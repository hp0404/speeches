# -*- coding: utf-8 -*-
from typing import List

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

from app.auth import auth_request
from app.models import Speeches
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


@app.get("/speeches/", response_model=List[Speeches])
def read_speeches(offset: int = 0, limit: int = 5, auth: bool = Depends(auth_request)):
    with Session(engine) as session:
        statement = (
            select(Speeches)
            .order_by(Speeches.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        speeches = session.exec(statement).all()
        return speeches


@app.post("/speeches/", response_model=Speeches)
def create_speeches(speech: Speeches, auth: bool = Depends(auth_request)):
    with Session(engine) as session:
        session.add(speech)
        session.commit()
        session.refresh(speech)
        return speech
