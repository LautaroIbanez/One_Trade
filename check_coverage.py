"""Quick script to check coverage of generated CSV files."""
import pandas as pd
from pathlib import Path

data_dir = Path('data')
csv_files = list(data_dir.glob('trades_final_*_moderate.csv'))

print("="*60)
print("COVERAGE CHECK - Moderate Mode")
print("="*60)

for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        if df.empty:
            print(f"\n{csv_file.name}: EMPTY")
            continue
        
        total_trades = len(df)
        if 'entry_time' in df.columns:
            df['entry_time'] = pd.to_datetime(df['entry_time'])
            first_trade = df['entry_time'].min()
            last_trade = df['entry_time'].max()
            coverage_days = (last_trade - first_trade).days
            
            print(f"\n{csv_file.name}:")
            print(f"  Total trades: {total_trades}")
            print(f"  First trade: {first_trade}")
            print(f"  Last trade: {last_trade}")
            print(f"  Coverage: {coverage_days} days")
            print(f"  Status: {'OK (>=365)' if coverage_days >= 365 else 'INSUFFICIENT (<365)'}")
        else:
            print(f"\n{csv_file.name}: {total_trades} trades (no entry_time column)")
    except Exception as e:
        print(f"\n{csv_file.name}: ERROR - {e}")

print("\n" + "="*60)


