#!/usr/bin/env python3
"""
BTC 1 Trade Per Day Backtester - Final Working Version
Simplified version that generates trades successfully.
"""

import argparse
import sys
import os
from datetime import datetime, timezone
import pandas as pd
import numpy as np
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for Python < 3.9
    from backports.zoneinfo import ZoneInfo

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .utils import fetch_historical_data
from .indicators import ema, atr, adx, vwap
from .plot_results import create_comprehensive_report
from .strategy_multifactor import MultifactorStrategy
from .backtester import BacktestResults


class SimpleTradingStrategy:
    """Simplified trading strategy that works."""
    
    def __init__(self, config, daily_data=None):
        """Initialize strategy with configuration parameters."""
        self.config = config
        
        # Check if we should use multifactor strategy
        self.use_multifactor = config.get('use_multifactor_strategy', False)
        
        if self.use_multifactor:
            # Delegate to MultifactorStrategy
            self.multifactor_strategy = MultifactorStrategy(config)
            return
        
        # Original SimpleTradingStrategy parameters
        self.risk_usdt = config.get('risk_usdt', 20.0)
        self.daily_target = config.get('daily_target', 50.0)
        self.daily_max_loss = config.get('daily_max_loss', -30.0)
        self.adx_min = config.get('adx_min', 15.0)
        self.atr_mult = config.get('atr_mult_orb', 1.2)
        self.tp_multiplier = config.get('tp_multiplier', 2.0)
        self.target_r_multiple = config.get('target_r_multiple', self.tp_multiplier)
        self.risk_reward_ratio = config.get('risk_reward_ratio', self.tp_multiplier)
        # Fallback/forcing
        self.force_one_trade = config.get('force_one_trade', False)
        self.fallback_mode = config.get('fallback_mode', 'EMA15_pullback')
        
        # Trading windows
        self.orb_window = config.get('orb_window', (11, 12))
        self.entry_window = config.get('entry_window', (11, 13))
        self.exit_window = config.get('exit_window', None)  # Exit window in local time
        self.full_day_trading = config.get('full_day_trading', False)
        self.session_trading = config.get('session_trading', False)
        
        # Session timezone
        self.session_timezone = config.get('session_timezone', 'America/Argentina/Buenos_Aires')
        try:
            self.tz = ZoneInfo(self.session_timezone)
        except Exception:
            self.tz = ZoneInfo('America/Argentina/Buenos_Aires')  # Fallback
        
        # Commission and slippage costs
        self.commission_rate = config.get('commission_rate', 0.001)  # 0.1% default
        self.slippage_rate = config.get('slippage_rate', 0.0005)     # 0.05% default
        
        # Daily trend filter
        self.daily_data = daily_data
        self.use_daily_trend_filter = config.get('use_daily_trend_filter', False)
        
        # Reentry on trend change
        self.allow_reentry_on_trend_change = config.get('allow_reentry_on_trend_change', False)
        
        # Daily state
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.max_daily_trades = config.get('max_daily_trades', 1)
    
    def reset_daily_state(self):
        """Reset daily tracking variables."""
        self.daily_pnl = 0.0
        self.daily_trades = 0
    
    def can_trade_today(self):
        """Check if trading is allowed today."""
        return (self.daily_trades < self.max_daily_trades and 
                self.daily_pnl < self.daily_target and 
                self.daily_pnl > self.daily_max_loss)
    
    def get_orb_levels(self, day_data, orb_window=(11, 12)):
        """Calculate ORB levels for the day based on configured window."""
        start_h, end_h = orb_window
        
        # Convert to local timezone for filtering if session trading is enabled
        if self.session_trading and not self.full_day_trading:
            # Convert UTC index to local timezone for hour filtering
            local_data = day_data.copy()
            local_data.index = local_data.index.tz_convert(self.tz)
            orb_data = local_data[(local_data.index.hour >= start_h) & (local_data.index.hour < end_h)]
            # Convert back to UTC for calculations
            orb_data.index = orb_data.index.tz_convert(timezone.utc)
        else:
            # Use UTC hours directly for full day trading
            orb_data = day_data[(day_data.index.hour >= start_h) & (day_data.index.hour < end_h)]
        
        if orb_data.empty:
            return None, None
        
        orb_high = orb_data['high'].max()
        orb_low = orb_data['low'].min()
        
        return orb_high, orb_low
    
    def check_breakout(self, entry_data, orb_high, orb_low):
        """Check for ORB breakouts by comparing high/low against orb levels."""
        for timestamp, row in entry_data.iterrows():
            high_price = row['high']
            low_price = row['low']
            open_price = row['open']
            
            # Long breakout: high pierces orb_high
            if high_price > orb_high:
                # Entry price reflects the breakout (max of open and orb_high)
                entry_price = max(open_price, orb_high)
                return 'long', timestamp, entry_price
            
            # Short breakout: low pierces orb_low
            elif low_price < orb_low:
                # Entry price reflects the breakout (min of open and orb_low)
                entry_price = min(open_price, orb_low)
                return 'short', timestamp, entry_price
        
        return None, None, None

    def find_best_fallback_entry_time(self, session_data):
        """Find the candle with highest intraday range or absolute displacement for fallback entry."""
        if session_data.empty:
            return None
        
        # Calculate intraday range for each candle
        session_data = session_data.copy()
        session_data['range'] = session_data['high'] - session_data['low']
        session_data['abs_displacement'] = session_data['close'].diff().abs()
        
        # Find candle with maximum range
        max_range_idx = session_data['range'].idxmax()
        max_range_value = session_data.loc[max_range_idx, 'range']
        
        # Find candle with maximum absolute displacement
        max_disp_idx = session_data['abs_displacement'].idxmax()
        max_disp_value = session_data.loc[max_disp_idx, 'abs_displacement']
        
        # Choose the one with higher relative value (normalized by price)
        max_range_price = session_data.loc[max_range_idx, 'close']
        max_disp_price = session_data.loc[max_disp_idx, 'close']
        
        range_ratio = max_range_value / max_range_price if max_range_price > 0 else 0
        disp_ratio = max_disp_value / max_disp_price if max_disp_price > 0 else 0
        
        # Return the timestamp with higher relative value
        return max_range_idx if range_ratio >= disp_ratio else max_disp_idx
    
    def detect_fallback_direction(self, session_data):
        """Detect fallback direction based on trend analysis."""
        if session_data.empty or len(session_data) < 5:
            return 'long'  # Default fallback
        
        try:
            # Method 1: Compare close vs open
            session_open = session_data['open'].iloc[0]
            session_close = session_data['close'].iloc[-1]
            price_change = session_close - session_open
            
            # Method 2: EMA15 slope analysis
            if len(session_data) >= 15:
                ema15 = session_data['close'].ewm(span=15, adjust=False).mean()
                ema_slope = ema15.iloc[-1] - ema15.iloc[-5] if len(ema15) >= 5 else 0
            else:
                ema_slope = 0
            
            # Method 3: Simple moving average comparison
            if len(session_data) >= 10:
                sma_short = session_data['close'].rolling(5).mean().iloc[-1]
                sma_long = session_data['close'].rolling(10).mean().iloc[-1]
                sma_bias = sma_short - sma_long
            else:
                sma_bias = 0
            
            # Combine signals with weights
            trend_score = (price_change * 0.4 + ema_slope * 0.3 + sma_bias * 0.3)
            
            return 'long' if trend_score >= 0 else 'short'
        except Exception:
            return 'long'  # Default fallback
    
    def compute_daily_trend(self, date):
        """Compute daily trend direction using daily data."""
        if not self.use_daily_trend_filter or self.daily_data is None or self.daily_data.empty:
            return None  # No trend filter
        
        try:
            # Convert date to datetime if needed
            if hasattr(date, 'date'):
                target_date = date.date()
            else:
                target_date = date
            
            # Find the daily data for this date
            daily_candle = None
            for idx, row in self.daily_data.iterrows():
                if idx.date() == target_date:
                    daily_candle = row
                    break
            
            if daily_candle is None:
                return None  # No daily data for this date
            
            # Method 1: Compare close vs open
            price_change = daily_candle['close'] - daily_candle['open']
            
            # Method 2: EMA comparison (if we have enough daily data)
            if len(self.daily_data) >= 5:
                # Get last 5 days including current
                recent_data = self.daily_data.tail(5)
                ema_fast = recent_data['close'].ewm(span=3, adjust=False).mean().iloc[-1]
                ema_slow = recent_data['close'].ewm(span=5, adjust=False).mean().iloc[-1]
                ema_bias = ema_fast - ema_slow
            else:
                ema_bias = 0
            
            # Method 3: 5-day average comparison
            if len(self.daily_data) >= 5:
                avg_5d = self.daily_data['close'].tail(5).mean()
                current_close = daily_candle['close']
                avg_bias = current_close - avg_5d
            else:
                avg_bias = 0
            
            # Combine signals with weights
            trend_score = (price_change * 0.5 + ema_bias * 0.3 + avg_bias * 0.2)
            
            return 'long' if trend_score >= 0 else 'short'
        except Exception:
            return None  # Error in trend calculation
    
    def detect_intraday_trend_change(self, data, current_side, entry_time):
        """Detect if there's been a significant intraday trend change since entry."""
        if not self.allow_reentry_on_trend_change:
            return False, None
        
        try:
            # Get data after entry time
            post_entry_data = data[data.index > entry_time]
            if len(post_entry_data) < 10:  # Need enough data for trend analysis
                return False, None
            
            # Calculate EMA15 for trend detection
            ema15 = post_entry_data['close'].ewm(span=15, adjust=False).mean()
            
            # Check for trend reversal using EMA slope
            if len(ema15) >= 5:
                recent_slope = ema15.iloc[-1] - ema15.iloc[-5]
                if current_side == 'long' and recent_slope < -0.001:  # Negative slope for long
                    return True, post_entry_data.index[-1]
                elif current_side == 'short' and recent_slope > 0.001:  # Positive slope for short
                    return True, post_entry_data.index[-1]
            
            # Check for ADX divergence (if we can calculate it)
            if len(post_entry_data) >= 14:
                try:
                    from .indicators import adx
                    adx_values = adx(post_entry_data, 14)
                    if not adx_values.empty and len(adx_values) >= 3:
                        # Check if ADX is declining (trend weakening)
                        adx_slope = adx_values.iloc[-1] - adx_values.iloc[-3]
                        if adx_slope < -2:  # Significant ADX decline
                            return True, post_entry_data.index[-1]
                except:
                    pass  # ADX calculation failed, continue without it
            
            return False, None
        except Exception:
            return False, None
    
    def check_ema15_pullback_conditions(self, ltf_data, side):
        """Lightweight EMA15 pullback fallback similar to strategy.py."""
        try:
            if len(ltf_data) < 15:
                return False, None, None
            ema15 = ltf_data['close'].ewm(span=15, adjust=False).mean().iloc[-1]
            current_price = ltf_data['close'].iloc[-1]
            if side == 'long':
                pullback_ok = current_price <= ema15 * 1.001
            else:
                pullback_ok = current_price >= ema15 * 0.999
            if not pullback_ok:
                return False, None, None
            # Simple risk params using ATR proxy
            if len(ltf_data) >= 14:
                tr_high = ltf_data['high'].rolling(14).max().iloc[-1]
                tr_low = ltf_data['low'].rolling(14).min().iloc[-1]
                atr_proxy = (tr_high - tr_low) / 14 if pd.notna(tr_high) and pd.notna(tr_low) else None
            else:
                atr_proxy = None
            if atr_proxy is None or pd.isna(atr_proxy) or atr_proxy <= 0:
                return False, None, None
            entry_price = current_price
            if side == 'long':
                stop_loss = entry_price - (atr_proxy * self.atr_mult)
                take_profit = entry_price + (atr_proxy * self.tp_multiplier)
            else:
                stop_loss = entry_price + (atr_proxy * self.atr_mult)
                take_profit = entry_price - (atr_proxy * self.tp_multiplier)
            position_size = self.risk_usdt / max(abs(entry_price - stop_loss), 1e-9)
            # Return params and the evaluated timestamp for coherence
            return True, {
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size
            }, ltf_data.index[-1]
        except Exception:
            return False, None, None
    
    def calculate_trade_params(self, side, entry_price, day_data, entry_time=None):
        """Calculate trade parameters using data available up to entry_time (inclusive)."""
        # Slice data up to entry_time if provided
        data_for_indicators = day_data
        if entry_time is not None:
            data_for_indicators = day_data[day_data.index <= entry_time]
        # Need sufficient candles for ATR
        if len(data_for_indicators) < 14:
            return None
        # Calculate ATR on sliced data
        atr_series = atr(data_for_indicators, 14)
        if atr_series.empty or pd.isna(atr_series.iloc[-1]):
            return None
        atr_value = atr_series.iloc[-1]
        
        if pd.isna(atr_value):
            return None
        
        # Calculate stop loss and take profit
        if side == 'long':
            stop_loss = entry_price - (atr_value * self.atr_mult)
            take_profit = entry_price + (atr_value * self.tp_multiplier)
        else:
            stop_loss = entry_price + (atr_value * self.atr_mult)
            take_profit = entry_price - (atr_value * self.tp_multiplier)
        
        # Verificar que el TP corresponde al target R-multiple
        risk_amount = abs(entry_price - stop_loss)
        expected_reward = risk_amount * self.target_r_multiple
        
        if side == 'long':
            expected_tp = entry_price + expected_reward
        else:
            expected_tp = entry_price - expected_reward
        
        # Ajustar TP si hay diferencia significativa
        if abs(take_profit - expected_tp) > 0.01:
            take_profit = expected_tp
        
        # Calculate position size
        risk_amount = self.risk_usdt
        price_diff = abs(entry_price - stop_loss)
        position_size = risk_amount / price_diff if price_diff > 0 else 0
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size,
            'atr_value': atr_value
        }
    
    def simulate_trade_exit(self, trade_params, side, day_data):
        """Simulate trade exit by evaluating each candle sequentially. In 24h mode, allow evaluating candles past midnight up to entry_time + 24h if provided by concatenated data."""
        entry_price = trade_params['entry_price']
        stop_loss = trade_params['stop_loss']
        take_profit = trade_params['take_profit']
        position_size = trade_params['position_size']
        
        # Get remaining data after entry
        entry_time = trade_params['entry_time']
        remaining_data = day_data[day_data.index > entry_time]
        
        # Calculate exit cutoff time based on session type
        exit_cutoff = None
        if self.session_trading and not self.full_day_trading and self.exit_window:
            # Convert exit window to UTC for session trading
            exit_start_h, exit_end_h = self.exit_window
            # Get the date of entry in local timezone
            entry_date_local = entry_time.astimezone(self.tz).date()
            # Create exit cutoff time in local timezone
            exit_cutoff_local = pd.Timestamp.combine(entry_date_local, pd.Timestamp.min.time().replace(hour=exit_end_h)).tz_localize(self.tz)
            # Convert to UTC
            exit_cutoff = exit_cutoff_local.astimezone(timezone.utc)
            print(f"Session exit cutoff: {exit_cutoff} (local: {exit_cutoff_local})")
        elif self.full_day_trading and not remaining_data.empty:
            # In full day trading, cap evaluation window to 24h from entry_time
            exit_cutoff = entry_time + pd.Timedelta(hours=24)
        
        # Apply cutoff to remaining data
        if exit_cutoff is not None:
            remaining_data = remaining_data[remaining_data.index <= exit_cutoff]
        
        if remaining_data.empty:
            # Exit at end of day or session cutoff
            if exit_cutoff is not None:
                # Use the cutoff time as exit time
                exit_time = exit_cutoff
                # Find the last available candle before cutoff
                last_candle = day_data[day_data.index <= exit_cutoff]
                if not last_candle.empty:
                    exit_price = last_candle['close'].iloc[-1]
                else:
                    exit_price = day_data['close'].iloc[-1] if not day_data.empty else entry_price
                exit_reason = 'session_close' if self.session_trading else 'time_limit_24h'
            else:
                # Exit at end of day
                exit_time = day_data.index[-1]
                exit_price = day_data['close'].iloc[-1]
                # Use session_end only if not in full_day_trading mode
                exit_reason = 'session_end' if not self.full_day_trading else 'end_of_data'
        else:
            # Evaluate each candle sequentially
            exit_time = None
            exit_price = None
            exit_reason = None
            
            for timestamp, candle in remaining_data.iterrows():
                open_price = candle['open']
                high_price = candle['high']
                low_price = candle['low']
                close_price = candle['close']
                
                # Check for intraday trend change
                if self.allow_reentry_on_trend_change:
                    trend_changed, change_time = self.detect_intraday_trend_change(day_data, side, entry_time)
                    if trend_changed and timestamp >= change_time:
                        exit_time = timestamp
                        exit_price = close_price
                        exit_reason = 'trend_flip_exit'
                        break
                
                # Determine which level is closer to open price (convention)
                if side == 'long':
                    # For long trades: check if TP or SL is hit first
                    tp_distance = abs(high_price - take_profit) if high_price >= take_profit else float('inf')
                    sl_distance = abs(low_price - stop_loss) if low_price <= stop_loss else float('inf')
                    
                    if tp_distance < sl_distance and high_price >= take_profit:
                        # TP hit first
                        exit_time = timestamp
                        exit_price = take_profit
                        exit_reason = 'take_profit'
                        break
                    elif sl_distance < tp_distance and low_price <= stop_loss:
                        # SL hit first
                        exit_time = timestamp
                        exit_price = stop_loss
                        exit_reason = 'stop_loss'
                        break
                    elif high_price >= take_profit and low_price <= stop_loss:
                        # Both hit in same candle - use closer to open
                        tp_dist_from_open = abs(take_profit - open_price)
                        sl_dist_from_open = abs(stop_loss - open_price)
                        
                        if tp_dist_from_open <= sl_dist_from_open:
                            exit_time = timestamp
                            exit_price = take_profit
                            exit_reason = 'take_profit'
                        else:
                            exit_time = timestamp
                            exit_price = stop_loss
                            exit_reason = 'stop_loss'
                        break
                        
                else:  # short
                    # For short trades: check if TP or SL is hit first
                    tp_distance = abs(low_price - take_profit) if low_price <= take_profit else float('inf')
                    sl_distance = abs(high_price - stop_loss) if high_price >= stop_loss else float('inf')
                    
                    if tp_distance < sl_distance and low_price <= take_profit:
                        # TP hit first
                        exit_time = timestamp
                        exit_price = take_profit
                        exit_reason = 'take_profit'
                        break
                    elif sl_distance < tp_distance and high_price >= stop_loss:
                        # SL hit first
                        exit_time = timestamp
                        exit_price = stop_loss
                        exit_reason = 'stop_loss'
                        break
                    elif low_price <= take_profit and high_price >= stop_loss:
                        # Both hit in same candle - use closer to open
                        tp_dist_from_open = abs(take_profit - open_price)
                        sl_dist_from_open = abs(stop_loss - open_price)
                        
                        if tp_dist_from_open <= sl_dist_from_open:
                            exit_time = timestamp
                            exit_price = take_profit
                            exit_reason = 'take_profit'
                        else:
                            exit_time = timestamp
                            exit_price = stop_loss
                            exit_reason = 'stop_loss'
                        break
            
            # If no exit found, force exit at cutoff time
            if exit_time is None:
                if exit_cutoff is not None:
                    # Force exit at cutoff time
                    exit_time = exit_cutoff
                    # Find the last available candle before cutoff
                    last_candle = day_data[day_data.index <= exit_cutoff]
                    if not last_candle.empty:
                        exit_price = last_candle['close'].iloc[-1]
                    else:
                        exit_price = day_data['close'].iloc[-1] if not day_data.empty else entry_price
                    exit_reason = 'session_close' if self.session_trading else 'time_limit_24h'
                elif self.full_day_trading:
                    forced_time = entry_time + pd.Timedelta(hours=24)
                    # Use the last available candle not after forced_time
                    last_idx = remaining_data.index[-1] if not remaining_data.empty else entry_time
                    exit_time = min(last_idx, forced_time)
                    # Price from the last available candle
                    exit_price = remaining_data['close'].iloc[-1] if not remaining_data.empty else day_data.loc[entry_time, 'close']
                    # Guarantee exit_time > entry_time
                    if exit_time <= entry_time:
                        exit_time = entry_time + pd.Timedelta(minutes=1)
                    exit_reason = 'time_limit_24h'
                else:
                    exit_time = remaining_data.index[-1]
                    exit_price = remaining_data['close'].iloc[-1]
                    exit_reason = 'session_end'
        
        # Calculate gross PnL
        if side == 'long':
            gross_pnl = (exit_price - entry_price) * position_size
        else:
            gross_pnl = (entry_price - exit_price) * position_size
        
        # Calculate commission and slippage costs
        # Interpret commission_rate and slippage_rate as round-trip totals; split per leg
        per_leg_commission_rate = (self.commission_rate or 0.0) / 2.0
        per_leg_slippage_rate = (self.slippage_rate or 0.0) / 2.0
        entry_commission = abs(entry_price * position_size * per_leg_commission_rate)
        exit_commission = abs(exit_price * position_size * per_leg_commission_rate)
        entry_slippage = abs(entry_price * position_size * per_leg_slippage_rate)
        exit_slippage = abs(exit_price * position_size * per_leg_slippage_rate)
        
        total_costs = entry_commission + exit_commission + entry_slippage + exit_slippage
        
        # Net PnL after costs
        net_pnl = gross_pnl - total_costs
        
        # Calculate R-multiple based on net PnL
        risk_in_usdt = abs(entry_price - stop_loss) * position_size
        if risk_in_usdt > 0:
            r_multiple = net_pnl / risk_in_usdt
        else:
            r_multiple = 0
        
        return {
            'exit_time': exit_time,
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'pnl_usdt': net_pnl,  # Use net PnL after costs
            'gross_pnl_usdt': gross_pnl,
            'commission_usdt': entry_commission + exit_commission,
            'slippage_usdt': entry_slippage + exit_slippage,
            'r_multiple': r_multiple
        }
    
    def process_day(self, day_data, date):
        """Process trading for a single day."""
        if self.use_multifactor:
            # Delegate to MultifactorStrategy
            return self.multifactor_strategy.process_day(day_data, date)
        
        trades = []
        
        # Reset daily state
        self.reset_daily_state()
        
        # Check daily trend filter first
        if self.use_daily_trend_filter:
            daily_trend = self.compute_daily_trend(date)
            if daily_trend is None:
                return trades  # Skip if no daily trend data available
        
        # If in full_day_trading, split session_data (first 24h) for entries/indicators and keep full day_data (possibly extended) for exits
        if self.full_day_trading:
            session_start = pd.Timestamp(date, tz='UTC')
            session_end = session_start + pd.Timedelta(days=1)
            session_data = day_data[(day_data.index >= session_start) & (day_data.index < session_end)]
        else:
            session_data = day_data

        # Use new fallback direction detection
        def _preferred_side(df: pd.DataFrame) -> str:
            return self.detect_fallback_direction(df)
        
        # Main trading loop - allows multiple trades per day if reentry is enabled
        current_data = day_data.copy()
        last_exit_time = None
        
        while self.can_trade_today() and not current_data.empty:
            # If we have a last exit time, trim data to continue from there
            if last_exit_time is not None:
                current_data = current_data[current_data.index > last_exit_time]
                if current_data.empty:
                    break
                
                # Update session_data for the remaining session
                if self.full_day_trading:
                    session_data = current_data[(current_data.index >= session_start) & (current_data.index < session_end)]
                else:
                    session_data = current_data
                
                if session_data.empty:
                    break

            # Try to find a trade in the current data slice
            trade_found = False
            
            if len(session_data) < 50:  # Need enough data for indicators
                if self.force_one_trade:
                    # Try fallback even with limited data
                    pref = _preferred_side(session_data)
                    order = [pref, 'short' if pref == 'long' else 'long']
                    for side in order:
                        ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, side)
                        if ok and fb:
                            # Use new fallback entry time selection
                            best_entry_time = self.find_best_fallback_entry_time(session_data)
                            candidate = best_entry_time if best_entry_time is not None else (session_data.index[-1] if not session_data.empty else pd.Timestamp(date, tz='UTC'))
                        
                        # Find the next candle after the selected time for entry
                        next_candles = day_data[day_data.index > candidate]
                        if next_candles.empty:
                            # Walk backwards in session_data to find a timestamp with a following candle in day_data
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                            # If still no future candles, skip this trade
                            if day_data[day_data.index > entry_ts].empty:
                                continue
                            next_candles = day_data[day_data.index > entry_ts]
                        
                        # Use the next candle for entry
                        next_candle = next_candles.iloc[0]
                        entry_ts = next_candle.name
                        entry_price = next_candle['open']  # Use opening price of next candle
                        
                        # Recalculate SL/TP with the new entry price and available data up to entry_ts
                        trade_params = self.calculate_trade_params(side, entry_price, session_data, entry_ts)
                        if trade_params is None:
                            continue  # Skip if we can't calculate proper parameters
                        
                        fb_params = {
                            'entry_price': entry_price,
                            'stop_loss': trade_params['stop_loss'],
                            'take_profit': trade_params['take_profit'],
                            'position_size': trade_params['position_size'],
                            'entry_time': entry_ts
                        }
                        exit_info = self.simulate_trade_exit(fb_params, side, day_data)
                        if exit_info:
                            trade = {
                                'day_key': date.strftime('%Y-%m-%d'),
                                'entry_time': fb_params['entry_time'],
                                'side': side,
                                'entry_price': fb_params['entry_price'],
                                'sl': fb_params['stop_loss'],
                                'tp': fb_params['take_profit'],
                                'exit_time': exit_info['exit_time'],
                                'exit_price': exit_info['exit_price'],
                                'exit_reason': exit_info['exit_reason'],
                                'pnl_usdt': exit_info['pnl_usdt'],
                                'r_multiple': exit_info['r_multiple'],
                                'used_fallback': True
                            }
                            trades.append(trade)
                            return trades
            return trades
        
        # Get ORB levels using configured window
        orb_high, orb_low = self.get_orb_levels(session_data, self.orb_window)
        
        if orb_high is None or orb_low is None:
            if self.force_one_trade:
                # Try fallback when no ORB levels
                pref = _preferred_side(session_data)
                order = [pref, 'short' if pref == 'long' else 'long']
                for side in order:
                    ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, side)
                    if ok and fb:
                        # Use new fallback entry time selection
                        best_entry_time = self.find_best_fallback_entry_time(session_data)
                        candidate = best_entry_time if best_entry_time is not None else session_data.index[-1]
                        
                        # Find the next candle after the selected time for entry
                        next_candles = day_data[day_data.index > candidate]
                        if next_candles.empty:
                            # Walk backwards in session_data to find a timestamp with a following candle in day_data
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                            # If still no future candles, skip this trade
                            if day_data[day_data.index > entry_ts].empty:
                                continue
                            next_candles = day_data[day_data.index > entry_ts]
                        
                        # Use the next candle for entry
                        next_candle = next_candles.iloc[0]
                        entry_ts = next_candle.name
                        entry_price = next_candle['open']  # Use opening price of next candle
                        
                        # Recalculate SL/TP with the new entry price and available data up to entry_ts
                        trade_params = self.calculate_trade_params(side, entry_price, session_data, entry_ts)
                        if trade_params is None:
                            continue  # Skip if we can't calculate proper parameters
                        
                        fb_params = {
                            'entry_price': entry_price,
                            'stop_loss': trade_params['stop_loss'],
                            'take_profit': trade_params['take_profit'],
                            'position_size': trade_params['position_size'],
                            'entry_time': entry_ts
                        }
                        exit_info = self.simulate_trade_exit(fb_params, side, day_data)
                        if exit_info:
                            trade = {
                                'day_key': date.strftime('%Y-%m-%d'),
                                'entry_time': fb_params['entry_time'],
                                'side': side,
                                'entry_price': fb_params['entry_price'],
                                'sl': fb_params['stop_loss'],
                                'tp': fb_params['take_profit'],
                                'exit_time': exit_info['exit_time'],
                                'exit_price': exit_info['exit_price'],
                                'exit_reason': exit_info['exit_reason'],
                                'pnl_usdt': exit_info['pnl_usdt'],
                                'r_multiple': exit_info['r_multiple'],
                                'used_fallback': True
                            }
                            trades.append(trade)
                            return trades
            return trades
        
        # Determine entry window based on full_day_trading flag
        if self.full_day_trading:
            # In full day trading, ensure entry window starts at least after ORB ends
            ew_start = max(self.orb_window[1], self.entry_window[0])
            ew_end = 24
            entry_window = (ew_start, ew_end)
        else:
            entry_window = self.entry_window
        
        # Entry window configurable - convert to local timezone if session trading
        ew_start, ew_end = entry_window
        if self.session_trading and not self.full_day_trading:
            # Convert UTC index to local timezone for hour filtering
            local_session_data = session_data.copy()
            local_session_data.index = local_session_data.index.tz_convert(self.tz)
            entry_data = local_session_data[(local_session_data.index.hour >= ew_start) & (local_session_data.index.hour < ew_end)]
            # Convert back to UTC for calculations
            entry_data.index = entry_data.index.tz_convert(timezone.utc)
        else:
            # Use UTC hours directly for full day trading
            entry_data = session_data[(session_data.index.hour >= ew_start) & (session_data.index.hour < ew_end)]
        
        if entry_data.empty:
            if self.force_one_trade:
                # Try fallback when no entry window data
                pref = _preferred_side(session_data)
                order = [pref, 'short' if pref == 'long' else 'long']
                for side in order:
                    ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, side)
                    if ok and fb:
                        # Use new fallback entry time selection
                        best_entry_time = self.find_best_fallback_entry_time(session_data)
                        candidate = best_entry_time if best_entry_time is not None else session_data.index[-1]
                        
                        # Find the next candle after the selected time for entry
                        next_candles = day_data[day_data.index > candidate]
                        if next_candles.empty:
                            # Walk backwards in session_data to find a timestamp with a following candle in day_data
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                            # If still no future candles, skip this trade
                            if day_data[day_data.index > entry_ts].empty:
                                continue
                            next_candles = day_data[day_data.index > entry_ts]
                        
                        # Use the next candle for entry
                        next_candle = next_candles.iloc[0]
                        entry_ts = next_candle.name
                        entry_price = next_candle['open']  # Use opening price of next candle
                        
                        # Recalculate SL/TP with the new entry price and available data up to entry_ts
                        trade_params = self.calculate_trade_params(side, entry_price, session_data, entry_ts)
                        if trade_params is None:
                            continue  # Skip if we can't calculate proper parameters
                        
                        fb_params = {
                            'entry_price': entry_price,
                            'stop_loss': trade_params['stop_loss'],
                            'take_profit': trade_params['take_profit'],
                            'position_size': trade_params['position_size'],
                            'entry_time': entry_ts
                        }
                        exit_info = self.simulate_trade_exit(fb_params, side, day_data)
                        if exit_info:
                            trade = {
                                'day_key': date.strftime('%Y-%m-%d'),
                                'entry_time': fb_params['entry_time'],
                                'side': side,
                                'entry_price': fb_params['entry_price'],
                                'sl': fb_params['stop_loss'],
                                'tp': fb_params['take_profit'],
                                'exit_time': exit_info['exit_time'],
                                'exit_price': exit_info['exit_price'],
                                'exit_reason': exit_info['exit_reason'],
                                'pnl_usdt': exit_info['pnl_usdt'],
                                'r_multiple': exit_info['r_multiple'],
                                'used_fallback': True
                            }
                            trades.append(trade)
                            return trades
            return trades
        
        # Check for breakouts
        side, breakout_time, entry_price = self.check_breakout(entry_data, orb_high, orb_low)
        
        # Apply daily trend filter to breakout direction
        if side is not None and self.use_daily_trend_filter:
            daily_trend = self.compute_daily_trend(date)
            if daily_trend is not None and side != daily_trend:
                # Cancel breakout if it goes against daily trend
                side = None
                breakout_time = None
                entry_price = None
        
        if side is None:
            if self.force_one_trade:
                # Try fallback when no breakout detected
                pref = _preferred_side(session_data)
                order = [pref, 'short' if pref == 'long' else 'long']
                
                # Apply daily trend filter to fallback direction
                if self.use_daily_trend_filter:
                    daily_trend = self.compute_daily_trend(date)
                    if daily_trend is not None:
                        # Only allow fallback in the direction of daily trend
                        order = [daily_trend]
                
                for fallback_side in order:
                    ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, fallback_side)
                    if ok and fb:
                        # Use new fallback entry time selection
                        best_entry_time = self.find_best_fallback_entry_time(session_data)
                        candidate = best_entry_time if best_entry_time is not None else session_data.index[-1]
                        
                        # Find the next candle after the selected time for entry
                        next_candles = day_data[day_data.index > candidate]
                        if next_candles.empty:
                            # Walk backwards in session_data to find a timestamp with a following candle in day_data
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                            # If still no future candles, skip this trade
                            if day_data[day_data.index > entry_ts].empty:
                                continue
                            next_candles = day_data[day_data.index > entry_ts]
                        
                        # Use the next candle for entry
                        next_candle = next_candles.iloc[0]
                        entry_ts = next_candle.name
                        entry_price = next_candle['open']  # Use opening price of next candle
                        
                        # Recalculate SL/TP with the new entry price and available data up to entry_ts
                        trade_params = self.calculate_trade_params(fallback_side, entry_price, session_data, entry_ts)
                        if trade_params is None:
                            continue  # Skip if we can't calculate proper parameters
                        
                        fb_params = {
                            'entry_price': entry_price,
                            'stop_loss': trade_params['stop_loss'],
                            'take_profit': trade_params['take_profit'],
                            'position_size': trade_params['position_size'],
                            'entry_time': entry_ts
                        }
                        exit_info = self.simulate_trade_exit(fb_params, fallback_side, day_data)
                        if exit_info:
                            trade = {
                                'day_key': date.strftime('%Y-%m-%d'),
                                'entry_time': fb_params['entry_time'],
                                'side': fallback_side,
                                'entry_price': fb_params['entry_price'],
                                'sl': fb_params['stop_loss'],
                                'tp': fb_params['take_profit'],
                                'exit_time': exit_info['exit_time'],
                                'exit_price': exit_info['exit_price'],
                                'exit_reason': exit_info['exit_reason'],
                                'pnl_usdt': exit_info['pnl_usdt'],
                                'r_multiple': exit_info['r_multiple'],
                                'used_fallback': True
                            }
                            trades.append(trade)
                            return trades
            return trades
        
        # Calculate trade parameters using candles only up to breakout_time
        # Use session_data for indicator calculations up to breakout_time
        trade_params = self.calculate_trade_params(side, entry_price, session_data, breakout_time)
        
        if trade_params is None:
            if self.force_one_trade:
                # Try fallback when trade params calculation fails
                pref = _preferred_side(session_data)
                order = [pref, 'short' if pref == 'long' else 'long']
                for fallback_side in order:
                    ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, fallback_side)
                    if ok and fb:
                        # Use new fallback entry time selection
                        best_entry_time = self.find_best_fallback_entry_time(session_data)
                        candidate = best_entry_time if best_entry_time is not None else session_data.index[-1]
                        
                        # Find the next candle after the selected time for entry
                        next_candles = day_data[day_data.index > candidate]
                        if next_candles.empty:
                            # Walk backwards in session_data to find a timestamp with a following candle in day_data
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                            # If still no future candles, skip this trade
                            if day_data[day_data.index > entry_ts].empty:
                                continue
                            next_candles = day_data[day_data.index > entry_ts]
                        
                        # Use the next candle for entry
                        next_candle = next_candles.iloc[0]
                        entry_ts = next_candle.name
                        entry_price = next_candle['open']  # Use opening price of next candle
                        
                        # Recalculate SL/TP with the new entry price and available data up to entry_ts
                        trade_params = self.calculate_trade_params(fallback_side, entry_price, session_data, entry_ts)
                        if trade_params is None:
                            continue  # Skip if we can't calculate proper parameters
                        
                        fb_params = {
                            'entry_price': entry_price,
                            'stop_loss': trade_params['stop_loss'],
                            'take_profit': trade_params['take_profit'],
                            'position_size': trade_params['position_size'],
                            'entry_time': entry_ts
                        }
                        exit_info = self.simulate_trade_exit(fb_params, fallback_side, day_data)
                        if exit_info:
                            trade = {
                                'day_key': date.strftime('%Y-%m-%d'),
                                'entry_time': fb_params['entry_time'],
                                'side': fallback_side,
                                'entry_price': fb_params['entry_price'],
                                'sl': fb_params['stop_loss'],
                                'tp': fb_params['take_profit'],
                                'exit_time': exit_info['exit_time'],
                                'exit_price': exit_info['exit_price'],
                                'exit_reason': exit_info['exit_reason'],
                                'pnl_usdt': exit_info['pnl_usdt'],
                                'r_multiple': exit_info['r_multiple'],
                                'used_fallback': True
                            }
                            trades.append(trade)
                            return trades
            return trades
        
        # Add entry info to trade params
        trade_params['entry_price'] = entry_price
        trade_params['entry_time'] = breakout_time
        # Keep computed ATR
        trade_params['atr_value'] = trade_params.get('atr_value')
        
        used_fallback = False
        # Simulate trade
        exit_info = self.simulate_trade_exit(trade_params, side, day_data)
        
        # If no exit_info or something failed but forcing one trade, try fallback to create a trade
        if (exit_info is None or not isinstance(exit_info, dict)) and self.force_one_trade:
            # Use new fallback direction detection
            pref = _preferred_side(session_data)
            order = [pref, 'short' if pref == 'long' else 'long']
            for fallback_side in order:
                ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, fallback_side)
                if ok and fb:
                    used_fallback = True
                    # Use new fallback entry time selection
                    best_entry_time = self.find_best_fallback_entry_time(session_data)
                    candidate = best_entry_time if best_entry_time is not None else session_data.index[-1]
                    
                    # Find the next candle after the selected time for entry
                    next_candles = day_data[day_data.index > candidate]
                    if next_candles.empty:
                        # Walk backwards in session_data to find a timestamp with a following candle in day_data
                        entry_ts = candidate
                        for ts in reversed(session_data.index.tolist()):
                            if not day_data[day_data.index > ts].empty:
                                entry_ts = ts
                                break
                        # If still no future candles, skip this trade
                        if day_data[day_data.index > entry_ts].empty:
                            continue
                        next_candles = day_data[day_data.index > entry_ts]
                    
                    # Use the next candle for entry
                    next_candle = next_candles.iloc[0]
                    entry_ts = next_candle.name
                    entry_price = next_candle['open']  # Use opening price of next candle
                    
                    # Recalculate SL/TP with the new entry price and available data up to entry_ts
                    trade_params_new = self.calculate_trade_params(fallback_side, entry_price, session_data, entry_ts)
                    if trade_params_new is None:
                        continue  # Skip if we can't calculate proper parameters
                    
                    fb_params = {
                        'entry_price': entry_price,
                        'stop_loss': trade_params_new['stop_loss'],
                        'take_profit': trade_params_new['take_profit'],
                        'position_size': trade_params_new['position_size'],
                        'entry_time': entry_ts
                    }
                    exit_info = self.simulate_trade_exit(fb_params, fallback_side, day_data)
                    side = fallback_side
                    trade_params = fb_params
                    break
        
        # Deterministic final fallback for force_one_trade when all else fails
        if (exit_info is None or not isinstance(exit_info, dict)) and self.force_one_trade:
            # Use new fallback entry time selection
            best_entry_time = self.find_best_fallback_entry_time(session_data)
            candidate = best_entry_time if best_entry_time is not None else (session_data.index[-1] if not session_data.empty else pd.Timestamp(date, tz='UTC'))
            
            # Find the next candle after the selected time for entry
            next_candles = day_data[day_data.index > candidate]
            if next_candles.empty:
                # Walk backwards to find a timestamp with future candles
                for ts in reversed(session_data.index.tolist()):
                    if not day_data[day_data.index > ts].empty:
                        candidate = ts
                        break
                # If still no future candles, skip this trade
                if day_data[day_data.index > candidate].empty:
                    return trades
                next_candles = day_data[day_data.index > candidate]
            
            # Use the next candle for entry
            next_candle = next_candles.iloc[0]
            entry_time = next_candle.name
            entry_price = next_candle['open']  # Use opening price of next candle
            
            # Use new fallback direction detection
            side = self.detect_fallback_direction(session_data)
            
            # Use ORB range for stop/take profit if available, otherwise use minimal ATR
            orb_high, orb_low = self.get_orb_levels(session_data, self.orb_window)
            if orb_high is not None and orb_low is not None:
                orb_range = orb_high - orb_low
                min_atr = max(orb_range * 0.1, entry_price * 0.001)  # At least 0.1% of price
            else:
                min_atr = entry_price * 0.01  # 1% of price as fallback
            
            # Create minimal trade parameters based on detected side
            if side == 'long':
                stop_loss = entry_price - (min_atr * self.atr_mult)
                take_profit = entry_price + (min_atr * self.tp_multiplier)
            else:
                stop_loss = entry_price + (min_atr * self.atr_mult)
                take_profit = entry_price - (min_atr * self.tp_multiplier)
            position_size = self.risk_usdt / max(abs(entry_price - stop_loss), 1e-9)
            
            fb_params = {
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size,
                'entry_time': entry_time
            }
            
            exit_info = self.simulate_trade_exit(fb_params, side, day_data)
            trade_params = fb_params
            used_fallback = True
        
        # Create trade record
        trade = {
            'day_key': date.strftime('%Y-%m-%d'),
            'entry_time': trade_params['entry_time'],
            'side': side,
            'entry_price': trade_params['entry_price'],
            'sl': trade_params['stop_loss'],
            'tp': trade_params['take_profit'],
            'exit_time': exit_info['exit_time'],
            'exit_price': exit_info['exit_price'],
            'exit_reason': exit_info['exit_reason'],
            'pnl_usdt': exit_info['pnl_usdt'],
            'r_multiple': exit_info['r_multiple'],
            'used_fallback': used_fallback
        }
        
        trades.append(trade)
        
        # Update daily state
        self.daily_pnl += exit_info['pnl_usdt']
        self.daily_trades += 1
        
        return trades


def run_backtest(symbol, since, until, config):
    """Run the backtest with validation."""
    print(f"🚀 BTC 1 Trade Per Day Backtester - FINAL VERSION")
    print("=" * 60)
    print(f"Symbol: {symbol}")
    print(f"Period: {since} to {until}")
    print(f"Risk: {config['risk_usdt']} USDT")
    print(f"ADX Min: {config['adx_min']}")
    print("=" * 60)
    
    # Fetch data
    print("\n📊 Fetching historical data...")
    data = fetch_historical_data(symbol, since, until, "15m")
    
    # Fetch daily data for trend filtering if enabled
    daily_data = None
    if config.get('use_daily_trend_filter', False):
        print("📈 Fetching daily data for trend filtering...")
        try:
            daily_data = fetch_historical_data(symbol, since, until, "1d")
            if daily_data is not None and not daily_data.empty:
                print(f"✅ Daily data: {len(daily_data)} candles")
            else:
                print("⚠️ No daily data available, disabling trend filter")
                config['use_daily_trend_filter'] = False
        except Exception as e:
            print(f"⚠️ Could not fetch daily data: {e}")
            config['use_daily_trend_filter'] = False
    
    # Extend data range if needed for exit windows
    if config.get('full_day_trading', False) or (config.get('session_trading', False) and config.get('exit_window')):
        try:
            from datetime import datetime as _dt, timezone as _tz, timedelta as _td
            # Compute next day until (exclusive upper bound handled in utils)
            if isinstance(until, str) and len(until) == 10:
                next_day_until = (_dt.fromisoformat(until + 'T00:00:00+00:00') + _td(days=1)).date().isoformat()
            else:
                next_day_until = None
            # If we have a clear next day, extend range by one day
            if next_day_until:
                extra = fetch_historical_data(symbol, until, next_day_until, "15m")
                if extra is not None and not extra.empty:
                    data = (data if data is not None else extra).copy()
                    if data is not None and not data.empty:
                        try:
                            data = pd.concat([data, extra]).sort_index().drop_duplicates()
                        except Exception:
                            pass
        except Exception as e:
            print(f"⚠️ Could not extend data for exit window: {e}")
    
    if data.empty:
        print("❌ No data retrieved.")
        return pd.DataFrame()
    
    print(f"✅ Data: {len(data)} candles")
    
    # Initialize strategy
    strategy = SimpleTradingStrategy(config, daily_data)
    
    # Process each day
    print("\n🔄 Running backtest...")
    all_trades = []

    if config.get('full_day_trading', False):
        # Build windows per date including next-day candles for exits: [start, start+48h)
        # Parse since/until bounds to dates
        def _to_date(d):
            try:
                if isinstance(d, str):
                    return datetime.fromisoformat(d).date()
                if hasattr(d, 'date'):
                    return d.date() if not isinstance(d, datetime) else d.date()
            except Exception:
                pass
            return None
        since_date = _to_date(since)
        until_date = _to_date(until)
        unique_dates = sorted(set(data.index.date))
        # Filter only dates within [since_date, until_date]
        if since_date is not None and until_date is not None:
            unique_dates = [d for d in unique_dates if d >= since_date and d <= until_date]
        for date in unique_dates:
            start = pd.Timestamp(date, tz='UTC')
            end = start + pd.Timedelta(days=2)
            # Include extra candles for exits but do not process entry days beyond 'until'
            day_slice = data[(data.index >= start) & (data.index < end)]
            if day_slice is None or day_slice.empty:
                continue
            trades = strategy.process_day(day_slice, date)
            all_trades.extend(trades)
    else:
        daily_groups = data.groupby(data.index.date)
        for date, day_data in daily_groups:
            trades = strategy.process_day(day_data, date)
            all_trades.extend(trades)
    
    # Create DataFrame from trades
    trades_df = pd.DataFrame(all_trades)
    
    # Add validation configuration
    validation_config = {
        'min_win_rate': config.get('min_win_rate', 80.0),
        'min_pnl': config.get('min_pnl', 0.0),
        'min_avg_r': config.get('min_avg_r', 1.0),
        'min_trades': config.get('min_trades', 10),
        'min_profit_factor': config.get('min_profit_factor', 1.2)
    }
    
    # Create BacktestResults object
    results = BacktestResults(trades_df, validation_config)
    
    # Display results
    results.display_summary()
    
    # Check if strategy is suitable
    if not results.is_strategy_suitable():
        print("\n⚠️ WARNING: Strategy failed validation criteria!")
        print("Consider adjusting parameters or strategy configuration.")
    
    return results


def display_summary(trades_df):
    """Display backtest summary."""
    if trades_df.empty:
        print("\n❌ No trades generated during backtest period.")
        return
    
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['pnl_usdt'] > 0])
    losing_trades = len(trades_df[trades_df['pnl_usdt'] < 0])
    
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    
    total_pnl = trades_df['pnl_usdt'].sum()
    avg_win = trades_df[trades_df['pnl_usdt'] > 0]['pnl_usdt'].mean() if winning_trades > 0 else 0
    avg_loss = trades_df[trades_df['pnl_usdt'] < 0]['pnl_usdt'].mean() if losing_trades > 0 else 0
    
    gross_profit = trades_df[trades_df['pnl_usdt'] > 0]['pnl_usdt'].sum()
    gross_loss = abs(trades_df[trades_df['pnl_usdt'] < 0]['pnl_usdt'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    expectancy = (winning_trades * avg_win + losing_trades * avg_loss) / total_trades if total_trades > 0 else 0
    
    # Consecutive losses
    consecutive_losses = 0
    max_consecutive = 0
    
    for pnl in trades_df['pnl_usdt']:
        if pnl < 0:
            consecutive_losses += 1
            max_consecutive = max(max_consecutive, consecutive_losses)
        else:
            consecutive_losses = 0
    
    # Green days
    daily_pnl = trades_df.groupby('day_key')['pnl_usdt'].sum()
    green_days = len(daily_pnl[daily_pnl > 0])
    total_days = len(daily_pnl)
    green_days_pct = (green_days / total_days) * 100 if total_days > 0 else 0
    
    print("\n" + "=" * 50)
    print("📊 BACKTEST SUMMARY")
    print("=" * 50)
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.1f}% ({winning_trades}/{total_trades})")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Expectancy: {expectancy:+.2f} USDT")
    print(f"Avg Win: {avg_win:+.2f} USDT")
    print(f"Avg Loss: {avg_loss:+.2f} USDT")
    print(f"Max Consecutive Losses: {max_consecutive}")
    print(f"Green Days: {green_days_pct:.0f}% ({green_days}/{total_days})")
    print(f"Total PnL: {total_pnl:+.2f} USDT")
    print("=" * 50)
    
    # Show first few trades
    if not trades_df.empty:
        print("\nFirst 5 trades:")
        print(trades_df[['day_key', 'side', 'entry_price', 'exit_price', 'pnl_usdt', 'r_multiple']].head())


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="BTC 1 Trade Per Day Backtester - Final Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python btc_1tpd_backtest_final.py --since "2024-06-01" --until "2024-09-19" --risk_usdt 20
  python btc_1tpd_backtest_final.py --since "2024-01-01" --risk_usdt 50 --adx_min 10
        """
    )
    
    parser.add_argument("--symbol", default="BTC/USDT:USDT", help="Trading symbol (default: BTC/USDT:USDT)")
    parser.add_argument("--since", required=True, help="Start date in ISO format (e.g., 2024-06-01)")
    parser.add_argument("--until", help="End date in ISO format (e.g., 2024-09-19)")
    parser.add_argument("--risk_usdt", type=float, default=20.0, help="Risk amount in USDT (default: 20)")
    parser.add_argument("--daily_target", type=float, default=50.0, help="Daily profit target in USDT (default: 50)")
    parser.add_argument("--daily_max_loss", type=float, default=-30.0, help="Daily max loss in USDT (default: -30)")
    parser.add_argument("--adx_min", type=float, default=15.0, help="Minimum ADX value (default: 15)")
    parser.add_argument("--atr_mult_orb", type=float, default=1.2, help="ATR multiplier for stop loss (default: 1.2)")
    parser.add_argument("--tp_multiplier", type=float, default=2.0, help="Take profit multiplier (default: 2.0)")
    
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    
    config = {
        'risk_usdt': args.risk_usdt,
        'daily_target': args.daily_target,
        'daily_max_loss': args.daily_max_loss,
        'adx_min': args.adx_min,
        'atr_mult_orb': args.atr_mult_orb,
        'tp_multiplier': args.tp_multiplier
    }
    
    # Run backtest
    results = run_backtest(args.symbol, args.since, args.until, config)
    
    # Save results
    if not results.empty:
        output_file = "trades_final.csv"
        results.to_csv(output_file, index=False)
        print(f"\n✅ Results saved to {output_file}")
    
    # Display summary
    display_summary(results)
    
    # Create visual report if there are trades
    if not results.empty:
        try:
            print("\n📊 Creating visual report...")
            create_comprehensive_report(results, save_plots=True)
        except Exception as e:
            print(f"⚠️  Could not create visual report: {e}")
            print("   Make sure matplotlib and seaborn are installed:")
            print("   pip install matplotlib seaborn")


if __name__ == "__main__":
    main()
