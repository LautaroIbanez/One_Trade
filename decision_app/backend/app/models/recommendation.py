"""
Recommendation models for storing trading recommendations and their history.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Recommendation(Base):
    """Model for storing daily trading recommendations."""
    
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    price_target = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    strategy_weights = Column(JSON, nullable=True)  # Strategy contribution weights
    market_conditions = Column(JSON, nullable=True)  # Market regime analysis
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    history = relationship("RecommendationHistory", back_populates="recommendation")


class RecommendationHistory(Base):
    """Model for tracking recommendation performance and updates."""
    
    __tablename__ = "recommendation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)
    price_at_recommendation = Column(Float, nullable=False)
    price_target = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    strategy_weights = Column(JSON, nullable=True)
    market_conditions = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Performance tracking
    price_at_execution = Column(Float, nullable=True)
    execution_timestamp = Column(DateTime(timezone=True), nullable=True)
    pnl_percentage = Column(Float, nullable=True)
    pnl_absolute = Column(Float, nullable=True)
    was_profitable = Column(Boolean, nullable=True)
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="history")

