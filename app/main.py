# -*- coding: utf-8 -*-
"""This module contains main FastAPI instance & adds tags metadata."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.api.api_v1.api import api_router
from app.core.config import get_settings

settings = get_settings()
tags_metadata = [
    {
        "name": "ETL pipeline",
        "description": "Operations with texts: CRUD",
    },
    {
        "name": "NLP pipeline",
        "description": "Operations with NLP model: extracts text statistics, noun phrases, entities",
    },
]
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version="1.0.0",
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
app.include_router(api_router)


@app.get("/", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    """Redirects to /docs page by default."""
    return RedirectResponse(url="/docs")
