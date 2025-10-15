# One Trade Decision-Centric App - Arquitectura del Sistema

**Versión:** 1.0  
**Fecha:** Octubre 2025  
**Estado:** Diseño Inicial

---

## Índice

1. [Visión General](#visión-general)
2. [Principios de Diseño](#principios-de-diseño)
3. [Arquitectura de Alto Nivel](#arquitectura-de-alto-nivel)
4. [Módulos del Sistema](#módulos-del-sistema)
5. [Flujo de Datos](#flujo-de-datos)
6. [Modelo de Datos](#modelo-de-datos)
7. [Infraestructura y Despliegue](#infraestructura-y-despliegue)
8. [Seguridad y Rendimiento](#seguridad-y-rendimiento)

---

## Visión General

### Objetivo del Sistema

Proporcionar al usuario una **recomendación diaria clara y accionable** sobre qué hacer con sus inversiones (COMPRAR, MANTENER, VENDER) basada en análisis automatizado de múltiples estrategias de trading y datos de mercado actualizados.

### Usuarios Objetivo

- **Trader Individual**: Persona que opera sus propias inversiones y necesita orientación basada en datos
- **Analista de Mercado**: Profesional que valida estrategias y compara rendimientos
- **Gestor de Cartera**: Usuario que supervisa múltiples activos y necesita decisiones rápidas

### Casos de Uso Principales

1. **Consulta Diaria de Recomendación**
   - Usuario abre la app
   - Sistema muestra recomendación del día para cada activo
   - Usuario ve confianza, razones y condiciones de invalidación

2. **Análisis de Estrategias**
   - Usuario ejecuta backtests con diferentes parámetros
   - Sistema compara rendimientos y genera métricas
   - Usuario selecciona estrategia óptima

3. **Gestión de Datos**
   - Sistema importa datos automáticamente cada día
   - Usuario puede forzar actualización manual
   - Sistema valida calidad y notifica problemas

4. **Auditoría y Aprendizaje**
   - Usuario revisa historial de recomendaciones pasadas
   - Sistema muestra efectividad de decisiones previas
   - Usuario ajusta parámetros basándose en resultados

---

## Principios de Diseño

### 1. Claridad sobre Complejidad

**Decisión:** Priorizar recomendaciones claras y accionables sobre mostrar todos los detalles técnicos.

**Justificación:** El usuario no quiere ser un científico de datos, quiere saber qué hacer.

**Implementación:**
- Dashboard principal muestra solo: Acción + Confianza + Razón Principal
- Detalles técnicos disponibles en secciones avanzadas
- Lenguaje natural sin jerga financiera

### 2. Confiabilidad sobre Velocidad

**Decisión:** Garantizar que los datos y cálculos sean correctos antes de mostrar recomendaciones.

**Justificación:** Una recomendación errónea puede resultar en pérdidas financieras significativas.

**Implementación:**
- Triple validación de datos (formato, rango, coherencia)
- Backtests con múltiples periodos antes de activar estrategia
- Sistema de confianza con umbrales mínimos

### 3. Modularidad y Extensibilidad

**Decisión:** Arquitectura de microservicios/módulos independientes.

**Justificación:** Facilita agregar nuevas fuentes de datos, estrategias y activos sin rediseñar todo.

**Implementación:**
- Interfaces estándar para conectores, estrategias y recomendadores
- Comunicación a través de mensajes/eventos
- Hot-reload de estrategias sin reiniciar sistema

### 4. Observabilidad y Auditoría

**Decisión:** Registrar todas las decisiones y su razonamiento.

**Justificación:** Permite aprender de errores, cumplir regulaciones y ganar confianza del usuario.

**Implementación:**
- Log estructurado de cada recomendación con timestamp
- Trazabilidad desde dato original hasta decisión final
- Dashboard de métricas de efectividad histórica

---

## Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Web App)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Dashboard   │  │  Backtests   │  │   Config     │             │
│  │   Diario     │  │  Comparador  │  │  Estrategias │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼ REST/GraphQL API
┌─────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY / BFF                            │
│         (Rate Limiting, Auth, Request Routing)                       │
└─────────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  RECOMMENDATION  │  │   BACKTEST       │  │   DATA INGESTION │
│     ENGINE       │  │    ENGINE        │  │      SERVICE     │
│                  │  │                  │  │                  │
│ • Condensador    │  │ • Executor       │  │ • Connectors     │
│ • Decisor        │  │ • Evaluador      │  │ • Validator      │
│ • Explicador     │  │ • Comparador     │  │ • Scheduler      │
└──────────────────┘  └──────────────────┘  └──────────────────┘
           │                    │                    │
           └────────────────────┴────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │  Market    │  │  Backtest  │  │ Decisions  │  │  Metadata  │   │
│  │   Data     │  │  Results   │  │  History   │  │  & Config  │   │
│  │ TimeSeries │  │   Store    │  │   Store    │  │   Store    │   │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                             │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│   │ Binance  │   │  Kraken  │   │ CoinGecko│   │ Custom   │       │
│   │   API    │   │   API    │   │   API    │   │  Feeds   │       │
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Módulos del Sistema

### 1. Data Ingestion Service

**Responsabilidad:** Obtener, validar y almacenar datos de mercado.

**Componentes:**
- **Connectors:** Adaptadores para cada fuente de datos (Binance, Kraken, etc.)
- **Validator:** Pipeline de validación multi-nivel
- **Scheduler:** Cron jobs para actualizaciones automáticas
- **Cache Manager:** Gestión de datos en memoria para acceso rápido

**Interfaces:**

```python
class DataConnector(ABC):
    @abstractmethod
    async def fetch_ohlcv(self, symbol: str, timeframe: str, 
                          start: datetime, end: datetime) -> pd.DataFrame:
        """Fetch OHLCV data from source."""
        pass
    
    @abstractmethod
    async def fetch_latest(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Fetch only latest candles."""
        pass

class DataValidator:
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """Run all validation checks."""
        return ValidationResult(
            is_valid=bool,
            errors=List[str],
            warnings=List[str],
            metrics=Dict[str, Any]
        )
```

**Tecnologías:**
- Python 3.11+ con asyncio para concurrencia
- CCXT para exchanges crypto (unificado)
- Pandas para manipulación de datos
- Pydantic para validación de schemas

**Migración desde v2.0:**
- Reutilizar `one_trade/data_fetch.py` y `one_trade/data_store.py`
- Agregar validación más estricta
- Implementar retry logic y circuit breakers

---

### 2. Backtest Engine

**Responsabilidad:** Ejecutar simulaciones históricas de estrategias.

**Componentes:**
- **Strategy Framework:** Interfaz estándar para todas las estrategias
- **Executor:** Motor de simulación con soporte multi-activo
- **Metrics Calculator:** Cálculo de Sharpe, drawdown, expectancy, etc.
- **Comparator:** Análisis comparativo de resultados

**Interfaces:**

```python
class TradingStrategy(ABC):
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, index: int) -> Optional[Signal]:
        """Generate buy/sell signal at given index."""
        pass
    
    @abstractmethod
    def should_close(self, data: pd.DataFrame, index: int, 
                     position: Position) -> Tuple[bool, str]:
        """Determine if open position should be closed."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> StrategyMetadata:
        """Return strategy configuration and parameters."""
        pass

class BacktestResult:
    symbol: str
    strategy_name: str
    start_date: datetime
    end_date: datetime
    metrics: PerformanceMetrics
    trades: List[Trade]
    equity_curve: pd.DataFrame
    execution_time: float
```

**Optimizaciones:**
- Paralelización de backtests multi-activo con ProcessPoolExecutor
- Caché de indicadores técnicos precalculados
- Vectorización con NumPy para operaciones sobre series temporales

**Migración desde v2.0:**
- Aprovechar `one_trade/backtest.py` como base
- Extender con soporte multi-activo y multi-timeframe
- Agregar métricas avanzadas (heatmaps, correlaciones)

---

### 3. Recommendation Engine

**Responsabilidad:** Generar recomendación diaria basada en señales activas.

**Componentes:**

#### 3.1. Signal Condenser

Agrega señales de múltiples estrategias y fuentes.

```python
class SignalCondenser:
    def aggregate_signals(self, 
                         backtest_results: List[BacktestResult],
                         live_indicators: Dict[str, Any],
                         market_context: MarketContext) -> AggregatedSignal:
        """
        Combina:
        - Señales de estrategias validadas
        - Indicadores técnicos en tiempo real
        - Contexto de mercado (volatilidad, volumen, noticias)
        
        Returns: Señal agregada con pesos y confianza
        """
        pass

class AggregatedSignal:
    symbol: str
    timestamp: datetime
    direction: Literal['BUY', 'SELL', 'HOLD']
    strength: float  # 0-100
    contributing_signals: List[ContributingSignal]
    confidence: float  # 0-100
```

**Lógica de Agregación:**

1. **Filtro de Estrategias Activas:** Solo estrategias con performance positiva en últimos N días
2. **Ponderación:** Por Sharpe ratio, win rate y consistency
3. **Desempate:** Si señales contradictorias, usar estrategia con mejor track record reciente

#### 3.2. Decision Generator

Convierte señal agregada en recomendación accionable.

```python
class DecisionGenerator:
    def generate_decision(self, 
                         signal: AggregatedSignal,
                         current_position: Optional[Position],
                         risk_profile: RiskProfile) -> Decision:
        """
        Genera decisión considerando:
        - Señal agregada
        - Posición actual (si existe)
        - Perfil de riesgo del usuario
        - Condiciones de mercado
        """
        pass

class Decision:
    action: Literal['BUY', 'SELL', 'HOLD', 'REDUCE', 'INCREASE']
    confidence: float  # 0-100
    reasons: List[Reason]
    invalidation_conditions: List[Condition]
    suggested_sizing: Optional[float]  # % of capital
    expiry: datetime  # Cuándo re-evaluar
```

**Reglas de Decisión:**

| Señal | Posición Actual | Confianza | Acción Recomendada |
|-------|----------------|-----------|-------------------|
| BUY   | None           | >70%      | COMPRAR           |
| BUY   | None           | 50-70%    | MANTENER (esperar) |
| BUY   | Long           | >80%      | AUMENTAR posición  |
| SELL  | Long           | >70%      | VENDER            |
| SELL  | None           | >70%      | MANTENER fuera    |
| HOLD  | Any            | Any       | SIN CAMBIOS       |

#### 3.3. Explainability Module

Genera explicaciones en lenguaje natural.

```python
class Explainer:
    def explain(self, decision: Decision) -> Explanation:
        """
        Convierte decisión técnica en texto legible:
        
        "Te recomiendo COMPRAR BTC/USDT con confianza del 85%.
        
        Razones:
        • Estrategia Baseline detectó tendencia alcista (EMA 20 > EMA 50)
        • RSI en 42 (zona de sobreventa, favorable para compra)
        • Volumen incrementó 30% en últimas 24h
        • Backtest muestra 72% win rate en condiciones similares
        
        Condiciones de invalidación:
        ⚠️ Si precio cae por debajo de $65,000 (SL sugerido)
        ⚠️ Si RSI supera 80 (sobrecompra)
        
        Próxima revisión: Mañana a las 09:00 ART
        "
        """
        pass

class Explanation:
    title: str
    summary: str
    reasons: List[ReasonDetail]
    warnings: List[Warning]
    next_review: datetime
    confidence_breakdown: Dict[str, float]  # Por estrategia
```

**Migración desde v2.0:**
- **NUEVO MÓDULO:** No existe en v2.0, implementar desde cero
- Integrar con backtest existente para obtener señales
- Usar templates de texto con f-strings para explicaciones

---

### 4. API Gateway / BFF (Backend for Frontend)

**Responsabilidad:** Exponer endpoints unificados para el frontend.

**Endpoints Principales:**

```
GET  /api/v1/recommendations/daily
     → Recomendación del día para todos los activos

GET  /api/v1/recommendations/{symbol}/latest
     → Última recomendación para símbolo específico

GET  /api/v1/recommendations/history?symbol={symbol}&from={date}&to={date}
     → Historial de recomendaciones

POST /api/v1/backtests
     → Ejecutar nuevo backtest
     Body: { symbol, strategy, start_date, end_date, params }

GET  /api/v1/backtests/{id}
     → Obtener resultado de backtest

GET  /api/v1/backtests/compare?ids={id1},{id2},{id3}
     → Comparar múltiples backtests

POST /api/v1/data/refresh
     → Forzar actualización de datos

GET  /api/v1/data/status
     → Estado de datos disponibles

GET  /api/v1/strategies
     → Listar estrategias disponibles

GET  /api/v1/strategies/{name}/performance
     → Performance histórica de estrategia
```

**Tecnologías:**
- **Framework:** FastAPI (Python) o Express (Node.js)
- **Validación:** Pydantic models
- **Autenticación:** JWT tokens
- **Rate Limiting:** Redis con sliding window
- **Documentación:** OpenAPI/Swagger automática

**Ejemplo de Response:**

```json
{
  "status": "success",
  "data": {
    "symbol": "BTC/USDT",
    "timestamp": "2025-10-11T09:00:00Z",
    "decision": {
      "action": "BUY",
      "confidence": 85,
      "explanation": {
        "summary": "Tendencia alcista confirmada con múltiples indicadores",
        "reasons": [
          {
            "type": "TECHNICAL",
            "indicator": "EMA_CROSS",
            "detail": "EMA 20 cruzó por encima de EMA 50",
            "weight": 0.4
          },
          {
            "type": "MOMENTUM",
            "indicator": "RSI",
            "detail": "RSI en zona de sobreventa (42)",
            "weight": 0.3
          }
        ],
        "invalidation": [
          {
            "condition": "Precio < $65,000",
            "action": "EXIT_POSITION"
          }
        ]
      },
      "suggested_sizing": 0.05,
      "expiry": "2025-10-12T09:00:00Z"
    }
  }
}
```

---

### 5. Frontend (Web App)

**Responsabilidad:** Interfaz de usuario interactiva.

**Tecnologías Propuestas:**
- **Framework:** React 18+ con TypeScript
- **State Management:** Zustand o React Query
- **UI Components:** Shadcn/ui + Tailwind CSS
- **Charts:** Recharts o Apache ECharts
- **Build:** Vite

**Páginas Principales:**

#### 5.1. Dashboard Diario (`/`)

**Vista Principal:**
```
┌─────────────────────────────────────────────────────────┐
│  One Trade - Recomendación del Día          🔔 🌙 👤   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  🟢 COMPRAR BTC/USDT                             │  │
│  │                                                   │  │
│  │  Confianza: ████████░░ 85%                       │  │
│  │                                                   │  │
│  │  💡 Razón principal:                             │  │
│  │  Tendencia alcista confirmada. RSI en zona      │  │
│  │  favorable (42) y volumen creciente.            │  │
│  │                                                   │  │
│  │  📊 [Ver detalles] [Ver backtest] [Ejecutar]   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  🟡 MANTENER ETH/USDT                            │  │
│  │  Confianza: ███████░░░ 68%                      │  │
│  │  Señales contradictorias. Esperar confirmación. │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Actualizado: Hace 5 min | Próxima revisión: 09:00 ART │
└─────────────────────────────────────────────────────────┘
```

**Componentes:**
- `RecommendationCard`: Tarjeta por activo
- `ConfidenceMeter`: Visualización de confianza
- `ReasonsList`: Lista de razones
- `ActionButton`: CTA principal

#### 5.2. Backtest Comparator (`/backtests`)

- Tabla de backtests ejecutados
- Gráficos comparativos (equity curves, drawdowns)
- Heatmap de parámetros óptimos
- Filtros por periodo, estrategia, activo

#### 5.3. Data Status (`/data`)

- Estado de conexión a fuentes
- Última actualización por activo
- Gaps detectados
- Botón de refresh manual

#### 5.4. Configuración (`/settings`)

- Perfil de riesgo (conservador, moderado, agresivo)
- Activos a monitorear
- Notificaciones
- API keys (si es necesario)

**Migración desde v2.0:**
- Reutilizar componentes de `webapp_v2/interactive_app.py` como referencia
- Migrar de Dash a React para mejor UX y flexibilidad
- Mantener esquema de colores y branding

---

## Flujo de Datos

### 1. Flujo de Actualización Diaria (Automático)

```
[06:00 ART] Scheduler despierta
     │
     ▼
[Data Ingestion] Descarga datos nuevos
     │
     ├─→ [Validator] Valida calidad
     │        │
     │        ├─ ✅ OK → Almacena en DB
     │        └─ ❌ ERROR → Alerta + Retry
     │
     ▼
[Backtest Engine] Re-ejecuta estrategias con datos actualizados
     │
     ├─→ [Executor] Simula últimas 24h/7días/30días
     │        │
     │        └─→ [Metrics] Calcula performance
     │
     ▼
[Recommendation Engine] Genera decisión
     │
     ├─→ [Condenser] Agrega señales
     ├─→ [Generator] Crea decisión
     └─→ [Explainer] Genera explicación
     │
     ▼
[Notification Service] Notifica usuario (email/push)
     │
     ▼
[Cache] Almacena en Redis para acceso rápido
     │
     ▼
[Dashboard] Usuario consulta al abrir app
```

### 2. Flujo de Consulta Manual (Usuario)

```
[Usuario] Abre dashboard
     │
     ▼
[Frontend] Llama GET /api/v1/recommendations/daily
     │
     ▼
[API Gateway] Autentica y enruta
     │
     ▼
[Cache Check] ¿Existe en Redis?
     │
     ├─ ✅ Hit → Retorna cached (rápido, <50ms)
     │
     └─ ❌ Miss → [Recommendation Engine]
                       │
                       └─→ Genera on-demand
                       └─→ Cachea resultado
                       └─→ Retorna (lento, ~2s)
     │
     ▼
[Frontend] Renderiza cards
```

### 3. Flujo de Backtest Manual

```
[Usuario] Configura y lanza backtest
     │
     ▼
[Frontend] POST /api/v1/backtests
     │
     ▼
[API Gateway] Valida parámetros
     │
     ▼
[Job Queue] Encola tarea (Celery/RQ)
     │
     ▼
[Worker] Ejecuta backtest en background
     │
     ├─→ [Data Layer] Lee datos históricos
     ├─→ [Strategy] Aplica lógica
     ├─→ [Metrics] Calcula resultados
     │
     ▼
[Storage] Guarda resultado con ID
     │
     ▼
[WebSocket] Notifica frontend "Backtest completado"
     │
     ▼
[Frontend] Navega a /backtests/{id}
```

---

## Modelo de Datos

### Base de Datos Principal (PostgreSQL + TimescaleDB)

#### 1. Market Data (Time Series)

```sql
CREATE TABLE market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(30, 8) NOT NULL,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(symbol, timeframe, timestamp_utc)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('market_data', 'timestamp_utc');

-- Indexes
CREATE INDEX idx_market_data_symbol_time 
    ON market_data(symbol, timestamp_utc DESC);
```

#### 2. Backtest Results

```sql
CREATE TABLE backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_params JSONB,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    total_return DECIMAL(10, 4),
    total_return_pct DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    profit_factor DECIMAL(10, 4),
    win_rate DECIMAL(10, 4),
    execution_time_seconds DECIMAL(10, 2),
    equity_curve JSONB,
    trades JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE INDEX idx_backtest_symbol_strategy 
    ON backtest_results(symbol, strategy_name, created_at DESC);
```

#### 3. Decisions History

```sql
CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    action VARCHAR(20) NOT NULL, -- BUY, SELL, HOLD
    confidence DECIMAL(5, 2) NOT NULL, -- 0-100
    reasoning JSONB NOT NULL,
    contributing_signals JSONB,
    invalidation_conditions JSONB,
    suggested_sizing DECIMAL(5, 4),
    expiry TIMESTAMPTZ,
    backtest_references UUID[], -- Array de IDs
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_decisions_symbol_time 
    ON decisions(symbol, timestamp DESC);
```

#### 4. Strategy Metadata

```sql
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    version VARCHAR(20),
    parameters JSONB,
    is_active BOOLEAN DEFAULT true,
    author VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE strategy_performance (
    id BIGSERIAL PRIMARY KEY,
    strategy_id UUID REFERENCES strategies(id),
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    daily_return DECIMAL(10, 4),
    cumulative_return DECIMAL(10, 4),
    trades_count INTEGER,
    UNIQUE(strategy_id, symbol, date)
);
```

### Cache Layer (Redis)

```
Keys:
- recommendation:{symbol}:latest → JSON de última recomendación (TTL: 1h)
- backtest:{id}:result → Resultado de backtest (TTL: 7d)
- market_data:{symbol}:{timeframe}:latest → Última vela (TTL: 15m)
- user:{user_id}:settings → Configuración de usuario (TTL: 24h)

Structures:
- sorted_set: strategy_rankings:{symbol} → Ranking de estrategias por performance
- list: notification_queue → Cola de notificaciones pendientes
```

---

## Infraestructura y Despliegue

### Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────────────┐
│                    CLOUD (AWS/GCP)                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐     ┌─────────────────┐           │
│  │   Load Balancer │────▶│  Frontend CDN   │           │
│  │    (Nginx)      │     │  (CloudFront)   │           │
│  └─────────────────┘     └─────────────────┘           │
│          │                                               │
│          ▼                                               │
│  ┌─────────────────┐     ┌─────────────────┐           │
│  │  API Gateway    │────▶│  Redis Cluster  │           │
│  │  (FastAPI x3)   │     │    (Cache)      │           │
│  └─────────────────┘     └─────────────────┘           │
│          │                                               │
│          ├─────────────┬─────────────┐                  │
│          ▼             ▼             ▼                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   Data   │  │ Backtest │  │   Rec    │             │
│  │ Ingestion│  │  Engine  │  │  Engine  │             │
│  │ (x2)     │  │  (x4)    │  │  (x2)    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│          │             │             │                  │
│          └─────────────┴─────────────┘                  │
│                    │                                     │
│                    ▼                                     │
│  ┌──────────────────────────────────────┐              │
│  │      PostgreSQL + TimescaleDB        │              │
│  │         (Primary + Replica)          │              │
│  └──────────────────────────────────────┘              │
│                                                          │
│  ┌──────────────────────────────────────┐              │
│  │      Job Queue (Celery + RabbitMQ)   │              │
│  └──────────────────────────────────────┘              │
│                                                          │
│  ┌──────────────────────────────────────┐              │
│  │   Monitoring (Prometheus + Grafana)  │              │
│  └──────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

### Estrategia de Contenedorización (Docker)

```dockerfile
# Ejemplo: recommendation-engine/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run as non-root
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose (Desarrollo):**

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: onetrade
      POSTGRES_USER: onetrade
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./api
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://onetrade:${DB_PASSWORD}@postgres/onetrade
      REDIS_URL: redis://redis:6379
    ports:
      - "8000:8000"

  recommendation_engine:
    build: ./recommendation_engine
    depends_on:
      - postgres
      - redis

  worker:
    build: ./worker
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

### CI/CD Pipeline (GitHub Actions)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: onetrade/api:${{ github.sha }}

  deploy_staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - run: kubectl set image deployment/api api=onetrade/api:${{ github.sha }}
```

---

## Seguridad y Rendimiento

### Seguridad

#### 1. Autenticación y Autorización

- **JWT Tokens** con refresh tokens
- **RBAC**: Roles (Admin, User, Viewer)
- **API Keys** para integraciones externas
- **Rate Limiting**: 100 req/min por usuario, 1000 req/min por IP

#### 2. Protección de Datos

- **Encriptación en tránsito**: TLS 1.3
- **Encriptación en reposo**: Postgres con extensión pgcrypto
- **Secrets Management**: Hashicorp Vault o AWS Secrets Manager
- **Audit Logs**: Toda acción crítica registrada

#### 3. Validación de Inputs

```python
from pydantic import BaseModel, Field, validator

class BacktestRequest(BaseModel):
    symbol: str = Field(..., regex=r'^[A-Z]+/[A-Z]+$')
    strategy: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: date
    
    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
```

### Rendimiento

#### 1. Optimizaciones de Base de Datos

- **Particionamiento** de `market_data` por mes (TimescaleDB)
- **Indexes** optimizados para queries frecuentes
- **Connection Pooling** (PgBouncer)
- **Read Replicas** para queries analíticas

#### 2. Caché Strategy

```
Layer 1 (Redis): Datos hot (última hora)
Layer 2 (DB): Datos warm (último mes)
Layer 3 (Object Storage): Datos cold (histórico)
```

#### 3. Paralelización

```python
from concurrent.futures import ProcessPoolExecutor

def run_backtests_parallel(configs: List[BacktestConfig]) -> List[BacktestResult]:
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_backtest, config) for config in configs]
        return [f.result() for f in futures]
```

#### 4. Métricas de Performance

**SLOs (Service Level Objectives):**

| Métrica | Target | Medición |
|---------|--------|----------|
| API Latency (P95) | < 200ms | Prometheus |
| Backtest Duration | < 10s para 1 año | App logs |
| Data Update Lag | < 5 min | Monitoring |
| Dashboard Load | < 2s | Lighthouse |
| Uptime | > 99.5% | Pingdom |

---

## Próximos Pasos

1. **Validación:** Revisar este documento con stakeholders y ajustar según feedback
2. **Prototipo:** Implementar MVP del Recommendation Engine (Fase 3)
3. **Integración:** Conectar motor con backtest existente de One Trade v2.0
4. **Testing:** Validar con datos históricos y comparar con decisiones manuales
5. **Iteración:** Refinar explicaciones y umbrales de confianza

---

**Documento vivo**: Esta arquitectura evolucionará conforme avance la implementación.







