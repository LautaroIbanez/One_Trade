#!/usr/bin/env python3
"""
Simple server to test CORS and basic functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Simple Test Server")

# CORS middleware
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

@app.get("/")
def read_root():
    return {"Hello": "World", "timestamp": datetime.now().isoformat()}

@app.get("/test-cors")
def test_cors():
    return {"message": "CORS working!", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/enhanced-recommendations/supported-symbols")
def get_supported_symbols():
    return ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"]

@app.get("/api/v1/enhanced-recommendations/generate/{symbol}")
def generate_recommendation(symbol: str, timeframe: str = "1d", days: int = 30):
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "days": days,
        "recommendation": "BUY",
        "confidence": 0.85,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
