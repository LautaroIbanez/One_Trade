#!/usr/bin/env python3
"""
Minimal server to test basic functionality.
"""

print("Starting minimal server...")

try:
    from fastapi import FastAPI
    print("FastAPI imported successfully")
except ImportError as e:
    print(f"Error importing FastAPI: {e}")
    exit(1)

try:
    from fastapi.middleware.cors import CORSMiddleware
    print("CORSMiddleware imported successfully")
except ImportError as e:
    print(f"Error importing CORSMiddleware: {e}")
    exit(1)

try:
    from datetime import datetime
    print("datetime imported successfully")
except ImportError as e:
    print(f"Error importing datetime: {e}")
    exit(1)

print("Creating FastAPI app...")
app = FastAPI(title="Minimal Test Server")

print("Adding CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Defining routes...")

@app.get("/")
def read_root():
    return {"Hello": "World", "timestamp": datetime.now().isoformat()}

@app.get("/test")
def test():
    return {"status": "OK", "message": "Minimal server working"}

@app.get("/api/v1/enhanced-recommendations/supported-symbols")
def get_supported_symbols():
    return ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"]

print("All routes defined successfully")

if __name__ == "__main__":
    print("Starting server...")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
