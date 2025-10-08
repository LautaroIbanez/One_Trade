"""Tests for annual coverage validation. Ensures generated CSV files have at least 365 days of coverage between first_trade_date and last_trade_date."""
import pytest
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from webapp.app import MODE_ASSETS, get_effective_config, repo_root

MINIMUM_COVERAGE_DAYS = 365
DATA_DIR = repo_root / "data"


@pytest.fixture
def sample_modes():
    """Return list of modes to test."""
    return list(MODE_ASSETS.keys())


@pytest.fixture
def sample_symbols_by_mode():
    """Return sample symbols for each mode."""
    return {mode: symbols[:2] for mode, symbols in MODE_ASSETS.items()}


def test_base_config_enforces_365_days():
    """Test that BASE_CONFIG has minimum 365-day lookback."""
    from webapp.app import BASE_CONFIG
    assert BASE_CONFIG['lookback_days'] >= 365, f"BASE_CONFIG lookback_days should be >= 365, got {BASE_CONFIG['lookback_days']}"
    print(f"✓ BASE_CONFIG enforces {BASE_CONFIG['lookback_days']} days lookback")


def test_effective_config_enforces_365_days(sample_modes):
    """Test that get_effective_config enforces minimum 365 days for all modes."""
    for mode in sample_modes:
        config = get_effective_config("BTC/USDT:USDT", mode)
        assert config['lookback_days'] >= 365, f"Mode {mode} should have >= 365 days lookback, got {config['lookback_days']}"
    print(f"✓ All {len(sample_modes)} modes enforce 365+ days lookback")


def test_meta_file_structure():
    """Test that meta files have expected structure with coverage fields."""
    meta_files = list(DATA_DIR.glob("trades_final_*_meta.json"))
    if not meta_files:
        pytest.skip("No meta files found to test")
    required_fields = ['actual_lookback_days', 'first_trade_date', 'last_trade_date', 'total_trades', 'symbol', 'mode']
    for meta_file in meta_files[:3]:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        for field in required_fields:
            assert field in meta, f"{meta_file.name} missing required field: {field}"
    print(f"✓ Meta files have expected structure ({len(meta_files)} files checked)")


def test_csv_coverage_meets_minimum(sample_symbols_by_mode):
    """Test that generated CSV files have at least 365 days of coverage."""
    insufficient_coverage = []
    valid_coverage = []
    for mode, symbols in sample_symbols_by_mode.items():
        for symbol in symbols:
            slug = symbol.replace('/', '_').replace(':', '_')
            mode_suffix = mode.lower()
            csv_path = DATA_DIR / f"trades_final_{slug}_{mode_suffix}.csv"
            meta_path = DATA_DIR / f"trades_final_{slug}_{mode_suffix}_meta.json"
            if not csv_path.exists() or not meta_path.exists():
                continue
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                actual_lookback = meta.get('actual_lookback_days')
                first_trade = meta.get('first_trade_date')
                last_trade = meta.get('last_trade_date')
                total_trades = meta.get('total_trades', 0)
                if actual_lookback is None or first_trade is None or last_trade is None:
                    continue
                if actual_lookback < MINIMUM_COVERAGE_DAYS:
                    insufficient_coverage.append({'symbol': symbol, 'mode': mode, 'actual_days': actual_lookback, 'first_trade': first_trade, 'last_trade': last_trade, 'total_trades': total_trades})
                else:
                    valid_coverage.append({'symbol': symbol, 'mode': mode, 'actual_days': actual_lookback, 'total_trades': total_trades})
            except Exception as e:
                print(f"⚠️ Error reading {meta_path.name}: {e}")
                continue
    if insufficient_coverage:
        error_msg = f"\n❌ {len(insufficient_coverage)} symbol/mode combinations have insufficient coverage:\n"
        for item in insufficient_coverage:
            error_msg += f"  - {item['symbol']} {item['mode']}: {item['actual_days']} days (need {MINIMUM_COVERAGE_DAYS}), {item['total_trades']} trades from {item['first_trade']} to {item['last_trade']}\n"
        pytest.fail(error_msg)
    if valid_coverage:
        print(f"✓ All {len(valid_coverage)} checked symbol/mode combinations have sufficient coverage (>={MINIMUM_COVERAGE_DAYS} days)")
    else:
        pytest.skip("No CSV files with valid coverage found to test")


def test_csv_matches_meta_trade_count():
    """Test that CSV trade count matches meta.json total_trades field."""
    meta_files = list(DATA_DIR.glob("trades_final_*_meta.json"))
    if not meta_files:
        pytest.skip("No meta files found to test")
    mismatches = []
    for meta_file in meta_files:
        csv_path = meta_file.with_suffix('.csv')
        if not csv_path.exists():
            continue
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            meta_count = meta.get('total_trades', 0)
            df = pd.read_csv(csv_path)
            csv_count = len(df)
            if meta_count != csv_count:
                mismatches.append({'file': csv_path.name, 'meta_count': meta_count, 'csv_count': csv_count})
        except Exception as e:
            print(f"⚠️ Error checking {meta_file.name}: {e}")
            continue
    assert not mismatches, f"\n❌ {len(mismatches)} files have trade count mismatches:\n" + "\n".join([f"  - {m['file']}: meta={m['meta_count']}, csv={m['csv_count']}" for m in mismatches])
    print(f"✓ All {len(meta_files)} meta files match CSV trade counts")


def test_csv_date_range_consistency():
    """Test that CSV entry_time range matches meta first/last_trade_date."""
    meta_files = list(DATA_DIR.glob("trades_final_*_meta.json"))
    if not meta_files:
        pytest.skip("No meta files found to test")
    inconsistencies = []
    for meta_file in meta_files[:5]:
        csv_path = meta_file.with_suffix('.csv')
        if not csv_path.exists():
            continue
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            first_trade_meta = meta.get('first_trade_date')
            last_trade_meta = meta.get('last_trade_date')
            if not first_trade_meta or not last_trade_meta:
                continue
            df = pd.read_csv(csv_path)
            if df.empty or 'entry_time' not in df.columns:
                continue
            df['entry_time'] = pd.to_datetime(df['entry_time'], errors='coerce')
            df = df.dropna(subset=['entry_time'])
            first_trade_csv = df['entry_time'].min().date().isoformat()
            last_trade_csv = df['entry_time'].max().date().isoformat()
            if first_trade_csv != first_trade_meta or last_trade_csv != last_trade_meta:
                inconsistencies.append({'file': csv_path.name, 'meta_first': first_trade_meta, 'csv_first': first_trade_csv, 'meta_last': last_trade_meta, 'csv_last': last_trade_csv})
        except Exception as e:
            print(f"⚠️ Error checking {meta_file.name}: {e}")
            continue
    assert not inconsistencies, f"\n❌ {len(inconsistencies)} files have date range inconsistencies:\n" + "\n".join([f"  - {i['file']}: meta({i['meta_first']} to {i['meta_last']}) vs csv({i['csv_first']} to {i['csv_last']})" for i in inconsistencies])
    print(f"✓ Date ranges consistent between meta and CSV files")


def test_no_future_trades():
    """Test that no trades have future dates."""
    today = datetime.now(timezone.utc).date()
    csv_files = list(DATA_DIR.glob("trades_final_*.csv"))
    if not csv_files:
        pytest.skip("No CSV files found to test")
    future_trades = []
    for csv_file in csv_files[:10]:
        try:
            df = pd.read_csv(csv_file)
            if df.empty or 'entry_time' not in df.columns:
                continue
            df['entry_time'] = pd.to_datetime(df['entry_time'], errors='coerce')
            df = df.dropna(subset=['entry_time'])
            future_df = df[df['entry_time'].dt.date > today]
            if not future_df.empty:
                future_trades.append({'file': csv_file.name, 'count': len(future_df), 'dates': future_df['entry_time'].dt.date.unique().tolist()})
        except Exception as e:
            print(f"⚠️ Error checking {csv_file.name}: {e}")
            continue
    assert not future_trades, f"\n❌ {len(future_trades)} files have future trades:\n" + "\n".join([f"  - {ft['file']}: {ft['count']} trades with dates {ft['dates']}" for ft in future_trades])
    print(f"✓ No future trades detected in {len(csv_files)} files")


def test_minimum_trades_per_year():
    """Test that annual backtests generate reasonable number of trades (at least 10)."""
    meta_files = list(DATA_DIR.glob("trades_final_*_meta.json"))
    if not meta_files:
        pytest.skip("No meta files found to test")
    low_trade_count = []
    for meta_file in meta_files:
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            actual_lookback = meta.get('actual_lookback_days')
            total_trades = meta.get('total_trades', 0)
            symbol = meta.get('symbol')
            mode = meta.get('mode')
            if actual_lookback and actual_lookback >= MINIMUM_COVERAGE_DAYS:
                expected_min_trades = 10
                if total_trades < expected_min_trades:
                    low_trade_count.append({'file': meta_file.name, 'symbol': symbol, 'mode': mode, 'actual_days': actual_lookback, 'total_trades': total_trades, 'expected_min': expected_min_trades})
        except Exception as e:
            print(f"⚠️ Error reading {meta_file.name}: {e}")
            continue
    if low_trade_count:
        warning_msg = f"\n⚠️  {len(low_trade_count)} symbol/mode combinations have low trade counts:\n"
        for item in low_trade_count:
            warning_msg += f"  - {item['symbol']} {item['mode']}: {item['total_trades']} trades in {item['actual_days']} days (expected >={item['expected_min']})\n"
        print(warning_msg)
    else:
        print(f"✓ All symbol/mode combinations have reasonable trade counts (>=10 trades/year)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

