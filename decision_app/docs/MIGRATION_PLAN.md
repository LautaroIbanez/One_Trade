# Plan de Migración - One Trade v2.0 → Decision-Centric App

Este documento detalla cómo migrar/reutilizar código existente de One Trade v2.0 hacia el nuevo sistema Decision-Centric.

---

## 🎯 Objetivo de la Migración

**Reutilizar** el 60-70% del código existente que es estable y funcional, mientras se **reescribe** o **extiende** el 30-40% para soportar las nuevas funcionalidades.

---

## 📊 Análisis del Código Existente

### Inventario de Módulos v2.0

| Módulo | Archivo(s) | LoC | Estado | Acción |
|--------|-----------|-----|--------|--------|
| Data Store | `one_trade/data_store.py` | ~160 | ✅ Estable | **REUTILIZAR** con extensiones |
| Data Fetch | `one_trade/data_fetch.py` | ~120 | ✅ Estable | **REUTILIZAR** como base |
| Backtest Engine | `one_trade/backtest.py` | ~180 | ✅ Estable | **EXTENDER** para multi-activo |
| Broker Simulator | `one_trade/broker_sim.py` | ~250 | ✅ Estable | **REUTILIZAR** sin cambios |
| Strategies | `one_trade/strategy.py` | ~200 | ✅ Funcional | **ADAPTAR** a nueva interfaz |
| Metrics Calculator | `one_trade/metrics.py` | ~150 | ✅ Completo | **REUTILIZAR** + agregar métricas |
| Scheduler | `one_trade/scheduler.py` | ~180 | ✅ Estable | **REUTILIZAR** sin cambios |
| Config Models | `config/models.py` | ~200 | ✅ Completo | **EXTENDER** con nuevos settings |
| Web App (Dash) | `webapp_v2/interactive_app.py` | ~800 | ⚠️ Limitado | **REEMPLAZAR** con React |
| CLI | `cli/` | ~150 | ✅ Útil | **MANTENER** para debugging |

**Total Código v2.0**: ~2,390 LoC  
**Reutilizable**: ~1,670 LoC (70%)  
**A reescribir**: ~720 LoC (30%)

---

## 🔄 Estrategia de Migración

### Enfoque: "Strangler Fig Pattern"

Construir el nuevo sistema alrededor del viejo, migrando módulo por módulo sin romper funcionalidad existente.

```
┌─────────────────────────────────────┐
│     One Trade v2.0 (ACTUAL)         │  ← Sigue funcionando
│  • Backtesting manual                │
│  • Webapp Dash                       │
│  • CLI                               │
└──────────────┬──────────────────────┘
               │ Shared Core Modules
┌──────────────▼──────────────────────┐
│   CORE MODULES (Reutilizados)       │
│  • data_store.py                     │
│  • backtest.py                       │
│  • broker_sim.py                     │
│  • strategies.py                     │
└──────────────┬──────────────────────┘
               │ Extensiones
┌──────────────▼──────────────────────┐
│   Decision-Centric App (NUEVO)      │  ← Nueva funcionalidad
│  • Recommendation Engine             │
│  • API REST                          │
│  • React Dashboard                   │
└─────────────────────────────────────┘
```

### Fases de Migración

**Fase 1: Setup Dual**
- Crear carpeta `decision_app/` sin tocar `one_trade/`
- v2.0 sigue operando normalmente

**Fase 2: Import Core**
- Copiar módulos core a `decision_app/core/`
- Agregar tests de regresión

**Fase 3: Extend**
- Agregar nuevas funcionalidades sobre core existente
- Testing paralelo (v2.0 vs nuevo)

**Fase 4: Transition**
- Feature parity alcanzada
- Usuarios migran gradualmente
- v2.0 en modo maintenance

**Fase 5: Sunset**
- Deprecar v2.0
- Todo migrado a Decision-Centric App

---

## 📦 Migración Por Módulo

### 1. Data Store (`one_trade/data_store.py`)

#### Estado Actual (v2.0)

```python
class DataStore:
    def __init__(self, storage_path: str, data_format: str, local_tz: str):
        ...
    
    def read_data(self, symbol: str, timeframe: str) -> Tuple[pd.DataFrame, datetime]:
        ...
    
    def write_data(self, symbol: str, timeframe: str, data: pd.DataFrame, source: str):
        ...
    
    def read_data_filtered(self, symbol: str, timeframe: str, 
                           start_date: str, end_date: str):
        ...  # Agregado recientemente
    
    def check_gaps(self, symbol: str, timeframe: str):
        ...
```

#### Cambios Necesarios

1. **Migrar storage de archivos → PostgreSQL + TimescaleDB**

```python
# decision_app/core/data/store.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DataStore:
    """Drop-in replacement with DB backend."""
    
    def __init__(self, db_url: str, local_tz: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.local_tz = local_tz
        # Mantener caché en memoria para compatibilidad
        self._cache = {}
    
    def read_data(self, symbol: str, timeframe: str) -> Tuple[pd.DataFrame, datetime]:
        """Compatible API, implementación con SQL."""
        query = """
        SELECT timestamp_utc, open, high, low, close, volume
        FROM market_data
        WHERE symbol = %s AND timeframe = %s
        ORDER BY timestamp_utc
        """
        df = pd.read_sql(query, self.engine, params=[symbol, timeframe])
        return df, df['timestamp_utc'].max()
    
    # ... resto de métodos con misma signature
```

2. **Agregar método de migración**

```python
def migrate_from_files(self, old_storage_path: Path):
    """Migrate CSV/Parquet files to PostgreSQL."""
    for file in old_storage_path.glob("*.csv"):
        symbol, timeframe = self._parse_filename(file.name)
        df = pd.read_csv(file)
        self.bulk_insert(symbol, timeframe, df)
```

#### Plan de Acción

- [ ] Crear nueva clase `DataStore` con backend SQL
- [ ] Mantener misma API pública (drop-in replacement)
- [ ] Script de migración de archivos → DB
- [ ] Tests de paridad (mismos resultados en ambos)

**Esfuerzo**: 2-3 días  
**Prioridad**: Alta (foundational)

---

### 2. Data Fetcher (`one_trade/data_fetch.py`)

#### Estado Actual (v2.0)

```python
class DataFetcher:
    def __init__(self, exchange_config: ExchangeConfig):
        self.exchange = ccxt.binance(...)
    
    def fetch_ohlcv(self, symbol: str, timeframe: str, since: datetime):
        ...
    
    def fetch_incremental(self, symbol: str, timeframe: str, last_timestamp: datetime):
        ...
    
    def reconcile_gaps(self, symbol: str, timeframe: str, gaps: List):
        ...
```

#### Cambios Necesarios

1. **Multi-exchange support** (actualmente solo Binance)

```python
# decision_app/core/data/connectors/base.py
from abc import ABC, abstractmethod

class ExchangeConnector(ABC):
    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str, 
                         start: datetime, end: datetime) -> pd.DataFrame:
        pass

# decision_app/core/data/connectors/binance.py
class BinanceConnector(ExchangeConnector):
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str, 
                         start: datetime, end: datetime) -> pd.DataFrame:
        # Implementación reutilizada de v2.0
        ...

# decision_app/core/data/connectors/kraken.py
class KrakenConnector(ExchangeConnector):
    ...  # Nuevo

# decision_app/core/data/connectors/factory.py
def get_connector(exchange_name: str) -> ExchangeConnector:
    connectors = {
        'binance': BinanceConnector,
        'kraken': KrakenConnector,
        # ...
    }
    return connectors[exchange_name]()
```

2. **Async/await** para concurrencia

```python
# Actual (v2.0): Síncrono
data = fetcher.fetch_ohlcv('BTC/USDT', '15m', since)

# Nuevo: Asíncrono
data = await fetcher.fetch_ohlcv('BTC/USDT', '15m', since)

# Múltiples símbolos en paralelo
tasks = [
    fetcher.fetch_ohlcv('BTC/USDT', '15m', since),
    fetcher.fetch_ohlcv('ETH/USDT', '15m', since),
]
results = await asyncio.gather(*tasks)
```

#### Plan de Acción

- [ ] Crear interfaz `ExchangeConnector`
- [ ] Migrar código Binance a BinanceConnector
- [ ] Convertir a async/await
- [ ] Tests con datos mock

**Esfuerzo**: 2-3 días  
**Prioridad**: Alta

---

### 3. Backtest Engine (`one_trade/backtest.py`)

#### Estado Actual (v2.0)

Funciona bien para **single symbol**, necesita extensión para multi-activo.

```python
class BacktestEngine:
    def run_backtest(self, symbol: str, start_date: str, end_date: str, 
                     progress_callback: Optional[Callable] = None) -> Dict:
        ...
```

#### Cambios Necesarios

1. **Multi-symbol support**

```python
class BacktestEngine:
    def run_backtest_multi(self, symbols: List[str], start_date: str, 
                           end_date: str, allocation: Dict[str, float]) -> Dict:
        """
        Backtest portfolio con múltiples símbolos.
        
        Args:
            symbols: ['BTC/USDT', 'ETH/USDT']
            allocation: {'BTC/USDT': 0.6, 'ETH/USDT': 0.4}
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.run_backtest(symbol, start_date, end_date)
        
        # Combinar equity curves con allocation
        combined_equity = self._combine_equity_curves(results, allocation)
        combined_metrics = self._calculate_portfolio_metrics(combined_equity)
        
        return {
            'symbols': symbols,
            'individual_results': results,
            'portfolio_metrics': combined_metrics,
            'equity_curve': combined_equity
        }
```

2. **Guardar resultados en DB** (actualmente CSV)

```python
def _save_results(self, result: BacktestResult) -> UUID:
    """Save to PostgreSQL and return ID."""
    session = self.Session()
    db_result = BacktestResultModel(
        symbol=result.symbol,
        strategy_name=result.strategy_name,
        ...
    )
    session.add(db_result)
    session.commit()
    return db_result.id
```

#### Plan de Acción

- [ ] Extender con `run_backtest_multi()`
- [ ] Integrar con DB para persistencia
- [ ] Mantener backward compatibility con v2.0
- [ ] Tests de regresión

**Esfuerzo**: 3-4 días  
**Prioridad**: Media (puede hacerse después)

---

### 4. Strategies (`one_trade/strategy.py`)

#### Estado Actual (v2.0)

```python
class BaseStrategy(ABC):
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, index: int) -> Optional[Signal]:
        pass
    
    @abstractmethod
    def should_close(self, data: pd.DataFrame, index: int, 
                     position: Position) -> Tuple[bool, str]:
        pass

class BaselineStrategy(BaseStrategy):
    ...

class CurrentStrategy(BaseStrategy):
    ...
```

#### Cambios Necesarios

1. **Agregar metadata** para Recommendation Engine

```python
class BaseStrategy(ABC):
    ...
    
    @abstractmethod
    def get_metadata(self) -> StrategyMetadata:
        """Return strategy info for recommendation engine."""
        pass
    
    @abstractmethod
    def get_confidence(self, signal: Signal, market_context: Dict) -> float:
        """
        Return confidence score 0-100 for this signal.
        
        Args:
            signal: Generated signal
            market_context: Volatility, volume, trend strength, etc.
        
        Returns:
            Confidence score 0-100
        """
        pass

@dataclass
class StrategyMetadata:
    name: str
    version: str
    description: str
    parameters: Dict[str, Any]
    performance_metrics: Optional[PerformanceMetrics]  # From backtests
    ideal_conditions: List[str]  # ["trending market", "high volatility"]
```

2. **Strategy Registry** para descubrimiento dinámico

```python
# decision_app/core/strategies/registry.py
class StrategyRegistry:
    _strategies: Dict[str, Type[BaseStrategy]] = {}
    
    @classmethod
    def register(cls, name: str):
        def decorator(strategy_class: Type[BaseStrategy]):
            cls._strategies[name] = strategy_class
            return strategy_class
        return decorator
    
    @classmethod
    def list_strategies(cls) -> List[str]:
        return list(cls._strategies.keys())
    
    @classmethod
    def get_strategy(cls, name: str, params: Dict) -> BaseStrategy:
        return cls._strategies[name](**params)

# Uso
@StrategyRegistry.register('baseline')
class BaselineStrategy(BaseStrategy):
    ...

@StrategyRegistry.register('current')
class CurrentStrategy(BaseStrategy):
    ...

# Dinamically load
strategy = StrategyRegistry.get_strategy('baseline', params)
```

#### Plan de Acción

- [ ] Agregar métodos `get_metadata()` y `get_confidence()`
- [ ] Implementar StrategyRegistry
- [ ] Migrar estrategias existentes
- [ ] Tests unitarios

**Esfuerzo**: 2-3 días  
**Prioridad**: Media

---

### 5. Recommendation Engine (NUEVO)

**No existe en v2.0, implementar desde cero.**

Ver [ARCHITECTURE.md](ARCHITECTURE.md#3-recommendation-engine) para diseño completo.

#### Dependencias de v2.0

- **Backtest Results**: Input para condensador
- **Strategies**: Para obtener señales activas
- **Market Data**: Para contexto actual

#### Plan de Acción

- [ ] Implementar `SignalCondenser`
- [ ] Implementar `DecisionGenerator`
- [ ] Implementar `Explainer`
- [ ] Integrar con backtests
- [ ] Tests con datos históricos

**Esfuerzo**: 1 semana  
**Prioridad**: **CRÍTICA** (core feature)

---

### 6. Web App (`webapp_v2/interactive_app.py`)

#### Estado Actual (v2.0)

Dash app con ~800 LoC. Funcional pero limitada.

#### Acción

**REEMPLAZAR completamente con React.**

Razones:
- Dash no soporta UX compleja que necesitamos
- React tiene mejor ecosistema de componentes
- Performance superior para dashboards interactivos

#### Plan de Migración

1. **Identificar componentes reutilizables** (lógica, no código)

| Componente Dash | Equivalente React | Estado |
|----------------|------------------|---------|
| Dashboard cards | `<RecommendationCard>` | 📋 Nuevo |
| Backtest form | `<BacktestForm>` | ♻️ Adaptar lógica |
| Progress bar | `<ProgressBar>` | ✅ Librería |
| Backtest results | `<BacktestResults>` | ♻️ Adaptar |

2. **Migrar lógica de callbacks a API endpoints**

```python
# Dash (v2.0)
@app.callback(
    Output("backtest-results", "children"),
    Input("run-backtest-btn", "n_clicks"),
    State("symbol-select", "value"),
    ...
)
def run_backtest(n_clicks, symbol, ...):
    results = engine.run_backtest(symbol, ...)
    return render_results(results)

# FastAPI (nuevo)
@app.post("/api/v1/backtests")
async def create_backtest(config: BacktestConfig):
    task = run_backtest_task.delay(config.dict())
    return {"task_id": task.id, "status": "PENDING"}
```

```typescript
// React (nuevo)
function RunBacktestButton() {
  const mutation = useMutation({
    mutationFn: (config: BacktestConfig) =>
      api.post('/api/v1/backtests', config),
    onSuccess: (data) => {
      toast.success(`Backtest iniciado: ${data.task_id}`);
      navigate(`/backtests/${data.task_id}`);
    }
  });
  
  return <Button onClick={() => mutation.mutate(config)}>Run</Button>;
}
```

#### Plan de Acción

- [ ] Setup proyecto React con Vite
- [ ] Crear componentes base (layout, navigation)
- [ ] Migrar pantalla de Dashboard
- [ ] Migrar pantalla de Backtests
- [ ] Migrar pantalla de Data
- [ ] E2E tests

**Esfuerzo**: 2 semanas  
**Prioridad**: Alta

---

## 🗂️ Estructura de Directorios

### Estructura Propuesta

```
one_trade/                        # Proyecto existente (mantener)
├── one_trade/                    # Módulos core v2.0
├── webapp_v2/                    # Dash app (deprecar gradualmente)
├── cli/                          # CLI (mantener)
└── tests/                        # Tests v2.0

decision_app/                     # NUEVO PROYECTO
├── backend/
│   ├── api/                      # FastAPI app
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── recommendations.py
│   │   │   ├── backtests.py
│   │   │   └── data.py
│   │   └── dependencies.py
│   ├── core/                     # Core modules (migrados + nuevos)
│   │   ├── data/
│   │   │   ├── store.py          # Migrado de one_trade/data_store.py
│   │   │   ├── fetcher.py        # Migrado de one_trade/data_fetch.py
│   │   │   └── connectors/
│   │   ├── backtest/
│   │   │   ├── engine.py         # Migrado de one_trade/backtest.py
│   │   │   ├── broker.py         # Migrado de one_trade/broker_sim.py
│   │   │   └── metrics.py        # Migrado de one_trade/metrics.py
│   │   ├── strategies/
│   │   │   ├── base.py           # Migrado de one_trade/strategy.py
│   │   │   ├── baseline.py
│   │   │   └── registry.py       # NUEVO
│   │   ├── recommendation/       # NUEVO (core feature)
│   │   │   ├── condenser.py
│   │   │   ├── generator.py
│   │   │   └── explainer.py
│   │   └── shared/
│   │       ├── models.py
│   │       └── utils.py
│   ├── workers/                  # Celery tasks
│   │   └── tasks.py
│   ├── tests/
│   └── requirements.txt
├── frontend/                     # React app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── docs/                         # Documentación
│   ├── ARCHITECTURE.md
│   ├── TECHNICAL_DECISIONS.md
│   ├── MIGRATION_PLAN.md         # Este documento
│   └── API_CONTRACTS.md
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 🧪 Testing Strategy

### Tests de Paridad

Para cada módulo migrado, crear tests que comparan v2.0 vs nuevo:

```python
# tests/test_migration_parity.py
import pytest
from one_trade.data_store import DataStore as DataStoreV2
from decision_app.core.data.store import DataStore as DataStoreNew

def test_data_store_parity():
    """Ensure new DataStore returns same results as v2.0."""
    # Setup
    store_v2 = DataStoreV2("data_incremental", "csv", "America/Argentina/Buenos_Aires")
    store_new = DataStoreNew("postgresql://localhost/test", "America/Argentina/Buenos_Aires")
    
    # Migrate test data
    store_new.migrate_from_files(Path("data_incremental"))
    
    # Compare
    df_v2, ts_v2 = store_v2.read_data("BTC/USDT", "15m")
    df_new, ts_new = store_new.read_data("BTC/USDT", "15m")
    
    pd.testing.assert_frame_equal(df_v2, df_new)
    assert ts_v2 == ts_new
```

### Integration Tests

```python
def test_end_to_end_backtest():
    """Test full backtest flow: data fetch → backtest → results."""
    # Same as v2.0 but with new stack
    ...
```

---

## 📅 Timeline de Migración

### Semana 1-2: Foundation

- [x] Documentación de arquitectura
- [ ] Setup repos (backend + frontend)
- [ ] Docker Compose con servicios
- [ ] CI/CD pipeline básico

### Semana 3: Core Modules Migration

- [ ] Migrar DataStore a PostgreSQL
- [ ] Migrar DataFetcher con async
- [ ] Tests de paridad

### Semana 4: Backtest Extension

- [ ] Extender BacktestEngine
- [ ] Integrar con DB
- [ ] Tests de regresión

### Semana 5-6: Strategies + Registry

- [ ] Agregar metadata a estrategias
- [ ] Implementar StrategyRegistry
- [ ] Migrar estrategias existentes

### Semana 7-8: Recommendation Engine (CRÍTICO)

- [ ] Implementar Condenser
- [ ] Implementar Generator
- [ ] Implementar Explainer
- [ ] Tests con datos históricos

### Semana 9-10: API + Frontend

- [ ] Endpoints REST completos
- [ ] React dashboard
- [ ] Integración frontend-backend

### Semana 11: Testing & QA

- [ ] E2E tests
- [ ] Performance testing
- [ ] Security audit

### Semana 12: Deployment

- [ ] Deploy staging
- [ ] Beta testing
- [ ] Deploy producción

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|-----------|
| Bugs en código migrado | Media | Alto | Tests de paridad exhaustivos |
| Performance degradation | Baja | Alto | Benchmarks pre/post migración |
| Complejidad de DB | Media | Medio | Usar ORM (SQLAlchemy) |
| React learning curve | Baja | Medio | Prototipo temprano |
| Scope creep | Alta | Alto | Roadmap estricto, MVP first |

---

## ✅ Checklist de Go-Live

Antes de deprecar v2.0:

- [ ] Feature parity alcanzada
- [ ] Performance ≥ v2.0
- [ ] Tests de regresión pasando
- [ ] Documentación completa
- [ ] Al menos 5 usuarios beta satisfechos
- [ ] Monitoring en producción funcionando
- [ ] Plan de rollback documentado

---

## 📚 Referencias

- [One Trade v2.0 Codebase](../../one_trade/)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [TECHNICAL_DECISIONS.md](TECHNICAL_DECISIONS.md)

---

**Última actualización**: Octubre 2025  
**Próxima revisión**: Semana 3 (post-foundation)







