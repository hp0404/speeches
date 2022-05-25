from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse

from app.api.api_v1.endpoints import features, notifications, speeches
from app.core.auth import auth_request

dependencies = [Depends(auth_request)]

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(speeches.router, dependencies=dependencies)
api_router.include_router(features.router, dependencies=dependencies)
api_router.include_router(notifications.router, dependencies=dependencies)


@api_router.get("/", include_in_schema=False)
def docs_redirect() -> RedirectResponse:
    """Redirects to /docs page by default."""
    return RedirectResponse(url="/docs")
