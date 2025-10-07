#!/usr/bin/env python3
"""
Script de verificación y actualización automática de datos para One Trade.

Este script:
1. Verifica la frescura de los archivos _meta.json
2. Detecta datos desactualizados (last_backtest_until < hoy)
3. Ejecuta refresh_trades para actualizar datos obsoletos
4. Genera un reporte de estado

Uso:
    python verify_and_update_data.py [--force] [--symbol SYMBOL] [--mode MODE]

Opciones:
    --force: Fuerza actualización incluso si los datos están frescos
    --symbol: Actualiza solo un símbolo específico (ej: BTC/USDT:USDT)
    --mode: Actualiza solo un modo específico (conservative, moderate, aggressive)
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
base_dir = Path(__file__).resolve().parent
if str(base_dir) not in sys.path:
    sys.path.append(str(base_dir))

from webapp.app import refresh_trades, MODE_ASSETS

def check_meta_freshness(meta_path: Path) -> dict:
    """
    Check if a meta.json file is fresh (up to date).
    
    Returns:
        dict with keys: 'is_fresh', 'last_backtest_until', 'days_old', 'last_error'
    """
    if not meta_path.exists():
        return {
            'is_fresh': False,
            'last_backtest_until': None,
            'days_old': None,
            'reason': 'Meta file does not exist',
            'last_error': None
        }
    
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        last_until = meta.get('last_backtest_until')
        last_error = meta.get('last_error')
        
        if not last_until:
            return {
                'is_fresh': False,
                'last_backtest_until': None,
                'days_old': None,
                'reason': 'No last_backtest_until field',
                'last_error': last_error
            }
        
        today = datetime.now(timezone.utc).date()
        last_date = datetime.fromisoformat(last_until).date() if isinstance(last_until, str) else last_until
        days_old = (today - last_date).days
        
        is_fresh = last_date >= today
        
        return {
            'is_fresh': is_fresh,
            'last_backtest_until': last_until,
            'days_old': days_old,
            'reason': 'Data is current' if is_fresh else f'Data is {days_old} days old',
            'last_error': last_error
        }
    except Exception as e:
        logger.error(f"Error reading {meta_path}: {e}")
        return {
            'is_fresh': False,
            'last_backtest_until': None,
            'days_old': None,
            'reason': f'Error reading meta file: {str(e)}',
            'last_error': None
        }


def scan_data_directory():
    """
    Scan data directory for all meta.json files and check freshness.
    
    Returns:
        list of dicts with file info and freshness status
    """
    data_dir = base_dir / "data"
    if not data_dir.exists():
        logger.warning(f"Data directory does not exist: {data_dir}")
        return []
    
    meta_files = list(data_dir.glob("*_meta.json"))
    results = []
    
    for meta_path in meta_files:
        # Parse filename to extract symbol and mode
        filename = meta_path.stem.replace('_meta', '')
        parts = filename.split('_')
        
        # Try to extract symbol and mode
        # Format: trades_final_BTC_USDT_USDT_moderate
        symbol = None
        mode = None
        
        if len(parts) >= 5:
            # Last part is mode
            mode = parts[-1]
            # Symbol is between 'final' and mode
            symbol_parts = parts[2:-1]
            symbol = '/'.join(symbol_parts[:2]) + ':' + symbol_parts[2] if len(symbol_parts) >= 3 else None
        
        freshness = check_meta_freshness(meta_path)
        
        results.append({
            'meta_path': meta_path,
            'csv_path': meta_path.with_suffix('.csv'),
            'symbol': symbol,
            'mode': mode,
            **freshness
        })
    
    return results


def update_stale_data(file_info: dict, force: bool = False) -> bool:
    """
    Update stale data for a specific file.
    
    Returns:
        True if update was successful, False otherwise
    """
    symbol = file_info['symbol']
    mode = file_info['mode']
    
    if not symbol or not mode:
        logger.warning(f"Cannot update {file_info['meta_path']}: missing symbol or mode")
        return False
    
    logger.info(f"Updating {symbol} {mode}...")
    
    try:
        result_msg = refresh_trades(symbol, mode)
        
        if result_msg.startswith("OK"):
            logger.info(f"✅ {result_msg}")
            return True
        elif result_msg.startswith("WARNING"):
            logger.warning(f"⚠️ {result_msg}")
            return False
        else:
            logger.error(f"❌ {result_msg}")
            return False
    except Exception as e:
        logger.error(f"❌ Error updating {symbol} {mode}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Verify and update One Trade data freshness")
    parser.add_argument('--force', action='store_true', help='Force update even if data is fresh')
    parser.add_argument('--symbol', type=str, help='Update only specific symbol')
    parser.add_argument('--mode', type=str, choices=['conservative', 'moderate', 'aggressive'], help='Update only specific mode')
    parser.add_argument('--report-only', action='store_true', help='Only report status, do not update')
    
    args = parser.parse_args()
    
    logger.info("🔍 Scanning data directory...")
    files_info = scan_data_directory()
    
    if not files_info:
        logger.warning("No meta files found in data directory")
        return
    
    # Filter by symbol/mode if specified
    if args.symbol:
        files_info = [f for f in files_info if f['symbol'] == args.symbol]
    if args.mode:
        files_info = [f for f in files_info if f['mode'] == args.mode]
    
    # Print report
    print("\n" + "=" * 80)
    print("DATA FRESHNESS REPORT")
    print("=" * 80)
    
    fresh_count = 0
    stale_count = 0
    error_count = 0
    
    for file_info in files_info:
        status_icon = "✅" if file_info['is_fresh'] else "⚠️"
        symbol = file_info['symbol'] or "Unknown"
        mode = file_info['mode'] or "Unknown"
        
        print(f"\n{status_icon} {symbol} ({mode})")
        print(f"   Last update: {file_info['last_backtest_until']}")
        print(f"   Status: {file_info['reason']}")
        
        if file_info['last_error']:
            print(f"   Last error: {file_info['last_error']['type']} - {file_info['last_error']['detail']}")
            error_count += 1
        
        if file_info['is_fresh']:
            fresh_count += 1
        else:
            stale_count += 1
    
    print("\n" + "=" * 80)
    print(f"Summary: {fresh_count} fresh, {stale_count} stale, {error_count} with errors")
    print("=" * 80 + "\n")
    
    # Update stale data if not report-only
    if not args.report_only:
        stale_files = [f for f in files_info if not f['is_fresh'] or args.force]
        
        if stale_files:
            logger.info(f"Updating {len(stale_files)} stale file(s)...")
            
            success_count = 0
            fail_count = 0
            
            for file_info in stale_files:
                if update_stale_data(file_info, force=args.force):
                    success_count += 1
                else:
                    fail_count += 1
            
            print("\n" + "=" * 80)
            print(f"UPDATE SUMMARY: {success_count} succeeded, {fail_count} failed")
            print("=" * 80 + "\n")
        else:
            logger.info("All data is fresh. Use --force to update anyway.")
    else:
        logger.info("Report-only mode. No updates performed.")


if __name__ == "__main__":
    main()

