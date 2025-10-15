"""
Recommendation endpoints for the API.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.core.database import get_db
from app.models.recommendation import Recommendation, RecommendationHistory
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationHistoryResponse,
    RecommendationSummary,
)
from app.core.exceptions import NotFoundError, ValidationError
from app.services.recommendation_service import recommendation_service

router = APIRouter()


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    timeframe: Optional[str] = Query(None, description="Filter by timeframe"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
):
    """Get recommendations with optional filtering."""
    
    query = select(Recommendation)
    
    # Apply filters
    filters = []
    if symbol:
        filters.append(Recommendation.symbol == symbol)
    if timeframe:
        filters.append(Recommendation.timeframe == timeframe)
    if is_active is not None:
        filters.append(Recommendation.is_active == is_active)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Order by creation date (newest first) and limit
    query = query.order_by(desc(Recommendation.created_at)).limit(limit)
    
    result = await db.execute(query)
    recommendations = result.scalars().all()
    
    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific recommendation by ID."""
    
    query = select(Recommendation).where(Recommendation.id == recommendation_id)
    result = await db.execute(query)
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise NotFoundError(f"Recommendation with ID {recommendation_id} not found")
    
    return recommendation


@router.post("/", response_model=RecommendationResponse)
async def create_recommendation(
    recommendation: RecommendationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new recommendation."""
    
    # Validate action
    if recommendation.action not in ["BUY", "SELL", "HOLD"]:
        raise ValidationError("Action must be BUY, SELL, or HOLD")
    
    # Create recommendation
    db_recommendation = Recommendation(**recommendation.dict())
    db.add(db_recommendation)
    await db.commit()
    await db.refresh(db_recommendation)
    
    return db_recommendation


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendation(
    symbol: str = Query(..., description="Trading symbol"),
    timeframe: str = Query("1h", description="Timeframe"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new recommendation using the recommendation engine."""
    
    try:
        # Generate recommendation using the service
        recommendation = await recommendation_service.generate_recommendation(
            db=db,
            symbol=symbol,
            timeframe=timeframe
        )
        
        return recommendation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-batch", response_model=List[RecommendationResponse])
async def generate_batch_recommendations(
    symbols: List[str] = Query(..., description="List of trading symbols"),
    timeframe: str = Query("1h", description="Timeframe"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    """Generate recommendations for multiple symbols."""
    
    recommendations = []
    
    for symbol in symbols:
        try:
            recommendation = await recommendation_service.generate_recommendation(
                db=db,
                symbol=symbol,
                timeframe=timeframe
            )
            recommendations.append(recommendation)
        except Exception as e:
            # Log error but continue with other symbols
            print(f"Failed to generate recommendation for {symbol}: {str(e)}")
            continue
    
    return recommendations


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
async def update_recommendation(
    recommendation_id: int,
    recommendation_update: RecommendationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an existing recommendation."""
    
    # Get existing recommendation
    query = select(Recommendation).where(Recommendation.id == recommendation_id)
    result = await db.execute(query)
    db_recommendation = result.scalar_one_or_none()
    
    if not db_recommendation:
        raise NotFoundError(f"Recommendation with ID {recommendation_id} not found")
    
    # Update fields
    update_data = recommendation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recommendation, field, value)
    
    await db.commit()
    await db.refresh(db_recommendation)
    
    return db_recommendation


@router.delete("/{recommendation_id}")
async def delete_recommendation(
    recommendation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a recommendation (soft delete by setting is_active=False)."""
    
    # Get existing recommendation
    query = select(Recommendation).where(Recommendation.id == recommendation_id)
    result = await db.execute(query)
    db_recommendation = result.scalar_one_or_none()
    
    if not db_recommendation:
        raise NotFoundError(f"Recommendation with ID {recommendation_id} not found")
    
    # Soft delete
    db_recommendation.is_active = False
    await db.commit()
    
    return {"message": "Recommendation deleted successfully"}


@router.get("/{recommendation_id}/history", response_model=List[RecommendationHistoryResponse])
async def get_recommendation_history(
    recommendation_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
):
    """Get history for a specific recommendation."""
    
    # Verify recommendation exists
    query = select(Recommendation).where(Recommendation.id == recommendation_id)
    result = await db.execute(query)
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise NotFoundError(f"Recommendation with ID {recommendation_id} not found")
    
    # Get history
    query = (
        select(RecommendationHistory)
        .where(RecommendationHistory.recommendation_id == recommendation_id)
        .order_by(desc(RecommendationHistory.created_at))
        .limit(limit)
    )
    
    result = await db.execute(query)
    history = result.scalars().all()
    
    return history


@router.get("/summary/stats", response_model=RecommendationSummary)
async def get_recommendation_summary(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
):
    """Get recommendation summary statistics."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base query
    query = select(Recommendation).where(
        and_(
            Recommendation.created_at >= start_date,
            Recommendation.created_at <= end_date,
        )
    )
    
    if symbol:
        query = query.where(Recommendation.symbol == symbol)
    
    result = await db.execute(query)
    recommendations = result.scalars().all()
    
    if not recommendations:
        return RecommendationSummary(
            total_recommendations=0,
            buy_recommendations=0,
            sell_recommendations=0,
            hold_recommendations=0,
            average_confidence=0.0,
            profitable_recommendations=0,
            total_pnl_percentage=0.0,
            win_rate=0.0,
        )
    
    # Calculate statistics
    total_recommendations = len(recommendations)
    buy_recommendations = sum(1 for r in recommendations if r.action == "BUY")
    sell_recommendations = sum(1 for r in recommendations if r.action == "SELL")
    hold_recommendations = sum(1 for r in recommendations if r.action == "HOLD")
    average_confidence = sum(r.confidence for r in recommendations) / total_recommendations
    
    # Get history for PnL calculations
    history_query = (
        select(RecommendationHistory)
        .where(RecommendationHistory.recommendation_id.in_([r.id for r in recommendations]))
        .where(RecommendationHistory.pnl_percentage.isnot(None))
    )
    
    history_result = await db.execute(history_query)
    history = history_result.scalars().all()
    
    profitable_recommendations = sum(1 for h in history if h.was_profitable)
    total_pnl_percentage = sum(h.pnl_percentage for h in history if h.pnl_percentage)
    win_rate = profitable_recommendations / len(history) if history else 0.0
    
    return RecommendationSummary(
        total_recommendations=total_recommendations,
        buy_recommendations=buy_recommendations,
        sell_recommendations=sell_recommendations,
        hold_recommendations=hold_recommendations,
        average_confidence=average_confidence,
        profitable_recommendations=profitable_recommendations,
        total_pnl_percentage=total_pnl_percentage,
        win_rate=win_rate,
    )


@router.get("/latest/active", response_model=List[RecommendationResponse])
async def get_latest_active_recommendations(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest active recommendations."""
    
    try:
        recommendations = await recommendation_service.get_latest_recommendations(
            db=db,
            limit=limit
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{recommendation_id}/execute")
async def execute_recommendation(
    recommendation_id: int,
    execution_price: float = Query(..., description="Price at which the recommendation was executed"),
    pnl_percentage: float = Query(..., description="PnL percentage of the trade"),
    db: AsyncSession = Depends(get_db),
):
    """Record the execution of a recommendation."""
    
    try:
        recommendation = await recommendation_service.update_recommendation_performance(
            db=db,
            recommendation_id=recommendation_id,
            execution_price=execution_price,
            pnl_percentage=pnl_percentage
        )
        
        return {
            "message": "Recommendation execution recorded successfully",
            "recommendation_id": recommendation_id,
            "pnl_percentage": pnl_percentage,
            "was_profitable": pnl_percentage > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))