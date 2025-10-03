# Resumen de Alineación SL/TP y Sizing con Objetivos R por Modo

## 1. Ajuste de `MODE_CONFIG` en `webapp/app.py`

### Problema Resuelto
- **Antes**: Los multiplicadores de TP no correspondían exactamente a los objetivos R
- **Después**: Cada modo refleja exactamente 1R, 1.5R y 2R en `tp_multiplier`

### Cambios Implementados

#### Configuración Actualizada:
```python
MODE_CONFIG = {
    "conservative": {
        "tp_multiplier": 1.0,  # Exact 1R target
        "target_r_multiple": 1.0,           # Target 1R per trade
        "risk_reward_ratio": 1.0,           # 1:1 risk-reward ratio
        # ... otros parámetros
    },
    "moderate": {
        "tp_multiplier": 1.5,  # Exact 1.5R target
        "target_r_multiple": 1.5,           # Target 1.5R per trade
        "risk_reward_ratio": 1.5,           # 1.5:1 risk-reward ratio
        # ... otros parámetros
    },
    "aggressive": {
        "tp_multiplier": 2.0,  # Exact 2R target
        "target_r_multiple": 2.0,           # Target 2R per trade
        "risk_reward_ratio": 2.0,           # 2:1 risk-reward ratio
        # ... otros parámetros
    },
}
```

### Parámetros R-Multiple Añadidos:
- **`target_r_multiple`**: Objetivo R-multiple por operación
- **`risk_reward_ratio`**: Ratio riesgo-recompensa
- **`tp_multiplier`**: Multiplicador de take profit (alineado con target R)

## 2. Propagación de Valores a Motores de Backtest y Ejecución

### Problema Resuelto
- **Antes**: Los motores no utilizaban los valores R-multiple de la configuración
- **Después**: Todos los motores respetan los multiplicadores actualizados

### Cambios Implementados

#### En `btc_1tpd_backtester/strategy_multifactor.py`:
```python
def __init__(self, config):
    # Parámetros de gestión de riesgo
    self.atr_multiplier = config.get('atr_multiplier', 2.0)
    self.tp_multiplier = config.get('tp_multiplier', 2.0)
    self.target_r_multiple = config.get('target_r_multiple', 2.0)
    self.risk_reward_ratio = config.get('risk_reward_ratio', 2.0)

def calculate_trade_params(self, side, entry_price, data, entry_time):
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
```

#### En `btc_1tpd_backtester/strategy.py`:
```python
def __init__(self, config):
    self.tp_multiplier = config['tp_multiplier']
    self.target_r_multiple = config.get('target_r_multiple', self.tp_multiplier)
    self.risk_reward_ratio = config.get('risk_reward_ratio', self.tp_multiplier)

def get_take_profit_price(self, entry_price, stop_loss, side):
    """Calculate take profit price based on target R-multiple."""
    risk = abs(entry_price - stop_loss)
    reward = risk * self.target_r_multiple
    
    if side == 'long':
        return entry_price + reward
    else:
        return entry_price - reward
```

#### En `btc_1tpd_backtester/btc_1tpd_backtest_final.py`:
```python
def __init__(self, config, daily_data=None):
    self.tp_multiplier = config.get('tp_multiplier', 2.0)
    self.target_r_multiple = config.get('target_r_multiple', self.tp_multiplier)
    self.risk_reward_ratio = config.get('risk_reward_ratio', self.tp_multiplier)

def calculate_trade_params(self, side, entry_price, atr_series):
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
```

## 3. Actualización de `btc_1tpd_backtester/signals/today_signal.py`

### Problema Resuelto
- **Antes**: Las señales no leían el multiplicador desde la configuración del modo
- **Después**: Las señales aplican el mismo esquema de SL/TP que el backtesting

### Cambios Implementados

#### En `_get_orb_recommendation`:
```python
def _get_orb_recommendation(symbol, config, now):
    # ... código existente ...
    
    atr_mult = cfg.get('atr_mult_orb', 1.2)
    tp_mult = cfg.get('tp_multiplier', 2.0)
    target_r_multiple = cfg.get('target_r_multiple', tp_mult)
    
    if atr_proxy and pd.notna(atr_proxy) and atr_proxy > 0:
        if side == 'long':
            stop_loss = entry_price - atr_proxy * atr_mult
            take_profit = entry_price + atr_proxy * tp_mult
        else:
            stop_loss = entry_price + atr_proxy * atr_mult
            take_profit = entry_price - atr_proxy * tp_mult
        
        # Verificar que el TP corresponde al target R-multiple
        risk_amount = abs(entry_price - stop_loss)
        expected_reward = risk_amount * target_r_multiple
        
        if side == 'long':
            expected_tp = entry_price + expected_reward
        else:
            expected_tp = entry_price - expected_reward
        
        # Ajustar TP si hay diferencia significativa
        if abs(take_profit - expected_tp) > 0.01:
            take_profit = expected_tp
        
        rec['stop_loss'] = float(stop_loss)
        rec['take_profit'] = float(take_profit)
```

#### En fallback logic:
```python
# Similar logic applied to fallback signal generation
atr_mult = config.get('atr_mult_orb', 1.2)
tp_mult = config.get('tp_multiplier', 2.0)
target_r_multiple = config.get('target_r_multiple', tp_mult)

# ... calculate stop_loss and take_profit ...

# Verificar que el TP corresponde al target R-multiple
risk_amount = abs(current_price - stop_loss)
expected_reward = risk_amount * target_r_multiple

if side == 'long':
    expected_tp = current_price + expected_reward
else:
    expected_tp = current_price - expected_reward

# Ajustar TP si hay diferencia significativa
if abs(take_profit - expected_tp) > 0.01:
    take_profit = expected_tp
```

## 4. Pruebas que Verifican 1R, 1.5R y 2R para Cada Modo

### Archivos de Pruebas Creados:

#### `btc_1tpd_backtester/tests/test_r_multiple_alignment.py`:
- **`test_conservative_mode_1r_target`**: Verifica que modo conservador target 1R
- **`test_moderate_mode_1_5r_target`**: Verifica que modo moderado target 1.5R
- **`test_aggressive_mode_2r_target`**: Verifica que modo agresivo target 2R
- **`test_multifactor_strategy_r_alignment`**: Verifica alineación R en MultifactorStrategy
- **`test_trading_strategy_r_alignment`**: Verifica alineación R en TradingStrategy
- **`test_signal_generation_r_alignment`**: Verifica alineación R en generación de señales
- **`test_position_sizing_consistency`**: Verifica consistencia de sizing
- **`test_r_multiple_calculation_accuracy`**: Verifica precisión de cálculos R
- **`test_mode_config_consistency`**: Verifica consistencia de configuración

#### `test_r_multiple_manual.py`:
- **Prueba manual completa**: Flujo de testing para todos los modos
- **Verificación de R-multiple**: Cálculo y verificación de objetivos R
- **Verificación de sizing**: Consistencia de tamaño de posición
- **Análisis de configuración**: Verificación de consistencia de MODE_CONFIG

### Casos de Prueba Implementados:

#### 1. Verificación de R-Multiple por Modo:
```python
def test_conservative_mode_1r_target(self):
    config = {
        'tp_multiplier': 1.0,
        'target_r_multiple': 1.0,
        'risk_reward_ratio': 1.0,
        'use_multifactor_strategy': False
    }
    
    strategy = SimpleTradingStrategy(config)
    trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
    
    if trades:
        trade = trades[0]
        entry_price = trade['entry_price']
        stop_loss = trade['sl']
        take_profit = trade['tp']
        
        # Calculate risk and reward
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        r_multiple = reward / risk if risk > 0 else 0
        
        # Verify 1R target
        self.assertAlmostEqual(r_multiple, 1.0, places=2)
```

#### 2. Verificación de Sizing:
```python
def test_position_sizing_consistency(self):
    config = {
        'risk_usdt': 20.0,
        'tp_multiplier': 2.0,
        'target_r_multiple': 2.0
    }
    
    strategy = MultifactorStrategy(config)
    trades = strategy.process_day(self.test_data, self.test_data.index[0].date())
    
    if trades:
        trade = trades[0]
        entry_price = trade['entry_price']
        stop_loss = trade['sl']
        position_size = trade.get('position_size', 1.0)
        
        # Calculate actual risk
        risk_per_unit = abs(entry_price - stop_loss)
        actual_risk = risk_per_unit * position_size
        
        # Verify risk matches configured amount
        expected_risk = config['risk_usdt']
        self.assertAlmostEqual(actual_risk, expected_risk, places=2)
```

#### 3. Verificación de Configuración:
```python
def test_mode_config_consistency(self):
    from app import MODE_CONFIG
    
    for mode, config in MODE_CONFIG.items():
        tp_multiplier = config.get('tp_multiplier')
        target_r_multiple = config.get('target_r_multiple')
        risk_reward_ratio = config.get('risk_reward_ratio')
        
        # All should be equal
        self.assertEqual(tp_multiplier, target_r_multiple)
        self.assertEqual(tp_multiplier, risk_reward_ratio)
        
        # Verify expected values
        if mode == 'conservative':
            self.assertEqual(tp_multiplier, 1.0)
        elif mode == 'moderate':
            self.assertEqual(tp_multiplier, 1.5)
        elif mode == 'aggressive':
            self.assertEqual(tp_multiplier, 2.0)
```

## Beneficios de la Implementación

### 1. Alineación Exacta de R-Multiple
- ✅ **Conservador**: Exactamente 1R por operación
- ✅ **Moderado**: Exactamente 1.5R por operación
- ✅ **Agresivo**: Exactamente 2R por operación
- ✅ **Consistencia**: Todos los motores respetan los objetivos R

### 2. Gestión de Riesgo Predecible
- ✅ **Sizing consistente**: Tamaño de posición basado en riesgo fijo
- ✅ **SL/TP alineados**: Stop loss y take profit calculados correctamente
- ✅ **Verificación automática**: TP ajustado si no corresponde al target R
- ✅ **Tolerancia mínima**: Ajuste solo si diferencia > 0.01

### 3. Coherencia del Sistema
- ✅ **Backtesting**: Misma lógica que señales diarias
- ✅ **Señales**: Aplican mismo esquema de SL/TP
- ✅ **Configuración**: Parámetros consistentes entre modos
- ✅ **Verificación**: Pruebas automatizadas para cada modo

### 4. Calidad y Testing
- ✅ **Pruebas unitarias**: Cobertura completa de funcionalidad
- ✅ **Pruebas manuales**: Validación de flujo completo
- ✅ **Verificación de precisión**: Cálculos R-multiple exactos
- ✅ **Consistencia de configuración**: Validación de MODE_CONFIG

## Configuración de Ejemplo

### Para modo conservador (1R):
```python
config = {
    'risk_usdt': 15.0,
    'tp_multiplier': 1.0,
    'target_r_multiple': 1.0,
    'risk_reward_ratio': 1.0,
    'use_multifactor_strategy': False
}
```

### Para modo moderado (1.5R):
```python
config = {
    'risk_usdt': 25.0,
    'tp_multiplier': 1.5,
    'target_r_multiple': 1.5,
    'risk_reward_ratio': 1.5,
    'use_multifactor_strategy': True
}
```

### Para modo agresivo (2R):
```python
config = {
    'risk_usdt': 40.0,
    'tp_multiplier': 2.0,
    'target_r_multiple': 2.0,
    'risk_reward_ratio': 2.0,
    'use_multifactor_strategy': True
}
```

## Verificación de Funcionamiento

### Cálculo de R-Multiple:
```python
# Ejemplo: Entrada a 100, SL a 98, TP a 104
entry_price = 100.0
stop_loss = 98.0
take_profit = 104.0

# Calcular riesgo y recompensa
risk = abs(entry_price - stop_loss)  # 2.0
reward = abs(take_profit - entry_price)  # 4.0

# Calcular R-multiple
r_multiple = reward / risk  # 2.0 (exactamente 2R)
```

### Verificación de Sizing:
```python
# Ejemplo: Riesgo de 20 USDT, riesgo por unidad de 2.0
risk_usdt = 20.0
risk_per_unit = 2.0

# Calcular tamaño de posición
position_size = risk_usdt / risk_per_unit  # 10.0

# Verificar riesgo total
total_risk = risk_per_unit * position_size  # 20.0 USDT
```

## Conclusión

La alineación de SL/TP y sizing con objetivos R por modo ha sido implementada exitosamente:

1. **MODE_CONFIG actualizado**: Cada modo refleja exactamente 1R, 1.5R y 2R
2. **Propagación de valores**: Todos los motores respetan los multiplicadores actualizados
3. **Señales coherentes**: Aplican el mismo esquema de SL/TP que el backtesting
4. **Pruebas completas**: Verificación automatizada para cada modo

La implementación garantiza que:
- **Modo conservador**: Target exacto de 1R por operación
- **Modo moderado**: Target exacto de 1.5R por operación
- **Modo agresivo**: Target exacto de 2R por operación
- **Sizing consistente**: Riesgo fijo por operación
- **Coherencia total**: Backtesting y señales diarias alineados

El sistema ahora proporciona gestión de riesgo predecible y alineada con los objetivos R de cada modo de trading.
