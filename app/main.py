# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.auth import auth_request
from app.routers import speeches, features, notifications
from app.core.config import settings

tags_metadata = [
    {
        "name": "speeches",
        "description": "Operations with texts: creating & reading",
    },
    {
        "name": "features",
        "description": "Operations with NLP model: extracting features, reading features",
    },
]
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version="0.0.2",
    contact={"name": "support", "email": settings.EMAILS_FROM_EMAIL},
    openapi_tags=tags_metadata,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(speeches.router, dependencies=[Depends(auth_request)])
app.include_router(features.router, dependencies=[Depends(auth_request)])
app.include_router(notifications.router, dependencies=[Depends(auth_request)])


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url="/docs")
