# Recommendation Engine - Prototipo Funcional

Motor de recomendaciones inteligente que genera decisiones diarias (BUY/SELL/HOLD) basadas en análisis multi-estrategia con explicaciones en lenguaje natural.

---

## 🎯 Qué es este PoC

Este es un **prototipo funcional** del componente core del sistema "One Trade Decision-Centric App": el **Recommendation Engine**.

### Características Implementadas

✅ **Signal Condenser**: Agrega señales de múltiples estrategias con pesos configurables
✅ **Decision Generator**: Convierte señales agregadas en BUY/SELL/HOLD con niveles de confianza
✅ **Explainability Module**: Genera explicaciones en lenguaje natural para cada decisión
✅ **Integración con One Trade v2.0**: Reutiliza estrategias, backtester y datos existentes
✅ **Tests Unitarios**: Cobertura de todos los módulos principales
✅ **Demo Script**: Script interactivo para probar el motor

---

## 📁 Estructura del Código

```
decision_app/
├── recommendation_engine/
│   ├── __init__.py
│   ├── recommendation.py      # Tipos core y orchestrator
│   ├── condenser.py           # Signal aggregation
│   ├── decisor.py             # Decision generation
│   └── explainer.py           # Natural language explanations
├── integration/
│   ├── __init__.py
│   └── backtest_adapter.py    # Adapter para One Trade v2.0
├── tests/
│   ├── __init__.py
│   └── test_recommendation_engine.py
└── demo_recommendation_engine.py
```

---

## 🚀 Cómo Usar

### 1. Instalar Dependencias

El motor reutiliza las dependencias existentes de One Trade v2.0:

```bash
pip install -r requirements.txt
```

### 2. Asegurarse de Tener Datos

```bash
python run_cli.py update_data
```

### 3. Ejecutar Demo

**Modo Histórico** (Recomendaciones diarias de los últimos 30 días):

```bash
python decision_app/demo_recommendation_engine.py --mode daily
```

**Modo Actual** (Recomendación más reciente):

```bash
python decision_app/demo_recommendation_engine.py --mode latest
```

### 4. Ejecutar Tests

```bash
pytest decision_app/tests/test_recommendation_engine.py -v
```

---

## 🔧 Arquitectura

### 1. RecommendationEngine (Orchestrator)

Coordina todo el proceso:

```python
from decision_app.integration.backtest_adapter import RecommendationBacktestAdapter
from config import load_config

config = load_config("config/config.yaml")
adapter = RecommendationBacktestAdapter(config)

recommendation = adapter.get_latest_recommendation("BTC/USDT")
print(f"{recommendation.action}: {recommendation.reasoning}")
```

### 2. SignalCondenser

Agrega señales de múltiples estrategias:

- Aplica pesos configurables a cada estrategia
- Calcula fuerza agregada ponderada
- Detecta consenso entre estrategias

```python
strategy_weights = {
    "CurrentStrategy": 0.6,    # 60% de peso
    "BaselineStrategy": 0.4     # 40% de peso
}
```

### 3. DecisionGenerator

Convierte señales en decisiones:

- **BUY**: Si `aggregated_strength > 0` y `confidence >= threshold`
- **SELL**: Si `aggregated_strength < 0` y `confidence >= threshold`
- **HOLD**: Si confianza es baja o señales conflictivas

Calcula:
- Niveles de confianza (0-100%)
- Stop Loss / Take Profit basados en ATR
- Precio de entrada

### 4. ExplainabilityModule

Genera explicaciones legibles:

```
🟢 COMPRAR BTC/USDT
Confianza: 75%

💡 Razón: Tendencia alcista confirmada por 2 estrategia(s). 
Ema Cross Long. Volumen creciente (+25%)

⚠️ Invalidar si el precio cae por debajo de $65,000
```

---

## 📊 Ejemplo de Salida

```
================================================================================
DEMO: One Trade Decision-Centric App - Recommendation Engine
================================================================================

✅ Configuración cargada
   - Exchange: binance
   - Estrategias: CurrentStrategy (60%), BaselineStrategy (40%)
   - Umbral de confianza: 60%

Generando recomendaciones diarias para BTC/USDT
Periodo: 2024-12-13 a 2025-01-12

✅ Generadas 30 recomendaciones diarias

================================================================================
ÚLTIMAS 5 RECOMENDACIONES
================================================================================

🟢 BUY BTC/USDT
Confianza: 72%
Precio de entrada: $67,234.50
Stop Loss: $66,100.00
Take Profit: $69,500.00

💡 Razón: Tendencia alcista confirmada por 2 estrategia(s). 
Ema Cross Long, Baseline Long. Precio subió 3.2% en últimas 5 velas

⚠️ Invalidar si el precio cae por debajo de $66,100.00
📊 Señales de soporte: 2
--------------------------------------------------------------------------------

⚪ HOLD BTC/USDT
Confianza: 45%

💡 Razón: Señales mixtas detectadas (1 alcistas, 1 bajistas). 
La falta de consenso sugiere esperar mayor claridad antes de operar.

📊 Señales de soporte: 2
--------------------------------------------------------------------------------

================================================================================
ESTADÍSTICAS DEL PERIODO
================================================================================

Total de recomendaciones: 30
  🟢 BUY:  8 (26.7%)
  🔴 SELL: 5 (16.7%)
  ⚪ HOLD: 17 (56.7%)

Confianza promedio: 52.3%
Confianza promedio (BUY/SELL): 68.5%
```

---

## 🧪 Tests

El módulo incluye tests completos:

```bash
pytest decision_app/tests/test_recommendation_engine.py -v
```

**Tests incluidos:**

- `TestSignalCondenser`: Agregación de señales
  - Señales vacías
  - Señales unidireccionales
  - Señales conflictivas
  
- `TestDecisionGenerator`: Generación de decisiones
  - Sin señales → HOLD
  - Señales fuertes → BUY/SELL
  - Señales débiles → HOLD
  
- `TestExplainabilityModule`: Explicaciones
  - HOLD sin señales
  - BUY con razones
  - SELL con invalidación
  
- `TestRecommendationEngine`: Integración completa
  - Con estrategias reales
  - Consistencia de resultados

---

## 📈 Uso Programático

### Obtener Recomendación Actual

```python
from config import load_config
from decision_app.integration.backtest_adapter import RecommendationBacktestAdapter

config = load_config("config/config.yaml")
adapter = RecommendationBacktestAdapter(config)

rec = adapter.get_latest_recommendation("BTC/USDT")

if rec.action.value == "BUY":
    print(f"Comprar a ${rec.entry_price:.2f}")
    print(f"Stop Loss: ${rec.stop_loss:.2f}")
    print(f"Razón: {rec.reasoning}")
```

### Generar Recomendaciones Históricas

```python
df = adapter.generate_daily_recommendations(
    symbol="BTC/USDT",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

df.to_csv("recommendations_2024.csv")

buy_signals = df[df["action"] == "BUY"]
print(f"Total de señales BUY: {len(buy_signals)}")
```

### Configurar Pesos de Estrategias

```python
custom_weights = {
    "CurrentStrategy": 0.7,
    "BaselineStrategy": 0.3
}

adapter = RecommendationBacktestAdapter(
    config=config,
    strategy_weights=custom_weights
)
```

---

## 🎯 Roadmap

### ✅ Completado (Día 2)

- [x] Diseño de arquitectura
- [x] Signal Condenser
- [x] Decision Generator
- [x] Explainability Module
- [x] Integración con v2.0
- [x] Tests unitarios
- [x] Demo script

### 🚧 Próximos Pasos

- [ ] Agregar más estrategias (RSI, MACD, Bollinger Bands)
- [ ] Sistema de backtesting de recomendaciones
- [ ] Métricas de precisión (win rate de recomendaciones)
- [ ] Persistencia de recomendaciones en base de datos
- [ ] API REST para servir recomendaciones
- [ ] Frontend para visualizar recomendaciones diarias

---

## 🔍 Detalles Técnicos

### Cálculo de Confianza

```
confidence = (aggregated_strength × 0.6) + (consensus_factor × 0.4)

donde:
- aggregated_strength: Fuerza ponderada de señales (-1 a 1)
- consensus_factor: % de estrategias que coinciden (0 a 1)
```

### Umbrales

- **Confianza mínima para BUY/SELL**: 60% (configurable)
- **Confianza alta**: > 75%
- **Stop Loss**: 2 × ATR
- **Take Profit**: 3 × ATR (ratio 1.5:1)

### Pesos por Defecto

- **CurrentStrategy**: 60% (EMA + RSI + MACD)
- **BaselineStrategy**: 40% (EMA + RSI simple)

---

## 📝 Logs y Debugging

Para debugging detallado:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

adapter = RecommendationBacktestAdapter(config)
rec = adapter.get_latest_recommendation("BTC/USDT")
```

---

## 🤝 Contribuir

Este es un prototipo inicial. Sugerencias de mejora:

1. **Más estrategias**: Implementar nuevas estrategias en `one_trade/strategy.py`
2. **Mejores explicaciones**: Enriquecer el `ExplainabilityModule`
3. **Optimización de pesos**: ML para aprender pesos óptimos
4. **Market regime detection**: Adaptar pesos según condiciones de mercado

---

## 📞 Contacto

Para preguntas o feedback sobre este PoC, abrir un issue o contactar al equipo.

---

**Última actualización**: Octubre 2025
**Versión**: 1.0.0-alpha
**Estado**: ✅ PoC Funcional

