#!/usr/bin/env python3
"""Script to start the final working webapp."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from webapp_v2.final_app import app

if __name__ == "__main__":
    print("="*70)
    print("🚀 One Trade v2.0 - Final Working Web Interface")
    print("="*70)
    print("📊 Dashboard: http://127.0.0.1:8054")
    print("📈 Features:")
    print("   - View all saved backtests")
    print("   - Execute backtests from webapp")
    print("   - Update data from webapp")
    print("   - Clean, simple interface")
    print("⚡ Press Ctrl+C to stop the server")
    print("="*70)
    print()
    
    try:
        app.run(debug=False, host="127.0.0.1", port=8054)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)


