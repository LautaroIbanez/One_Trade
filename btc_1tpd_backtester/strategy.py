"""
Trading Strategy Module
Implements the 1 trade per day BTC strategy with ORB and fallback logic.
Now supports delegation to MultifactorStrategy.
Includes WindowedSignalStrategy for windowed daily quota implementation.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timezone, timedelta
from .indicators import (
    ema, atr, adx, vwap, opening_range_high, opening_range_low,
    opening_range_breakout, engulfing_pattern, volume_confirmation,
    calculate_r_multiple, get_macro_bias, is_trading_session,
    is_entry_window, is_orb_window, rsi, macd
)
from .strategy_multifactor import MultifactorStrategy

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class TradingStrategy:
    """Main trading strategy class implementing 1 trade per day logic."""
    
    def __init__(self, config):
        """Initialize strategy with configuration parameters."""
        self.config = config
        
        # Check if we should use multifactor strategy
        self.use_multifactor = config.get('use_multifactor_strategy', False)
        
        if self.use_multifactor:
            # Delegate to MultifactorStrategy
            self.multifactor_strategy = MultifactorStrategy(config)
            return
        
        # Original ORB strategy parameters
        self.signal_tf = config['signal_tf']
        self.risk_usdt = config['risk_usdt']
        self.daily_target = config['daily_target']
        self.daily_max_loss = config['daily_max_loss']
        self.force_one_trade = config['force_one_trade']
        self.fallback_mode = config['fallback_mode']
        self.adx_min = config['adx_min']
        self.min_rr_ok = config['min_rr_ok']
        self.atr_mult_orb = config['atr_mult_orb']
        self.atr_mult_fallback = config['atr_mult_fallback']
        self.tp_multiplier = config['tp_multiplier']
        self.target_r_multiple = config.get('target_r_multiple', self.tp_multiplier)
        self.risk_reward_ratio = config.get('risk_reward_ratio', self.tp_multiplier)
        
        # Trading windows and full day trading
        self.orb_window = config.get('orb_window', (11, 12))
        self.entry_window = config.get('entry_window', (11, 18))  # Extended to 18:00 UTC
        self.full_day_trading = config.get('full_day_trading', False)
        
        # Capital and leverage for position sizing
        self.initial_capital = config.get("initial_capital", 1000.0)
        self.leverage = config.get("leverage", 1.0)
        
        # Session times (UTC) - use configured windows or defaults
        self.orb_start = self.orb_window[0]
        self.orb_end = self.orb_window[1]
        self.entry_start = self.entry_window[0]
        self.entry_end = self.entry_window[1]
        self.session_end = 17  # 17:00 UTC
        
        # Adjust entry window for full day trading
        if self.full_day_trading:
            # Ensure entry starts after ORB ends and goes until 24:00
            self.entry_start = max(self.orb_window[1], self.entry_window[0])
            self.entry_end = 24
        
        # Daily state
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.max_daily_trades = 1
        
        # ORB levels cache (per day)
        self.orb_cache = {}
        
    def reset_daily_state(self):
        """Reset daily tracking variables."""
        if self.use_multifactor:
            return self.multifactor_strategy.reset_daily_state()
        
        self.daily_pnl = 0.0
        self.daily_trades = 0
    
    def get_orb_levels(self, ltf_data, current_time):
        """Calculate and cache ORB levels for the day."""
        # Get date key for caching
        if hasattr(current_time, 'date'):
            date_key = current_time.date()
        else:
            date_key = current_time.date()
        
        # Return cached levels if available
        if date_key in self.orb_cache:
            return self.orb_cache[date_key]
        
        # Calculate ORB levels for 11:00-12:00 UTC
        if hasattr(current_time, 'to_pydatetime'):
            dt = current_time.to_pydatetime()
        else:
            dt = current_time
        
        orb_start_time = dt.replace(hour=self.orb_start, minute=0, second=0, microsecond=0)
        orb_end_time = dt.replace(hour=self.orb_end, minute=0, second=0, microsecond=0)
        
        # Filter data for ORB window
        orb_data = ltf_data[(ltf_data.index >= orb_start_time) & (ltf_data.index < orb_end_time)]
        
        if orb_data.empty:
            self.orb_cache[date_key] = (None, None)
            return None, None
        
        orb_high = orb_data['high'].max()
        orb_low = orb_data['low'].min()
        
        # Cache the results
        self.orb_cache[date_key] = (orb_high, orb_low)
        return orb_high, orb_low
        
    def is_daily_target_reached(self):
        """Check if daily profit target is reached."""
        return self.daily_pnl >= self.daily_target
        
    def is_daily_loss_limit_reached(self):
        """Check if daily loss limit is reached."""
        return self.daily_pnl <= self.daily_max_loss
        
    def can_trade_today(self):
        """Check if trading is allowed today."""
        if self.use_multifactor:
            return self.multifactor_strategy.can_trade_today()
        
        return (self.daily_trades < self.max_daily_trades and 
                not self.is_daily_target_reached() and 
                not self.is_daily_loss_limit_reached())
        
    def calculate_position_size(self, entry_price, stop_loss):
        """Calculate position size based on risk management and capital constraints."""
        risk_amount = self.risk_usdt
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff == 0:
            return 0
            
        # Calculate position size based on risk
        position_size = risk_amount / price_diff
        
        # Apply capital and leverage constraints
        max_position_size = (self.initial_capital * self.leverage) / entry_price
        position_size = min(position_size, max_position_size)
        
        # Additional safety: max 1% of equity per trade
        max_equity_risk = risk_amount / (entry_price * 0.01)
        position_size = min(position_size, max_equity_risk)
        
        return position_size
    
    def get_stop_loss_price(self, entry_price, side, atr_value, is_orb=True):
        """Calculate stop loss price."""
        atr_mult = self.atr_mult_orb if is_orb else self.atr_mult_fallback
        
        if side == 'long':
            return entry_price - (atr_value * atr_mult)
        else:
            return entry_price + (atr_value * atr_mult)
    
    def get_take_profit_price(self, entry_price, stop_loss, side):
        """Calculate take profit price based on target R-multiple."""
        risk = abs(entry_price - stop_loss)
        reward = risk * self.target_r_multiple
        
        if side == 'long':
            return entry_price + reward
        else:
            return entry_price - reward
    
    def check_orb_conditions(self, ltf_data, htf_data, side):
        """Check Opening Range Breakout conditions."""
        try:
            # Get current time
            current_time = ltf_data.index[-1]
            
            # Check if we're in entry window (11:00-13:00 UTC)
            if not (self.entry_start <= current_time.hour < self.entry_end):
                return False, None, None, None
            
            # Get ORB levels (cached)
            orb_high, orb_low = self.get_orb_levels(ltf_data, current_time)
            
            if pd.isna(orb_high) or pd.isna(orb_low):
                return False, None, None, None
            
            # Check for breakout in entry window
            current_price = ltf_data['close'].iloc[-1]
            breakout_detected = False
            
            if side == 'long' and current_price > orb_high:
                breakout_detected = True
            elif side == 'short' and current_price < orb_low:
                breakout_detected = True
            
            if not breakout_detected:
                return False, orb_high, orb_low, None
            
            # Get current price as entry price
            entry_price = current_price
            
            # Calculate indicators
            atr_value = atr(ltf_data, 14).iloc[-1]
            adx_value = adx(ltf_data, 14).iloc[-1]
            vwap_value = vwap(ltf_data).iloc[-1]
            
            # Check confirmations (relaxed)
            volume_ok = volume_confirmation(ltf_data, 20)
            adx_ok = adx_value >= self.adx_min
            
            if side == 'long':
                vwap_ok = entry_price > vwap_value
            else:
                vwap_ok = entry_price < vwap_value
            
            # Relaxed conditions: Only require volume and ADX, VWAP is nice-to-have
            if volume_ok and adx_ok:
                stop_loss = self.get_stop_loss_price(entry_price, side, atr_value, True)
                take_profit = self.get_take_profit_price(entry_price, stop_loss, side)
                
                # Calculate position size with capital and leverage constraints
                position_size = self.calculate_position_size(entry_price, stop_loss)
                
                # Skip trade if position size is zero (insufficient capital/leverage)
                if position_size <= 0:
                    return False, orb_high, orb_low, None
                
                # Recalculate effective risk based on capped position size
                effective_risk_usdt = abs(entry_price - stop_loss) * position_size
                
                return True, orb_high, orb_low, {
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'atr_value': atr_value,
                    'adx_value': adx_value,
                    'vwap_value': vwap_value,
                    'position_size': position_size,
                    'effective_risk_usdt': effective_risk_usdt
                }
            
            return False, orb_high, orb_low, None
            
        except Exception as e:
            print(f"Error in ORB check: {e}")
            return False, None, None, None
    
    def check_ema15_pullback_conditions(self, ltf_data, htf_data, side):
        """Check EMA15 pullback conditions for fallback strategy."""
        try:
            if len(ltf_data) < 15:
                return False, None
            
            # Calculate EMA15
            ema15 = ema(ltf_data, 15).iloc[-1]
            current_price = ltf_data['close'].iloc[-1]
            
            # Check pullback to EMA15
            if side == 'long':
                pullback_ok = current_price <= ema15 * 1.001  # Small tolerance
                engulfing_ok, engulfing_type = engulfing_pattern(ltf_data)
                engulfing_ok = engulfing_ok and engulfing_type == 'bullish'
            else:
                pullback_ok = current_price >= ema15 * 0.999  # Small tolerance
                engulfing_ok, engulfing_type = engulfing_pattern(ltf_data)
                engulfing_ok = engulfing_ok and engulfing_type == 'bearish'
            
            if not pullback_ok or not engulfing_ok:
                return False, None
            
            # Check volume confirmation
            if not volume_confirmation(ltf_data, 20):
                return False, None
            
            # Calculate trade parameters
            entry_price = current_price
            atr_value = atr(ltf_data, 14).iloc[-1]
            stop_loss = self.get_stop_loss_price(entry_price, side, atr_value, False)
            take_profit = self.get_take_profit_price(entry_price, stop_loss, side)
            
            # Calculate position size with capital and leverage constraints
            position_size = self.calculate_position_size(entry_price, stop_loss)
            
            # Skip trade if position size is zero (insufficient capital/leverage)
            if position_size <= 0:
                return False, None
            
            # Recalculate effective risk based on capped position size
            effective_risk_usdt = abs(entry_price - stop_loss) * position_size
            
            # Check R/R ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0
            
            if rr_ratio >= self.min_rr_ok:
                return True, {
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'atr_value': atr_value,
                    'rr_ratio': rr_ratio,
                    'ema15': ema15,
                    'position_size': position_size,
                    'effective_risk_usdt': effective_risk_usdt
                }
            
            return False, None
            
        except Exception as e:
            print(f"Error in EMA15 pullback check: {e}")
            return False, None
    
    def get_trade_signal(self, ltf_data, htf_data, current_time):
        """Get trading signal for current timestamp."""
        if self.use_multifactor:
            # Delegate to multifactor strategy
            # Convert to the format expected by MultifactorStrategy
            date = current_time.date()
            trades = self.multifactor_strategy.process_day(ltf_data, date)
            
            if trades:
                trade = trades[0]  # Get first trade
                return {
                    'side': trade['side'],
                    'strategy': 'multifactor',
                    'entry_price': trade['entry_price'],
                    'stop_loss': trade['sl'],
                    'take_profit': trade['tp'],
                    'reliability_score': trade.get('reliability_score', 0.0),
                    'position_size': self.calculate_position_size(trade['entry_price'], trade['sl']),
                    'effective_risk_usdt': abs(trade['entry_price'] - trade['sl']) * self.calculate_position_size(trade['entry_price'], trade['sl'])
                }
            return None
        
        # Original ORB strategy logic
        try:
            # Check if we can trade today
            if not self.can_trade_today():
                return None
            
            # Check if we're in entry window
            if not is_entry_window(current_time):
                return None
            
            # Get macro bias (but don't restrict trades based on it)
            macro_bias = get_macro_bias(htf_data)
            
            # Try both long and short ORB strategies regardless of macro bias
            for side in ['long', 'short']:
                orb_ok, orb_high, orb_low, trade_params = self.check_orb_conditions(ltf_data, htf_data, side)
                if orb_ok and trade_params:
                    return {
                        'side': side,
                        'strategy': 'orb',
                        'entry_price': trade_params['entry_price'],
                        'stop_loss': trade_params['stop_loss'],
                        'take_profit': trade_params['take_profit'],
                        'orb_high': orb_high,
                        'orb_low': orb_low,
                        'confirmations': {
                            'atr': trade_params['atr_value'],
                            'adx': trade_params['adx_value'],
                            'vwap': trade_params['vwap_value']
                        },
                        'position_size': trade_params['position_size'],
                        'effective_risk_usdt': trade_params['effective_risk_usdt']
                    }
            
            # Try fallback strategies if ORB didn't work and we're forcing one trade
            if self.force_one_trade and current_time.hour >= 13:
                if self.fallback_mode in ['EMA15_pullback', 'BestOfBoth']:
                    for side in ['long', 'short']:
                        ema_ok, trade_params = self.check_ema15_pullback_conditions(ltf_data, htf_data, side)
                        if ema_ok and trade_params:
                            return {
                                'side': side,
                                'strategy': 'ema15_pullback',
                                'entry_price': trade_params['entry_price'],
                                'stop_loss': trade_params['stop_loss'],
                                'take_profit': trade_params['take_profit'],
                                'rr_ratio': trade_params['rr_ratio'],
                                'ema15': trade_params['ema15'],
                                'position_size': trade_params['position_size'],
                                'effective_risk_usdt': trade_params['effective_risk_usdt']
                            }
            
            return None
            
        except Exception as e:
            print(f"Error getting trade signal: {e}")
            return None
    
    def should_exit_trade(self, trade, current_price, current_time, is_break_even=False):
        """Check if trade should be exited."""
        try:
            # Force close at session end (only if not in full_day_trading mode)
            if not self.full_day_trading and current_time.hour >= self.session_end:
                return True, 'session_end', current_price
            
            # Check stop loss
            if trade['side'] == 'long':
                if current_price <= trade['stop_loss']:
                    return True, 'stop_loss', current_price
                if current_price >= trade['take_profit']:
                    return True, 'take_profit', current_price
                if is_break_even and current_price >= trade['break_even_price']:
                    return True, 'break_even', current_price
            else:  # short
                if current_price >= trade['stop_loss']:
                    return True, 'stop_loss', current_price
                if current_price <= trade['take_profit']:
                    return True, 'take_profit', current_price
                if is_break_even and current_price <= trade['break_even_price']:
                    return True, 'break_even', current_price
            
            return False, None, None
            
        except Exception as e:
            print(f"Error checking exit conditions: {e}")
            return True, 'error', current_price
    
    def calculate_trade_pnl(self, trade, exit_price, exit_reason):
        """Calculate trade PnL."""
        try:
            entry_price = trade['entry_price']
            side = trade['side']
            position_size = trade['position_size']
            
            if side == 'long':
                pnl = (exit_price - entry_price) * position_size
            else:
                pnl = (entry_price - exit_price) * position_size
            
            return pnl
            
        except Exception as e:
            print(f"Error calculating PnL: {e}")
            return 0.0


class WindowedSignalStrategy:
    """Window-aware signal generator with daily quota management. Encapsulates configuration for entry windows, timezone, and risk sizing. Implements pure signal generation with EMA/RSI/MACD alignment and ATR-based stops."""
    MAX_TRADES_PER_DAY = 1
    DEFAULT_TIMEZONE = 'America/Argentina/Buenos_Aires'
    DEFAULT_ENTRY_WINDOWS = [(5, 8), (11, 14)]
    DEFAULT_ATR_MULTIPLIER = 2.0
    DEFAULT_RISK_REWARD_RATIO = 1.5
    DEFAULT_EMA_FAST = 9
    DEFAULT_EMA_SLOW = 21
    DEFAULT_RSI_PERIOD = 14
    DEFAULT_ATR_PERIOD = 14
    def __init__(self, config: dict):
        """Initialize windowed signal strategy with configuration. Args: config: Dictionary containing entry_windows (list of tuples), timezone (str), risk_usdt (float), leverage (float), atr_multiplier (float), risk_reward_ratio (float), ema_fast (int), ema_slow (int), rsi_period (int), atr_period (int)"""
        self.config = config
        self.entry_windows = config.get('entry_windows', self.DEFAULT_ENTRY_WINDOWS)
        self.timezone_str = config.get('timezone', self.DEFAULT_TIMEZONE)
        try:
            self.local_tz = ZoneInfo(self.timezone_str)
        except Exception as e:
            logger.warning(f"Failed to load timezone {self.timezone_str}, falling back to UTC: {e}")
            self.local_tz = timezone.utc
        self.risk_usdt = config.get('risk_usdt', 20.0)
        self.leverage = config.get('leverage', 1.0)
        self.initial_capital = config.get('initial_capital', 1000.0)
        self.atr_multiplier = config.get('atr_multiplier', self.DEFAULT_ATR_MULTIPLIER)
        self.risk_reward_ratio = config.get('risk_reward_ratio', self.DEFAULT_RISK_REWARD_RATIO)
        self.ema_fast = config.get('ema_fast', self.DEFAULT_EMA_FAST)
        self.ema_slow = config.get('ema_slow', self.DEFAULT_EMA_SLOW)
        self.rsi_period = config.get('rsi_period', self.DEFAULT_RSI_PERIOD)
        self.atr_period = config.get('atr_period', self.DEFAULT_ATR_PERIOD)
        self._market_data = None
        self._indicator_frame = None
        self._daily_trade_counts = {}
        logger.info(f"WindowedSignalStrategy initialized with windows={self.entry_windows}, tz={self.timezone_str}, risk={self.risk_usdt}")
    def _to_local(self, dt: datetime) -> datetime:
        """Convert UTC datetime to local timezone (ART). Args: dt: UTC datetime. Returns: datetime in local timezone"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(self.local_tz)
    def set_market_data(self, data: pd.DataFrame):
        """Sort incoming OHLCV data and pre-compute indicators. Args: data: DataFrame with OHLCV columns and datetime index"""
        self._market_data = data.sort_index()
        self._prepare_indicator_frame()
        logger.debug(f"Market data set: {len(self._market_data)} bars, date range {self._market_data.index[0]} to {self._market_data.index[-1]}")
    def _prepare_indicator_frame(self):
        """Pre-compute EMA, RSI, MACD, and ATR columns on the market data."""
        if self._market_data is None or self._market_data.empty:
            self._indicator_frame = None
            return
        df = self._market_data.copy()
        df['ema_fast'] = ema(df, self.ema_fast)
        df['ema_slow'] = ema(df, self.ema_slow)
        df['rsi'] = rsi(df, self.rsi_period)
        macd_result = macd(df)
        if isinstance(macd_result, tuple) and len(macd_result) >= 2:
            df['macd'] = macd_result[0]
            df['macd_signal'] = macd_result[1]
        else:
            df['macd'] = macd_result if isinstance(macd_result, pd.Series) else pd.Series(index=df.index, dtype=float)
            df['macd_signal'] = pd.Series(index=df.index, dtype=float)
        df['atr'] = atr(df, self.atr_period)
        self._indicator_frame = df
        logger.debug(f"Indicators computed: EMA({self.ema_fast}/{self.ema_slow}), RSI({self.rsi_period}), MACD, ATR({self.atr_period})")
    def _reset_counter_if_needed(self, dt: datetime):
        """Reset daily trade counter if a new local calendar day has started. Args: dt: Current datetime (UTC)"""
        local_dt = self._to_local(dt)
        local_date = local_dt.date()
        if local_date not in self._daily_trade_counts:
            for existing_date in list(self._daily_trade_counts.keys()):
                if existing_date < local_date:
                    del self._daily_trade_counts[existing_date]
            self._daily_trade_counts[local_date] = 0
            logger.debug(f"Daily counter reset for {local_date}")
    def record_trade(self, dt: datetime):
        """Record that a trade was executed on this local calendar day. Args: dt: Trade datetime (UTC)"""
        local_dt = self._to_local(dt)
        local_date = local_dt.date()
        self._daily_trade_counts[local_date] = self._daily_trade_counts.get(local_date, 0) + 1
        logger.debug(f"Trade recorded for {local_date}, count now {self._daily_trade_counts[local_date]}")
    def is_time_in_entry_window(self, dt: datetime) -> bool:
        """Check if the given datetime falls within any configured entry window. Args: dt: Datetime to check (UTC). Returns: True if within entry window, False otherwise"""
        local_dt = self._to_local(dt)
        local_hour = local_dt.hour
        for window_start, window_end in self.entry_windows:
            if window_start <= local_hour < window_end:
                return True
        return False
    def can_trade_today(self, dt: datetime) -> bool:
        """Check if we can still trade today based on daily quota. Args: dt: Current datetime (UTC). Returns: True if daily quota not reached, False otherwise"""
        self._reset_counter_if_needed(dt)
        local_dt = self._to_local(dt)
        local_date = local_dt.date()
        count = self._daily_trade_counts.get(local_date, 0)
        can_trade = count < self.MAX_TRADES_PER_DAY
        if not can_trade:
            logger.debug(f"Daily quota reached for {local_date}: {count}/{self.MAX_TRADES_PER_DAY}")
        return can_trade
    def compute_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate position size honouring per-trade risk budgets and leverage caps. Args: entry_price: Entry price, stop_loss: Stop loss price. Returns: Position size in base currency"""
        if entry_price <= 0 or stop_loss <= 0:
            return 0.0
        risk_distance = abs(entry_price - stop_loss)
        if risk_distance == 0:
            return 0.0
        position_size_by_risk = self.risk_usdt / risk_distance
        max_position_by_capital = (self.initial_capital * self.leverage) / entry_price
        position_size = min(position_size_by_risk, max_position_by_capital)
        return max(position_size, 0.0)
    def generate_signal(self, index: int) -> dict:
        """Generate pure trading signal at given index. Uses EMA/RSI/MACD alignment rules first, falls back to simple momentum when indicators unavailable. Args: index: Integer index into indicator frame. Returns: dict with keys: side (str), entry_price (float), sl (float), tp (float), reason (str), valid (bool)"""
        if self._indicator_frame is None or index >= len(self._indicator_frame) or index < 0:
            logger.debug(f"Invalid signal generation: index={index}, frame_len={len(self._indicator_frame) if self._indicator_frame is not None else 0}")
            return {'side': None, 'entry_price': None, 'sl': None, 'tp': None, 'reason': 'no_data', 'valid': False}
        row = self._indicator_frame.iloc[index]
        entry_price = row['close']
        atr_value = row['atr']
        ema_fast_val = row['ema_fast']
        ema_slow_val = row['ema_slow']
        rsi_val = row['rsi']
        macd_val = row['macd']
        macd_signal_val = row['macd_signal']
        if pd.isna(entry_price) or entry_price <= 0:
            logger.debug(f"signal_generation_failed: invalid entry_price={entry_price}")
            return {'side': None, 'entry_price': None, 'sl': None, 'tp': None, 'reason': 'invalid_price', 'valid': False}
        has_indicators = not pd.isna(ema_fast_val) and not pd.isna(ema_slow_val) and not pd.isna(rsi_val) and not pd.isna(macd_val) and not pd.isna(macd_signal_val)
        if has_indicators:
            bullish = (ema_fast_val > ema_slow_val) and (rsi_val < 70) and (macd_val > macd_signal_val)
            bearish = (ema_fast_val < ema_slow_val) and (rsi_val > 30) and (macd_val < macd_signal_val)
            if bullish:
                side = 'long'
                reason = 'ema_rsi_macd_bullish'
            elif bearish:
                side = 'short'
                reason = 'ema_rsi_macd_bearish'
            else:
                logger.debug(f"no_alignment: ema_fast={ema_fast_val:.2f}, ema_slow={ema_slow_val:.2f}, rsi={rsi_val:.1f}, macd={macd_val:.2f}, signal={macd_signal_val:.2f}")
                return {'side': None, 'entry_price': None, 'sl': None, 'tp': None, 'reason': 'no_alignment', 'valid': False}
        else:
            if index > 0:
                prev_close = self._indicator_frame.iloc[index - 1]['close']
                if not pd.isna(prev_close) and prev_close > 0:
                    if entry_price > prev_close:
                        side = 'long'
                        reason = 'momentum_fallback_bullish'
                    elif entry_price < prev_close:
                        side = 'short'
                        reason = 'momentum_fallback_bearish'
                    else:
                        logger.debug(f"fallback_no_momentum: entry_price={entry_price}, prev_close={prev_close}")
                        return {'side': None, 'entry_price': None, 'sl': None, 'tp': None, 'reason': 'no_momentum', 'valid': False}
                else:
                    logger.debug(f"fallback_invalid_prev_close: prev_close={prev_close}")
                    return {'side': None, 'entry_price': None, 'sl': None, 'tp': None, 'reason': 'invalid_prev_data', 'valid': False}
            else:
                logger.debug(f"fallback_insufficient_history: index={index}")
                return {'side': None, 'entry_price': None, 'sl': None, 'tp': None, 'reason': 'insufficient_history', 'valid': False}
        if pd.isna(atr_value) or atr_value <= 0:
            default_atr = entry_price * 0.02
            logger.warning(f"Invalid ATR={atr_value}, using default 2% of price: {default_atr}")
            atr_value = default_atr
        stop_distance = atr_value * self.atr_multiplier
        if side == 'long':
            sl = entry_price - stop_distance
            tp = entry_price + (stop_distance * self.risk_reward_ratio)
        else:
            sl = entry_price + stop_distance
            tp = entry_price - (stop_distance * self.risk_reward_ratio)
        if sl <= 0 or tp <= 0:
            logger.warning(f"Invalid stop/target: sl={sl}, tp={tp}, using fallback")
            sl = entry_price * 0.98 if side == 'long' else entry_price * 1.02
            tp = entry_price * 1.03 if side == 'long' else entry_price * 0.97
        logger.debug(f"signal_generated: side={side}, entry={entry_price:.2f}, sl={sl:.2f}, tp={tp:.2f}, reason={reason}")
        return {'side': side, 'entry_price': entry_price, 'sl': sl, 'tp': tp, 'reason': reason, 'valid': True}
