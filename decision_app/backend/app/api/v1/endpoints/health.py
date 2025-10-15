"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database connectivity."""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "healthy" if result.scalar() == 1 else "unhealthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "services": {
            "api": "healthy",
            "database": db_status,
        }
    }

