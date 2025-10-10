#!/usr/bin/env python3
"""Simple script to start the working webapp."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from webapp_v2.working_app import app

if __name__ == "__main__":
    print("="*60)
    print("🚀 One Trade v2.0 - Working Web Interface")
    print("="*60)
    print("📊 Dashboard: http://127.0.0.1:8052")
    print("📈 Features:")
    print("   - View saved backtests")
    print("   - Check data status")
    print("   - Run backtests via CLI")
    print("⚡ Press Ctrl+C to stop the server")
    print("="*60)
    print()
    
    try:
        app.run(debug=False, host="127.0.0.1", port=8052)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
