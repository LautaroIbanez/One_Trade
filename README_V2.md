# One Trade v2.0 - Modular Backtesting System

Sistema de backtesting modular y robusto con persistencia incremental de datos, validaciones estrictas y arquitectura limpia.

## 🎯 Características Principales

- **Datos Incrementales**: Persistencia CSV/Parquet con actualización incremental y detección de huecos
- **Scheduling Robusto**: Ventanas de trading configurables (06:00-12:00 ART entrada, 19:00-20:00 ART cierre forzado)
- **Límite Diario Estricto**: Máximo 1 trade por día con validaciones y assertions
- **Doble Timezone**: UTC + ART en todos los registros
- **Estrategias Intercambiables**: Sistema actual (EMA/RSI/MACD) + Baseline simple con switch configurable
- **Métricas Completas**: CAGR, Sharpe, Max DD, Win Rate, Profit Factor, Expectancy, distribución PnL
- **Broker Simulado**: Fills realistas con slippage, fees y gestión de SL/TP
- **CLI Rico**: Interfaz de línea de comandos con Rich para visualización elegante
- **Testing Completo**: Tests unitarios y e2e con pytest

## 📦 Instalación

### Requisitos

- Python 3.10+
- pip

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

**Nota sobre TA-Lib**: Si deseas usar indicadores técnicos más avanzados, instala TA-Lib:

**Windows**:
```bash
pip install TA-Lib
```

**Linux/Mac**:
```bash
# Instalar dependencias del sistema primero
sudo apt-get install ta-lib  # Debian/Ubuntu
brew install ta-lib          # macOS

# Luego instalar el paquete Python
pip install TA-Lib
```

## 🚀 Uso Rápido

### 1. Validar Configuración

```bash
python -m cli.main validate
```

### 2. Actualizar Datos de Mercado

```bash
# Actualizar todos los símbolos y timeframes del config
python -m cli.main update-data

# Actualizar símbolos específicos
python -m cli.main update-data --symbols BTC/USDT --timeframes 15m
```

### 3. Verificar Datos Disponibles

```bash
python -m cli.main check-data
```

### 4. Ejecutar Backtest

```bash
# Backtest con configuración por defecto
python -m cli.main backtest BTC/USDT

# Backtest con fechas específicas
python -m cli.main backtest BTC/USDT --start-date 2023-01-01 --end-date 2023-12-31

# Backtest con estrategia específica
python -m cli.main backtest BTC/USDT --strategy baseline
```

## 📁 Estructura del Proyecto

```
One_Trade/
├── config/
│   ├── __init__.py
│   ├── config.yaml          # Configuración principal
│   └── models.py            # Modelos Pydantic de validación
├── one_trade/
│   ├── __init__.py
│   ├── data_store.py        # Almacenamiento incremental CSV/Parquet
│   ├── data_fetch.py        # Cliente exchange con retries
│   ├── strategy.py          # Estrategias (Current + Baseline)
│   ├── scheduler.py         # Ventanas de trading y límites diarios
│   ├── broker_sim.py        # Simulador de broker
│   ├── metrics.py           # Cálculo de métricas
│   ├── backtest.py          # Motor de backtest
│   └── logging_config.py    # Configuración de logging
├── cli/
│   ├── __init__.py
│   └── main.py              # CLI con Click y Rich
├── tests/
│   ├── __init__.py
│   ├── test_data_store.py
│   ├── test_scheduler.py
│   ├── test_broker.py
│   ├── test_strategy.py
│   ├── test_metrics.py
│   └── test_backtest_e2e.py
├── data_incremental/        # Datos OHLCV persistentes
├── logs/                    # Archivos de log
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README_V2.md
```

## ⚙️ Configuración

El archivo `config/config.yaml` controla todos los parámetros del sistema:

### Exchange
```yaml
exchange:
  name: "binance"
  rate_limit:
    max_requests_per_minute: 1200
    retry_attempts: 5
```

### Datos
```yaml
data:
  symbols:
    - "BTC/USDT"
    - "ETH/USDT"
  timeframes:
    - "15m"
    - "1d"
  storage_path: "data_incremental"
  format: "csv"  # csv | parquet
```

### Estrategia
```yaml
strategy:
  type: "current"  # current | baseline
  
  current:  # Estrategia del sistema existente
    indicators:
      ema_fast: 12
      ema_slow: 26
      rsi_period: 14
  
  baseline:  # Estrategia simple
    indicators:
      ema_period: 50
      rsi_period: 14
```

### Scheduling
```yaml
scheduling:
  entry_window:
    start: "06:00"  # ART
    end: "12:00"
  forced_close_window:
    start: "19:00"
    end: "20:00"
  max_trades_per_day: 1
```

### Risk Management
```yaml
risk:
  stop_loss:
    type: "atr"  # atr | percentage | fixed
    atr_multiplier: 2.0
  take_profit:
    type: "atr"
    atr_multiplier: 3.0
  position_sizing:
    method: "fixed_risk"
    risk_per_trade_pct: 1.0
```

## 🧪 Testing

Ejecutar todos los tests:

```bash
pytest
```

Ejecutar tests específicos:

```bash
# Tests unitarios
pytest tests/test_data_store.py
pytest tests/test_scheduler.py

# Tests e2e
pytest tests/test_backtest_e2e.py

# Con coverage
pytest --cov=one_trade --cov-report=html
```

## 📊 Formato de Datos

### CSV Incremental

Los datos se almacenan con el siguiente formato:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| timestamp_utc | datetime | Timestamp UTC |
| timestamp_art | datetime | Timestamp ART |
| open | float | Precio apertura |
| high | float | Precio máximo |
| low | float | Precio mínimo |
| close | float | Precio cierre |
| volume | float | Volumen |
| source | string | Origen (exchange_timeframe) |
| last_updated_utc | datetime | Última actualización |

### Registro de Trades

Los trades se guardan con:

| Columna | Descripción |
|---------|-------------|
| date | Fecha del trade |
| symbol | Símbolo |
| side | long/short |
| entry_time_utc | Hora entrada UTC |
| entry_time_art | Hora entrada ART |
| entry_price | Precio entrada |
| exit_time_utc | Hora salida UTC |
| exit_time_art | Hora salida ART |
| exit_price | Precio salida |
| pnl | PnL absoluto |
| pnl_pct | PnL porcentual |
| fees | Fees totales |
| entry_reason | Motivo entrada |
| exit_reason | Motivo salida |

## 📈 Métricas Calculadas

- **Retorno Total**: Absoluto y porcentual
- **CAGR**: Tasa de crecimiento anual compuesta
- **Max Drawdown**: Máxima caída desde peak
- **Sharpe Ratio**: Retorno ajustado por riesgo
- **Win Rate**: Porcentaje de trades ganadores
- **Profit Factor**: Ganancias brutas / Pérdidas brutas
- **Expectancy**: PnL promedio por trade
- **Average Win/Loss**: Ganancias y pérdidas promedio
- **Daily PnL Distribution**: Estadísticas de PnL diario

## 🔍 Validaciones

El sistema incluye validaciones estrictas:

### Scheduler
- ✅ Entrada solo en ventana 06:00-12:00 ART
- ✅ Máximo 1 trade por día (con assertion)
- ✅ Cierre forzado 19:00-20:00 ART si posición abierta
- ✅ Contador diario con reset automático

### Datos
- ✅ Detección de huecos temporales
- ✅ Reconciliación de duplicados (keep=last)
- ✅ Validación de columnas requeridas
- ✅ Timestamps siempre con timezone

### Strict Mode
```yaml
validation:
  strict_mode: true  # Lanza excepciones en violaciones
  check_trade_limit_daily: true
  check_entry_windows: true
  check_forced_close: true
```

## 🛠️ Desarrollo

### Agregar Nueva Estrategia

1. Crear clase que herede de `BaseStrategy`:

```python
from one_trade.strategy import BaseStrategy, Signal

class MyStrategy(BaseStrategy):
    def generate_signal(self, data, current_idx):
        # Tu lógica aquí
        return Signal(...)
    
    def should_close(self, data, current_idx, position_side, entry_price, entry_time):
        # Tu lógica de cierre
        return False, ""
```

2. Registrar en `StrategyFactory`:

```python
# En strategy.py
elif strategy_type == "my_strategy":
    return MyStrategy(config)
```

### Formateo y Linting

```bash
# Formatear código
black one_trade cli tests

# Ordenar imports
isort one_trade cli tests

# Type checking
mypy one_trade

# Linting
flake8 one_trade cli tests
```

## 📝 Logs

Los logs se guardan en formato estructurado:

```
2023-10-09 10:30:15 - one_trade.backtest - INFO - Starting backtest for BTC/USDT
2023-10-09 10:30:16 - one_trade.scheduler - INFO - Entry window: 06:00-12:00 ART
2023-10-09 10:30:20 - one_trade.broker_sim - INFO - Position opened: LONG at 30000.00
```

## 🔄 Migración desde Sistema Anterior

Los datos antiguos en `data/` se conservan como backup. El nuevo sistema:

1. Usa `data_incremental/` para nuevos datos
2. No requiere migración inmediata
3. Puede convivir con el sistema anterior

Para migrar completamente:

```bash
# Actualizar datos nuevos
python -m cli.main update-data

# Verificar cobertura
python -m cli.main check-data

# Ejecutar backtest comparativo
python -m cli.main backtest BTC/USDT --start-date 2023-01-01
```

## 🚧 Limitaciones Actuales (Fase 1)

- ✅ Exchange: Solo Binance (Bybit en fase 2)
- ✅ Símbolos: BTC/USDT, ETH/USDT (expandible)
- ✅ UI: Solo CLI (Dash webapp en fase 2)
- ✅ Timeframes: 15m, 1d (expandible)

## 📚 Recursos

- [Documentación CCXT](https://docs.ccxt.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Pytest Documentation](https://docs.pytest.org/)

## 🤝 Contribuir

1. Escribir tests para nuevas features
2. Mantener type hints
3. Seguir formateo black/isort
4. Documentar funciones con docstrings
5. Actualizar README con cambios

## 📄 Licencia

[Especificar licencia]

## 🙋 Soporte

Para issues, consultas o mejoras, revisar:

- Logs en `logs/one_trade.log`
- Tests con `pytest -v`
- Validación con `python -m cli.main validate`

