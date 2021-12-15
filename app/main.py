# -*- coding: utf-8 -*-
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from starlette import status
from starlette.responses import RedirectResponse

from app.models import Speeches
from app.database import engine
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def auth_request(token: str = Depends(oauth2_scheme)) -> bool:
    """Using a single secret token to auth one single user.
    This has be to updated once/if we need more users; but
    the rest of the code would work without changes."""
    return token == settings.SECRET_TOKEN


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/speeches/")
def read_speeches():
    with Session(engine) as session:
        return session.exec(select(Speeches)).all()


@app.post("/speeches/")
def create_speeches(speech: Speeches, authenticated: bool = Depends(auth_request)):
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    with Session(engine) as session:
        session.add(speech)
        session.commit()
        session.refresh(speech)
        return speech
