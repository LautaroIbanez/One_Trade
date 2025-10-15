# 📋 Product Backlog - One Trade Decision-Centric App

**Proyecto**: One Trade Decision-Centric App
**Timeline**: 12 Semanas
**Última Actualización**: Octubre 2025 - Día 2

---

## 📊 Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| **Total de User Stories** | 58 |
| **Story Points Totales** | ~220 puntos |
| **Fases** | 6 (0-5) |
| **Duración** | 12 semanas |
| **Prioridad Alta** | 18 items |
| **Prioridad Media** | 25 items |
| **Prioridad Baja** | 15 items |

---

## 🎯 Sistema de Estimación

| Tamaño | Story Points | Duración Estimada | Descripción |
|--------|-------------|-------------------|-------------|
| **XS** | 1 | 2-4 horas | Cambio trivial, config simple |
| **S** | 2 | 0.5-1 día | Feature pequeño, 1-2 archivos |
| **M** | 3 | 1-2 días | Feature mediano, múltiples archivos |
| **L** | 5 | 3-5 días | Feature complejo, módulo completo |
| **XL** | 8 | 1 semana | Epic, múltiples módulos |

---

## 📈 Prioridades

- **P0 (Crítico)**: Bloqueante, debe hacerse primero
- **P1 (Alto)**: Importante para MVP
- **P2 (Medio)**: Mejora significativa
- **P3 (Bajo)**: Nice to have, puede posponerse

---

# 🚀 FASE 0: Preparación y Setup (Semanas 1-2)

**Objetivo**: Completar infraestructura básica y validar PoCs

**Estado Actual**: 
- ✅ Documentación arquitectura completa
- ✅ PoC Recommendation Engine funcional
- ❌ Setup repos y CI/CD pendiente
- ❌ Prototipos UI/UX pendientes

## Epics de Fase 0

### Epic 0.1: Setup de Proyecto

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **SETUP-001** | Como dev, necesito repositorios separados para backend y frontend | - Repos creados en GitHub/GitLab<br>- README con setup instructions<br>- .gitignore configurado<br>- Branch protection rules | 2 | P0 | Ninguna |
| **SETUP-002** | Como dev, necesito Docker Compose con servicios básicos | - PostgreSQL 15<br>- Redis 7<br>- RabbitMQ 3.12<br>- PgAdmin (opcional)<br>- docker-compose.yml funcional | 3 | P0 | SETUP-001 |
| **SETUP-003** | Como dev, necesito CI/CD pipeline básico | - GitHub Actions o GitLab CI<br>- Lint en cada push<br>- Tests automáticos<br>- Build de Docker images | 5 | P1 | SETUP-001 |
| **SETUP-004** | Como dev, necesito estructura de proyecto backend | - FastAPI app inicializada<br>- Folder structure (routers, services, models)<br>- Alembic para migrations<br>- pytest configurado | 3 | P0 | SETUP-002 |
| **SETUP-005** | Como dev, necesito estructura de proyecto frontend | - React + Vite setup<br>- TypeScript configurado<br>- Tailwind CSS + Shadcn/ui<br>- React Router<br>- Zustand + React Query | 3 | P0 | SETUP-001 |
| **SETUP-006** | Como dev, necesito variables de entorno configuradas | - .env.example en ambos repos<br>- Secrets en CI/CD<br>- Config validation en startup | 1 | P1 | SETUP-004, SETUP-005 |

**Subtotal Fase 0.1**: 17 puntos

### Epic 0.2: Prototipos UI/UX

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **UX-001** | Como PM, necesito wireframes de dashboard principal | - Mockup de vista diaria<br>- Mockup de historial<br>- Mockup de configuración<br>- Figma o similar | 3 | P1 | Ninguna |
| **UX-002** | Como PM, necesito prototipo navegable | - Prototipo interactivo en Figma<br>- Flujo completo de usuario<br>- 3-5 pantallas principales | 5 | P2 | UX-001 |
| **UX-003** | Como dev, necesito design system definido | - Paleta de colores<br>- Tipografía<br>- Componentes base (botones, cards, inputs)<br>- Tokens CSS/Tailwind | 3 | P2 | UX-001 |

**Subtotal Fase 0.2**: 11 puntos

### Epic 0.3: Validación PoC Recommendation Engine

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **POC-001** | Como dev, necesito integrar PoC en estructura backend | - Código movido a backend/services/<br>- Adaptado a FastAPI<br>- Tests funcionando | 3 | P0 | SETUP-004 |
| **POC-002** | Como trader, necesito ver precisión del PoC con datos históricos | - Backtest de 1 año<br>- Win rate calculado<br>- Sharpe ratio de recomendaciones<br>- Reporte generado | 5 | P1 | POC-001 |
| **POC-003** | Como dev, necesito documentar hallazgos del PoC | - Documento con resultados<br>- Recomendaciones de mejora<br>- Ajustes necesarios identificados | 2 | P1 | POC-002 |

**Subtotal Fase 0.3**: 10 puntos

**TOTAL FASE 0**: 38 puntos (~2 semanas para 2 devs)

---

# 📥 FASE 1: Ingesta de Datos (Semanas 3-4)

**Objetivo**: Sistema robusto de ingesta y validación de datos multi-exchange

## Epics de Fase 1

### Epic 1.1: Conectores Multi-Exchange

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **DATA-001** | Como sistema, necesito conector asíncrono para Binance | - Cliente async con ccxt<br>- Manejo de rate limits<br>- Retry logic<br>- Logging detallado | 3 | P0 | SETUP-004 |
| **DATA-002** | Como sistema, necesito conector para Coinbase Pro | - Similar a DATA-001<br>- Normalización de datos<br>- Tests con datos reales | 3 | P2 | DATA-001 |
| **DATA-003** | Como sistema, necesito conector para Kraken | - Similar a DATA-001<br>- Handling de formatos específicos | 3 | P3 | DATA-001 |
| **DATA-004** | Como dev, necesito abstracción unificada de exchanges | - Interface ExchangeConnector<br>- Factory pattern<br>- Config por exchange en YAML | 2 | P0 | DATA-001 |
| **DATA-005** | Como sistema, necesito cache de API responses | - Redis para responses recientes<br>- TTL configurable<br>- Invalidación inteligente | 3 | P1 | DATA-001 |

**Subtotal Fase 1.1**: 14 puntos

### Epic 1.2: Pipeline de Validación

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **VAL-001** | Como sistema, necesito validación de schema | - Pydantic models para OHLCV<br>- Validación de tipos<br>- Rangos válidos (precio > 0, etc.) | 2 | P0 | DATA-004 |
| **VAL-002** | Como sistema, necesito detección de gaps temporales | - Identificar períodos faltantes<br>- Algoritmo de detección<br>- Logging de gaps | 3 | P1 | VAL-001 |
| **VAL-003** | Como sistema, necesito llenado de gaps | - Forward fill para gaps pequeños<br>- API fetch para gaps grandes<br>- Marcado de datos sintéticos | 5 | P1 | VAL-002 |
| **VAL-004** | Como sistema, necesito detección de anomalías | - Spikes de precio inverosímiles<br>- Volumen = 0<br>- Duplicados<br>- Alertas configurables | 3 | P1 | VAL-001 |
| **VAL-005** | Como usuario, necesito ver reporte de calidad de datos | - Dashboard en frontend<br>- Métricas: completeness, gaps, anomalías<br>- Por activo y timeframe | 3 | P2 | VAL-004 |

**Subtotal Fase 1.2**: 16 puntos

### Epic 1.3: Almacenamiento Optimizado

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **STORE-001** | Como sistema, necesito schema TimescaleDB para OHLCV | - Hypertable configurada<br>- Particiones por tiempo<br>- Índices optimizados<br>- Migration script | 3 | P0 | SETUP-002 |
| **STORE-002** | Como sistema, necesito compresión automática | - Compression policy para datos >1 mes<br>- Compresión configurada<br>- Verificación de espacio ahorrado | 2 | P1 | STORE-001 |
| **STORE-003** | Como sistema, necesito retención configurable | - Retention policy (ej: 5 años)<br>- Configurable por activo<br>- Cleanup automático | 2 | P2 | STORE-001 |
| **STORE-004** | Como dev, necesito ORM/query layer | - SQLAlchemy async<br>- Queries optimizadas para timeseries<br>- Helper functions (get_ohlcv, get_range) | 3 | P0 | STORE-001 |
| **STORE-005** | Como sistema, necesito backup automático | - Daily backup de PostgreSQL<br>- Storage en S3 o local<br>- Restauración testeada | 3 | P1 | STORE-001 |

**Subtotal Fase 1.3**: 13 puntos

### Epic 1.4: Scheduler y Jobs

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **JOB-001** | Como sistema, necesito Celery configurado | - Worker funcionando<br>- Beat scheduler<br>- Flower para monitoring (opcional) | 3 | P0 | SETUP-002 |
| **JOB-002** | Como sistema, necesito job de actualización diaria | - Fetch diario a las 00:05 UTC<br>- Para todos los activos configurados<br>- Retry en caso de fallo | 3 | P0 | JOB-001, DATA-004 |
| **JOB-003** | Como sistema, necesito job de validación post-ingesta | - Ejecuta pipeline de validación<br>- Envía alertas si problemas<br>- Logs estructurados | 2 | P1 | JOB-001, VAL-004 |
| **JOB-004** | Como admin, necesito trigger manual de ingesta | - API endpoint /api/data/ingest<br>- Parámetros: symbol, start_date, end_date<br>- Autenticación requerida | 2 | P1 | JOB-001 |

**Subtotal Fase 1.4**: 10 puntos

**TOTAL FASE 1**: 53 puntos (~2 semanas para 2 devs)

---

# ⚙️ FASE 2: Motor de Backtesting Mejorado (Semanas 5-6)

**Objetivo**: Refactorizar motor existente para multi-activo, multi-estrategia y performance

## Epics de Fase 2

### Epic 2.1: Refactoring del Motor

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **BT-001** | Como dev, necesito BacktestEngine async | - Convertir a async/await<br>- Compatible con FastAPI<br>- Tests de paridad con v2.0 | 5 | P0 | SETUP-004 |
| **BT-002** | Como trader, necesito backtest multi-activo simultáneo | - Ejecutar BTC, ETH, etc. en paralelo<br>- Aggregated portfolio metrics<br>- Correlaciones entre activos | 5 | P1 | BT-001 |
| **BT-003** | Como dev, necesito framework de estrategias extensible | - Base class Strategy con protocolo claro<br>- Plugin system para nuevas estrategias<br>- Registry de estrategias disponibles | 3 | P0 | BT-001 |
| **BT-004** | Como sistema, necesito cache de resultados de backtest | - Redis para resultados recientes<br>- Hash de parámetros como key<br>- Invalidación cuando cambian datos | 3 | P1 | BT-001, SETUP-002 |

**Subtotal Fase 2.1**: 16 puntos

### Epic 2.2: Métricas Avanzadas

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **METRIC-001** | Como trader, necesito métricas de riesgo avanzadas | - Sortino Ratio<br>- Calmar Ratio<br>- Maximum Adverse Excursion<br>- Profit Factor | 3 | P1 | BT-001 |
| **METRIC-002** | Como trader, necesito análisis de drawdown detallado | - Underwater plot<br>- Top 5 drawdowns<br>- Duración promedio<br>- Recovery time | 3 | P1 | METRIC-001 |
| **METRIC-003** | Como trader, necesito análisis de trades por condiciones | - Performance por día de semana<br>- Performance por hora<br>- Performance por régimen de mercado | 5 | P2 | BT-001 |
| **METRIC-004** | Como dev, necesito export de métricas a JSON/CSV | - Formato estándar<br>- Compatible con BI tools<br>- API endpoint | 2 | P1 | METRIC-001 |

**Subtotal Fase 2.2**: 13 puntos

### Epic 2.3: Comparador de Estrategias

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **COMP-001** | Como trader, necesito comparar múltiples estrategias visualmente | - Tabla comparativa de métricas<br>- Gráfico equity curves superpuestas<br>- Ranking automático | 5 | P1 | BT-003, METRIC-001 |
| **COMP-002** | Como trader, necesito tests estadísticos de diferencia | - t-test de returns<br>- p-value de significancia<br>- Interpretación en texto | 3 | P2 | COMP-001 |
| **COMP-003** | Como trader, necesito guardar comparaciones favoritas | - Guardar en DB<br>- Nombrar comparaciones<br>- Recuperar fácilmente | 2 | P2 | COMP-001 |

**Subtotal Fase 2.3**: 10 puntos

### Epic 2.4: Optimización de Parámetros

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **OPT-001** | Como trader, necesito grid search de parámetros | - Definir ranges de parámetros<br>- Ejecutar todas combinaciones<br>- Mostrar heatmap de resultados | 5 | P1 | BT-003 |
| **OPT-002** | Como trader, necesito walk-forward optimization | - Split en train/test<br>- Optimizar en train<br>- Validar en test<br>- Detección de overfitting | 8 | P2 | OPT-001 |
| **OPT-003** | Como trader, necesito optimización con algoritmos genéticos | - Implementar con DEAP o similar<br>- Fitness function configurable<br>- Exportar mejores individuos | 8 | P3 | OPT-001 |

**Subtotal Fase 2.4**: 21 puntos

**TOTAL FASE 2**: 60 puntos (~2 semanas para 2-3 devs)

---

# 🤖 FASE 3: Recommendation Engine a Producción (Semanas 7-8)

**Objetivo**: Convertir PoC en sistema productivo con más estrategias y optimizaciones

**Estado Actual**: PoC funcional con 2 estrategias (Current, Baseline)

## Epics de Fase 3

### Epic 3.1: Estrategias Adicionales

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **STRAT-001** | Como trader, necesito estrategia RSI pura | - RSI(14) con umbrales 30/70<br>- Tests unitarios<br>- Backtest validado | 2 | P1 | BT-003 |
| **STRAT-002** | Como trader, necesito estrategia Bollinger Bands | - BB(20, 2)<br>- Señales en toque de bandas<br>- Squeeze detection | 3 | P1 | STRAT-001 |
| **STRAT-003** | Como trader, necesito estrategia MACD Histogram | - MACD(12,26,9)<br>- Señales en cruce de 0<br>- Divergencias básicas | 3 | P1 | STRAT-001 |
| **STRAT-004** | Como trader, necesito estrategia Volume Profile | - VWAP<br>- Volume zones<br>- POC (Point of Control) | 5 | P2 | STRAT-001 |
| **STRAT-005** | Como trader, necesito estrategia Mean Reversion | - Z-score basado<br>- Señales extremas (-2/+2)<br>- Time decay | 3 | P2 | STRAT-001 |
| **STRAT-006** | Como trader, necesito estrategia Ichimoku Cloud | - Kumo, Tenkan, Kijun<br>- Señales en cruces<br>- Cloud breakouts | 5 | P2 | STRAT-001 |

**Subtotal Fase 3.1**: 21 puntos

### Epic 3.2: Optimización del Condenser

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **COND-001** | Como sistema, necesito pesos adaptativos por activo | - Tabla de pesos en DB<br>- Pesos diferentes BTC vs ETH<br>- Update vía API | 3 | P1 | STRAT-001 |
| **COND-002** | Como sistema, necesito detección de régimen de mercado | - Trending vs Ranging<br>- Alta/Baja volatilidad<br>- Ajustar pesos según régimen | 5 | P1 | COND-001 |
| **COND-003** | Como trader, necesito backtesting de combinaciones de pesos | - Grid search de pesos<br>- Encontrar óptimos<br>- Validación out-of-sample | 5 | P2 | COND-001 |
| **COND-004** | Como sistema, necesito ensemble voting mechanisms | - Majority voting<br>- Weighted voting<br>- Stacking de señales | 3 | P2 | COND-001 |

**Subtotal Fase 3.2**: 16 puntos

### Epic 3.3: Explicabilidad Mejorada

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **EXP-001** | Como trader, necesito desglose de contribución por estrategia | - Mostrar % de cada estrategia en decisión<br>- Visualización tipo treemap<br>- Detalle de señales | 3 | P1 | POC-001 |
| **EXP-002** | Como trader, necesito análisis técnico en explicación | - Mencionar niveles clave (soportes/resistencias)<br>- Indicadores actuales (RSI=45)<br>- Contexto de mercado | 3 | P1 | EXP-001 |
| **EXP-003** | Como trader, necesito histórico de precisión de estrategias | - Win rate por estrategia<br>- Últimos 30 días<br>- Badge de confianza | 3 | P2 | EXP-001 |
| **EXP-004** | Como trader, necesito alertas de cambio de recomendación | - Notificación si cambia BUY→SELL<br>- Email/Push/Telegram<br>- Configurable | 5 | P2 | EXP-001 |

**Subtotal Fase 3.3**: 14 puntos

### Epic 3.4: API y Persistencia

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **REC-001** | Como frontend, necesito API REST para recomendaciones | - GET /api/recommendations/latest/{symbol}<br>- GET /api/recommendations/history/{symbol}<br>- POST /api/recommendations/generate<br>- Documentado en Swagger | 3 | P0 | POC-001 |
| **REC-002** | Como sistema, necesito guardar recomendaciones en DB | - Tabla recommendations con schema<br>- Timestamp, symbol, action, confidence, reasoning<br>- Índices optimizados | 2 | P0 | REC-001 |
| **REC-003** | Como sistema, necesito job diario de generación | - Celery task a las 06:00 UTC<br>- Para todos los activos<br>- Notificaciones en caso de error | 2 | P0 | REC-001, JOB-001 |
| **REC-004** | Como trader, necesito API de feedback | - POST /api/recommendations/{id}/feedback<br>- Marcar útil/no útil<br>- Tracking de mejoras | 3 | P2 | REC-001 |

**Subtotal Fase 3.4**: 10 puntos

**TOTAL FASE 3**: 61 puntos (~2 semanas para 2-3 devs)

---

# 🎨 FASE 4: Dashboard y Frontend (Semanas 9-10)

**Objetivo**: Interfaz moderna y responsiva en React

## Epics de Fase 4

### Epic 4.1: Dashboard Principal

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **UI-001** | Como trader, necesito vista de recomendación diaria | - Card prominente con decisión<br>- Indicador de confianza visual<br>- Reasoning expandible<br>- Responsive | 5 | P0 | REC-001, UX-001 |
| **UI-002** | Como trader, necesito lista de activos seguidos | - Grid/List view<br>- Filtros (BUY/SELL/HOLD)<br>- Sort por confianza<br>- Quick actions | 3 | P0 | UI-001 |
| **UI-003** | Como trader, necesito gráfico de precio con señales | - Recharts o TradingView lightweight<br>- Overlay de recomendaciones históricas<br>- Indicadores técnicos | 8 | P1 | UI-001 |
| **UI-004** | Como trader, necesito widget de performance de recomendaciones | - Win rate últimos 30 días<br>- Profit simulado si se siguen<br>- Gráfico de tendencia | 5 | P1 | UI-001 |

**Subtotal Fase 4.1**: 21 puntos

### Epic 4.2: Historial y Análisis

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **HIST-001** | Como trader, necesito historial de recomendaciones | - Tabla con paginación<br>- Filtros por fecha, activo, action<br>- Export a CSV | 3 | P1 | REC-001 |
| **HIST-002** | Como trader, necesito ver resultado de recomendaciones pasadas | - Marcar aciertos/fallos<br>- % real de ganancia si se siguió<br>- Análisis de accuracy | 5 | P1 | HIST-001 |
| **HIST-003** | Como trader, necesito calendario de recomendaciones | - Calendar view<br>- Color coding por action<br>- Click para detalles | 5 | P2 | HIST-001 |

**Subtotal Fase 4.2**: 13 puntos

### Epic 4.3: Comparador de Backtests

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **BTUI-001** | Como trader, necesito interfaz de configuración de backtest | - Form con parámetros<br>- Selector de estrategia(s)<br>- Validación de inputs<br>- Preview de config | 5 | P1 | BT-001 |
| **BTUI-002** | Como trader, necesito visualización de resultados | - Equity curve chart<br>- Drawdown chart<br>- Tabla de métricas<br>- Trade timeline | 8 | P1 | BTUI-001, METRIC-001 |
| **BTUI-003** | Como trader, necesito comparar múltiples backtests | - Layout side-by-side o tabs<br>- Highlight diferencias<br>- Export comparación a PDF | 5 | P1 | BTUI-002, COMP-001 |
| **BTUI-004** | Como trader, necesito guardar configuraciones de backtest | - Save presets<br>- Load rápido<br>- Share via link | 3 | P2 | BTUI-001 |

**Subtotal Fase 4.3**: 21 puntos

### Epic 4.4: Configuración y Administración

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **ADMIN-001** | Como trader, necesito gestión de activos seguidos | - Add/remove símbolos<br>- Priorizar favoritos<br>- Guardar en backend | 3 | P1 | Ninguna |
| **ADMIN-002** | Como trader, necesito configurar notificaciones | - Toggles por tipo (email, push)<br>- Horarios preferidos<br>- Umbral de confianza mínimo | 3 | P1 | ADMIN-001 |
| **ADMIN-003** | Como trader, necesito configurar pesos de estrategias | - Sliders interactivos<br>- Reset a defaults<br>- Preview de impacto | 5 | P2 | COND-001 |
| **ADMIN-004** | Como admin, necesito panel de logs y health | - Logs recientes<br>- Status de jobs<br>- DB health metrics | 5 | P2 | JOB-001 |

**Subtotal Fase 4.4**: 16 puntos

### Epic 4.5: Autenticación y Usuarios

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **AUTH-001** | Como usuario, necesito registro y login | - Sign up form<br>- Login con JWT<br>- Password reset<br>- Email verification | 5 | P0 | SETUP-005 |
| **AUTH-002** | Como usuario, necesito perfil editable | - Update info<br>- Cambiar password<br>- Avatar upload (opcional) | 3 | P1 | AUTH-001 |
| **AUTH-003** | Como admin, necesito roles y permisos | - Admin vs User roles<br>- Protected routes<br>- API authorization | 5 | P2 | AUTH-001 |

**Subtotal Fase 4.5**: 13 puntos

**TOTAL FASE 4**: 84 puntos (~2-3 semanas para 2 frontend devs)

---

# 🔄 FASE 5: Automatización y QA (Semanas 11-12)

**Objetivo**: Jobs, monitoring, testing completo y deployment

## Epics de Fase 5

### Epic 5.1: Jobs Programados

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **AUTO-001** | Como sistema, necesito job de ingesta nocturna | - Ya implementado en JOB-002<br>- Validación y logging | 0 | P0 | JOB-002 |
| **AUTO-002** | Como sistema, necesito job de generación de recomendaciones | - Ya implementado en REC-003<br>- Con retry logic | 0 | P0 | REC-003 |
| **AUTO-003** | Como sistema, necesito job de cálculo de métricas de precisión | - Analizar recomendaciones pasadas<br>- Comparar con precio real<br>- Update accuracy metrics | 3 | P1 | REC-002 |
| **AUTO-004** | Como sistema, necesito job de backup diario | - DB backup<br>- Upload a S3 o storage<br>- Verificación de integridad | 3 | P1 | STORE-005 |
| **AUTO-005** | Como sistema, necesito job de cleanup de datos antiguos | - Borrar datos >5 años<br>- Según retention policy<br>- Con confirmación | 2 | P2 | STORE-003 |

**Subtotal Fase 5.1**: 8 puntos

### Epic 5.2: Monitoring y Observabilidad

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **MON-001** | Como DevOps, necesito Prometheus para métricas | - Exporter configurado<br>- Métricas custom (req/s, latency)<br>- Business metrics (recomendaciones/día) | 5 | P1 | SETUP-002 |
| **MON-002** | Como DevOps, necesito Grafana dashboards | - Dashboard de sistema<br>- Dashboard de negocio<br>- Alertas configuradas | 5 | P1 | MON-001 |
| **MON-003** | Como dev, necesito logging estructurado | - JSON logs<br>- Niveles apropiados<br>- Correlation IDs<br>- ELK stack (opcional) | 3 | P1 | SETUP-004 |
| **MON-004** | Como DevOps, necesito health checks | - /health endpoint<br>- Readiness probe<br>- Liveness probe<br>- DB connection check | 2 | P0 | SETUP-004 |
| **MON-005** | Como PM, necesito alertas de negocio | - Slack/Email si 0 recomendaciones generadas<br>- Si accuracy < 40%<br>- Si job falla 3x | 3 | P1 | MON-001 |

**Subtotal Fase 5.2**: 18 puntos

### Epic 5.3: Testing Completo

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **TEST-001** | Como dev, necesito >80% code coverage en backend | - Unit tests completos<br>- pytest-cov<br>- CI enforcement | 5 | P1 | Todas las fases |
| **TEST-002** | Como QA, necesito integration tests | - Tests de API completos<br>- Tests de jobs<br>- Tests de DB | 5 | P1 | TEST-001 |
| **TEST-003** | Como QA, necesito E2E tests en frontend | - Playwright o Cypress<br>- Critical user flows<br>- CI integration | 8 | P1 | UI-001 |
| **TEST-004** | Como dev, necesito load testing | - Locust o K6<br>- Simular 1000 usuarios<br>- Identificar bottlenecks | 5 | P2 | TEST-002 |
| **TEST-005** | Como QA, necesito tests de paridad con v2.0 | - Mismo input → mismo output<br>- Validar migración correcta<br>- Automated regression suite | 5 | P0 | BT-001 |

**Subtotal Fase 5.3**: 28 puntos

### Epic 5.4: Deployment y DevOps

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **DEPLOY-001** | Como DevOps, necesito Dockerfiles optimizados | - Multi-stage builds<br>- Minimal images (Alpine)<br>- Security scanning | 3 | P0 | SETUP-002 |
| **DEPLOY-002** | Como DevOps, necesito Kubernetes manifests | - Deployments<br>- Services<br>- Ingress<br>- ConfigMaps/Secrets | 5 | P1 | DEPLOY-001 |
| **DEPLOY-003** | Como DevOps, necesito CI/CD completo | - Build → Test → Deploy<br>- Staging environment<br>- Manual approval para prod | 5 | P1 | SETUP-003 |
| **DEPLOY-004** | Como DevOps, necesito estrategia de rollback | - Blue-green deployment<br>- Database migration rollback<br>- Documented procedure | 3 | P1 | DEPLOY-002 |
| **DEPLOY-005** | Como DevOps, necesito secrets management | - Vault o AWS Secrets Manager<br>- No secrets in code<br>- Rotation automática | 3 | P2 | DEPLOY-002 |

**Subtotal Fase 5.4**: 19 puntos

### Epic 5.5: Documentación Final

| ID | User Story | Criterios de Aceptación | Puntos | Prioridad | Dependencias |
|----|-----------|------------------------|--------|-----------|--------------|
| **DOC-001** | Como usuario, necesito guía de usuario completa | - Tutoriales paso a paso<br>- Screenshots<br>- FAQs<br>- Video (opcional) | 3 | P1 | UI-001 |
| **DOC-002** | Como dev, necesito API documentation actualizada | - Swagger/OpenAPI completo<br>- Ejemplos de uso<br>- Error codes | 2 | P1 | REC-001 |
| **DOC-003** | Como DevOps, necesito runbook operacional | - Common issues y soluciones<br>- Scaling procedures<br>- Disaster recovery | 3 | P1 | DEPLOY-001 |
| **DOC-004** | Como PM, necesito release notes | - Changelog detallado<br>- Migration guide desde v2.0<br>- Known issues | 2 | P1 | Todas las fases |

**Subtotal Fase 5.5**: 10 puntos

**TOTAL FASE 5**: 83 puntos (~2-3 semanas para 2-3 devs)

---

# 📊 Resumen de Story Points por Fase

| Fase | Nombre | Story Points | Duración Estimada | Team Size |
|------|--------|-------------|-------------------|-----------|
| **0** | Preparación y Setup | 38 | 2 semanas | 2 devs |
| **1** | Ingesta de Datos | 53 | 2 semanas | 2 devs |
| **2** | Motor de Backtesting | 60 | 2 semanas | 2-3 devs |
| **3** | Recommendation Engine | 61 | 2 semanas | 2-3 devs |
| **4** | Dashboard y Frontend | 84 | 2-3 semanas | 2 frontend devs |
| **5** | Automatización y QA | 83 | 2-3 semanas | 2-3 devs |
| **TOTAL** | | **379 puntos** | **12-14 semanas** | **2-3 devs** |

---

# 🎯 Priorización Global

## Must Have (MVP)

Estos items son **críticos** para un MVP funcional:

- ✅ SETUP-001 a SETUP-006 (Infraestructura básica)
- ✅ DATA-001, DATA-004, VAL-001 (Ingesta básica de Binance)
- ✅ STORE-001, STORE-004 (Almacenamiento funcional)
- ✅ BT-001, BT-003 (Motor de backtest refactorizado)
- ✅ STRAT-001 a STRAT-003 (3-4 estrategias básicas)
- ✅ REC-001 a REC-003 (API y persistencia de recomendaciones)
- ✅ UI-001, UI-002 (Dashboard básico)
- ✅ AUTH-001 (Login básico)
- ✅ TEST-001, TEST-005 (Testing básico)
- ✅ DEPLOY-001, DEPLOY-003 (Deployment funcional)

**Total MVP**: ~120 puntos (~6 semanas con 2 devs)

## Should Have (Full Product)

Mejoras importantes pero no bloqueantes:

- METRIC-001 a METRIC-004 (Métricas avanzadas)
- COMP-001 (Comparador visual)
- EXP-001 a EXP-003 (Explicabilidad mejorada)
- BTUI-001 a BTUI-003 (UI de backtesting)
- MON-001 a MON-003 (Monitoring completo)

## Could Have (Nice to Have)

Features deseables pero posponibles:

- OPT-002, OPT-003 (Optimización avanzada)
- STRAT-004 a STRAT-006 (Estrategias adicionales)
- UX-002, UX-003 (Design system completo)
- TEST-004 (Load testing)
- DEPLOY-005 (Secrets management avanzado)

---

# 🔗 Dependencias Críticas

## Bloqueadores de Path Crítico

Estos items bloquean múltiples tareas si no se completan:

1. **SETUP-001** (Repos) → Bloquea TODO
2. **SETUP-002** (Docker Compose) → Bloquea DATA, BT, REC, JOB
3. **SETUP-004** (Backend structure) → Bloquea toda lógica de negocio
4. **DATA-004** (Abstracción exchanges) → Bloquea ingesta avanzada
5. **BT-001** (BacktestEngine async) → Bloquea Fase 2 y 3
6. **REC-001** (API) → Bloquea todo el frontend

## Diagrama de Dependencias (Simplificado)

```
SETUP-001 (Repos)
    ├─► SETUP-002 (Docker)
    │       ├─► DATA-001 (Connectors)
    │       ├─► STORE-001 (TimescaleDB)
    │       └─► JOB-001 (Celery)
    │
    ├─► SETUP-004 (Backend)
    │       ├─► BT-001 (Backtest async)
    │       │       ├─► BT-003 (Strategies framework)
    │       │       └─► METRIC-001 (Metrics)
    │       │
    │       ├─► REC-001 (API)
    │       │       └─► UI-001 (Dashboard)
    │       │
    │       └─► AUTH-001 (Login)
    │
    └─► SETUP-005 (Frontend)
            └─► UI-001 (Dashboard)
```

---

# 📅 Sprint Planning Sugerido

## Sprint 1 (Semana 1-2): Foundation

**Goal**: Infraestructura lista para desarrollo

**Tasks**:
- SETUP-001 a SETUP-006
- POC-001 (Migrar PoC)
- UX-001 (Wireframes básicos)

**Deliverable**: Repos configurados, CI/CD básico, PoC integrado

---

## Sprint 2 (Semana 3-4): Data Pipeline

**Goal**: Ingesta y validación de datos funcionando

**Tasks**:
- DATA-001, DATA-004, DATA-005
- VAL-001, VAL-002, VAL-003
- STORE-001, STORE-004
- JOB-001, JOB-002

**Deliverable**: Pipeline de datos end-to-end

---

## Sprint 3 (Semana 5-6): Backtest Engine

**Goal**: Motor de backtesting refactorizado

**Tasks**:
- BT-001, BT-002, BT-003, BT-004
- METRIC-001, METRIC-002, METRIC-004
- COMP-001

**Deliverable**: Backtest multi-activo con métricas

---

## Sprint 4 (Semana 7-8): Recommendation Engine

**Goal**: Sistema de recomendaciones en producción

**Tasks**:
- STRAT-001 a STRAT-003
- COND-001, COND-002
- EXP-001, EXP-002
- REC-001 a REC-003

**Deliverable**: Recomendaciones diarias automáticas

---

## Sprint 5 (Semana 9-10): Frontend MVP

**Goal**: Dashboard funcional

**Tasks**:
- AUTH-001
- UI-001, UI-002, UI-003
- HIST-001, HIST-002
- ADMIN-001, ADMIN-002

**Deliverable**: Usuario puede ver recomendaciones diarias

---

## Sprint 6 (Semana 11-12): QA y Deploy

**Goal**: Sistema en producción

**Tasks**:
- TEST-001 a TEST-003, TEST-005
- MON-001 a MON-004
- DEPLOY-001 a DEPLOY-003
- DOC-001 a DOC-004

**Deliverable**: Sistema deployed y monitoreado

---

# 📈 Tracking y Métricas

## Velocity Esperada

Asumiendo team de 2 devs:
- Velocity por sprint (2 semanas): ~30-40 puntos
- Total: 379 puntos ≈ 10-12 sprints

## Métricas de Progreso

| Métrica | Cálculo | Target |
|---------|---------|--------|
| **Burndown** | Story points restantes vs tiempo | Linear downward |
| **Completion Rate** | Tasks completadas / Total tasks | 100% en 12 semanas |
| **Blocked Items** | Tasks bloqueadas > 3 días | < 5% |
| **Bug Rate** | Bugs encontrados / Story points | < 0.2 bugs/punto |
| **Code Coverage** | Lines covered / Total lines | > 80% |

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Scope creep | Alta | Alto | Strict priorización, MVP primero |
| API externa falla | Media | Alto | Retry logic, fallbacks, cache |
| Performance issues | Media | Medio | Load testing early, optimización continua |
| Team cambios | Baja | Alto | Documentación exhaustiva, pair programming |
| Data quality | Alta | Alto | Pipeline de validación robusto |

---

# 🚀 Cómo Usar Este Backlog

## Para Product Manager

1. **Priorizar**: Revisar P0/P1/P2 y ajustar según negocio
2. **Roadmap**: Usar fases como milestones
3. **Stakeholders**: Comunicar progreso por fase completada

## Para Tech Lead

1. **Sprint Planning**: Seleccionar tasks según dependencias
2. **Asignación**: Distribuir según expertise (backend/frontend)
3. **Code Review**: Usar criterios de aceptación como checklist

## Para Developers

1. **Pick Task**: Elegir según prioridad y dependencias
2. **Implementar**: Seguir criterios de aceptación
3. **Update**: Mover a "Done" y actualizar documentación

## Para QA

1. **Test Cases**: Crear desde criterios de aceptación
2. **Regression**: Usar TEST-005 como baseline
3. **E2E**: Implementar TEST-003 para flujos críticos

---

# 📝 Convenciones

## Estado de Tasks

- **TODO**: No iniciada
- **IN PROGRESS**: En desarrollo
- **IN REVIEW**: En code review
- **BLOCKED**: Esperando dependencia
- **DONE**: Completada y en main

## Naming de Branches

```
feature/SETUP-001-create-repos
bugfix/REC-003-job-timezone
hotfix/DEPLOY-001-security-patch
```

## Commits

```
[SETUP-001] Add GitHub repos with CI/CD config

- Created backend and frontend repos
- Added GitHub Actions workflows
- Configured branch protection
```

---

# 🎉 Milestones

| Milestone | Criterio de Éxito | Fecha Target |
|-----------|-------------------|--------------|
| **M0: Foundation Ready** | Repos + CI/CD + Docker funcionando | Fin Semana 2 |
| **M1: Data Pipeline Live** | Ingesta automática funcionando | Fin Semana 4 |
| **M2: Backtest Refactored** | Motor async con nuevas métricas | Fin Semana 6 |
| **M3: Recommendations Auto** | Recomendaciones diarias generadas | Fin Semana 8 |
| **M4: Dashboard Live** | Frontend funcional con auth | Fin Semana 10 |
| **M5: Production Ready** | Sistema deployed y monitoreado | Fin Semana 12 |

---

# ✅ Checklist de Go-Live

Antes de lanzar a producción, verificar:

- [ ] Todos los P0 y P1 completados
- [ ] Code coverage > 80%
- [ ] E2E tests pasando
- [ ] Load testing completado
- [ ] Monitoring configurado
- [ ] Alertas funcionando
- [ ] Backups automáticos activos
- [ ] Rollback plan documentado
- [ ] Security audit completado
- [ ] User documentation lista
- [ ] Runbook operacional completo
- [ ] Stakeholders aprobaron demo

---

**Última Actualización**: Octubre 2025 - Día 2
**Mantenedor**: Product & Tech Team
**Próxima Revisión**: Fin de Sprint 1

---

*Este backlog es un documento vivo. Actualizar conforme avanza el proyecto.*



