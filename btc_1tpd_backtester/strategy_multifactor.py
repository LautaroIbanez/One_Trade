#!/usr/bin/env python3
"""
Estrategia Multifactor con Control de Fiabilidad
Combina filtros de tendencia multitemporal, confirmaciones de momentum/volumen
y gestión dinámica de SL/TP para sesiones y trading 24h.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional, Union
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from .indicators import ema, atr, adx, vwap, rsi, macd


class MultifactorStrategy:
    """
    Estrategia multifactor que combina múltiples indicadores técnicos
    para generar señales de trading con control de fiabilidad.
    """
    
    def __init__(self, config: Dict):
        """
        Inicializar estrategia multifactor con configuración.
        
        Args:
            config: Diccionario de configuración con parámetros de la estrategia
        """
        self.config = config
        
        # Parámetros básicos
        self.risk_usdt = config.get('risk_usdt', 20.0)
        self.initial_capital = config.get('initial_capital', 1000.0)
        self.leverage = config.get('leverage', 1.0)
        
        # Parámetros de trading
        self.force_one_trade = config.get('force_one_trade', True)
        self.max_daily_trades = config.get('max_daily_trades', 1)
        self.daily_target = config.get('daily_target', 50.0)
        self.daily_max_loss = config.get('daily_max_loss', -30.0)
        
        # Ventanas de trading
        self.orb_window = config.get('orb_window', (8, 9))
        self.entry_window = config.get('entry_window', (11, 14))
        self.exit_window = config.get('exit_window', (20, 22))
        self.full_day_trading = False  # Always use session trading
        self.session_trading = True
        
        # Timezone
        self.session_timezone = config.get('session_timezone', 'America/Argentina/Buenos_Aires')
        try:
            self.tz = ZoneInfo(self.session_timezone)
        except Exception:
            self.tz = ZoneInfo('America/Argentina/Buenos_Aires')
        
        # Parámetros de indicadores
        self.ema_fast = config.get('ema_fast', 12)
        self.ema_slow = config.get('ema_slow', 26)
        self.adx_period = config.get('adx_period', 14)
        self.adx_min = config.get('adx_min', 25.0)
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.macd_fast = config.get('macd_fast', 12)
        self.macd_slow = config.get('macd_slow', 26)
        self.macd_signal = config.get('macd_signal', 9)
        
        # Parámetros de gestión de riesgo
        self.atr_multiplier = config.get('atr_multiplier', 2.0)
        self.tp_multiplier = config.get('tp_multiplier', 2.0)
        self.target_r_multiple = config.get('target_r_multiple', 2.0)
        self.risk_reward_ratio = config.get('risk_reward_ratio', 2.0)
        self.dynamic_sl = config.get('dynamic_sl', True)
        self.trailing_stop = config.get('trailing_stop', False)
        self.trailing_stop_atr = config.get('trailing_stop_atr', 1.5)
        
        # Parámetros de fiabilidad
        self.min_reliability_score = config.get('min_reliability_score', 0.6)
        self.volume_confirmation = config.get('volume_confirmation', True)
        self.volume_threshold = config.get('volume_threshold', 1.2)  # 1.2x promedio
        self.momentum_confirmation = config.get('momentum_confirmation', True)
        
        # Costos
        self.commission_rate = config.get('commission_rate', 0.001)
        self.slippage_rate = config.get('slippage_rate', 0.0005)
        
        # Estado diario
        self.daily_pnl = 0.0
        self.daily_trades = 0
        
        # Datos diarios para filtro de tendencia
        self.daily_data = None
        self.use_daily_trend_filter = config.get('use_daily_trend_filter', False)
        
        # Reentrada
        self.allow_reentry_on_trend_change = config.get('allow_reentry_on_trend_change', False)
    
    def reset_daily_state(self):
        """Resetear estado diario."""
        self.daily_pnl = 0.0
        self.daily_trades = 0
    
    def can_trade_today(self) -> bool:
        """Verificar si se puede operar hoy."""
        return (self.daily_trades < self.max_daily_trades and 
                self.daily_pnl < self.daily_target and 
                self.daily_pnl > self.daily_max_loss)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcular todos los indicadores técnicos necesarios.
        
        Args:
            data: DataFrame con datos OHLCV
            
        Returns:
            DataFrame con indicadores calculados
        """
        df = data.copy()
        
        # EMAs
        df['ema_fast'] = ema(df['close'], self.ema_fast)
        df['ema_slow'] = ema(df['close'], self.ema_slow)
        df['ema_trend'] = np.where(df['ema_fast'] > df['ema_slow'], 1, -1)
        
        # ADX
        df['adx'] = adx(df, self.adx_period)
        df['adx_strength'] = np.where(df['adx'] >= self.adx_min, 1, 0)
        
        # RSI
        df['rsi'] = rsi(df['close'], self.rsi_period)
        df['rsi_signal'] = np.where(df['rsi'] < self.rsi_oversold, 1, 
                                   np.where(df['rsi'] > self.rsi_overbought, -1, 0))
        
        # MACD
        macd_line, signal_line, histogram = macd(df['close'], self.macd_fast, self.macd_slow, self.macd_signal)
        df['macd'] = macd_line
        df['macd_signal'] = signal_line
        df['macd_histogram'] = histogram
        df['macd_trend'] = np.where(df['macd'] > df['macd_signal'], 1, -1)
        
        # ATR
        df['atr'] = atr(df, 14)
        
        # VWAP
        df['vwap'] = vwap(df)
        df['vwap_deviation'] = (df['close'] - df['vwap']) / df['vwap'] * 100
        
        # Volumen
        if 'volume' in df.columns:
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['volume_confirmation'] = np.where(df['volume_ratio'] >= self.volume_threshold, 1, 0)
        else:
            df['volume_confirmation'] = 1  # Sin datos de volumen
        
        return df
    
    def calculate_reliability_score(self, data: pd.DataFrame, index: int) -> float:
        """
        Calcular puntuación de fiabilidad para una señal.
        
        Args:
            data: DataFrame con indicadores
            index: Índice del punto de evaluación
            
        Returns:
            Puntuación de fiabilidad entre 0 y 1
        """
        if index < max(self.ema_slow, self.adx_period, self.rsi_period):
            return 0.0
        
        scores = []
        
        # 1. Tendencia EMA (peso: 0.25)
        if 'ema_trend' in data.columns:
            ema_score = 1.0 if data['ema_trend'].iloc[index] != 0 else 0.5
            scores.append(('ema_trend', ema_score, 0.25))
        
        # 2. Fuerza ADX (peso: 0.20)
        if 'adx_strength' in data.columns:
            adx_score = data['adx_strength'].iloc[index]
            scores.append(('adx_strength', adx_score, 0.20))
        
        # 3. Momentum RSI (peso: 0.15)
        if 'rsi_signal' in data.columns:
            rsi_score = 0.8 if abs(data['rsi_signal'].iloc[index]) == 1 else 0.4
            scores.append(('rsi_momentum', rsi_score, 0.15))
        
        # 4. MACD (peso: 0.20)
        if 'macd_trend' in data.columns:
            macd_score = 1.0 if data['macd_trend'].iloc[index] != 0 else 0.5
            scores.append(('macd_trend', macd_score, 0.20))
        
        # 5. Confirmación de volumen (peso: 0.10)
        if 'volume_confirmation' in data.columns:
            vol_score = data['volume_confirmation'].iloc[index]
            scores.append(('volume_confirmation', vol_score, 0.10))
        
        # 6. Desviación VWAP (peso: 0.10)
        if 'vwap_deviation' in data.columns:
            vwap_dev = abs(data['vwap_deviation'].iloc[index])
            vwap_score = min(1.0, vwap_dev / 2.0)  # Normalizar a 2% desviación
            scores.append(('vwap_deviation', vwap_score, 0.10))
        
        # Calcular puntuación ponderada
        total_score = sum(score * weight for _, score, weight in scores)
        total_weight = sum(weight for _, _, weight in scores)
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def detect_signal(self, data: pd.DataFrame, index: int) -> Tuple[Optional[str], float]:
        """
        Detectar señal de trading en un punto específico.
        
        Args:
            data: DataFrame con indicadores
            index: Índice del punto de evaluación
            
        Returns:
            Tupla (dirección, puntuación de fiabilidad)
        """
        if index < max(self.ema_slow, self.adx_period, self.rsi_period):
            return None, 0.0
        
        # Calcular puntuación de fiabilidad
        reliability = self.calculate_reliability_score(data, index)
        
        if reliability < self.min_reliability_score:
            return None, reliability
        
        # Determinar dirección basada en indicadores
        signals = []
        
        # EMA Trend
        if 'ema_trend' in data.columns:
            signals.append(data['ema_trend'].iloc[index])
        
        # MACD Trend
        if 'macd_trend' in data.columns:
            signals.append(data['macd_trend'].iloc[index])
        
        # RSI Signal (invertido para momentum)
        if 'rsi_signal' in data.columns:
            rsi_signal = data['rsi_signal'].iloc[index]
            if rsi_signal == 1:  # Oversold -> Bullish
                signals.append(1)
            elif rsi_signal == -1:  # Overbought -> Bearish
                signals.append(-1)
        
        # Determinar dirección final
        if not signals:
            return None, reliability
        
        signal_sum = sum(signals)
        if signal_sum > 0:
            return 'long', reliability
        elif signal_sum < 0:
            return 'short', reliability
        else:
            return None, reliability
    
    def calculate_trade_params(self, side: str, entry_price: float, data: pd.DataFrame, 
                             entry_time: pd.Timestamp) -> Optional[Dict]:
        """
        Calcular parámetros de la operación.
        
        Args:
            side: Dirección de la operación ('long' o 'short')
            entry_price: Precio de entrada
            data: DataFrame con datos e indicadores
            entry_time: Timestamp de entrada
            
        Returns:
            Diccionario con parámetros de la operación
        """
        try:
            # Encontrar el índice correspondiente al entry_time
            entry_idx = data.index.get_loc(entry_time)
            
            # ATR para stop loss
            atr_value = data['atr'].iloc[entry_idx] if 'atr' in data.columns else entry_price * 0.01
            
            # Calcular stop loss
            if side == 'long':
                stop_loss = entry_price - (atr_value * self.atr_multiplier)
                take_profit = entry_price + (atr_value * self.tp_multiplier)
            else:
                stop_loss = entry_price + (atr_value * self.atr_multiplier)
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
            
            # Calcular tamaño de posición
            risk_amount = self.risk_usdt
            price_diff = abs(entry_price - stop_loss)
            position_size = risk_amount / price_diff if price_diff > 0 else 0
            
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
        """
        Simular salida de la operación.
        
        Args:
            trade_params: Parámetros de la operación
            side: Dirección de la operación
            data: DataFrame con datos
            
        Returns:
            Diccionario con información de salida
        """
        entry_price = trade_params['entry_price']
        stop_loss = trade_params['stop_loss']
        take_profit = trade_params['take_profit']
        position_size = trade_params['position_size']
        entry_time = trade_params['entry_time']
        
        # Obtener datos posteriores a la entrada
        remaining_data = data[data.index > entry_time]
        
        # Calcular cutoff time para session trading
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
            # Salida forzada
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
            # Evaluar cada vela
            exit_time = None
            exit_price = None
            exit_reason = None
            
            for timestamp, candle in remaining_data.iterrows():
                high_price = candle['high']
                low_price = candle['low']
                close_price = candle['close']
                
                # Verificar TP y SL
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
            
            # Si no se encontró salida, forzar
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
        
        # Calcular PnL
        if side == 'long':
            gross_pnl = (exit_price - entry_price) * position_size
        else:
            gross_pnl = (entry_price - exit_price) * position_size
        
        # Calcular costos
        per_leg_commission = self.commission_rate / 2.0
        per_leg_slippage = self.slippage_rate / 2.0
        entry_commission = abs(entry_price * position_size * per_leg_commission)
        exit_commission = abs(exit_price * position_size * per_leg_commission)
        entry_slippage = abs(entry_price * position_size * per_leg_slippage)
        exit_slippage = abs(exit_price * position_size * per_leg_slippage)
        
        total_costs = entry_commission + exit_commission + entry_slippage + exit_slippage
        net_pnl = gross_pnl - total_costs
        
        # Calcular R-multiple
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
    
    def process_day(self, day_data: pd.DataFrame, date: datetime.date) -> List[Dict]:
        """
        Procesar trading para un día específico.
        
        Args:
            day_data: DataFrame con datos del día
            date: Fecha del día
            
        Returns:
            Lista de operaciones del día
        """
        trades = []
        
        # Resetear estado diario
        self.reset_daily_state()
        
        # Calcular indicadores
        data_with_indicators = self.calculate_indicators(day_data)
        
        # Usar datos de sesión
        session_data = day_data
        
        # Convertir a timezone local para filtrado
        local_session_data = session_data.copy()
        local_session_data.index = local_session_data.index.tz_convert(self.tz)
        
        # Filtrar por ventana de entrada
        ew_start, ew_end = self.entry_window
        entry_data_local = local_session_data[
            (local_session_data.index.hour >= ew_start) & 
            (local_session_data.index.hour < ew_end)
        ]
        
        # Convertir de vuelta a UTC
        entry_data_local.index = entry_data_local.index.tz_convert(timezone.utc)
        entry_data = entry_data_local
        
        if entry_data.empty:
            return trades
        
        # Buscar señales en la ventana de entrada
        for i, (timestamp, row) in enumerate(entry_data.iterrows()):
            if not self.can_trade_today():
                break
            
            # Encontrar índice en data_with_indicators
            try:
                idx = data_with_indicators.index.get_loc(timestamp)
            except KeyError:
                continue
            
            # Detectar señal
            signal_direction, reliability = self.detect_signal(data_with_indicators, idx)
            
            if signal_direction is None or reliability < self.min_reliability_score:
                continue
            
            # Calcular parámetros de la operación
            entry_price = row['open']  # Usar precio de apertura
            trade_params = self.calculate_trade_params(
                signal_direction, entry_price, data_with_indicators, timestamp
            )
            
            if trade_params is None:
                continue
            
            # Simular salida
            exit_info = self.simulate_trade_exit(trade_params, signal_direction, day_data)
            
            if exit_info:
                # Crear registro de operación
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
                    'reliability_score': reliability,
                    'used_multifactor': True
                }
                
                trades.append(trade)
                
                # Actualizar estado diario
                self.daily_pnl += exit_info['pnl_usdt']
                self.daily_trades += 1
                
                # Si force_one_trade está activado, salir después de la primera operación
                if self.force_one_trade:
                    break
        
        return trades
    
    def get_strategy_info(self) -> Dict:
        """
        Obtener información sobre la estrategia.
        
        Returns:
            Diccionario con información de la estrategia
        """
        return {
            'name': 'MultifactorStrategy',
            'version': '1.0.0',
            'description': 'Estrategia multifactor con control de fiabilidad',
            'indicators': ['EMA', 'ADX', 'RSI', 'MACD', 'ATR', 'VWAP'],
            'reliability_control': True,
            'dynamic_sl_tp': self.dynamic_sl,
            'trailing_stop': self.trailing_stop,
            'min_reliability_score': self.min_reliability_score
        }
