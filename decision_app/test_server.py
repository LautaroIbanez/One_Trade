#!/usr/bin/env python3
"""
Servidor de prueba simple para validar la funcionalidad básica
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import random
from datetime import datetime

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
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
                "reasoning": "Strong bullish momentum with RSI in favorable zone.",
                "created_at": datetime.now().isoformat(),
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
                "reasoning": "Bearish divergence detected.",
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
        ]
        
        mock_market_data = {
            "BTCUSDT": {"price": 67250.00, "change_24h": 2.4},
            "ETHUSDT": {"price": 3420.50, "change_24h": -1.8},
            "ADAUSDT": {"price": 0.485, "change_24h": 0.8}
        }
        
        # Route handling
        if path == '/health':
            response = {"status": "healthy", "version": "1.0.0"}
        elif path == '/api/v1/recommendations/':
            response = mock_recommendations
        elif path == '/api/v1/market-data/latest':
            response = [{"symbol": k, **v} for k, v in mock_market_data.items()]
        elif path == '/api/v1/recommendations/generate':
            # Generate new recommendation
            symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
            actions = ["BUY", "SELL", "HOLD"]
            new_rec = {
                "id": len(mock_recommendations) + 1,
                "symbol": random.choice(symbols),
                "action": random.choice(actions),
                "confidence": round(random.uniform(0.6, 0.95), 2),
                "reasoning": f"Mock recommendation generated at {datetime.now().isoformat()}",
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
            response = new_rec
        else:
            response = {"error": "Not found", "path": path}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), TestHandler)
    print("🚀 Test server running on http://localhost:8000")
    print("📊 Available endpoints:")
    print("  - GET /health")
    print("  - GET /api/v1/recommendations/")
    print("  - GET /api/v1/market-data/latest")
    print("  - GET /api/v1/recommendations/generate")
    print("\nPress Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

