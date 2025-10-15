# 📊 Strategy Roadmap - Implementación de Estrategias de Trading

**Proyecto**: One Trade Decision-Centric App
**Última Actualización**: Octubre 2025 - Día 2

---

## 🎯 Objetivo

Expandir el Recommendation Engine desde 2 estrategias base a un conjunto diversificado de **12+ estrategias** que cubran diferentes condiciones de mercado y estilos de trading.

---

## 📈 Estado Actual

**Implementadas** (Fase 0):
- ✅ **CurrentStrategy**: EMA(21/55) + RSI(14) + MACD(12,26,9) + Volume confirmación
- ✅ **BaselineStrategy**: EMA(21/55) + RSI(14) simple

**Pendientes**: 10 estrategias adicionales

---

## 🗺️ Roadmap de Estrategias

### Wave 1: Indicadores Clásicos (Prioridad Alta) - Semana 7

| ID | Estrategia | Descripción | Complejidad | Puntos | Estado |
|----|-----------|-------------|-------------|--------|--------|
| **STRAT-001** | RSI Pure | RSI(14) oversold(<30) / overbought(>70) | S | 2 | 📋 TODO |
| **STRAT-002** | Bollinger Bands | BB(20,2) touch bands + squeeze detection | S | 3 | 📋 TODO |
| **STRAT-003** | MACD Histogram | MACD histogram cruce de cero + divergencias | S | 3 | 📋 TODO |

**Target**: 3 estrategias momentum-based

### Wave 2: Volume & Price Action (Prioridad Media) - Semana 7-8

| ID | Estrategia | Descripción | Complejidad | Puntos | Estado |
|----|-----------|-------------|-------------|--------|--------|
| **STRAT-004** | Volume Profile | VWAP + POC + high/low volume zones | M | 5 | 📋 TODO |
| **STRAT-005** | Mean Reversion | Z-score based, señales en extremos | M | 3 | 📋 TODO |
| **STRAT-006** | Support/Resistance | Detección automática de niveles clave | M | 5 | 📋 TODO |

**Target**: Estrategias para mercados laterales

### Wave 3: Avanzadas (Prioridad Baja) - Semanas 9-10

| ID | Estrategia | Descripción | Complejidad | Puntos | Estado |
|----|-----------|-------------|-------------|--------|--------|
| **STRAT-007** | Ichimoku Cloud | Kumo, Tenkan/Kijun cruces, cloud breakouts | L | 5 | 📋 TODO |
| **STRAT-008** | ADX Trend Strength | ADX(14) para filtrar trending markets | M | 3 | 📋 TODO |
| **STRAT-009** | Fibonacci Retracements | Niveles automáticos 38.2%, 50%, 61.8% | M | 5 | 📋 TODO |
| **STRAT-010** | Harmonic Patterns | Detección de Gartley, Butterfly, etc. | L | 8 | 📋 TODO |

**Target**: Estrategias sofisticadas para traders avanzados

### Wave 4: Machine Learning (Futuro) - Post-MVP

| ID | Estrategia | Descripción | Complejidad | Puntos | Estado |
|----|-----------|-------------|-------------|--------|--------|
| **STRAT-011** | LSTM Price Prediction | Red neuronal para predicción de precio | XL | 13 | 🔮 Futuro |
| **STRAT-012** | Sentiment Analysis | Twitter/Reddit sentiment como señal | L | 8 | 🔮 Futuro |
| **STRAT-013** | Regime Detection ML | Clasificar mercado con Random Forest | L | 8 | 🔮 Futuro |

**Target**: Estrategias basadas en ML

---

## 🏗️ Arquitectura de Estrategias

### Base Class

Todas las estrategias heredan de `BaseStrategy`:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass
class StrategyMetadata:
    """Metadata de una estrategia"""
    name: str
    version: str
    author: str
    description: str
    timeframes: list[str]  # ej: ["1h", "4h", "1d"]
    suitable_for: str  # "trending", "ranging", "volatile", "all"
    risk_level: str  # "low", "medium", "high"
    
class SignalStrength:
    """Fuerza de señal normalizada"""
    value: float  # -1.0 (strong sell) to +1.0 (strong buy)
    confidence: float  # 0.0 to 1.0
    reasons: list[str]  # Razones legibles

class BaseStrategy(ABC):
    """Clase base para todas las estrategias"""
    
    @property
    @abstractmethod
    def metadata(self) -> StrategyMetadata:
        """Retorna metadata de la estrategia"""
        pass
    
    @abstractmethod
    def calculate_signal(self, data: pd.DataFrame) -> SignalStrength:
        """
        Calcula señal de trading basada en datos OHLCV
        
        Args:
            data: DataFrame con OHLCV + indicadores pre-calculados
            
        Returns:
            SignalStrength con valor, confianza y razones
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Valida que datos sean suficientes para la estrategia"""
        required_rows = self.get_required_periods()
        return len(data) >= required_rows
    
    def get_required_periods(self) -> int:
        """Períodos mínimos necesarios (ej: MA(200) necesita 200)"""
        return 200  # Override en cada estrategia
```

### Registro de Estrategias

```python
class StrategyRegistry:
    """Registry pattern para gestionar estrategias"""
    
    _strategies: dict[str, type[BaseStrategy]] = {}
    
    @classmethod
    def register(cls, strategy_class: type[BaseStrategy]) -> None:
        """Registra una estrategia"""
        metadata = strategy_class().metadata
        cls._strategies[metadata.name] = strategy_class
    
    @classmethod
    def get(cls, name: str) -> BaseStrategy:
        """Obtiene instancia de estrategia por nombre"""
        if name not in cls._strategies:
            raise ValueError(f"Strategy {name} not found")
        return cls._strategies[name]()
    
    @classmethod
    def list_all(cls) -> list[StrategyMetadata]:
        """Lista todas las estrategias disponibles"""
        return [s().metadata for s in cls._strategies.values()]

# Uso
@StrategyRegistry.register
class RSIPureStrategy(BaseStrategy):
    # Implementación
    pass
```

---

## 📋 Detalles de Implementación por Estrategia

### STRAT-001: RSI Pure Strategy

**Descripción**: Estrategia basada únicamente en RSI con niveles clásicos

**Indicadores**:
- RSI(14)

**Reglas de Señal**:
```python
if rsi < 30:
    signal = LONG  # Oversold
    strength = (30 - rsi) / 30  # 0.0 a 1.0
elif rsi > 70:
    signal = SHORT  # Overbought
    strength = (rsi - 70) / 30
else:
    signal = NEUTRAL
    strength = 0
```

**Criterios de Aceptación**:
- [ ] Clase RSIPureStrategy implementada
- [ ] Tests con 3 escenarios (oversold, overbought, neutral)
- [ ] Integrada con StrategyRegistry
- [ ] Backtest de 1 año con métricas
- [ ] Documentación inline

**Estimación**: 2 puntos (4-6 horas)

**Archivo**: `backend/strategies/rsi_pure.py`

---

### STRAT-002: Bollinger Bands Strategy

**Descripción**: Señales en toque de bandas + detección de squeeze

**Indicadores**:
- BB(20, 2) - Media móvil de 20 períodos, 2 desviaciones estándar
- Bandwidth para squeeze detection

**Reglas de Señal**:
```python
# Toque de banda inferior = oportunidad de compra
if close <= lower_band and bandwidth > 0.02:
    signal = LONG
    strength = (lower_band - close) / close
    
# Toque de banda superior = oportunidad de venta
elif close >= upper_band and bandwidth > 0.02:
    signal = SHORT
    strength = (close - upper_band) / close

# Squeeze (bandwidth muy bajo) = prepararse para breakout
elif bandwidth < 0.01:
    signal = NEUTRAL
    confidence = 0.3  # Baja confianza, esperar
```

**Criterios de Aceptación**:
- [ ] Cálculo correcto de BB
- [ ] Bandwidth calculation
- [ ] Squeeze detection
- [ ] Tests con datos sintéticos
- [ ] Backtest validado

**Estimación**: 3 puntos (6-8 horas)

**Archivo**: `backend/strategies/bollinger_bands.py`

---

### STRAT-003: MACD Histogram Strategy

**Descripción**: Cruces del histograma MACD con detección de divergencias

**Indicadores**:
- MACD(12, 26, 9)
- Histogram
- Price para divergencias

**Reglas de Señal**:
```python
# Cruce de histograma de negativo a positivo
if histogram[-1] > 0 and histogram[-2] <= 0:
    signal = LONG
    strength = min(abs(histogram[-1]) / 5, 1.0)

# Cruce de positivo a negativo
elif histogram[-1] < 0 and histogram[-2] >= 0:
    signal = SHORT
    strength = min(abs(histogram[-1]) / 5, 1.0)

# Divergencia alcista (precio baja, MACD sube)
if detect_bullish_divergence(price, macd):
    strength *= 1.2  # Boost
```

**Criterios de Aceptación**:
- [ ] Cálculo MACD correcto
- [ ] Detección de cruces
- [ ] Divergencias básicas
- [ ] Tests edge cases
- [ ] Comparación vs TradingView

**Estimación**: 3 puntos (6-8 horas)

**Archivo**: `backend/strategies/macd_histogram.py`

---

### STRAT-004: Volume Profile Strategy

**Descripción**: VWAP, POC y zonas de alto/bajo volumen

**Indicadores**:
- VWAP (Volume Weighted Average Price)
- Volume Profile
- POC (Point of Control) - precio con mayor volumen

**Reglas de Señal**:
```python
# Precio cruza VWAP desde abajo = señal alcista
if close > vwap and prev_close <= vwap:
    signal = LONG
    
# Precio en zona de alto volumen + cerca de POC = soporte/resistencia
if is_high_volume_zone(close) and near_poc(close):
    signal = NEUTRAL  # Esperar confirmación

# Breakout de zona de bajo volumen con volumen = fuerte señal
if breakout_low_volume_zone(close) and volume > avg_volume * 1.5:
    signal = LONG/SHORT (según dirección)
    strength = 0.8
```

**Criterios de Aceptación**:
- [ ] Cálculo VWAP correcto
- [ ] Volume profile binning
- [ ] POC calculation
- [ ] Tests con datos reales
- [ ] Performance optimizado

**Estimación**: 5 puntos (1-1.5 días)

**Archivo**: `backend/strategies/volume_profile.py`

---

### STRAT-005: Mean Reversion Strategy

**Descripción**: Z-score para detectar desviaciones extremas

**Indicadores**:
- Z-score: (precio - media) / std_dev
- Rolling window de 20 períodos

**Reglas de Señal**:
```python
z_score = (close - rolling_mean) / rolling_std

# Extremo inferior = oportunidad de compra
if z_score < -2:
    signal = LONG
    strength = min(abs(z_score) / 3, 1.0)
    confidence = 0.7 if z_score < -2.5 else 0.5

# Extremo superior = oportunidad de venta
elif z_score > 2:
    signal = SHORT
    strength = min(z_score / 3, 1.0)
    
# Return to mean = cerrar posición
elif abs(z_score) < 0.5:
    signal = NEUTRAL
```

**Criterios de Aceptación**:
- [ ] Z-score calculation
- [ ] Rolling statistics
- [ ] Tests con datos sintéticos
- [ ] Validación con mercados laterales
- [ ] Time decay si no revierte

**Estimación**: 3 puntos (6-8 horas)

**Archivo**: `backend/strategies/mean_reversion.py`

---

### STRAT-006: Support/Resistance Strategy

**Descripción**: Detección automática de niveles clave

**Algoritmo**:
```python
def detect_support_resistance(data: pd.DataFrame, window: int = 20):
    """
    Detecta S/R usando:
    1. Pivot points (local maxima/minima)
    2. Clustering de precios con densidad
    3. Round numbers (psicológicos)
    """
    
    # 1. Encontrar pivots
    pivots_high = data['high'].rolling(window, center=True).max()
    pivots_low = data['low'].rolling(window, center=True).min()
    
    # 2. Cluster pivots cercanos
    resistance_levels = cluster_pivots(pivots_high, threshold=0.02)
    support_levels = cluster_pivots(pivots_low, threshold=0.02)
    
    # 3. Agregar round numbers
    current_price = data['close'].iloc[-1]
    round_levels = find_round_numbers(current_price, range_pct=0.1)
    
    return support_levels, resistance_levels, round_levels
```

**Reglas de Señal**:
```python
# Precio cerca de soporte = oportunidad de compra
if is_near_level(close, support_levels, threshold=0.01):
    signal = LONG
    strength = 0.7
    
# Breakout de resistencia con volumen = señal fuerte
if close > resistance_level and volume > avg_volume * 1.3:
    signal = LONG
    strength = 0.9
```

**Criterios de Aceptación**:
- [ ] Detección de pivots
- [ ] Clustering de niveles
- [ ] Round numbers
- [ ] Señales en bounce/breakout
- [ ] Visualización en gráfico

**Estimación**: 5 puntos (1-1.5 días)

**Archivo**: `backend/strategies/support_resistance.py`

---

### STRAT-007: Ichimoku Cloud Strategy

**Descripción**: Sistema completo Ichimoku

**Componentes**:
```python
# Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
tenkan = (high_9 + low_9) / 2

# Kijun-sen (Base Line): (26-period high + 26-period low) / 2
kijun = (high_26 + low_26) / 2

# Senkou Span A (Leading Span A): (Tenkan + Kijun) / 2, shifted +26
span_a = (tenkan + kijun) / 2

# Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2, shifted +26
span_b = (high_52 + low_52) / 2

# Kumo (Cloud): Área entre Span A y Span B
cloud_top = max(span_a, span_b)
cloud_bottom = min(span_a, span_b)

# Chikou Span (Lagging Span): Close shifted -26
chikou = close.shift(-26)
```

**Reglas de Señal**:
```python
# Cruce Tenkan/Kijun (TK Cross)
if tenkan > kijun and prev_tenkan <= prev_kijun:
    signal = LONG
    
# Precio cruza cloud (Kumo Breakout)
if close > cloud_top and prev_close <= cloud_top:
    signal = LONG
    strength = 0.8
    
# Confirmación Chikou
if chikou > close_26_ago:
    strength += 0.1  # Boost
```

**Criterios de Aceptación**:
- [ ] Todos los componentes calculados
- [ ] TK cross detection
- [ ] Cloud breakout detection
- [ ] Chikou confirmation
- [ ] Tests exhaustivos
- [ ] Comparación vs TradingView

**Estimación**: 5 puntos (1-1.5 días)

**Archivo**: `backend/strategies/ichimoku_cloud.py`

---

### STRAT-008: ADX Trend Strength

**Descripción**: Filtro de trending markets usando ADX

**Indicadores**:
- ADX(14)
- +DI, -DI

**Uso**:
```python
# ADX mide FUERZA de tendencia, no dirección
# Combinar con otras estrategias como filtro

adx = calculate_adx(data, period=14)

# ADX > 25 = mercado trending (good for momentum strategies)
# ADX < 20 = mercado lateral (good for mean reversion)

if adx > 25:
    weight_momentum_strategies = 1.5  # Boost momentum
    weight_reversion_strategies = 0.5  # Reduce reversion
elif adx < 20:
    weight_momentum_strategies = 0.5
    weight_reversion_strategies = 1.5
```

**Criterios de Aceptación**:
- [ ] Cálculo ADX correcto
- [ ] +DI / -DI calculation
- [ ] Integration como filtro en Condenser
- [ ] Tests con datos trending y ranging
- [ ] Validación de mejora en win rate

**Estimación**: 3 puntos (6-8 horas)

**Archivo**: `backend/strategies/adx_filter.py`

---

### STRAT-009: Fibonacci Retracements

**Descripción**: Niveles de retroceso automáticos

**Algoritmo**:
```python
def calculate_fibonacci_levels(swing_high: float, swing_low: float):
    """
    Calcula niveles de Fibonacci entre swing high/low
    """
    diff = swing_high - swing_low
    
    levels = {
        "0.0": swing_low,
        "23.6": swing_low + diff * 0.236,
        "38.2": swing_low + diff * 0.382,
        "50.0": swing_low + diff * 0.50,
        "61.8": swing_low + diff * 0.618,
        "78.6": swing_low + diff * 0.786,
        "100.0": swing_high,
        "161.8": swing_low + diff * 1.618,  # Extension
        "261.8": swing_low + diff * 2.618,
    }
    return levels

# Detectar swing high/low automáticamente
def find_swing_points(data: pd.DataFrame, lookback: int = 50):
    """Encuentra swing high y low recientes"""
    recent_data = data.tail(lookback)
    swing_high = recent_data['high'].max()
    swing_low = recent_data['low'].min()
    return swing_high, swing_low
```

**Reglas de Señal**:
```python
# Precio cerca de nivel Fibonacci = oportunidad
if is_near_fib_level(close, levels, threshold=0.005):
    level_name = get_closest_level(close, levels)
    
    if level_name in ["38.2", "50.0", "61.8"]:  # Niveles clave
        signal = LONG  # Si viene de arriba
        strength = 0.6
```

**Criterios de Aceptación**:
- [ ] Detección automática de swings
- [ ] Cálculo de niveles
- [ ] Señales en bounces
- [ ] Extensiones para targets
- [ ] Visualización en gráfico

**Estimación**: 5 puntos (1-1.5 días)

**Archivo**: `backend/strategies/fibonacci.py`

---

### STRAT-010: Harmonic Patterns

**Descripción**: Detección de patrones armónicos (Gartley, Butterfly, etc.)

**Patrones a Detectar**:

1. **Gartley Pattern**:
   - XA: Impulso inicial
   - AB: Retroceso 61.8% de XA
   - BC: Retroceso 38.2-88.6% de AB
   - CD: Extensión 127.2% de BC
   - D = punto de entrada

2. **Butterfly Pattern**:
   - Similar pero CD = 161.8% de AB

**Algoritmo** (Complejo):
```python
def detect_gartley_pattern(data: pd.DataFrame, lookback: int = 100):
    """
    Detecta patrón Gartley usando ratios de Fibonacci
    """
    # 1. Encontrar posibles puntos X, A, B, C, D
    pivots = find_all_pivots(data, lookback)
    
    # 2. Validar ratios
    for combination in generate_xabcd_combinations(pivots):
        x, a, b, c, d = combination
        
        # Validar ratios de Fibonacci
        ab_xa_ratio = (b - a) / (x - a)
        bc_ab_ratio = (c - b) / (a - b)
        cd_bc_ratio = (d - c) / (b - c)
        
        if is_valid_gartley_ratios(ab_xa_ratio, bc_ab_ratio, cd_bc_ratio):
            return {
                "pattern": "Gartley",
                "points": combination,
                "completion": calculate_completion(d),
                "entry": d,
                "target": calculate_target(x, a, d)
            }
    return None
```

**Criterios de Aceptación**:
- [ ] Detección de Gartley
- [ ] Detección de Butterfly
- [ ] Validación de ratios
- [ ] Entry y target calculations
- [ ] Tests con patrones conocidos
- [ ] Performance < 100ms para 1000 candles

**Estimación**: 8 puntos (1.5-2 días)

**Complejidad**: Alta (requiere geometría de patrones)

**Archivo**: `backend/strategies/harmonic_patterns.py`

---

## 🔧 Sistema de Pesos Dinámicos

### Configuración por Condición de Mercado

```yaml
# config/strategy_weights.yaml

market_regimes:
  trending_bullish:
    detect:
      - adx > 25
      - ema_21 > ema_55
      - price > ema_200
    weights:
      CurrentStrategy: 0.30
      MACDHistogram: 0.25
      IchimokuCloud: 0.20
      RSIPure: 0.15
      BollingerBands: 0.10
      
  trending_bearish:
    detect:
      - adx > 25
      - ema_21 < ema_55
      - price < ema_200
    weights:
      CurrentStrategy: 0.30
      MACDHistogram: 0.25
      RSIPure: 0.20
      BollingerBands: 0.15
      MeanReversion: 0.10
      
  ranging:
    detect:
      - adx < 20
      - atr < atr_avg * 0.8
    weights:
      MeanReversion: 0.35
      BollingerBands: 0.30
      RSIPure: 0.20
      SupportResistance: 0.15
      
  volatile:
    detect:
      - atr > atr_avg * 1.5
      - volume > volume_avg * 2
    weights:
      CurrentStrategy: 0.25
      BollingerBands: 0.25
      VolumeProfile: 0.25
      SupportResistance: 0.25
```

---

## 🧪 Testing de Estrategias

### Template de Test

```python
# tests/strategies/test_rsi_pure.py

import pytest
import pandas as pd
from backend.strategies.rsi_pure import RSIPureStrategy

class TestRSIPureStrategy:
    
    @pytest.fixture
    def strategy(self):
        return RSIPureStrategy()
    
    @pytest.fixture
    def oversold_data(self):
        """Datos sintéticos con RSI < 30"""
        data = create_downtrend_data(periods=50, rsi_final=25)
        return data
    
    def test_oversold_generates_long_signal(self, strategy, oversold_data):
        signal = strategy.calculate_signal(oversold_data)
        assert signal.value > 0, "Should generate LONG signal"
        assert signal.confidence > 0.5
        assert "oversold" in signal.reasons[0].lower()
    
    def test_overbought_generates_short_signal(self, strategy):
        data = create_uptrend_data(periods=50, rsi_final=75)
        signal = strategy.calculate_signal(data)
        assert signal.value < 0, "Should generate SHORT signal"
    
    def test_neutral_range(self, strategy):
        data = create_neutral_data(periods=50, rsi_range=(40, 60))
        signal = strategy.calculate_signal(data)
        assert abs(signal.value) < 0.3, "Should be neutral"
    
    def test_metadata(self, strategy):
        meta = strategy.metadata
        assert meta.name == "RSI Pure"
        assert "momentum" in meta.suitable_for.lower()
    
    def test_backtest_performance(self, strategy):
        """Backtest de 1 año debe tener win rate > 45%"""
        results = run_backtest(strategy, symbol="BTC/USDT", period=365)
        assert results.win_rate > 0.45
        assert results.total_trades > 20
```

---

## 📊 Matriz de Estrategias vs Condiciones

| Estrategia | Trending | Ranging | Volatile | Baja Volatilidad | Timeframe Ideal |
|-----------|----------|---------|----------|-----------------|-----------------|
| CurrentStrategy | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 1h, 4h |
| BaselineStrategy | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | 4h, 1d |
| RSI Pure | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | 1h, 4h |
| Bollinger Bands | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | 1h, 4h |
| MACD Histogram | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ | 4h, 1d |
| Volume Profile | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 1h, 4h, 1d |
| Mean Reversion | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | 1h, 4h |
| Support/Resistance | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 4h, 1d |
| Ichimoku Cloud | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ | 4h, 1d |
| ADX Filter | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | 4h, 1d |
| Fibonacci | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 1d |
| Harmonic Patterns | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | 4h, 1d |

⭐⭐⭐ = Excelente | ⭐⭐ = Bueno | ⭐ = Aceptable

---

## 🎯 Plan de Implementación

### Semana 7: Core Strategies (Wave 1)

**Lunes-Martes**: STRAT-001 (RSI Pure)
- Implementar clase
- Tests unitarios
- Integrar con registry
- Backtest de validación

**Miércoles-Jueves**: STRAT-002 (Bollinger Bands)
- Implementar BB calculation
- Squeeze detection
- Tests y backtest

**Viernes**: STRAT-003 (MACD Histogram)
- Implementar histogram
- Basic divergences
- Tests

**Fin de Semana 7**: 3 estrategias nuevas funcionando

---

### Semana 8: Advanced Strategies (Wave 2)

**Lunes-Martes**: STRAT-004 (Volume Profile)
- VWAP calculation
- Volume profile binning
- POC detection

**Miércoles**: STRAT-005 (Mean Reversion)
- Z-score logic
- Tests con datos sintéticos

**Jueves-Viernes**: STRAT-006 (Support/Resistance)
- Pivot detection
- Level clustering
- Signal generation

**Fin de Semana 8**: 6 estrategias totales

---

### Semanas 9-10: Complex Strategies (Wave 3) - Opcional

Estas se pueden posponer si Wave 1 y 2 ya dan buenos resultados.

---

## 📈 Benchmarking de Estrategias

### Métricas a Trackear por Estrategia

```python
@dataclass
class StrategyPerformance:
    """Métricas de performance de cada estrategia"""
    
    # Trading metrics
    total_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    profit_factor: float
    
    # Risk metrics
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    
    # Signal metrics
    total_signals: int
    false_positives: int  # Señales que no llevaron a trade ganador
    true_positives: int
    precision: float  # TP / (TP + FP)
    recall: float  # TP / (TP + FN)
    
    # Contribution to ensemble
    weight_in_condenser: float
    contribution_score: float  # Qué % de decisiones finales vienen de esta
```

### Dashboard de Estrategias

Crear vista en frontend que muestre:

| Estrategia | Trades | Win% | Sharpe | Precision | Peso Actual | Última Señal |
|-----------|--------|------|--------|-----------|-------------|--------------|
| CurrentStrategy | 45 | 62% | 1.8 | 0.65 | 30% | LONG (hace 2h) |
| RSIPure | 38 | 58% | 1.5 | 0.60 | 15% | HOLD |
| BollingerBands | 52 | 55% | 1.3 | 0.57 | 20% | LONG |
| MACDHistogram | 41 | 61% | 1.7 | 0.63 | 25% | SHORT |
| MeanReversion | 67 | 53% | 1.1 | 0.55 | 10% | HOLD |

---

## 🚀 Optimización Continua

### Auto-tuning de Parámetros

```python
class StrategyOptimizer:
    """Optimizador automático de parámetros"""
    
    async def optimize_strategy(
        self, 
        strategy_class: type[BaseStrategy],
        symbol: str,
        train_period_days: int = 180,
        test_period_days: int = 90
    ):
        """
        Optimiza parámetros usando walk-forward
        
        Returns:
            Mejores parámetros encontrados
        """
        
        # 1. Definir grid de parámetros
        param_grid = strategy_class.get_param_grid()
        
        # 2. Split train/test
        train_data = get_data(symbol, days=train_period_days)
        test_data = get_data(symbol, days=test_period_days, offset=train_period_days)
        
        # 3. Grid search en train
        best_params = None
        best_sharpe = -999
        
        for params in param_grid:
            strategy = strategy_class(**params)
            backtest_result = run_backtest(strategy, train_data)
            
            if backtest_result.sharpe_ratio > best_sharpe:
                best_sharpe = backtest_result.sharpe_ratio
                best_params = params
        
        # 4. Validar en test (out-of-sample)
        strategy = strategy_class(**best_params)
        test_result = run_backtest(strategy, test_data)
        
        # 5. Detectar overfitting
        if test_result.sharpe_ratio < best_sharpe * 0.7:
            logger.warning("Possible overfitting detected")
        
        return best_params, test_result
```

### Pesos Adaptativos

Cada semana, re-calcular pesos basados en performance reciente:

```python
async def recalculate_weights_weekly():
    """Job semanal para ajustar pesos de estrategias"""
    
    # 1. Obtener performance últimas 4 semanas
    performances = await get_strategy_performances(days=28)
    
    # 2. Calcular pesos basados en Sharpe ratio normalizado
    total_sharpe = sum(p.sharpe_ratio for p in performances)
    
    new_weights = {}
    for perf in performances:
        # Peso proporcional a Sharpe ratio
        weight = perf.sharpe_ratio / total_sharpe
        
        # Limitar a 40% max, 5% min
        weight = max(0.05, min(0.40, weight))
        
        new_weights[perf.strategy_name] = weight
    
    # 3. Guardar en DB
    await update_strategy_weights(new_weights)
    
    # 4. Notificar cambios significativos
    if significant_change(old_weights, new_weights, threshold=0.1):
        await send_alert(f"Strategy weights updated: {new_weights}")
```

---

## 📚 Recursos de Aprendizaje

### Libros
- "Technical Analysis of Financial Markets" - John Murphy
- "Algorithmic Trading" - Ernie Chan
- "Advances in Financial Machine Learning" - Marcos López de Prado

### Indicadores y Fórmulas
- [TA-Lib Documentation](https://mrjbq7.github.io/ta-lib/)
- [Pandas TA](https://github.com/twopirllc/pandas-ta)
- [TradingView Pine Script](https://www.tradingview.com/pine-script-docs/)

### Backtesting Frameworks (Referencia)
- [Backtrader](https://www.backtrader.com/)
- [VectorBT](https://vectorbt.dev/)
- [Freqtrade](https://www.freqtrade.io/)

---

## ✅ Checklist de Nueva Estrategia

Antes de considerar una estrategia "completa":

- [ ] Clase implementada con BaseStrategy
- [ ] Metadata completa (name, version, suitable_for)
- [ ] calculate_signal() implementado
- [ ] get_required_periods() definido
- [ ] Tests unitarios (min 5 tests)
- [ ] Backtest de 1 año ejecutado
- [ ] Win rate > 45%
- [ ] Sharpe ratio > 0.5
- [ ] Documentación inline (docstrings)
- [ ] Agregada a StrategyRegistry
- [ ] Integrada en Condenser
- [ ] Performance benchmark < 50ms/signal
- [ ] Visualización en dashboard

---

## 📊 Roadmap Visual

```
Mes 1         Mes 2         Mes 3
├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤

Week 1-2      Week 3-4      Week 5-6      Week 7-8      Week 9-10     Week 11-12
Setup         Data          Backtest      Recommend     Frontend      Deploy
                                          ┌─────────────────────┐
                                          │  ESTRATEGIAS        │
                                          │  Wave 1: Week 7     │
                                          │  Wave 2: Week 8     │
                                          │  Wave 3: Week 9-10  │
                                          └─────────────────────┘
```

**Estrategias se implementan en paralelo con Fase 3 y 4**

---

## 🎯 KPIs de Éxito para Estrategias

| KPI | Target | Medición |
|-----|--------|----------|
| **Número de Estrategias** | 8-10 | Count |
| **Win Rate Promedio** | > 50% | Average de todas |
| **Sharpe Ratio Promedio** | > 1.0 | Average de todas |
| **Correlación Baja** | < 0.7 | Entre estrategias |
| **Cobertura de Regímenes** | 100% | Trending, Ranging, Volatile cubiertos |
| **Performance** | < 100ms | Tiempo de cálculo de señal |

---

**Próximo Paso**: Implementar STRAT-001 (RSI Pure) como prototipo

**Mantenedor**: Trading Strategy Team



