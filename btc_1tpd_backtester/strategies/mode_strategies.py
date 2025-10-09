#!/usr/bin/env python3
"""
Mode-specific trading strategies for Conservative, Moderate, and Aggressive modes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional, Union
from abc import ABC, abstractmethod
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from ..indicators import ema, atr, adx, rsi, bollinger_bands, heikin_ashi


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, config: Dict):
        """Initialize strategy with configuration."""
        self.config = config
        
        # Common parameters
        self.risk_usdt = config.get('risk_usdt', 20.0)
        self.initial_capital = config.get('initial_capital', 1000.0)
        self.leverage = config.get('leverage', 1.0)
        self.commission_rate = config.get('commission_rate', 0.001)
        self.slippage_rate = config.get('slippage_rate', 0.0005)
        
        # Session parameters
        self.entry_window = config.get('entry_window', (11, 14))
        self.exit_window = config.get('exit_window', (20, 22))
        self.session_timezone = config.get('session_timezone', 'America/Argentina/Buenos_Aires')
        try:
            self.tz = ZoneInfo(self.session_timezone)
        except Exception:
            self.tz = ZoneInfo('America/Argentina/Buenos_Aires')
        
        # Risk management
        self.max_drawdown = config.get('max_drawdown', 0.1)
        self.target_r_multiple = config.get('target_r_multiple', 1.0)
        self.risk_reward_ratio = config.get('risk_reward_ratio', 1.0)
        self.allow_shorts = config.get('allow_shorts', False)
        
        # State tracking
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.max_daily_trades = 1
    
    def reset_daily_state(self):
        """Reset daily tracking variables."""
        self.daily_pnl = 0.0
        self.daily_trades = 0
    
    def can_trade_today(self) -> bool:
        """Check if trading is allowed today."""
        return self.daily_trades < self.max_daily_trades
    
    def compute_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk management."""
        risk_amount = self.risk_usdt
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff == 0:
            return 0
            
        position_size = risk_amount / price_diff
        
        # Apply capital constraints
        max_position_size = (self.initial_capital * self.leverage) / entry_price
        position_size = min(position_size, max_position_size)
        
        return position_size
    
    def calculate_trade_params(self, side: str, entry_price: float, data: pd.DataFrame, 
                             entry_time: pd.Timestamp) -> Optional[Dict]:
        """Calculate trade parameters (SL/TP) based on strategy."""
        try:
            # Get ATR for stop loss calculation
            atr_value = atr(data, self.config.get('atr_period', 14)).iloc[-1]
            atr_mult = self.config.get('atr_multiplier', 2.0)
            
            # Calculate stop loss
            if side == 'long':
                stop_loss = entry_price - (atr_value * atr_mult)
                take_profit = entry_price + (atr_value * atr_mult * self.risk_reward_ratio)
            else:
                stop_loss = entry_price + (atr_value * atr_mult)
                take_profit = entry_price - (atr_value * atr_mult * self.risk_reward_ratio)
            
            # Calculate position size
            position_size = self.compute_position_size(entry_price, stop_loss)
            
            return {
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size,
                'atr_value': atr_value,
                'entry_time': entry_time
            }
        except Exception as e:
            print(f"Error calculating trade params: {e}")
            return None
    
    def simulate_trade_exit(self, trade_params: Dict, side: str, data: pd.DataFrame) -> Dict:
        """Simulate trade exit with session-based cutoff."""
        entry_price = trade_params['entry_price']
        stop_loss = trade_params['stop_loss']
        take_profit = trade_params['take_profit']
        position_size = trade_params['position_size']
        entry_time = trade_params['entry_time']
        
        # Get remaining data after entry
        remaining_data = data[data.index > entry_time]
        
        # Calculate exit cutoff for session trading
        exit_cutoff = None
        if self.exit_window:
            exit_start_h, exit_end_h = self.exit_window
            entry_date_local = entry_time.astimezone(self.tz).date()
            exit_cutoff_local = pd.Timestamp.combine(
                entry_date_local, 
                pd.Timestamp.min.time().replace(hour=exit_end_h)
            ).tz_localize(self.tz)
            exit_cutoff = exit_cutoff_local.astimezone(timezone.utc)
            remaining_data = remaining_data[remaining_data.index <= exit_cutoff]
        
        if remaining_data.empty:
            # Forced exit
            if exit_cutoff is not None:
                exit_time = exit_cutoff
                last_candle = data[data.index <= exit_cutoff]
                exit_price = last_candle['close'].iloc[-1] if not last_candle.empty else entry_price
                exit_reason = 'session_close'
            else:
                exit_time = data.index[-1]
                exit_price = data['close'].iloc[-1]
                exit_reason = 'session_end'
        else:
            # Evaluate each candle
            exit_time = None
            exit_price = None
            exit_reason = None
            
            for timestamp, candle in remaining_data.iterrows():
                high_price = candle['high']
                low_price = candle['low']
                
                # Check TP and SL
                if side == 'long':
                    if high_price >= take_profit:
                        exit_time = timestamp
                        exit_price = take_profit
                        exit_reason = 'take_profit'
                        break
                    elif low_price <= stop_loss:
                        exit_time = timestamp
                        exit_price = stop_loss
                        exit_reason = 'stop_loss'
                        break
                else:  # short
                    if low_price <= take_profit:
                        exit_time = timestamp
                        exit_price = take_profit
                        exit_reason = 'take_profit'
                        break
                    elif high_price >= stop_loss:
                        exit_time = timestamp
                        exit_price = stop_loss
                        exit_reason = 'stop_loss'
                        break
            
            # If no exit found, force exit
            if exit_time is None:
                if exit_cutoff is not None:
                    exit_time = exit_cutoff
                    last_candle = data[data.index <= exit_cutoff]
                    exit_price = last_candle['close'].iloc[-1] if not last_candle.empty else entry_price
                    exit_reason = 'session_close'
                else:
                    exit_time = remaining_data.index[-1]
                    exit_price = remaining_data['close'].iloc[-1]
                    exit_reason = 'session_end'
        
        # Calculate PnL
        if side == 'long':
            gross_pnl = (exit_price - entry_price) * position_size
        else:
            gross_pnl = (entry_price - exit_price) * position_size
        
        # Calculate costs
        per_leg_commission = self.commission_rate / 2.0
        per_leg_slippage = self.slippage_rate / 2.0
        entry_commission = abs(entry_price * position_size * per_leg_commission)
        exit_commission = abs(exit_price * position_size * per_leg_commission)
        entry_slippage = abs(entry_price * position_size * per_leg_slippage)
        exit_slippage = abs(exit_price * position_size * per_leg_slippage)
        
        total_costs = entry_commission + exit_commission + entry_slippage + exit_slippage
        net_pnl = gross_pnl - total_costs
        
        # Calculate R-multiple
        risk_amount = abs(entry_price - stop_loss) * position_size
        r_multiple = net_pnl / risk_amount if risk_amount > 0 else 0
        
        return {
            'exit_time': exit_time,
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'pnl_usdt': net_pnl,
            'gross_pnl_usdt': gross_pnl,
            'commission_usdt': entry_commission + exit_commission,
            'slippage_usdt': entry_slippage + exit_slippage,
            'r_multiple': r_multiple
        }
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate strategy-specific indicators."""
        pass
    
    @abstractmethod
    def detect_signal(self, data: pd.DataFrame, index: int) -> Tuple[Optional[str], float]:
        """Detect trading signal based on strategy rules."""
        pass
    
    def process_day(self, day_data: pd.DataFrame, date: datetime.date) -> List[Dict]:
        """Process trading for a single day."""
        trades = []
        
        # Reset daily state
        self.reset_daily_state()
        
        # Calculate indicators
        data_with_indicators = self.calculate_indicators(day_data)
        
        # Filter by entry window
        local_data = day_data.copy()
        local_data.index = local_data.index.tz_convert(self.tz)
        
        ew_start, ew_end = self.entry_window
        entry_data_local = local_data[
            (local_data.index.hour >= ew_start) & 
            (local_data.index.hour < ew_end)
        ]
        
        # Convert back to UTC
        entry_data_local.index = entry_data_local.index.tz_convert(timezone.utc)
        entry_data = entry_data_local
        
        if entry_data.empty:
            return trades
        
        # Look for signals in entry window
        for i, (timestamp, row) in enumerate(entry_data.iterrows()):
            if not self.can_trade_today():
                break
            
            # Find index in data_with_indicators
            try:
                idx = data_with_indicators.index.get_loc(timestamp)
            except KeyError:
                continue
            
            # Detect signal
            signal_direction, confidence = self.detect_signal(data_with_indicators, idx)
            
            if signal_direction is None:
                continue
            
            # Check if shorts are allowed
            if signal_direction == 'short' and not self.allow_shorts:
                continue
            
            # Calculate trade parameters
            entry_price = row['open']
            trade_params = self.calculate_trade_params(
                signal_direction, entry_price, data_with_indicators, timestamp
            )
            
            if trade_params is None:
                continue
            
            # Simulate exit
            exit_info = self.simulate_trade_exit(trade_params, signal_direction, day_data)
            
            if exit_info:
                # Create trade record
                trade = {
                    'day_key': date.strftime('%Y-%m-%d'),
                    'entry_time': trade_params['entry_time'],
                    'side': signal_direction,
                    'entry_price': trade_params['entry_price'],
                    'sl': trade_params['stop_loss'],
                    'tp': trade_params['take_profit'],
                    'exit_time': exit_info['exit_time'],
                    'exit_price': exit_info['exit_price'],
                    'exit_reason': exit_info['exit_reason'],
                    'pnl_usdt': exit_info['pnl_usdt'],
                    'r_multiple': exit_info['r_multiple'],
                    'strategy_type': self.config.get('strategy_type', 'unknown'),
                    'confidence': confidence
                }
                
                trades.append(trade)
                
                # Update daily state
                self.daily_pnl += exit_info['pnl_usdt']
                self.daily_trades += 1
                
                # Only one trade per day
                break
        
        return trades


class MeanReversionStrategy(BaseStrategy):
    """Mean Reversion strategy using Bollinger Bands, RSI, and ATR."""
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate mean reversion indicators."""
        df = data.copy()
        
        # Bollinger Bands
        bb_period = self.config.get('bollinger_period', 20)
        bb_std = self.config.get('bollinger_std', 2.0)
        bb_upper, bb_middle, bb_lower = bollinger_bands(df['close'], bb_period, bb_std)
        df['bb_upper'] = bb_upper
        df['bb_middle'] = bb_middle
        df['bb_lower'] = bb_lower
        
        # RSI
        rsi_period = self.config.get('rsi_period', 14)
        df['rsi'] = rsi(df['close'], rsi_period)
        
        # ATR
        atr_period = self.config.get('atr_period', 14)
        df['atr'] = atr(df, atr_period)
        
        # Volume
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
        else:
            df['volume_ratio'] = 1.0
        
        return df
    
    def detect_signal(self, data: pd.DataFrame, index: int) -> Tuple[Optional[str], float]:
        """Detect mean reversion signals."""
        if index < 20:  # Need enough data for indicators
            return None, 0.0
        
        # Get current values
        current_price = data['close'].iloc[index]
        bb_upper = data['bb_upper'].iloc[index]
        bb_middle = data['bb_middle'].iloc[index]
        bb_lower = data['bb_lower'].iloc[index]
        rsi_value = data['rsi'].iloc[index]
        volume_ratio = data['volume_ratio'].iloc[index]
        
        # Volume threshold
        volume_threshold = self.config.get('volume_threshold', 1.2)
        
        # Check for oversold conditions (long signal)
        if (current_price <= bb_lower and 
            rsi_value <= self.config.get('rsi_oversold', 30) and
            volume_ratio >= volume_threshold):
            return 'long', 0.8
        
        # Check for overbought conditions (short signal - if allowed)
        if (self.allow_shorts and
            current_price >= bb_upper and 
            rsi_value >= self.config.get('rsi_overbought', 70) and
            volume_ratio >= volume_threshold):
            return 'short', 0.8
        
        return None, 0.0


class TrendFollowingStrategy(BaseStrategy):
    """Trend Following strategy using Heikin Ashi, ADX, and EMA crossovers."""
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate trend following indicators."""
        df = data.copy()
        
        # Heikin Ashi
        if self.config.get('heikin_ashi', True):
            ha_data = heikin_ashi(df)
            df['ha_open'] = ha_data['ha_open']
            df['ha_high'] = ha_data['ha_high']
            df['ha_low'] = ha_data['ha_low']
            df['ha_close'] = ha_data['ha_close']
        
        # ADX
        adx_period = self.config.get('adx_period', 14)
        df['adx'] = adx(df, adx_period)
        
        # EMAs
        ema_fast = self.config.get('ema_fast', 9)
        ema_slow = self.config.get('ema_slow', 21)
        df['ema_fast'] = ema(df, ema_fast, 'close')
        df['ema_slow'] = ema(df, ema_slow, 'close')
        
        # ATR
        atr_period = self.config.get('atr_period', 14)
        df['atr'] = atr(df, atr_period)
        
        # Volume
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
        else:
            df['volume_ratio'] = 1.0
        
        return df
    
    def detect_signal(self, data: pd.DataFrame, index: int) -> Tuple[Optional[str], float]:
        """Detect trend following signals."""
        if index < 25:  # Need enough data for indicators
            return None, 0.0
        
        # Get current values
        adx_value = data['adx'].iloc[index]
        ema_fast = data['ema_fast'].iloc[index]
        ema_slow = data['ema_slow'].iloc[index]
        volume_ratio = data['volume_ratio'].iloc[index]
        
        # ADX threshold
        adx_threshold = self.config.get('adx_threshold', 25)
        volume_threshold = self.config.get('volume_threshold', 1.1)
        
        # Check for strong trend
        if adx_value < adx_threshold or volume_ratio < volume_threshold:
            return None, 0.0
        
        # Check for EMA crossover
        ema_fast_prev = data['ema_fast'].iloc[index-1]
        ema_slow_prev = data['ema_slow'].iloc[index-1]
        
        # Bullish crossover
        if (ema_fast > ema_slow and 
            ema_fast_prev <= ema_slow_prev):
            return 'long', 0.9
        
        # Bearish crossover (if shorts allowed)
        if (self.allow_shorts and
            ema_fast < ema_slow and 
            ema_fast_prev >= ema_slow_prev):
            return 'short', 0.9
        
        return None, 0.0


class BreakoutFadeStrategy(BaseStrategy):
    """Breakout Fade strategy for counter-trend trading."""
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate breakout fade indicators."""
        df = data.copy()
        
        # Bollinger Bands for extreme levels
        bb_period = self.config.get('bollinger_period', 20)
        bb_std = self.config.get('bollinger_std', 2.5)
        bb_upper, bb_middle, bb_lower = bollinger_bands(df['close'], bb_period, bb_std)
        df['bb_upper'] = bb_upper
        df['bb_middle'] = bb_middle
        df['bb_lower'] = bb_lower
        
        # RSI for extreme levels
        rsi_period = self.config.get('rsi_period', 14)
        df['rsi'] = rsi(df['close'], rsi_period)
        
        # ATR
        atr_period = self.config.get('atr_period', 14)
        df['atr'] = atr(df, atr_period)
        
        # Volume
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
        else:
            df['volume_ratio'] = 1.0
        
        # Price change for breakout detection
        breakout_period = self.config.get('breakout_period', 20)
        df['price_change'] = df['close'].pct_change(breakout_period)
        
        return df
    
    def detect_signal(self, data: pd.DataFrame, index: int) -> Tuple[Optional[str], float]:
        """Detect breakout fade signals."""
        if index < 25:  # Need enough data for indicators
            return None, 0.0
        
        # Get current values
        current_price = data['close'].iloc[index]
        bb_upper = data['bb_upper'].iloc[index]
        bb_lower = data['bb_lower'].iloc[index]
        rsi_value = data['rsi'].iloc[index]
        volume_ratio = data['volume_ratio'].iloc[index]
        price_change = data['price_change'].iloc[index]
        
        # Thresholds
        breakout_threshold = self.config.get('breakout_threshold', 0.02)
        volume_threshold = self.config.get('volume_threshold', 1.5)
        rsi_extreme_high = self.config.get('rsi_extreme_high', 80)
        rsi_extreme_low = self.config.get('rsi_extreme_low', 20)
        
        # Check for volume spike
        if volume_ratio < volume_threshold:
            return None, 0.0
        
        # Check for breakout and fade conditions
        # Bullish breakout fade (short signal)
        if (price_change > breakout_threshold and  # Recent breakout up
            current_price >= bb_upper and  # Price at extreme
            rsi_value >= rsi_extreme_high and  # RSI overbought
            self.allow_shorts):
            return 'short', 0.7
        
        # Bearish breakout fade (long signal)
        if (price_change < -breakout_threshold and  # Recent breakout down
            current_price <= bb_lower and  # Price at extreme
            rsi_value <= rsi_extreme_low):  # RSI oversold
            return 'long', 0.7
        
        return None, 0.0


def get_strategy_for_mode(mode: str, config: Dict) -> BaseStrategy:
    """Get the appropriate strategy class for a given mode."""
    strategy_type = config.get('strategy_type', 'trend_following')
    
    if strategy_type == 'mean_reversion':
        return MeanReversionStrategy(config)
    elif strategy_type == 'trend_following':
        return TrendFollowingStrategy(config)
    elif strategy_type == 'breakout_fade':
        return BreakoutFadeStrategy(config)
    else:
        # Default to trend following
        return TrendFollowingStrategy(config)

