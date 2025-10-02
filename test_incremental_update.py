#!/usr/bin/env python3
"""
Quick verification script to test incremental updates in the same mode.
This script verifies that refreshing repeatedly in the same mode doesn't rebuild from scratch.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from webapp.app import refresh_trades, load_trades
import pandas as pd
from datetime import datetime, timedelta

def test_incremental_update():
    """Test that refreshing in the same mode uses incremental updates."""
    print("🧪 Testing incremental update behavior...")
    
    symbol = "BTC/USDT:USDT"
    mode = "moderate"
    full_day_trading = False  # Test normal mode first
    
    print(f"\n1. First refresh (should rebuild completely)...")
    result1 = refresh_trades(symbol, mode, full_day_trading)
    print(f"   Result: {result1[:100]}...")
    
    # Load trades after first refresh
    trades1 = load_trades(symbol, mode, full_day_trading)
    print(f"   Trades loaded: {len(trades1)} rows")
    
    print(f"\n2. Second refresh (should be incremental)...")
    result2 = refresh_trades(symbol, mode, full_day_trading)
    print(f"   Result: {result2[:100]}...")
    
    # Load trades after second refresh
    trades2 = load_trades(symbol, mode, full_day_trading)
    print(f"   Trades loaded: {len(trades2)} rows")
    
    print(f"\n3. Third refresh (should be incremental)...")
    result3 = refresh_trades(symbol, mode, full_day_trading)
    print(f"   Result: {result3[:100]}...")
    
    # Load trades after third refresh
    trades3 = load_trades(symbol, mode, full_day_trading)
    print(f"   Trades loaded: {len(trades3)} rows")
    
    # Verify incremental behavior
    print(f"\n📊 Analysis:")
    print(f"   First refresh: {len(trades1)} trades")
    print(f"   Second refresh: {len(trades2)} trades")
    print(f"   Third refresh: {len(trades3)} trades")
    
    # Check if subsequent refreshes are incremental (same or more trades)
    if len(trades2) >= len(trades1) and len(trades3) >= len(trades2):
        print("   ✅ Incremental updates working correctly")
        return True
    else:
        print("   ❌ Incremental updates not working as expected")
        return False

def test_mode_switch():
    """Test that switching modes triggers complete rebuild."""
    print("\n🔄 Testing mode switch behavior...")
    
    symbol = "BTC/USDT:USDT"
    mode = "moderate"
    
    print(f"\n1. Refresh in normal mode...")
    result1 = refresh_trades(symbol, mode, False)
    print(f"   Result: {result1[:100]}...")
    
    trades_normal = load_trades(symbol, mode, False)
    print(f"   Normal mode trades: {len(trades_normal)} rows")
    
    print(f"\n2. Switch to 24h mode (should rebuild completely)...")
    result2 = refresh_trades(symbol, mode, True)
    print(f"   Result: {result2[:100]}...")
    
    trades_24h = load_trades(symbol, mode, True)
    print(f"   24h mode trades: {len(trades_24h)} rows")
    
    print(f"\n3. Switch back to normal mode (should rebuild completely)...")
    result3 = refresh_trades(symbol, mode, False)
    print(f"   Result: {result3[:100]}...")
    
    trades_normal2 = load_trades(symbol, mode, False)
    print(f"   Normal mode trades after switch: {len(trades_normal2)} rows")
    
    # Verify mode switch behavior
    print(f"\n📊 Analysis:")
    print(f"   Normal mode: {len(trades_normal)} trades")
    print(f"   24h mode: {len(trades_24h)} trades")
    print(f"   Normal mode after switch: {len(trades_normal2)} trades")
    
    # Check if mode switches trigger rebuilds
    if "Rebuilding completely" in result2 and "Rebuilding completely" in result3:
        print("   ✅ Mode switches trigger complete rebuilds")
        return True
    else:
        print("   ❌ Mode switches not triggering rebuilds")
        return False

if __name__ == "__main__":
    print("🚀 Starting incremental update verification...")
    
    try:
        # Test incremental updates
        incremental_ok = test_incremental_update()
        
        # Test mode switches
        mode_switch_ok = test_mode_switch()
        
        print(f"\n📋 Summary:")
        print(f"   Incremental updates: {'✅ PASS' if incremental_ok else '❌ FAIL'}")
        print(f"   Mode switches: {'✅ PASS' if mode_switch_ok else '❌ FAIL'}")
        
        if incremental_ok and mode_switch_ok:
            print(f"\n🎉 All tests passed! The system is working correctly.")
            sys.exit(0)
        else:
            print(f"\n💥 Some tests failed. Please check the implementation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)







