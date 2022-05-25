# -*- coding: utf-8 -*-
"""This module contains main FastAPI instance & adds tags metadata."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.api_v1.api import api_router

settings = get_settings()
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
    version="0.0.5",
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
