"""
One Trade Decision-Centric App - Backend Main Application
FastAPI application with async support and comprehensive API endpoints.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.exceptions import OneTradeException

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info("Starting One Trade Decision App backend")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down One Trade Decision App backend")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Sistema inteligente de recomendaciones de trading",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Security middleware - CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS.split(","),
        )

    # Test endpoint for CORS
    @app.get("/test-cors")
    def test_cors():
        return {"message": "CORS working!", "timestamp": datetime.now().isoformat()}

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Global exception handler
    @app.exception_handler(OneTradeException)
    async def onetrade_exception_handler(request, exc: OneTradeException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail,
            },
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )

