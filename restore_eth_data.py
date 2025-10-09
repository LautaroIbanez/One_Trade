"""Restore ETH data and create missing meta file."""
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timezone

def restore_eth_data():
    """Restore ETH data and create proper meta file."""
    
    # Check if ETH CSV exists
    eth_csv = Path('data/trades_final_ETH_USDT_USDT_moderate.csv')
    if not eth_csv.exists():
        print("ERROR: ETH CSV not found")
        return False
    
    # Load and verify data
    df = pd.read_csv(eth_csv)
    print(f"ETH CSV: {len(df)} trades found")
    
    if len(df) == 0:
        print("ERROR: ETH CSV is empty")
        return False
    
    # Convert entry_time to datetime
    df['entry_time'] = pd.to_datetime(df['entry_time'])
    
    # Calculate coverage
    first_trade = df['entry_time'].min()
    last_trade = df['entry_time'].max()
    coverage_days = (last_trade - first_trade).days
    
    print(f"First trade: {first_trade}")
    print(f"Last trade: {last_trade}")
    print(f"Coverage: {coverage_days} days")
    
    if coverage_days < 365:
        print(f"WARNING: Coverage {coverage_days} days < 365 minimum")
        return False
    
    # Create meta file
    meta_data = {
        "symbol": "ETH/USDT:USDT",
        "mode": "moderate",
        "total_trades": len(df),
        "first_trade": first_trade.isoformat(),
        "last_trade": last_trade.isoformat(),
        "actual_lookback_days": coverage_days,
        "last_backtest_until": last_trade.date().isoformat(),
        "last_update_attempt": datetime.now(timezone.utc).isoformat(),
        "full_day_trading": False,
        "session_trading": True,
        "validation_status": "PASSED",
        "win_rate": (len(df[df['pnl_usdt'] > 0]) / len(df) * 100) if len(df) > 0 else 0,
        "total_pnl": df['pnl_usdt'].sum() if 'pnl_usdt' in df.columns else 0,
        "created_by": "restore_script"
    }
    
    # Save meta file
    meta_file = Path('data/trades_final_ETH_USDT_USDT_moderate_meta.json')
    with open(meta_file, 'w') as f:
        json.dump(meta_data, f, indent=2)
    
    print(f"✅ Meta file created: {meta_file}")
    print(f"✅ ETH data restored: {len(df)} trades, {coverage_days} days coverage")
    
    return True

if __name__ == "__main__":
    restore_eth_data()

