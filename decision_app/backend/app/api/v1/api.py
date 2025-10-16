"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import recommendations, market_data, backtests, health, strategies, enhanced_recommendations, stats

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["recommendations"]
)

api_router.include_router(
    market_data.router,
    prefix="/market-data",
    tags=["market-data"]
)

api_router.include_router(
    backtests.router,
    prefix="/backtests",
    tags=["backtests"]
)

api_router.include_router(
    strategies.router,
    prefix="/strategies",
    tags=["strategies"]
)

api_router.include_router(
    enhanced_recommendations.router,
    prefix="/enhanced-recommendations",
    tags=["enhanced-recommendations"]
)

api_router.include_router(
    stats.router,
    tags=["stats"]
)

