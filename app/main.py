# -*- coding: utf-8 -*-
"""This module contains main FastAPI instance & adds tags metadata."""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from app.auth import auth_request
from app.core.config import get_settings
from app.routers import features, notifications, speeches

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
    version="0.0.4",
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
# adding router dependencies separately to keep /docs accessible
# otherwise would've set app-level dependecy
dependencies = [Depends(auth_request)]
app.include_router(speeches.router, dependencies=dependencies)
app.include_router(features.router, dependencies=dependencies)
app.include_router(notifications.router, dependencies=dependencies)


@app.get("/", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    """Default redirect."""
    return RedirectResponse(url="/docs")
