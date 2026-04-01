"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.ws.ai_ws import router as ai_ws_router
from app.api.ws.builds_ws import router as builds_ws_router
from app.api.ws.devices_ws import router as devices_ws_router
from app.api.ws.logs_ws import router as logs_ws_router
from app.api.ws.monitor_ws import router as monitor_ws_router
from app.config.logging_config import setup_logging
from app.config.settings import get_settings
from app.lifecycle import app_lifespan

settings = get_settings()
setup_logging(settings.debug)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=app_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(logs_ws_router)
app.include_router(builds_ws_router)
app.include_router(monitor_ws_router)
app.include_router(devices_ws_router)
app.include_router(ai_ws_router)
