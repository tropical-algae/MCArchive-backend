from functools import partial

import uvicorn
from fastapi import FastAPI

from mcarchive.app.api.routers import router as api_router
from mcarchive.app.utils.errors import add_exception_handler
from mcarchive.app.utils.events import add_middleware, lifespan
from mcarchive.core.config import settings
from mcarchive.core.logging import get_uvicorn_logger_config, logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    version=settings.VERSION,
    lifespan=partial(lifespan, logger=logger),
)
app.include_router(api_router, prefix=settings.API_PREFIX)
add_middleware(app=app)
add_exception_handler(app=app)


def run() -> None:
    uvicorn.run(
        "mcarchive.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_config=get_uvicorn_logger_config(),
        reload=True,
    )


if __name__ == "__main__":
    run()
