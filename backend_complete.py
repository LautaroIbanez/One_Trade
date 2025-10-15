#!/usr/bin/env python3
"""
One Trade Decision App - Complete Backend
FastAPI backend with all endpoints needed for the frontend
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="One Trade Decision App API",
    description="Complete Backend API for trading recommendations and backtests",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend principal
        "http://localhost:3001", 
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic Models
class EnhancedRecommendationResponse(BaseModel):
    symbol: str
    current_price: float
    recommendation: str
    confidence: float
    reasoning: str
    risk_assessment: Dict[str, Any]
    strategy_signals: List[Dict[str, Any]]
    scores: Dict[str, float]
    market_context: Dict[str, Any]
    timestamp: str

class BacktestResult(BaseModel):
    symbol: str
    strategy: str
    total_return: float
    total_trades: int
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_return_num: float
    sharpe_ratio_num: float
    max_drawdown_num: float
    win_rate_num: float

class StatsResponse(BaseModel):
    activeRecommendations: int
    totalPnL: float
    winRate: float
    maxDrawdown: float
    lastUpdate: str

# Configuration
SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
SUPPORTED_STRATEGIES = ["RSI", "MACD", "Bollinger_Bands", "Moving_Average", "Stochastic"]

# Mock price data
MOCK_PRICES = {
    "BTCUSDT": 65000.0,
    "ETHUSDT": 3200.0,
    "ADAUSDT": 0.45,
    "SOLUSDT": 180.0,
    "BNBUSDT": 580.0,
    "XRPUSDT": 0.52
}

# Routes
@app.get("/")
def read_root():
    return {
        "message": "One Trade Decision App API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "supported_symbols": "/api/v1/enhanced-recommendations/supported-symbols",
            "generate_recommendation": "/api/v1/enhanced-recommendations/generate/{symbol}",
            "batch_recommendations": "/api/v1/enhanced-recommendations/batch/{symbols}",
            "stats": "/api/v1/stats",
            "backtest_strategies": "/api/v1/backtests/strategies",
            "backtest_symbols": "/api/v1/backtests/symbols",
            "quick_backtest": "/api/v1/backtests/quick-test/{symbol}",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cors_enabled": True,
        "endpoints_available": True
    }

# Enhanced Recommendations Endpoints
@app.get("/api/v1/enhanced-recommendations/supported-symbols", response_model=List[str])
def get_supported_symbols():
    """Get list of supported trading symbols."""
    return SUPPORTED_SYMBOLS

@app.get("/api/v1/enhanced-recommendations/generate/{symbol}", response_model=EnhancedRecommendationResponse)
def generate_enhanced_recommendation(
    symbol: str, 
    timeframe: str = Query("1d", description="Timeframe"),
    days: int = Query(30, description="Days for analysis")
):
    """Generate enhanced trading recommendation for a symbol."""
    symbol_upper = symbol.upper()
    
    if symbol_upper not in SUPPORTED_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol_upper} not supported")
    
    # Generate realistic mock data
    current_price = MOCK_PRICES[symbol_upper] * (1 + random.uniform(-0.05, 0.05))
    
    # Generate recommendation
    recommendations = ["BUY", "SELL", "STRONG_BUY", "STRONG_SELL", "HOLD"]
    recommendation = random.choice(recommendations)
    confidence = random.uniform(0.6, 0.95)
    
    # Generate strategy signals
    strategy_signals = []
    for strategy in random.sample(SUPPORTED_STRATEGIES, 3):
        signal = random.choice(["BUY", "SELL", "HOLD"])
        strategy_confidence = random.uniform(0.5, 0.9)
        strategy_signals.append({
            "strategy": strategy,
            "signal": signal,
            "confidence": strategy_confidence,
            "weight": random.uniform(0.2, 0.8),
            "reasoning": f"{strategy} indicator suggests {signal} signal",
            "timestamp": datetime.now().isoformat()
        })
    
    # Generate scores
    buy_score = random.uniform(0.2, 0.8)
    sell_score = random.uniform(0.1, 0.6)
    hold_score = 1 - buy_score - sell_score
    
    return EnhancedRecommendationResponse(
        symbol=symbol_upper,
        current_price=round(current_price, 2),
        recommendation=recommendation,
        confidence=confidence,
        reasoning=f"Based on technical analysis of {', '.join([s['strategy'] for s in strategy_signals])} indicators",
        risk_assessment={
            "level": random.choice(["LOW", "MEDIUM", "HIGH"]),
            "consistency": random.uniform(0.5, 0.9),
            "signal_distribution": {s["strategy"]: s["confidence"] for s in strategy_signals},
            "factors": ["market_volatility", "technical_indicators", "volume_analysis"]
        },
        strategy_signals=strategy_signals,
        scores={
            "buy_score": buy_score,
            "sell_score": sell_score,
            "hold_score": hold_score
        },
        market_context={
            "trend": random.choice(["BULLISH", "BEARISH", "NEUTRAL"]),
            "volatility": random.choice(["LOW", "MEDIUM", "HIGH"]),
            "recent_performance": {
                "day_1": random.uniform(-0.1, 0.1),
                "day_7": random.uniform(-0.2, 0.2),
                "volatility": random.uniform(0.1, 0.5)
            },
            "market_activity": {
                "volume_24h": random.uniform(1000000, 10000000),
                "trades_24h": random.randint(1000, 10000),
                "price_momentum": random.uniform(-0.05, 0.05)
            }
        },
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/v1/enhanced-recommendations/batch/{symbols}")
def generate_batch_recommendations(
    symbols: str, 
    timeframe: str = Query("1d", description="Timeframe"),
    days: int = Query(30, description="Days for analysis")
):
    """Generate recommendations for multiple symbols."""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    results = {}
    
    for symbol in symbol_list:
        if symbol in SUPPORTED_SYMBOLS:
            try:
                rec = generate_enhanced_recommendation(symbol, timeframe, days)
                results[symbol] = rec.dict()
            except Exception as e:
                results[symbol] = {"error": str(e)}
        else:
            results[symbol] = {"error": f"Symbol {symbol} not supported"}
    
    return results

# Stats Endpoint
@app.get("/api/v1/stats", response_model=StatsResponse)
def get_stats():
    """Get trading statistics."""
    return StatsResponse(
        activeRecommendations=len(SUPPORTED_SYMBOLS),
        totalPnL=random.uniform(-50, 150),
        winRate=random.uniform(45, 85),
        maxDrawdown=random.uniform(-15, -2),
        lastUpdate=datetime.now().isoformat()
    )

# Backtest Endpoints
@app.get("/api/v1/backtests/strategies", response_model=List[str])
def get_backtest_strategies():
    """Get list of available backtest strategies."""
    return SUPPORTED_STRATEGIES

@app.get("/api/v1/backtests/symbols", response_model=List[str])
def get_backtest_symbols():
    """Get list of available backtest symbols."""
    return SUPPORTED_SYMBOLS

@app.get("/api/v1/backtests/quick-test/{symbol}", response_model=BacktestResult)
def run_quick_backtest(
    symbol: str,
    strategy: str = Query(..., description="Strategy name"),
    days: int = Query(30, description="Number of days"),
    initial_capital: float = Query(10000, description="Initial capital")
):
    """Run a quick backtest for a symbol and strategy."""
    symbol_upper = symbol.upper()
    
    if symbol_upper not in SUPPORTED_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol_upper} not supported")
    
    if strategy not in SUPPORTED_STRATEGIES:
        raise HTTPException(status_code=404, detail=f"Strategy {strategy} not supported")
    
    # Generate realistic backtest results
    total_return = random.uniform(-0.3, 0.8)
    total_trades = random.randint(5, 50)
    sharpe_ratio = random.uniform(-1.5, 2.5)
    max_drawdown = random.uniform(-0.25, -0.02)
    win_rate = random.uniform(0.4, 0.8)
    
    return BacktestResult(
        symbol=symbol_upper,
        strategy=strategy,
        total_return=total_return,
        total_trades=total_trades,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        win_rate=win_rate,
        total_return_num=total_return,
        sharpe_ratio_num=sharpe_ratio,
        max_drawdown_num=max_drawdown,
        win_rate_num=win_rate
    )

@app.options("/{path:path}")
def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS."""
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🚀 One Trade Decision App - Complete Backend")
    print("="*60)
    print()
    print("📡 API Documentation: http://localhost:8001/docs")
    print("🔗 API Base URL: http://localhost:8001")
    print("📊 Health Check: http://localhost:8001/health")
    print("📋 Supported Symbols:", ", ".join(SUPPORTED_SYMBOLS))
    print("🎯 Supported Strategies:", ", ".join(SUPPORTED_STRATEGIES))
    print()
    print("🌐 CORS Enabled for:")
    print("   - http://localhost:3000 (Frontend)")
    print("   - http://localhost:5173 (Vite)")
    print()
    print("⚡ Press Ctrl+C to stop the server")
    print("="*60)
    print()
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        exit(0)
