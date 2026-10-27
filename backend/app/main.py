from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.api import chat, sessions, hotels
from backend.app import checkout
from backend.app.core.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
from backend.app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Единый формат ошибок
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Роутеры
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(hotels.router)
app.include_router(checkout.router)

@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok",
        "service": "backend",
        "agent": "unavailable",
        "database": "connected"
    }