"""Debug script to capture full traceback of the 'close' KeyError."""
import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from btc_1tpd_backtester.btc_1tpd_backtest_final import run_backtest
from webapp.app import get_effective_config

symbol = "BTC/USDT:USDT"
mode = "moderate"
since = "2024-10-08"
until = "2025-10-08"

logger.info(f"Testing backtest for {symbol} {mode}")
logger.info(f"Period: {since} to {until}")

config = get_effective_config(symbol, mode)

try:
    results = run_backtest(symbol, since, until, config)
    logger.info(f"✓ Backtest completed successfully!")
    logger.info(f"Trades generated: {len(results.trades_df)}")
except KeyError as e:
    logger.error(f"\n{'='*60}")
    logger.error(f"KeyError caught: {e}")
    logger.error(f"{'='*60}\n")
    logger.error("Full traceback:")
    traceback.print_exc()
    logger.error(f"\n{'='*60}")
    logger.error("Analyzing traceback...")
    logger.error(f"{'='*60}")
    tb = traceback.format_exc()
    lines = tb.split('\n')
    for i, line in enumerate(lines):
        if '.py' in line and 'line' in line:
            logger.error(f"  {line}")
    logger.error(f"\nThe error '{e}' suggests the DataFrame is missing the 'close' column")
    logger.error(f"This could happen in:")
    logger.error(f"  1. Mode strategy process_day() when accessing day_data")
    logger.error(f"  2. Indicator calculations that expect specific columns")
    logger.error(f"  3. DataFrame operations that lose columns (groupby, resample, etc.)")
except Exception as e:
    logger.error(f"\nUnexpected error: {type(e).__name__}: {e}")
    traceback.print_exc()


