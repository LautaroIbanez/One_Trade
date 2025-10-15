#!/usr/bin/env python3
"""
One Trade Decision App - Simple Backend
FastAPI backend with proper CORS configuration
"""

import json
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="One Trade Decision App API",
    description="Backend API for trading recommendations",
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
class RecommendationResponse(BaseModel):
    symbol: str
    recommendation: str
    confidence: float
    timestamp: str
    details: Dict[str, Any]

class StatsResponse(BaseModel):
    activeRecommendations: int
    totalPnL: float
    winRate: float
    maxDrawdown: float
    lastUpdate: str

# Mock Data
SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]

MOCK_RECOMMENDATIONS = {
    "BTCUSDT": {"recommendation": "BUY", "confidence": 0.75, "strategy": "RSI + MACD"},
    "ETHUSDT": {"recommendation": "HOLD", "confidence": 0.65, "strategy": "MACD"},
    "ADAUSDT": {"recommendation": "SELL", "confidence": 0.55, "strategy": "Bollinger Bands"},
    "SOLUSDT": {"recommendation": "BUY", "confidence": 0.70, "strategy": "RSI"},
    "BNBUSDT": {"recommendation": "HOLD", "confidence": 0.60, "strategy": "MACD"},
    "XRPUSDT": {"recommendation": "BUY", "confidence": 0.68, "strategy": "RSI + Bollinger"}
}

MOCK_STATS = {
    "activeRecommendations": len(SUPPORTED_SYMBOLS),
    "totalPnL": 15.2,
    "winRate": 68.0,
    "maxDrawdown": -8.0
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

@app.get("/api/v1/enhanced-recommendations/supported-symbols", response_model=List[str])
def get_supported_symbols():
    """Get list of supported trading symbols."""
    return SUPPORTED_SYMBOLS

@app.get("/api/v1/enhanced-recommendations/generate/{symbol}", response_model=RecommendationResponse)
def generate_recommendation(symbol: str, timeframe: str = "1d", days: int = 30):
    """Generate trading recommendation for a symbol."""
    symbol_upper = symbol.upper()
    
    if symbol_upper not in SUPPORTED_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol_upper} not supported")
    
    mock_data = MOCK_RECOMMENDATIONS.get(symbol_upper, {
        "recommendation": "HOLD",
        "confidence": 0.60,
        "strategy": "Default"
    })
    
    return RecommendationResponse(
        symbol=symbol_upper,
        recommendation=mock_data["recommendation"],
        confidence=mock_data["confidence"],
        timestamp=datetime.now().isoformat(),
        details={
            "timeframe": timeframe,
            "days": days,
            "strategy": mock_data["strategy"],
            "indicators": {
                "rsi": 45.2 + (hash(symbol_upper) % 30),
                "macd": 0.001 + (hash(symbol_upper) % 10) * 0.001,
                "bollinger_position": 0.5 + (hash(symbol_upper) % 10) * 0.05
            }
        }
    )

@app.get("/api/v1/enhanced-recommendations/batch/{symbols}")
def generate_batch_recommendations(symbols: str, timeframe: str = "1d", days: int = 30):
    """Generate recommendations for multiple symbols."""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    results = {}
    
    for symbol in symbol_list:
        try:
            mock_data = MOCK_RECOMMENDATIONS.get(symbol, {
                "recommendation": "HOLD",
                "confidence": 0.60,
                "strategy": "Default"
            })
            
            results[symbol] = {
                "symbol": symbol,
                "recommendation": mock_data["recommendation"],
                "confidence": mock_data["confidence"],
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "timeframe": timeframe,
                    "days": days,
                    "strategy": mock_data["strategy"]
                }
            }
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    return results

@app.get("/api/v1/stats", response_model=StatsResponse)
def get_stats():
    """Get trading statistics."""
    return StatsResponse(
        activeRecommendations=MOCK_STATS["activeRecommendations"],
        totalPnL=MOCK_STATS["totalPnL"],
        winRate=MOCK_STATS["winRate"],
        maxDrawdown=MOCK_STATS["maxDrawdown"],
        lastUpdate=datetime.now().isoformat()
    )

@app.options("/{path:path}")
def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS."""
    return {"message": "OK"}

if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🚀 One Trade Decision App - Simple Backend")
    print("="*60)
    print()
    print("📡 API Documentation: http://localhost:8000/docs")
    print("🔗 API Base URL: http://localhost:8000")
    print("📊 Health Check: http://localhost:8000/health")
    print("📋 Supported Symbols:", ", ".join(SUPPORTED_SYMBOLS))
    print()
    print("🌐 CORS Enabled for:")
    print("   - http://localhost:3000 (Frontend)")
    print("   - http://localhost:5173 (Vite)")
    print()
    print("⚡ Press Ctrl+C to stop the server")
    print("="*60)
    print()
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        exit(0)
