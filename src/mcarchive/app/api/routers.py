from fastapi import APIRouter

from mcarchive.app.api.endpoints import archive, token

router = APIRouter()
router.include_router(archive.router, prefix="/archive", tags=["example_event_gpt"])
router.include_router(token.router, prefix="/user", tags=["user"])
