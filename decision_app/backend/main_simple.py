"""
One Trade Decision-Centric App - Backend Simple (Sin Base de Datos)
FastAPI application simplificada para testing sin dependencias de BD.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import List, Optional
import random

app = FastAPI(
    title="One Trade Decision App - Simple",
    description="Sistema inteligente de recomendaciones de trading (versión simplificada)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
mock_recommendations = [
    {
        "id": 1,
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "action": "BUY",
        "confidence": 0.85,
        "price_target": 72000.0,
        "stop_loss": 64500.0,
        "reasoning": "Strong bullish momentum with RSI in favorable zone. Volume increasing and price breaking above key resistance.",
        "strategy_weights": {
            "rsi_strategy": 0.25,
            "macd_strategy": 0.20,
            "bollinger_bands": 0.30,
            "volume_profile": 0.25
        },
        "market_conditions": {
            "trend": "bullish",
            "volatility": "medium",
            "volume": "high"
        },
        "created_at": datetime.now(timezone.utc),
        "is_active": True
    },
    {
        "id": 2,
        "symbol": "ETHUSDT",
        "timeframe": "4h",
        "action": "SELL",
        "confidence": 0.72,
        "price_target": 3100.0,
        "stop_loss": 3550.0,
        "reasoning": "Bearish divergence detected. MACD showing weakness and price approaching resistance level with decreasing volume.",
        "strategy_weights": {
            "rsi_strategy": 0.30,
            "macd_strategy": 0.35,
            "bollinger_bands": 0.20,
            "volume_profile": 0.15
        },
        "market_conditions": {
            "trend": "bearish",
            "volatility": "high",
            "volume": "medium"
        },
        "created_at": datetime.now(timezone.utc),
        "is_active": True
    },
    {
        "id": 3,
        "symbol": "ADAUSDT",
        "timeframe": "1d",
        "action": "HOLD",
        "confidence": 0.60,
        "price_target": None,
        "stop_loss": None,
        "reasoning": "Sideways consolidation pattern. Wait for clear breakout above resistance or breakdown below support before taking action.",
        "strategy_weights": {
            "rsi_strategy": 0.20,
            "macd_strategy": 0.15,
            "bollinger_bands": 0.40,
            "volume_profile": 0.25
        },
        "market_conditions": {
            "trend": "sideways",
            "volatility": "low",
            "volume": "low"
        },
        "created_at": datetime.now(timezone.utc),
        "is_active": True
    }
]

mock_market_data = {
    "BTCUSDT": {
        "price": 67250.00,
        "change_24h": 2.4,
        "high_24h": 68420.00,
        "low_24h": 65180.00,
        "volume_24h": 2400000000
    },
    "ETHUSDT": {
        "price": 3420.50,
        "change_24h": -1.8,
        "high_24h": 3520.00,
        "low_24h": 3380.00,
        "volume_24h": 1800000000
    },
    "ADAUSDT": {
        "price": 0.485,
        "change_24h": 0.8,
        "high_24h": 0.492,
        "low_24h": 0.478,
        "volume_24h": 245000000
    }
}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "development",
        "database": "mock",
    }

@app.get("/api/v1/health/")
async def detailed_health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "development",
        "database": "mock",
        "services": {
            "api": "healthy",
            "database": "mock",
        }
    }

# Recommendations endpoints
@app.get("/api/v1/recommendations/")
async def get_recommendations(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    is_active: Optional[bool] = True,
    limit: int = 100
):
    """Get recommendations with optional filtering."""
    recommendations = mock_recommendations.copy()
    
    # Apply filters
    if symbol:
        recommendations = [r for r in recommendations if r["symbol"] == symbol]
    if timeframe:
        recommendations = [r for r in recommendations if r["timeframe"] == timeframe]
    if is_active is not None:
        recommendations = [r for r in recommendations if r["is_active"] == is_active]
    
    return recommendations[:limit]

@app.get("/api/v1/recommendations/{recommendation_id}")
async def get_recommendation(recommendation_id: int):
    """Get a specific recommendation by ID."""
    for rec in mock_recommendations:
        if rec["id"] == recommendation_id:
            return rec
    
    raise HTTPException(status_code=404, detail="Recommendation not found")

@app.post("/api/v1/recommendations/generate")
async def generate_recommendation(
    symbol: str,
    timeframe: str = "1h"
):
    """Generate a new recommendation."""
    # Simple mock generation
    actions = ["BUY", "SELL", "HOLD"]
    action = random.choice(actions)
    confidence = random.uniform(0.6, 0.95)
    
    new_recommendation = {
        "id": len(mock_recommendations) + 1,
        "symbol": symbol,
        "timeframe": timeframe,
        "action": action,
        "confidence": confidence,
        "price_target": 72000.0 if action == "BUY" else 3100.0 if action == "SELL" else None,
        "stop_loss": 64500.0 if action == "BUY" else 3550.0 if action == "SELL" else None,
        "reasoning": f"Mock recommendation generated for {symbol} with {action} action and {confidence:.2%} confidence.",
        "strategy_weights": {
            "rsi_strategy": 0.25,
            "macd_strategy": 0.20,
            "bollinger_bands": 0.30,
            "volume_profile": 0.25
        },
        "market_conditions": {
            "trend": "bullish" if action == "BUY" else "bearish" if action == "SELL" else "sideways",
            "volatility": "medium",
            "volume": "high"
        },
        "created_at": datetime.now(timezone.utc),
        "is_active": True
    }
    
    mock_recommendations.append(new_recommendation)
    return new_recommendation

@app.get("/api/v1/recommendations/latest/active")
async def get_latest_active_recommendations(limit: int = 10):
    """Get the latest active recommendations."""
    active_recommendations = [r for r in mock_recommendations if r["is_active"]]
    return active_recommendations[:limit]

# Market data endpoints
@app.get("/api/v1/market-data/latest")
async def get_latest_market_data(
    symbols: Optional[str] = None
):
    """Get latest market data for specified symbols."""
    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
    else:
        symbol_list = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
    
    result = []
    for symbol in symbol_list:
        if symbol in mock_market_data:
            data = mock_market_data[symbol].copy()
            data["symbol"] = symbol
            result.append(data)
    
    return result

@app.get("/api/v1/market-data/symbols")
async def get_symbols():
    """Get all trading symbols."""
    return [
        {"symbol": "BTCUSDT", "base_asset": "BTC", "quote_asset": "USDT", "is_active": True},
        {"symbol": "ETHUSDT", "base_asset": "ETH", "quote_asset": "USDT", "is_active": True},
        {"symbol": "ADAUSDT", "base_asset": "ADA", "quote_asset": "USDT", "is_active": True},
    ]

@app.get("/api/v1/market-data/timeframes")
async def get_timeframes():
    """Get all supported timeframes."""
    return [
        {"timeframe": "1m", "description": "1 Minute", "seconds": 60, "is_active": True},
        {"timeframe": "5m", "description": "5 Minutes", "seconds": 300, "is_active": True},
        {"timeframe": "1h", "description": "1 Hour", "seconds": 3600, "is_active": True},
        {"timeframe": "4h", "description": "4 Hours", "seconds": 14400, "is_active": True},
        {"timeframe": "1d", "description": "1 Day", "seconds": 86400, "is_active": True},
    ]

# Backtest endpoints
@app.get("/api/v1/backtests/")
async def get_backtests(
    strategy_name: Optional[str] = None,
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
):
    """Get backtests with optional filtering."""
    mock_backtests = [
        {
            "id": 1,
            "name": "Multi-Strategy Portfolio (BTC/USDT)",
            "description": "Comprehensive backtest using multiple trading strategies on BTC/USDT",
            "strategy_name": "multi_strategy",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-10-01T00:00:00Z",
            "initial_capital": 10000.0,
            "status": "COMPLETED",
            "created_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc)
        }
    ]
    
    return mock_backtests[:limit]

@app.get("/api/v1/backtests/{backtest_id}")
async def get_backtest(backtest_id: int):
    """Get a specific backtest by ID."""
    if backtest_id == 1:
        return {
            "id": 1,
            "name": "Multi-Strategy Portfolio (BTC/USDT)",
            "description": "Comprehensive backtest using multiple trading strategies on BTC/USDT",
            "strategy_name": "multi_strategy",
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-10-01T00:00:00Z",
            "initial_capital": 10000.0,
            "status": "COMPLETED",
            "created_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc)
        }
    
    raise HTTPException(status_code=404, detail="Backtest not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_simple:app", host="0.0.0.0", port=8000, reload=True)

