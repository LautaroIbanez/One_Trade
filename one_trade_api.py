#!/usr/bin/env python3
"""
One Trade API - FastAPI backend for Decision App
Based on existing One Trade functionality
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add current directory to path for imports
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from config import load_config
    from one_trade.backtest import BacktestEngine
    from one_trade.strategy_extended import ExtendedStrategyFactory
except ImportError as e:
    print(f"Warning: Could not import One Trade modules: {e}")

app = FastAPI(
    title="One Trade API",
    description="FastAPI backend for One Trade Decision App",
    version="1.0.0"
)

# CORS middleware
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

# Initialize One Trade components
try:
    config = load_config("config/config.yaml")
    engine = BacktestEngine(config)
    strategy_factory = ExtendedStrategyFactory()
    print("✅ One Trade components initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize One Trade components: {e}")
    config = None
    engine = None
    strategy_factory = None

# Pydantic models
class RecommendationRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"
    days: int = 30

class RecommendationResponse(BaseModel):
    symbol: str
    recommendation: str
    confidence: float
    timestamp: str
    details: Dict[str, Any]

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    timeframe: str = "1d"
    days: int = 30

class BacktestResponse(BaseModel):
    symbol: str
    strategy: str
    total_trades: int
    win_rate: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    timestamp: str

# Routes
@app.get("/")
def read_root():
    return {
        "message": "One Trade API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "config": config is not None,
            "engine": engine is not None,
            "strategy_factory": strategy_factory is not None
        }
    }

@app.get("/api/v1/enhanced-recommendations/supported-symbols")
def get_supported_symbols():
    """Get list of supported trading symbols."""
    return ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]

@app.get("/api/v1/enhanced-recommendations/generate/{symbol}")
def generate_recommendation(
    symbol: str, 
    timeframe: str = "1d", 
    days: int = 30
):
    """Generate trading recommendation for a symbol."""
    try:
        # For now, return a mock recommendation
        # TODO: Integrate with real One Trade recommendation engine
        
        # Simple mock logic based on symbol
        symbol_upper = symbol.upper()
        if symbol_upper == "BTCUSDT":
            recommendation = "BUY"
            confidence = 0.75
        elif symbol_upper == "ETHUSDT":
            recommendation = "HOLD"
            confidence = 0.65
        elif symbol_upper == "ADAUSDT":
            recommendation = "SELL"
            confidence = 0.55
        else:
            recommendation = "HOLD"
            confidence = 0.60
        
        return RecommendationResponse(
            symbol=symbol_upper,
            recommendation=recommendation,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            details={
                "timeframe": timeframe,
                "days": days,
                "strategy": "mock_strategy",
                "indicators": {
                    "rsi": 45.2,
                    "macd": 0.001,
                    "bollinger_position": 0.6
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

@app.get("/api/v1/strategies")
def get_available_strategies():
    """Get list of available trading strategies."""
    try:
        if strategy_factory:
            strategies = strategy_factory.get_available_strategies()
        else:
            strategies = ["RSI Strategy", "MACD Strategy", "Bollinger Bands Strategy"]
        
        return {
            "strategies": strategies,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting strategies: {str(e)}")

@app.get("/api/v1/backtests/{symbol}")
def get_backtest_results(symbol: str):
    """Get backtest results for a symbol."""
    try:
        # Mock backtest results
        return BacktestResponse(
            symbol=symbol.upper(),
            strategy="RSI Strategy",
            total_trades=45,
            win_rate=0.62,
            total_return=0.15,
            sharpe_ratio=1.8,
            max_drawdown=0.08,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting backtest results: {str(e)}")

@app.post("/api/v1/backtests/run")
def run_backtest(request: BacktestRequest):
    """Run a new backtest."""
    try:
        # Mock backtest execution
        # TODO: Integrate with real One Trade backtest engine
        
        return BacktestResponse(
            symbol=request.symbol.upper(),
            strategy=request.strategy,
            total_trades=32,
            win_rate=0.68,
            total_return=0.12,
            sharpe_ratio=1.6,
            max_drawdown=0.06,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running backtest: {str(e)}")

@app.get("/api/v1/market-data/{symbol}")
def get_market_data(symbol: str, timeframe: str = "1d", days: int = 30):
    """Get market data for a symbol."""
    try:
        # Mock market data
        # TODO: Integrate with real market data source
        
        data = []
        base_price = 50000 if symbol.upper() == "BTCUSDT" else 3000
        current_time = datetime.now()
        
        for i in range(days):
            price = base_price * (1 + (i * 0.001))  # Simple mock trend
            data.append({
                "timestamp": (current_time - timedelta(days=days-i)).isoformat(),
                "price": price,
                "volume": 1000000 + (i * 1000)
            })
        
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "days": days,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting market data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🚀 One Trade API - FastAPI Backend")
    print("="*60)
    print()
    print("📡 API Documentation: http://127.0.0.1:8000/docs")
    print("🔗 API Base URL: http://127.0.0.1:8000")
    print("📊 Health Check: http://127.0.0.1:8000/health")
    print()
    print("⚡ Press Ctrl+C to stop the server")
    print("="*60)
    print()
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
