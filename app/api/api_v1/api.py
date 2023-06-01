# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from app.api.api_v1.endpoints import documents, embeddings, load, red_lines, sentiments
from app.core.auth import auth_request

dependencies = [Depends(auth_request)]

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(load.router, dependencies=dependencies)
api_router.include_router(documents.router, dependencies=dependencies)
api_router.include_router(red_lines.router, dependencies=dependencies)
api_router.include_router(embeddings.router, dependencies=dependencies)
api_router.include_router(sentiments.router, dependencies=dependencies)
