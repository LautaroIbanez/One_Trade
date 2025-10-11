#!/usr/bin/env python3
"""Script to start the interactive webapp."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from webapp_v2.interactive_app import app

if __name__ == "__main__":
    print("="*70)
    print("🚀 One Trade v2.0 - Interactive Web Interface (Improved)")
    print("="*70)
    print("📊 Dashboard: http://127.0.0.1:8053")
    print("")
    print("📈 Features:")
    print("   ✓ Interactive backtest execution with ThreadPoolExecutor")
    print("   ✓ Real-time data updates")
    print("   ✓ Automatic Dashboard refresh on backtest completion")
    print("   ✓ Reactive state management with dcc.Store")
    print("   ✓ Optimized loading with caching")
    print("   ✓ Robust error handling and logging")
    print("")
    print("🔧 Improvements:")
    print("   • Replaced Flask config with Dash Store components")
    print("   • Thread-safe async operations")
    print("   • Automatic cache invalidation")
    print("   • Enhanced validation and error messages")
    print("")
    print("⚡ Press Ctrl+C to stop the server")
    print("="*70)
    print()
    
    try:
        app.run(debug=False, host="127.0.0.1", port=8053)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)
