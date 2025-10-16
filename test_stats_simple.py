#!/usr/bin/env python3
"""
Simple test to verify CSV data structure for stats
"""

import pandas as pd
import glob
from pathlib import Path

def test_csv_stats():
    """Test reading and calculating stats from CSVs"""
    print("=" * 60)
    print("Testing CSV Data for Stats Calculation")
    print("=" * 60)
    
    # Find all trades_final_*.csv files
    csv_files = glob.glob("trades_final_*.csv")
    
    if not csv_files:
        print("\n❌ No trades_final_*.csv files found in current directory")
        return
    
    print(f"\n📊 Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  - {f}")
    
    print("\n" + "=" * 60)
    
    all_stats = []
    
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            
            # Extract symbol from filename
            filename = Path(file_path).stem
            parts = filename.split('_')
            symbol = parts[2] if len(parts) > 2 else 'UNKNOWN'
            
            # Calculate metrics
            total_trades = len(df)
            
            if total_trades == 0:
                print(f"\n⚠️  {symbol}: Empty CSV, skipping")
                continue
            
            # Calculate win rate from pnl_usdt
            if 'pnl_usdt' in df.columns:
                winning_trades = len(df[df['pnl_usdt'] > 0])
                losing_trades = len(df[df['pnl_usdt'] <= 0])
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                total_pnl_usdt = df['pnl_usdt'].sum()
                
                # Calculate max drawdown (simplified)
                cumulative_pnl = df['pnl_usdt'].cumsum()
                running_max = cumulative_pnl.expanding().max()
                drawdown = cumulative_pnl - running_max
                max_dd = drawdown.min()
                
                # Profit factor
                gross_profit = df[df['pnl_usdt'] > 0]['pnl_usdt'].sum()
                gross_loss = abs(df[df['pnl_usdt'] < 0]['pnl_usdt'].sum())
                profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
                
                # R-multiple
                avg_r = df['r_multiple'].mean() if 'r_multiple' in df.columns else 0
                
                # Get date range
                if 'exit_time' in df.columns:
                    df['exit_time_dt'] = pd.to_datetime(df['exit_time'])
                    first_date = df['exit_time_dt'].min().strftime('%Y-%m-%d')
                    last_date = df['exit_time_dt'].max().strftime('%Y-%m-%d')
                else:
                    first_date = 'N/A'
                    last_date = 'N/A'
                
                stats = {
                    'symbol': symbol,
                    'file': Path(file_path).name,
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'total_pnl_usdt': total_pnl_usdt,
                    'max_drawdown_usdt': max_dd,
                    'profit_factor': profit_factor,
                    'avg_r_multiple': avg_r,
                    'first_date': first_date,
                    'last_date': last_date
                }
                
                all_stats.append(stats)
                
                print(f"\n📈 {symbol} ({Path(file_path).name}):")
                print(f"  Trades: {total_trades} ({winning_trades}W / {losing_trades}L)")
                print(f"  Win Rate: {win_rate:.1f}%")
                print(f"  Total P&L: ${total_pnl_usdt:.2f} USDT")
                print(f"  Max Drawdown: ${max_dd:.2f} USDT")
                print(f"  Profit Factor: {profit_factor:.2f}")
                print(f"  Avg R-Multiple: {avg_r:.2f}")
                print(f"  Date Range: {first_date} to {last_date}")
            
            else:
                print(f"\n⚠️  {symbol}: No pnl_usdt column found")
                
        except Exception as e:
            print(f"\n❌ Error processing {file_path}: {e}")
    
    # Aggregate stats
    if all_stats:
        print("\n" + "=" * 60)
        print("AGGREGATED STATISTICS")
        print("=" * 60)
        
        total_symbols = len(all_stats)
        total_all_trades = sum(s['total_trades'] for s in all_stats)
        total_all_wins = sum(s['winning_trades'] for s in all_stats)
        
        agg_win_rate = (total_all_wins / total_all_trades * 100) if total_all_trades > 0 else 0
        agg_pnl = sum(s['total_pnl_usdt'] for s in all_stats)
        agg_max_dd = min(s['max_drawdown_usdt'] for s in all_stats)
        agg_pf = sum(s['profit_factor'] for s in all_stats) / total_symbols
        agg_r = sum(s['avg_r_multiple'] for s in all_stats) / total_symbols
        
        print(f"\nSymbols: {total_symbols}")
        print(f"Total Trades: {total_all_trades}")
        print(f"Overall Win Rate: {agg_win_rate:.1f}%")
        print(f"Total P&L: ${agg_pnl:.2f} USDT")
        print(f"Worst Drawdown: ${agg_max_dd:.2f} USDT")
        print(f"Avg Profit Factor: {agg_pf:.2f}")
        print(f"Avg R-Multiple: {agg_r:.2f}")
        
        print("\n✅ CSV validation completed successfully!")
        print(f"   Ready to serve via /api/v1/stats endpoint")
    
    else:
        print("\n⚠️  No valid stats calculated")

if __name__ == '__main__':
    test_csv_stats()

