#!/usr/bin/env python3
"""
Test script for /stats endpoint
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "decision_app" / "backend"))

from app.services.stats_service import stats_service

def test_stats_service():
    """Test the stats service directly"""
    print("=" * 60)
    print("Testing StatsService")
    print("=" * 60)
    
    # Test loading backtest results
    results = stats_service.get_latest_backtest_results()
    print(f"\n📊 Found {len(results)} backtest result files\n")
    
    for result in results:
        print(f"Symbol: {result['symbol']}")
        print(f"  Total Trades: {result['total_trades']}")
        print(f"  Win Rate: {result['win_rate']:.1f}%")
        print(f"  Total P&L: {result['total_pnl']:.2f}%")
        print(f"  Max Drawdown: {result['max_drawdown']:.2f}%")
        print(f"  Profit Factor: {result['profit_factor']:.2f}")
        print(f"  Avg R-Multiple: {result['avg_r_multiple']:.2f}")
        print(f"  Last Backtest: {result['last_backtest_date']}")
        print()
    
    # Test aggregated stats
    print("=" * 60)
    print("Aggregated Statistics")
    print("=" * 60)
    
    stats = stats_service.get_aggregated_stats()
    print(f"\nActive Recommendations: {stats['active_recommendations']}")
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    print(f"Avg P&L: {stats['total_pnl']:.2f}%")
    print(f"Max Drawdown: {stats['max_drawdown']:.2f}%")
    print(f"Profit Factor: {stats['profit_factor']:.2f}")
    print(f"Avg R-Multiple: {stats['avg_r_multiple']:.2f}")
    print(f"Data Source: {stats['data_source']}")
    print(f"Last Update: {stats['last_update']}")
    
    print("\n✅ Stats service test completed successfully!")
    
    return stats

if __name__ == '__main__':
    test_stats_service()

