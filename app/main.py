"""
FastAPI application entry point.

Registers all routers, CORS middleware, and startup lifecycle hooks.

Run:
    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — create tables on startup."""
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables created")
    print(f"[INFO] LLM Provider: {settings.LLM_PROVIDER}")
    yield
    print("[INFO] Shutting down")


app = FastAPI(
    title="AI Customer Support Operations Platform",
    description="AI-powered e-commerce refund management with multi-agent LangGraph workflow",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# REST API Routers
# ---------------------------------------------------------------------------
from app.api.auth import router as auth_router
from app.api.refunds import router as refunds_router
from app.api.customers import router as customers_router
from app.api.dashboard import router as dashboard_router
from app.api.analytics import router as analytics_router
from app.api.escalations import router as escalations_router
from app.api.websocket import router as ws_router
from app.api.voice import router as voice_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(refunds_router, prefix="/api/refunds", tags=["Refunds"])
app.include_router(customers_router, prefix="/api/customers", tags=["Customers"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(escalations_router, prefix="/api/escalations", tags=["Escalations"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "version": "1.0.0",
    }
