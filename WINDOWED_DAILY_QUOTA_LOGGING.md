# Windowed Daily Quota Implementation - Logging Expectations

This document outlines the comprehensive logging strategy implemented for the Windowed Daily Quota backtest system, ensuring full traceability at both daily and trade levels.

**Implementation Date**: October 8, 2025  
**Status**: ✓ COMPLETED

---

## Logging Architecture

### Logger Configuration
All modules use Python's standard `logging` framework with module-level loggers:

```python
import logging
logger = logging.getLogger(__name__)
```

**Log Levels Used:**
- `INFO`: High-level milestones (initialization, daily summaries, backtest completion)
- `DEBUG`: Detailed operational logs (signal generation, trade execution, window checks)
- `WARNING`: Defensive fallbacks (invalid ATR, timezone loading failures)
- `ERROR`: Invalid states (missing columns, invalid signal payloads)

---

## Module-by-Module Logging

### 1. WindowedSignalStrategy (`btc_1tpd_backtester/strategy.py`)

#### Initialization Logs
```python
logger.info(f"WindowedSignalStrategy initialized with windows={self.entry_windows}, tz={self.timezone_str}, risk={self.risk_usdt}")
```
**Emitted:** On instantiation  
**Purpose:** Confirm configuration loaded correctly

#### Market Data Logs
```python
logger.debug(f"Market data set: {len(self._market_data)} bars, date range {self._market_data.index[0]} to {self._market_data.index[-1]}")
logger.debug(f"Indicators computed: EMA({self.ema_fast}/{self.ema_slow}), RSI({self.rsi_period}), MACD, ATR({self.atr_period})")
```
**Emitted:** On `set_market_data()` and `_prepare_indicator_frame()`  
**Purpose:** Validate data ingestion and indicator computation

#### Daily Counter Reset Logs
```python
logger.debug(f"Daily counter reset for {local_date}")
```
**Emitted:** When a new local calendar day starts  
**Purpose:** Track daily quota reset events

#### Quota Status Logs
```python
logger.debug(f"Daily quota reached for {local_date}: {count}/{self.MAX_TRADES_PER_DAY}")
```
**Emitted:** When `can_trade_today()` returns `False` due to quota  
**Purpose:** Explain why trading is blocked

#### Signal Generation Logs
```python
# Invalid scenarios
logger.debug(f"Invalid signal generation: index={index}, frame_len={len(self._indicator_frame)}")
logger.debug(f"signal_generation_failed: invalid entry_price={entry_price}")
logger.debug(f"no_alignment: ema_fast={ema_fast_val:.2f}, ema_slow={ema_slow_val:.2f}, rsi={rsi_val:.1f}, macd={macd_val:.2f}, signal={macd_signal_val:.2f}")
logger.debug(f"fallback_no_momentum: entry_price={entry_price}, prev_close={prev_close}")
logger.debug(f"fallback_invalid_prev_close: prev_close={prev_close}")
logger.debug(f"fallback_insufficient_history: index={index}")

# Valid signals
logger.debug(f"signal_generated: side={side}, entry={entry_price:.2f}, sl={sl:.2f}, tp={tp:.2f}, reason={reason}")
```
**Emitted:** On every `generate_signal()` call  
**Purpose:** Full traceability of signal logic and fallback paths

#### Defensive Handling Logs
```python
logger.warning(f"Invalid ATR={atr_value}, using default 2% of price: {default_atr}")
logger.warning(f"Invalid stop/target: sl={sl}, tp={tp}, using fallback")
logger.warning(f"Failed to load timezone {self.timezone_str}, falling back to UTC: {e}")
```
**Emitted:** When defensive fallbacks are triggered  
**Purpose:** Alert to data quality issues without crashing

---

### 2. BacktestRunner (`btc_1tpd_backtester/backtest_runner.py`)

#### Initialization Logs
```python
logger.info(f"BacktestRunner initialized with {len(self.data)} bars from {self.data.index[0]} to {self.data.index[-1]}")
```
**Emitted:** On instantiation  
**Purpose:** Confirm data loaded and range

#### Daily Summary Logs
```python
logger.info(f"daily_summary: date={self._current_day}, trades={len(prev_day_trades)}, pnl={prev_day_pnl:.2f}")
```
**Emitted:** When a new ART day begins (via `_log_daily_summary`)  
**Purpose:** Per-day performance tracking

#### Trade Opening Logs
```python
logger.debug(f"trade_opened: time={current_time}, side={signal['side']}, entry={signal['entry_price']:.2f}, sl={signal['sl']:.2f}, tp={signal['tp']:.2f}, size={position_size:.4f}, reason={signal['reason']}")
```
**Emitted:** When a new trade is opened  
**Purpose:** Full trade entry details

#### Exit Condition Logs
```python
logger.debug(f"session_rollover: closing trade at {close:.2f} (next day)")
logger.debug(f"stop_loss_hit: long at {self._open_trade['sl']:.2f}")
logger.debug(f"take_profit_hit: long at {self._open_trade['tp']:.2f}")
logger.debug(f"stop_loss_hit: short at {self._open_trade['sl']:.2f}")
logger.debug(f"take_profit_hit: short at {self._open_trade['tp']:.2f}")
```
**Emitted:** When exit conditions are checked  
**Purpose:** Explain why trades close

#### Trade Closing Logs
```python
logger.debug(f"trade_closed: time={current_time}, side={self._open_trade['side']}, exit={exit_price:.2f}, pnl={pnl:.2f}, reason={exit_reason}")
```
**Emitted:** When a trade is closed  
**Purpose:** Full trade exit details

#### Backtest Completion Logs
```python
logger.info("Starting backtest execution...")
logger.info(f"Backtest complete: {len(self._trades)} trades executed")
```
**Emitted:** At start and end of `run()`  
**Purpose:** Mark backtest lifecycle

#### Metrics Calculation Logs
```python
logger.info(f"metrics_calculated: trades={total_trades}, pnl={total_pnl:.2f}, win_rate={win_rate:.1f}%, profit_factor={profit_factor:.2f}, max_dd={max_drawdown:.2f}, roi={roi:.1f}%")
```
**Emitted:** After `_calculate_metrics()`  
**Purpose:** Final performance summary

---

### 3. UI Utilities (`webapp/ui.py`)

#### Metrics Computation Logs
```python
logger.warning("compute_trade_metrics: empty or None DataFrame provided")
logger.error("compute_trade_metrics: 'pnl' column missing from DataFrame")
logger.info(f"compute_trade_metrics: total_trades={total_trades}, total_pnl={total_pnl:.2f}, win_rate={win_rate:.1f}%, max_dd={max_drawdown:.2f}")
```
**Emitted:** During `compute_trade_metrics()`  
**Purpose:** Validate inputs and report calculations

#### Trade Report Preparation Logs
```python
logger.error("prepare_trade_report: invalid backtest_result provided")
logger.warning("prepare_trade_report: '_trades' is not a DataFrame")
logger.info(f"prepare_trade_report: rendering {row_count} trade rows")
```
**Emitted:** During `prepare_trade_report()`  
**Purpose:** Track report generation and row counts

#### Banner Logic Logs
```python
logger.debug("signal_banner: no signal provided, level=ok")
logger.debug(f"signal_banner: invalid signal, reason={reason}, level=ok")
logger.error(f"signal_banner: invalid signal side={signal_side}, level=error")
logger.error(f"signal_banner: invalid entry_price={entry_price}, level=error")
logger.error(f"signal_banner: invalid stop/target sl={sl}, tp={tp}, level=error")
logger.debug(f"signal_ok_no_position: signal_side={signal_side}, level=ok")
logger.debug(f"signal_aligned: signal_side={signal_side}, position_side={open_position_side}, level=ok")
logger.warning(f"signal_reversal: signal_side={signal_side}, position_side={open_position_side}, level=warning")
```
**Emitted:** During `determine_signal_banner()`  
**Purpose:** Trace banner logic for each scenario

---

## Log Message Conventions

### Structured Keys
Log messages use consistent structured keys for parsability:

- **Event Types**: `daily_summary`, `trade_opened`, `trade_closed`, `signal_generated`, `signal_banner`
- **Contexts**: `date=`, `side=`, `entry=`, `exit=`, `pnl=`, `reason=`, `level=`
- **Quotes**: Values use no quotes for numbers, single quotes for strings

**Example:**
```
signal_generated: side=long, entry=50123.45, sl=49000.00, tp=51500.00, reason=ema_rsi_macd_bullish
```

### Reason Codes
Signal and exit reasons use snake_case identifiers:

**Signal Reasons:**
- `ema_rsi_macd_bullish`
- `ema_rsi_macd_bearish`
- `momentum_fallback_bullish`
- `momentum_fallback_bearish`
- `no_alignment`
- `no_momentum`
- `invalid_price`
- `no_data`
- `insufficient_history`
- `invalid_prev_data`

**Exit Reasons:**
- `stop_loss`
- `take_profit`
- `session_rollover`
- `end_of_data`

---

## Sample Log Output

### Typical Backtest Run
```
2025-10-08 12:00:00,123 - strategy - INFO - WindowedSignalStrategy initialized with windows=[(5, 8), (11, 14)], tz=America/Argentina/Buenos_Aires, risk=20.0
2025-10-08 12:00:00,234 - strategy - DEBUG - Market data set: 120 bars, date range 2024-01-01 00:00:00+00:00 to 2024-01-05 23:00:00+00:00
2025-10-08 12:00:00,345 - strategy - DEBUG - Indicators computed: EMA(9/21), RSI(14), MACD, ATR(14)
2025-10-08 12:00:00,456 - backtest_runner - INFO - BacktestRunner initialized with 120 bars from 2024-01-01 00:00:00+00:00 to 2024-01-05 23:00:00+00:00
2025-10-08 12:00:00,567 - backtest_runner - INFO - Starting backtest execution...
2025-10-08 12:00:00,678 - strategy - DEBUG - Daily counter reset for 2024-01-01
2025-10-08 12:00:00,789 - strategy - DEBUG - signal_generated: side=long, entry=50123.45, sl=49000.00, tp=51500.00, reason=ema_rsi_macd_bullish
2025-10-08 12:00:00,890 - strategy - DEBUG - Trade recorded for 2024-01-01, count now 1
2025-10-08 12:00:00,901 - backtest_runner - DEBUG - trade_opened: time=2024-01-01 12:00:00+00:00, side=long, entry=50123.45, sl=49000.00, tp=51500.00, size=0.0178, reason=ema_rsi_macd_bullish
2025-10-08 12:00:01,012 - backtest_runner - DEBUG - take_profit_hit: long at 51500.00
2025-10-08 12:00:01,123 - backtest_runner - DEBUG - trade_closed: time=2024-01-01 18:00:00+00:00, side=long, exit=51500.00, pnl=24.50, reason=take_profit
2025-10-08 12:00:01,234 - backtest_runner - INFO - daily_summary: date=2024-01-01, trades=1, pnl=24.50
2025-10-08 12:00:02,345 - strategy - DEBUG - Daily counter reset for 2024-01-02
...
2025-10-08 12:00:05,678 - backtest_runner - INFO - Backtest complete: 4 trades executed
2025-10-08 12:00:05,789 - backtest_runner - INFO - metrics_calculated: trades=4, pnl=98.00, win_rate=75.0%, profit_factor=3.50, max_dd=15.00, roi=9.8%
```

---

## Verification

### Running Tests with Logging
Enable verbose pytest output to see logs:

```bash
pytest btc_1tpd_backtester/tests/test_daily_strategy.py -v -s --log-cli-level=DEBUG
```

### Filtering Logs
Use grep to extract specific event types:

```bash
python backtest_script.py 2>&1 | grep "signal_generated"
python backtest_script.py 2>&1 | grep "daily_summary"
python backtest_script.py 2>&1 | grep "trade_opened\|trade_closed"
```

### Log Levels by Environment
- **Development**: `DEBUG` (all logs)
- **Testing**: `INFO` (milestones only)
- **Production**: `WARNING` (issues only)

Configure via:
```python
logging.basicConfig(level=logging.DEBUG)  # or INFO, WARNING
```

---

## Compliance Summary

✓ **Daily-level logging**: `daily_summary` emitted at each day transition with trade count and PnL  
✓ **Trade-level logging**: `trade_opened` and `trade_closed` with full details  
✓ **Signal traceability**: `signal_generated` with reason codes for all valid signals  
✓ **Window checks**: `DEBUG` logs for entry window and quota checks  
✓ **Exit reasons**: Structured logging for SL/TP/rollover/end-of-data exits  
✓ **Defensive handling**: `WARNING` logs for fallback scenarios  
✓ **Error states**: `ERROR` logs for invalid payloads

All logging requirements from Task 12 have been implemented and verified.

---

**Questions or Issues?**  
Refer to test files for examples of expected log output:
- `btc_1tpd_backtester/tests/test_daily_strategy.py`
- `webapp/test_ui_banner.py`

