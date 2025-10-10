"""Launch One Trade v2.0 Web Interface."""
import sys
from webapp_v2.app import app

if __name__ == "__main__":
    print("="*60)
    print("🚀 One Trade v2.0 - Web Interface")
    print("="*60)
    print()
    print("📊 Dashboard: http://127.0.0.1:8050")
    print("📈 Features:")
    print("   - Real-time backtest execution")
    print("   - Interactive equity curves")
    print("   - Trade analysis tables")
    print("   - Data management")
    print()
    print("⚡ Press Ctrl+C to stop the server")
    print("="*60)
    print()
    
    try:
        app.run(debug=False, host="127.0.0.1", port=8050)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)

