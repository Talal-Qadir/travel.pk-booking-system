from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.admin import router as admin_router
from app.api.bookings import router as bookings_router
from app.api.fares import router as fares_router
from app.api.holds import router as holds_router
from app.api.payments import router as payments_router
from app.api.webhooks import router as webhooks_router
from app.core.config import CORS_ORIGINS
from app.core.errors import error_payload
from app.db.database import init_db
from app.db.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_database()
    yield


app = FastAPI(title="Travel.pk Booking Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "Travel.pk Booking Service",
        "status": "ok",
        "docs": "/docs",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload("HTTP_ERROR", str(detail)),
    )


app.include_router(fares_router)
app.include_router(holds_router)
app.include_router(payments_router)
app.include_router(bookings_router)
app.include_router(webhooks_router)
app.include_router(admin_router)
