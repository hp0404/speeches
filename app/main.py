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
        "description": "Create, Read, Update, Delete: speeches",
    },
    {
        "name": "NLP pipeline",
        "description": "Classify texts",
    },
]
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version="2.0.0",
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
