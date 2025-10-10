#!/usr/bin/env python3
"""Script to start the interactive webapp."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from webapp_v2.interactive_app import app

if __name__ == "__main__":
    # Initialize server config
    with app.server.app_context():
        app.server.config['backtest_running'] = False
        app.server.config['data_running'] = False
        app.server.config['new_backtest_completed'] = False
    
    print("="*70)
    print("🚀 One Trade v2.0 - Interactive Web Interface")
    print("="*70)
    print("📊 Dashboard: http://127.0.0.1:8053")
    print("📈 Features:")
    print("   - Interactive backtest execution")
    print("   - Real-time data updates")
    print("   - Live progress indicators")
    print("   - View saved backtests")
    print("⚡ Press Ctrl+C to stop the server")
    print("="*70)
    print()
    
    try:
        app.run(debug=False, host="127.0.0.1", port=8053)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
