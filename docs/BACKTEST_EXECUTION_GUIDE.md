# Guía de Ejecución de Backtests

## Fecha
16 de Octubre, 2025

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Scripts Disponibles](#scripts-disponibles)
3. [Ejecución Paso a Paso](#ejecución-paso-a-paso)
4. [Validación de Resultados](#validación-de-resultados)
5. [Troubleshooting](#troubleshooting)

---

## Descripción General

El sistema One Trade dispone de múltiples formas de ejecutar backtests:

- **CLI moderna** (`python -m cli.main`) - Recomendado para uso diario
- **Webapp interactiva** (`webapp/app.py`) - Para visualización gráfica
- **Batch runner** (`manage_backtests.py`) - Para backtests masivos anuales

### Datos Actuales Disponibles

Según la última ejecución, tenemos:
- **5 backtests** completos
- **1,237 trades** totales
- **75.3% win rate** agregado
- **$24,880 USDT** de P&L total
- **Período**: Sept 2024 - Sept 2025

---

## Scripts Disponibles

### 1. CLI Moderna (Recomendado)

**Ubicación**: `cli/main.py`

**Uso básico**:
```bash
# Ver ayuda
python -m cli.main --help

# Backtest de 30 días
python -m cli.main backtest BTC/USDT --start-date 2024-01-01 --end-date 2024-01-31

# Backtest anual completo
python -m cli.main backtest BTC/USDT --start-date 2024-01-01 --end-date 2024-12-31

# Con estrategia específica
python -m cli.main backtest BTC/USDT --strategy baseline

# Actualizar datos antes de backtest
python -m cli.main update-data --symbols BTC/USDT --timeframes 15m
python -m cli.main backtest BTC/USDT
```

**Ventajas**:
- Salida formateada y colorida
- Validación automática de configuración
- Logging estructurado
- Recomendado para desarrollo

### 2. Batch Runner Anual

**Ubicación**: `manage_backtests.py`

**Uso**:
```bash
# Ejecutar backtests para todos los modos y símbolos
python manage_backtests.py

# Con fecha específica (365 días desde fecha)
python manage_backtests.py --since 2024-01-01

# Modo completo (730 días)
python manage_backtests.py --since full

# Forzar rebuild completo
python manage_backtests.py --force-rebuild

# Solo modos específicos
python manage_backtests.py --modes moderate aggressive

# Ver reporte sin ejecutar
python manage_backtests.py --report-only
```

**Características**:
- Ejecuta **todos los símbolos y modos** automáticamente
- Validación de cobertura (mínimo 365 días)
- Genera log estructurado en `data/backtest_execution_log.json`
- Ideal para ejecución nocturna/programada

**Modos disponibles**:
- `conservative`: 3 símbolos (BTC, ETH, BNB)
- `moderate`: 5 símbolos (+ SOL, ADA)
- `aggressive`: 8 símbolos (+ XRP, DOGE, AVAX)

### 3. Webapp Interactiva

**Ubicación**: `webapp/app.py`

**Inicio**:
```bash
cd webapp
python app.py
# Abrir http://localhost:8050
```

**Características**:
- Interfaz Dash con gráficos interactivos
- Ejecución de backtests desde UI
- Visualización de trades en precio
- Métricas y reportes en tiempo real

---

## Ejecución Paso a Paso

### Escenario 1: Primer Backtest

```bash
# 1. Validar instalación
pip install -r requirements.txt
python -m cli.main validate

# 2. Descargar datos (primera vez)
python -m cli.main update-data --symbols BTC/USDT --timeframes 15m

# 3. Verificar datos descargados
python -m cli.main check-data

# 4. Ejecutar backtest de prueba (30 días)
python -m cli.main backtest BTC/USDT --start-date 2024-01-01 --end-date 2024-01-31

# 5. Revisar resultados
# Los trades se guardan en: data_incremental/backtest_results/trades_*.csv
```

### Escenario 2: Backtest Anual Completo

```bash
# Opción A: Via CLI
python -m cli.main backtest BTC/USDT --start-date 2024-01-01 --end-date 2024-12-31

# Opción B: Via Batch Runner (todos los símbolos)
python manage_backtests.py --since 2024-01-01

# Ver reporte de ejecución
python manage_backtests.py --report-only
```

### Escenario 3: Backtests para Decision App

Para alimentar el endpoint `/api/v1/stats` con datos reales:

```bash
# 1. Ejecutar backtests que generan CSVs en root
python manage_backtests.py

# 2. Verificar CSVs generados
ls trades_final_*.csv

# 3. Validar estructura de datos
python test_stats_simple.py

# 4. Iniciar backend
cd decision_app/backend
python main.py

# 5. En otra terminal, probar endpoint
python test_stats_api.py
```

---

## Validación de Resultados

### Archivos Generados

Después de ejecutar backtests, deberías ver:

**En directorio root**:
```
trades_final_BTC_USDT_USDT.csv
trades_final_BTC_USDT_USDT_moderate.csv
trades_final_BTC_USDT_USDT_aggressive.csv
trades_final_BTC_USDT_USDT_conservative.csv
trades_final_ETH_USDT_USDT.csv
```

**En data/ (metadatos)**:
```
data/trades_final_BTC_USDT_USDT_moderate_meta.json
data/backtest_execution_log.json
```

### Verificar CSV

```bash
# Ver primeras líneas
head -5 trades_final_BTC_USDT_USDT.csv

# Contar trades
wc -l trades_final_BTC_USDT_USDT.csv

# Verificar columnas esperadas
python -c "import pandas as pd; df = pd.read_csv('trades_final_BTC_USDT_USDT.csv'); print(df.columns.tolist())"
```

**Columnas esperadas**:
- `day_key`
- `entry_time`
- `side` (LONG/SHORT)
- `entry_price`
- `sl` (stop loss)
- `tp` (take profit)
- `exit_time`
- `exit_price`
- `exit_reason`
- `pnl_usdt`
- `r_multiple`
- `used_fallback`

### Calcular Métricas Manualmente

```bash
python test_stats_simple.py
```

Salida esperada:
```
📈 BTC (trades_final_BTC_USDT_USDT.csv):
  Trades: 253 (192W / 61L)
  Win Rate: 75.9%
  Total P&L: $5161.40 USDT
  Max Drawdown: $-120.00 USDT
  Profit Factor: 5.23
  Avg R-Multiple: 1.02
```

---

## Troubleshooting

### Error: "No data found"

**Causa**: No se descargaron datos OHLCV

**Solución**:
```bash
python -m cli.main update-data --symbols BTC/USDT --timeframes 15m
```

### Error: "Insufficient coverage"

**Causa**: Backtest no alcanza 365 días mínimos

**Solución**:
```bash
# Forzar rebuild desde fecha anterior
python manage_backtests.py --since 2023-01-01 --force-rebuild
```

### Error: "API rate limit exceeded"

**Causa**: Demasiadas peticiones a Binance API

**Solución**:
1. Editar `config/config.yaml`:
```yaml
exchange:
  rate_limit:
    max_requests_per_minute: 600
    retry_attempts: 10
```

2. Esperar 1 minuto y reintentar

### Error: Pydantic version mismatch

**Causa**: Versión incompatible de pydantic-core

**Solución**:
```bash
pip install --upgrade pydantic pydantic-core
# O reinstalar todo
pip install -r requirements.txt --force-reinstall
```

### CSVs vacíos o sin trades

**Diagnóstico**:
```bash
# Ver logs
tail -f logs/one_trade.log

# Verificar configuración
python -m cli.main validate

# Revisar datos descargados
python -m cli.main check-data
```

**Posibles causas**:
- Estrategia no genera señales en el período
- Datos OHLCV corruptos o incompletos
- Configuración de entry/exit windows muy restrictiva

### Backend no inicia

**Diagnóstico**:
```bash
cd decision_app/backend
python -c "from app.core.config import settings; print('OK')"
```

**Si falla**, verificar:
1. Variables de entorno en `.env`
2. Base de datos `onetrade.db` existe
3. Dependencias instaladas: `pip install -r requirements.txt`

---

## Scripts de Verificación

### test_stats_simple.py

Valida estructura de CSVs y calcula métricas:

```bash
python test_stats_simple.py
```

### test_stats_api.py

Prueba endpoint `/api/v1/stats`:

```bash
# 1. Iniciar backend
cd decision_app/backend
python main.py

# 2. En otra terminal
python test_stats_api.py
```

---

## Mejores Prácticas

### 1. Ejecución Regular

```bash
# Cron job para backtests nocturnos
0 2 * * * cd /path/to/One_Trade && python manage_backtests.py --since auto
```

### 2. Backup de Resultados

```bash
# Crear backup antes de rebuild
tar -czf backtest_backup_$(date +%Y%m%d).tar.gz trades_final_*.csv data/*.json
```

### 3. Validación Pre-Producción

Antes de usar resultados en producción:

```bash
# 1. Ejecutar backtests
python manage_backtests.py

# 2. Validar CSVs
python test_stats_simple.py

# 3. Probar endpoint
cd decision_app/backend
python main.py &
sleep 5
python test_stats_api.py

# 4. Verificar frontend
cd decision_app/frontend
npm run dev
# Abrir http://localhost:5173 y revisar Dashboard
```

### 4. Monitoreo

```bash
# Ver progreso en tiempo real
tail -f logs/one_trade.log

# Verificar uso de memoria
ps aux | grep python

# Monitorear archivos generados
watch -n 5 'ls -lh trades_final_*.csv'
```

---

## Checklist de Ejecución

- [ ] Dependencias instaladas: `pip install -r requirements.txt`
- [ ] Configuración validada: `python -m cli.main validate`
- [ ] Datos actualizados: `python -m cli.main update-data`
- [ ] Backtest ejecutado: `python manage_backtests.py`
- [ ] CSVs generados: `ls trades_final_*.csv`
- [ ] Métricas validadas: `python test_stats_simple.py`
- [ ] Endpoint funciona: `python test_stats_api.py`
- [ ] Frontend actualizado: Dashboard muestra métricas reales

---

## Recursos Adicionales

- **QUICKSTART.md**: Guía rápida de inicio
- **README_V2.md**: Documentación completa del sistema
- **CRITICAL_ISSUES_CORRECTIONS.md**: Problemas resueltos y roadmap
- **webapp/app.py**: Código de la aplicación interactiva

---

## Soporte

Si encuentras problemas:

1. Revisar logs: `tail -f logs/one_trade.log`
2. Validar config: `python -m cli.main validate`
3. Ver este documento
4. Ejecutar scripts de diagnóstico

**Última actualización**: 16 de Octubre, 2025

