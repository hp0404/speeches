# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

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


@app.get("/speeches/")
def read_speeches():
    with Session(engine) as session:
        return session.exec(select(Speeches)).all()


@app.post("/speeches/")
def create_speeches(speech: Speeches):
    with Session(engine) as session:
        session.add(speech)
        session.commit()
        session.refresh(speech)
        return speech
