import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure backend directory is present in sys.path for direct module execution
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.infrastructure.database import init_db

from app.api.routers import (
    auth,
    automation,
    business,
    compliance,
    decision,
    documents,
    schemas,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Starting FlowMind AI backend in 100% Local Mode...")
    await init_db()
    yield
    logger.info("Shutting down FlowMind AI backend.")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Privacy-first intelligent business process automation "
        "(100% Local ML, SQLite, JWT Auth, Rules & Webhooks, Decision Engine, 3-Way Match, Norma 43, Verifactu & SII)"
    ),
    version="0.4.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    """Healthcheck endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "storage": settings.STORAGE_BACKEND,
        "database": "sqlite_async" if "sqlite" in settings.DATABASE_URL else "postgresql",
        "ai_engine": "pure_libraries_local",
        "auth": "jwt_rbac_api_keys",
        "automation": "rules_webhooks",
        "decision_engine": "sentinel_fact_graph_math_validator",
        "business_engines": "three_way_match_norma43_payroll_splitter",
        "compliance": "aeat_sii_verifactu_pii_redactor",
    }


# API Routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(schemas.router)
app.include_router(automation.router)
app.include_router(decision.router)
app.include_router(business.router)
app.include_router(compliance.router)