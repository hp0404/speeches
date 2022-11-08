from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse

from app.api.api_v1.endpoints import documents, load
from app.core.auth import auth_request

dependencies = [Depends(auth_request)]

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(load.router, dependencies=dependencies)
api_router.include_router(documents.router, dependencies=dependencies)
