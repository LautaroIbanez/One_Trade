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

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from .utils import fetch_historical_data
from .indicators import ema, atr, adx, vwap
from .plot_results import create_comprehensive_report


class SimpleTradingStrategy:
    """Simplified trading strategy that works."""
    
    def __init__(self, config):
        """Initialize strategy with configuration parameters."""
        self.config = config
        self.risk_usdt = config.get('risk_usdt', 20.0)
        self.daily_target = config.get('daily_target', 50.0)
        self.daily_max_loss = config.get('daily_max_loss', -30.0)
        self.adx_min = config.get('adx_min', 15.0)
        self.atr_mult = config.get('atr_mult_orb', 1.2)
        self.tp_multiplier = config.get('tp_multiplier', 2.0)
        # Fallback/forcing
        self.force_one_trade = config.get('force_one_trade', False)
        self.fallback_mode = config.get('fallback_mode', 'EMA15_pullback')
        
        # Trading windows
        self.orb_window = config.get('orb_window', (11, 12))
        self.entry_window = config.get('entry_window', (11, 13))
        self.full_day_trading = config.get('full_day_trading', False)
        
        # Commission and slippage costs
        self.commission_rate = config.get('commission_rate', 0.001)  # 0.1% default
        self.slippage_rate = config.get('slippage_rate', 0.0005)     # 0.05% default
        
        # Daily state
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.max_daily_trades = 1
    
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
        
        # In full_day_trading, cap evaluation window to 24h from entry_time if data available spans further
        if self.full_day_trading and not remaining_data.empty:
            cutoff_time = entry_time + pd.Timedelta(hours=24)
            remaining_data = remaining_data[remaining_data.index <= cutoff_time]
        
        if remaining_data.empty:
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
            
            # If no exit found, force exit at 24h cutoff in 24h mode, else end of session
            if exit_time is None:
                if self.full_day_trading:
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
        trades = []
        
        # Reset daily state
        self.reset_daily_state()
        
        # If in full_day_trading, split session_data (first 24h) for entries/indicators and keep full day_data (possibly extended) for exits
        if self.full_day_trading:
            session_start = pd.Timestamp(date, tz='UTC')
            session_end = session_start + pd.Timedelta(days=1)
            session_data = day_data[(day_data.index >= session_start) & (day_data.index < session_end)]
        else:
            session_data = day_data

        # Determine preferred fallback side based on simple EMA15 bias
        def _preferred_side(df: pd.DataFrame) -> str:
            try:
                if df is None or df.empty or len(df) < 5:
                    return 'long'
                ema15_val = df['close'].ewm(span=15, adjust=False).mean().iloc[-1]
                last_close = df['close'].iloc[-1]
                return 'long' if last_close >= ema15_val else 'short'
            except Exception:
                return 'long'

        if len(session_data) < 50:  # Need enough data for indicators
            if self.force_one_trade:
                # Try fallback even with limited data
                pref = _preferred_side(session_data)
                order = [pref, 'short' if pref == 'long' else 'long']
                for side in order:
                    ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, side)
                    if ok and fb:
                        # Choose an entry_time within session_data that has at least one future candle in full day_data
                        candidate = fb_ts if fb_ts is not None else (session_data.index[-1] if not session_data.empty else pd.Timestamp(date, tz='UTC'))
                        if not day_data[day_data.index > candidate].empty:
                            entry_ts = candidate
                        else:
                            # Walk backwards in session_data to find a timestamp with a following candle in day_data
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                        fb_params = {
                            'entry_price': fb['entry_price'],
                            'stop_loss': fb['stop_loss'],
                            'take_profit': fb['take_profit'],
                            'position_size': fb['position_size'],
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
                        candidate = fb_ts if fb_ts is not None else session_data.index[-1]
                        if not day_data[day_data.index > candidate].empty:
                            entry_ts = candidate
                        else:
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                        fb_params = {
                            'entry_price': fb['entry_price'],
                            'stop_loss': fb['stop_loss'],
                            'take_profit': fb['take_profit'],
                            'position_size': fb['position_size'],
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
        
        # Entry window configurable
        ew_start, ew_end = entry_window
        entry_data = session_data[(session_data.index.hour >= ew_start) & (session_data.index.hour < ew_end)]
        
        if entry_data.empty:
            if self.force_one_trade:
                # Try fallback when no entry window data
                pref = _preferred_side(session_data)
                order = [pref, 'short' if pref == 'long' else 'long']
                for side in order:
                    ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, side)
                    if ok and fb:
                        candidate = fb_ts if fb_ts is not None else session_data.index[-1]
                        if not day_data[day_data.index > candidate].empty:
                            entry_ts = candidate
                        else:
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                        fb_params = {
                            'entry_price': fb['entry_price'],
                            'stop_loss': fb['stop_loss'],
                            'take_profit': fb['take_profit'],
                            'position_size': fb['position_size'],
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
        
        if side is None:
            if self.force_one_trade:
                # Try fallback when no breakout detected
                pref = _preferred_side(session_data)
                order = [pref, 'short' if pref == 'long' else 'long']
                for fallback_side in order:
                    ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, fallback_side)
                    if ok and fb:
                        candidate = fb_ts if fb_ts is not None else session_data.index[-1]
                        if not day_data[day_data.index > candidate].empty:
                            entry_ts = candidate
                        else:
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                        fb_params = {
                            'entry_price': fb['entry_price'],
                            'stop_loss': fb['stop_loss'],
                            'take_profit': fb['take_profit'],
                            'position_size': fb['position_size'],
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
                        candidate = fb_ts if fb_ts is not None else session_data.index[-1]
                        if not day_data[day_data.index > candidate].empty:
                            entry_ts = candidate
                        else:
                            entry_ts = candidate
                            for ts in reversed(session_data.index.tolist()):
                                if not day_data[day_data.index > ts].empty:
                                    entry_ts = ts
                                    break
                        fb_params = {
                            'entry_price': fb['entry_price'],
                            'stop_loss': fb['stop_loss'],
                            'take_profit': fb['take_profit'],
                            'position_size': fb['position_size'],
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
            for fallback_side in ['long', 'short']:
                ok, fb, fb_ts = self.check_ema15_pullback_conditions(session_data, fallback_side)
                if ok and fb:
                    used_fallback = True
                    # Build minimal trade_params
                    candidate = fb_ts if fb_ts is not None else session_data.index[-1]
                    if not day_data[day_data.index > candidate].empty:
                        entry_ts = candidate
                    else:
                        entry_ts = candidate
                        for ts in reversed(session_data.index.tolist()):
                            if not day_data[day_data.index > ts].empty:
                                entry_ts = ts
                                break
                    fb_params = {
                        'entry_price': fb['entry_price'],
                        'stop_loss': fb['stop_loss'],
                        'take_profit': fb['take_profit'],
                        'position_size': fb['position_size'],
                        'entry_time': entry_ts
                    }
                    exit_info = self.simulate_trade_exit(fb_params, fallback_side, day_data)
                    side = fallback_side
                    trade_params = fb_params
                    break
        
        # Deterministic final fallback for force_one_trade when all else fails
        if (exit_info is None or not isinstance(exit_info, dict)) and self.force_one_trade:
            # Use the most recent price and create a minimal trade
            current_price = session_data['close'].iloc[-1] if not session_data.empty else 50000.0
            entry_time = session_data.index[-1] if not session_data.empty else pd.Timestamp(date, tz='UTC')
            
            # Ensure we have future candles for exit simulation
            if day_data[day_data.index > entry_time].empty:
                # Walk backwards to find a timestamp with future candles
                for ts in reversed(session_data.index.tolist()):
                    if not day_data[day_data.index > ts].empty:
                        entry_time = ts
                        break
            
            # Use ORB range for stop/take profit if available, otherwise use minimal ATR
            orb_high, orb_low = self.get_orb_levels(session_data, self.orb_window)
            if orb_high is not None and orb_low is not None:
                orb_range = orb_high - orb_low
                min_atr = max(orb_range * 0.1, current_price * 0.001)  # At least 0.1% of price
            else:
                min_atr = current_price * 0.01  # 1% of price as fallback
            
            # Create minimal trade parameters
            side = 'long'  # Default to long
            entry_price = current_price
            stop_loss = entry_price - (min_atr * self.atr_mult)
            take_profit = entry_price + (min_atr * self.tp_multiplier)
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
    """Run the backtest."""
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
    
    # If full_day_trading, also fetch next day to allow exits after midnight
    if config.get('full_day_trading', False):
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
            print(f"⚠️ Could not extend data for 24h mode: {e}")
    
    if data.empty:
        print("❌ No data retrieved.")
        return pd.DataFrame()
    
    print(f"✅ Data: {len(data)} candles")
    
    # Initialize strategy
    strategy = SimpleTradingStrategy(config)
    
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
    
    return pd.DataFrame(all_trades)


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
