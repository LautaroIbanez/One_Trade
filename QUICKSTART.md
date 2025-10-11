# One Trade v2.0 - Quick Start Guide

Guía rápida para comenzar a usar el sistema en menos de 5 minutos.

## 🚀 Instalación Rápida

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Validar Instalación

```bash
python -m cli.main validate
```

Deberías ver:
```
✓ Configuration is valid!

Summary:
  Exchange: binance
  Symbols: BTC/USDT, ETH/USDT
  Timeframes: 15m, 1d
  Strategy: current
  Initial Capital: $10,000.00
```

## 📊 Primera Ejecución

### 1. Descargar Datos

```bash
# Descargar datos de BTC/USDT en timeframe 15m
python -m cli.main update-data --symbols BTC/USDT --timeframes 15m
```

**Tiempo estimado**: 2-5 minutos (primera vez)

**Output esperado**:
```
Updating market data...
Fetching BTC/USDT 15m...
Saved 1500 new candles for BTC/USDT 15m
Data update completed successfully!
```

### 2. Verificar Datos

```bash
python -m cli.main check-data
```

Verás una tabla con los datos disponibles:

```
┌────────────┬───────────┬─────────────┬─────────────┬─────────┐
│ Symbol     │ Timeframe │ Start Date  │ End Date    │ Candles │
├────────────┼───────────┼─────────────┼─────────────┼─────────┤
│ BTC/USDT   │ 15m       │ 2023-01-01  │ 2023-12-31  │ 35040   │
└────────────┴───────────┴─────────────┴─────────────┴─────────┘
```

### 3. Ejecutar Tu Primer Backtest

```bash
# Backtest de 30 días con estrategia por defecto
python -m cli.main backtest BTC/USDT --start-date 2023-01-01 --end-date 2023-01-31
```

**Tiempo estimado**: 10-30 segundos

**Output esperado**:
```
Running backtest for BTC/USDT...
Backtest completed successfully!

╭─────────────────────────────────────────────────────────╮
│             Performance Metrics                         │
├─────────────────────────────┬───────────────────────────┤
│ Period                      │ 2023-01-01 to 2023-01-31 │
│ Duration (days)             │                       30 │
│                             │                           │
│ Initial Capital             │               $10,000.00 │
│ Final Equity                │               $10,250.00 │
│ Total Return                │     $250.00 (2.50%)      │
│ ...                         │                           │
╰─────────────────────────────┴───────────────────────────╯

Trades saved to: data_incremental/backtest_results
```

## 🎯 Próximos Pasos

### Probar Estrategia Baseline

```bash
python -m cli.main backtest BTC/USDT --strategy baseline --start-date 2023-01-01 --end-date 2023-12-31
```

### Backtest Completo de 1 Año

```bash
python -m cli.main backtest BTC/USDT --start-date 2023-01-01 --end-date 2023-12-31
```

### Actualizar Datos Regularmente

```bash
# Actualiza solo datos nuevos (incremental)
python -m cli.main update-data
```

### Uso Programático

Ver `example_usage.py`:

```bash
python example_usage.py
```

## ⚙️ Configuración Personalizada

Edita `config/config.yaml`:

### Cambiar Capital Inicial

```yaml
broker:
  initial_capital: 50000.0  # Cambiar a $50k
```

### Ajustar Ventana de Entrada

```yaml
scheduling:
  entry_window:
    start: "08:00"  # Cambiar a 8am-14pm
    end: "14:00"
```

### Cambiar Risk Management

```yaml
risk:
  position_sizing:
    risk_per_trade_pct: 2.0  # Arriesgar 2% por trade
  stop_loss:
    atr_multiplier: 1.5  # SL más ajustado
```

## 🧪 Verificar con Tests

```bash
# Ejecutar todos los tests
pytest

# Solo tests rápidos
pytest -k "not slow"

# Con verbose
pytest -v
```

## 📁 Archivos Generados

Después de ejecutar un backtest, encontrarás:

```
data_incremental/
├── BTC_USDT_15m.csv              # Datos OHLCV
└── backtest_results/
    └── trades_BTC_USDT_20231009_143022.csv  # Trades

logs/
└── one_trade.log                 # Logs del sistema
```

## 🆘 Solución de Problemas

### Error: "No data found"

```bash
# Descargar datos primero
python -m cli.main update-data --symbols BTC/USDT --timeframes 15m
```

### Error: "Configuration file not found"

```bash
# Verificar que config/config.yaml existe
ls config/config.yaml

# Si no existe, copiar desde template
cp config/config.yaml.template config/config.yaml
```

### Error: "Module not found"

```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: Rate limit exceeded

Editar `config/config.yaml`:

```yaml
exchange:
  rate_limit:
    max_requests_per_minute: 600  # Reducir a 600
    retry_attempts: 10  # Aumentar reintentos
```

## 💡 Tips

### 1. Usa Símbolos Válidos

```bash
# Correcto
python -m cli.main backtest BTC/USDT

# Incorrecto
python -m cli.main backtest BTCUSDT  # ❌ Falta /
```

### 2. Descarga Datos de a Poco

```bash
# Primero un mes
python -m cli.main update-data --symbols BTC/USDT

# Luego expandir
python -m cli.main update-data --symbols ETH/USDT
```

### 3. Revisa Logs

```bash
# Si algo falla, revisar logs
tail -f logs/one_trade.log
```

### 4. Strict Mode en Development

```yaml
validation:
  strict_mode: true  # Detecta violaciones inmediatamente
```

### 5. CSV vs Parquet

```yaml
data:
  format: "csv"     # Para debugging
  format: "parquet" # Para performance
```

## 📚 Comandos Útiles

```bash
# Ver ayuda general
python -m cli.main --help

# Ver ayuda de comando específico
python -m cli.main backtest --help

# Backtest con verbose logging
python -m cli.main --log-level DEBUG backtest BTC/USDT

# Actualizar solo un símbolo
python -m cli.main update-data --symbols BTC/USDT

# Validar configuración antes de backtest
python -m cli.main validate
```

## ✅ Checklist de Primera Ejecución

- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Validar config: `python -m cli.main validate`
- [ ] Descargar datos: `python -m cli.main update-data --symbols BTC/USDT --timeframes 15m`
- [ ] Verificar datos: `python -m cli.main check-data`
- [ ] Primer backtest: `python -m cli.main backtest BTC/USDT --start-date 2023-01-01 --end-date 2023-01-31`
- [ ] Revisar trades: `cat data_incremental/backtest_results/trades_*.csv`
- [ ] Ejecutar tests: `pytest`
- [ ] Leer README_V2.md completo

## 🎓 Recursos Adicionales

- **README_V2.md**: Documentación completa
- **IMPLEMENTATION_V2_SUMMARY.md**: Detalles de arquitectura
- **example_usage.py**: Uso programático
- **tests/**: Ejemplos de código

## 🤝 Soporte

Si encuentras problemas:

1. Revisar logs: `tail -f logs/one_trade.log`
2. Ejecutar tests: `pytest -v`
3. Validar config: `python -m cli.main validate`
4. Verificar datos: `python -m cli.main check-data`

---

**¡Listo!** Ya puedes comenzar a hacer backtesting con One Trade v2.0 🚀



