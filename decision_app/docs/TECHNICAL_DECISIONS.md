# Decisiones Técnicas - One Trade Decision-Centric App

Este documento registra las decisiones técnicas clave tomadas durante el diseño del sistema, siguiendo el formato ADR (Architecture Decision Record).

---

## Índice de Decisiones

1. [Stack de Backend: Python con FastAPI](#decision-1-stack-de-backend)
2. [Base de Datos: PostgreSQL + TimescaleDB](#decision-2-base-de-datos)
3. [Frontend: React + TypeScript](#decision-3-frontend)
4. [Cache Layer: Redis](#decision-4-cache-layer)
5. [Job Queue: Celery + RabbitMQ](#decision-5-job-queue)
6. [Arquitectura: Microservicios Modulares](#decision-6-arquitectura)
7. [Autenticación: JWT](#decision-7-autenticacion)
8. [Despliegue: Docker + Kubernetes](#decision-8-despliegue)

---

## Decision #1: Stack de Backend

### Contexto

Necesitamos un framework de backend para exponer APIs REST/GraphQL, ejecutar backtests y generar recomendaciones.

### Opciones Consideradas

**A. Python + FastAPI**
- ✅ Reutiliza código existente de One Trade v2.0
- ✅ Excelente para data science (pandas, numpy, scipy)
- ✅ FastAPI es rápido (basado en Starlette/Pydantic)
- ✅ Type hints nativos con Pydantic
- ⚠️ GIL puede ser limitante en CPU-bound tasks

**B. Node.js + Express/NestJS**
- ✅ Excelente para I/O asíncrono
- ✅ Mismo lenguaje que frontend (full-stack JS)
- ❌ Débil en cálculos numéricos comparado con Python
- ❌ Requiere reescribir todo el código existente

**C. Go**
- ✅ Performance excepcional
- ✅ Concurrencia nativa con goroutines
- ❌ Ecosistema de data science inmaduro
- ❌ Curva de aprendizaje para el equipo
- ❌ Reescritura completa necesaria

### Decisión

**Elegido: Python + FastAPI**

### Justificación

1. **Reutilización de código**: One Trade v2.0 ya tiene ~3000 líneas de Python testeado
2. **Ecosistema científico**: NumPy, Pandas, TA-Lib para trading
3. **Productividad**: Desarrollo rápido con type hints y validación automática
4. **Performance aceptable**: Con caché y async, FastAPI maneja >10k req/s
5. **GIL mitigation**: Usar ProcessPoolExecutor para backtests CPU-bound

### Consecuencias

**Positivas:**
- Velocidad de desarrollo alta
- Código existente aprovechable
- Fácil encontrar talento Python

**Negativas:**
- GIL requiere arquitectura cuidadosa para paralelismo
- Mayor consumo de memoria vs Go/Rust

### Mitigación de Riesgos

- Backtests largos en workers separados (Celery)
- Profiling con cProfile para identificar bottlenecks
- Considerar Cython para hot paths si es necesario

---

## Decision #2: Base de Datos

### Contexto

Necesitamos almacenar:
- Series temporales de mercado (alta escritura)
- Resultados de backtests (queries analíticas)
- Historial de decisiones (auditoría)
- Metadatos de estrategias

### Opciones Consideradas

**A. PostgreSQL + TimescaleDB**
- ✅ TimescaleDB optimizado para time-series
- ✅ Soporte nativo de JSON (JSONB)
- ✅ Maduro, battle-tested, excelente tooling
- ✅ Compresión automática de datos históricos
- ⚠️ Puede requerir tuning para alta carga

**B. MongoDB**
- ✅ Schema flexible
- ✅ Buen soporte de time-series (desde v5.0)
- ❌ Joins menos eficientes
- ❌ Transacciones ACID más limitadas
- ❌ Complejidad en queries analíticas

**C. ClickHouse**
- ✅ Performance extremo en queries analíticas
- ✅ Compresión excelente
- ❌ Overkill para nuestro volumen actual
- ❌ No es OLTP, solo OLAP
- ❌ Curva de aprendizaje empinada

**D. InfluxDB**
- ✅ Diseñado específicamente para time-series
- ❌ Débil en queries relacionales
- ❌ Ecosistema más pequeño
- ❌ Clustering solo en versión enterprise

### Decisión

**Elegido: PostgreSQL 15 + TimescaleDB 2.x**

### Justificación

1. **Balance perfecto**: ACID + time-series optimization
2. **Ecosistema maduro**: PgAdmin, pg_stat_statements, extensions
3. **Compresión inteligente**: TimescaleDB comprime automáticamente datos viejos
4. **Flexibilidad**: JSONB para datos semi-estructurados
5. **Costos**: Open source, sin licensing

### Implementación

```sql
-- Ejemplo de configuración
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE market_data (
    timestamp_utc TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    ...
);

-- Convert to hypertable
SELECT create_hypertable('market_data', 'timestamp_utc',
    chunk_time_interval => INTERVAL '7 days'
);

-- Compression policy (after 30 days)
SELECT add_compression_policy('market_data', INTERVAL '30 days');

-- Retention policy (keep 2 years)
SELECT add_retention_policy('market_data', INTERVAL '2 years');
```

### Consecuencias

**Positivas:**
- Queries rápidas con continuous aggregates
- Backup/restore estándar con pg_dump
- Compatible con ORMs (SQLAlchemy)

**Negativas:**
- Requiere tuning de `shared_buffers`, `work_mem`
- Backups grandes si no se usan compression policies

---

## Decision #3: Frontend

### Contexto

Necesitamos un dashboard interactivo, responsive, con gráficos en tiempo real.

### Opciones Consideradas

**A. React + TypeScript**
- ✅ Ecosistema enorme, cualquier componente existe
- ✅ Type safety con TypeScript
- ✅ Hooks modernos para state management
- ⚠️ Bundle size puede crecer

**B. Vue.js 3 + TypeScript**
- ✅ Más simple que React
- ✅ Performance ligeramente mejor
- ❌ Ecosistema más pequeño
- ❌ Menos talento disponible

**C. Svelte**
- ✅ Performance excelente (compilado, no runtime)
- ✅ Código muy limpio
- ❌ Ecosistema joven
- ❌ Menos componentes pre-hechos
- ❌ Riesgo de adopción

**D. Dash (Python) - Actual de v2.0**
- ✅ Backend y frontend en Python
- ❌ Limitado para UX compleja
- ❌ Menos flexible que React
- ❌ Difícil customizar

### Decisión

**Elegido: React 18 + TypeScript + Vite**

### Justificación

1. **Madurez**: Battle-tested en miles de apps
2. **Talento**: Fácil contratar React developers
3. **Componentes**: Shadcn/ui + Tailwind = UI moderna sin esfuerzo
4. **Type Safety**: TypeScript previene bugs
5. **Tooling**: Vite = builds rápidos, HMR instantáneo

### Stack Completo

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.2.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.4.0",
    "recharts": "^2.8.0",
    "date-fns": "^2.30.0",
    "axios": "^1.5.0"
  },
  "devDependencies": {
    "vite": "^4.5.0",
    "@vitejs/plugin-react": "^4.1.0",
    "tailwindcss": "^3.3.0",
    "eslint": "^8.50.0",
    "prettier": "^3.0.0"
  }
}
```

### Consecuencias

**Positivas:**
- Desarrollo rápido con componentes reutilizables
- Excelente developer experience
- Fácil encontrar soluciones a problemas

**Negativas:**
- Bundle size inicial ~200KB (mitigable con code splitting)
- Complejidad en state management si no se estructura bien

### Mitigación

- **Code splitting** por rutas con React.lazy()
- **Tree shaking** automático con Vite
- **Memoization** con useMemo/useCallback para re-renders
- **React Query** para evitar prop drilling

---

## Decision #4: Cache Layer

### Contexto

Necesitamos reducir latencia de API y carga en base de datos para datos consultados frecuentemente.

### Opciones Consideradas

**A. Redis**
- ✅ In-memory, extremadamente rápido (<1ms)
- ✅ Estructuras de datos ricas (hashes, sorted sets, streams)
- ✅ Pub/Sub para notificaciones
- ✅ Persistencia opcional (RDB + AOF)
- ⚠️ Requiere memoria RAM proporcional al dataset

**B. Memcached**
- ✅ Simple, muy rápido
- ❌ Solo key-value string
- ❌ Sin persistencia
- ❌ Menos features que Redis

**C. Varnish**
- ✅ Excelente para HTTP caching
- ❌ Overkill para nuestra use case
- ❌ Menos flexible que Redis

### Decisión

**Elegido: Redis 7.x**

### Justificación

1. **Versatilidad**: Sirve como cache, pub/sub, job queue
2. **Performance**: Sub-millisecond latency
3. **Estructuras ricas**: Sorted sets para rankings, hashes para objetos
4. **Clustering**: Redis Cluster para escalar horizontalmente
5. **Ecosistema**: Excelentes clientes en Python (redis-py, aioredis)

### Estrategia de Cache

```python
# Patrón Cache-Aside
async def get_recommendation(symbol: str) -> Recommendation:
    # 1. Check cache
    cached = await redis.get(f"recommendation:{symbol}:latest")
    if cached:
        return Recommendation.parse_raw(cached)
    
    # 2. Miss: Generate from scratch
    rec = await generate_recommendation(symbol)
    
    # 3. Store in cache (TTL 1 hour)
    await redis.setex(
        f"recommendation:{symbol}:latest",
        3600,
        rec.json()
    )
    
    return rec
```

### Políticas de Invalidación

| Dato | TTL | Invalidación Manual |
|------|-----|---------------------|
| Recomendación latest | 1h | Cuando llega dato nuevo |
| Backtest result | 7d | Nunca (inmutable) |
| Market data latest | 15m | Cada candle |
| User settings | 24h | On update |

### Consecuencias

**Positivas:**
- API responses <50ms para hits
- Reducción de 80%+ en queries a DB
- Pub/Sub para actualizaciones en tiempo real

**Negativas:**
- Complejidad de invalidación (cache coherence)
- Memoria RAM requerida (~4GB para nuestro caso)
- Necesidad de monitoreo (hit rate, evictions)

---

## Decision #5: Job Queue

### Contexto

Backtests largos no pueden ejecutarse sincrónicamente en requests HTTP (timeout). Necesitamos procesamiento asíncrono.

### Opciones Consideradas

**A. Celery + RabbitMQ**
- ✅ Maduro, usado por miles de companies
- ✅ Soporte de workflows complejos
- ✅ Retry, rate limiting, schedules
- ⚠️ Setup complejo (broker + backend)

**B. Celery + Redis**
- ✅ Menos componentes (Redis es broker y backend)
- ⚠️ Redis no es tan robusto como RabbitMQ para queues
- ⚠️ Posible pérdida de mensajes si Redis crashea

**C. RQ (Redis Queue)**
- ✅ Más simple que Celery
- ✅ Integración nativa con Redis
- ❌ Menos features (no workflows complejos)
- ❌ Menor comunidad

**D. AWS SQS + Lambda**
- ✅ Serverless, escalado automático
- ❌ Vendor lock-in
- ❌ Cold start latency
- ❌ Costos impredecibles

### Decisión

**Elegido: Celery 5.x + RabbitMQ 3.x**

### Justificación

1. **Confiabilidad**: RabbitMQ garantiza delivery de mensajes
2. **Features**: Chains, groups, chords para workflows
3. **Monitoring**: Flower dashboard out-of-the-box
4. **Escalabilidad**: Workers horizontalmente escalables
5. **Python-native**: Integración perfecta con FastAPI

### Ejemplo de Implementación

```python
# tasks.py
from celery import Celery

app = Celery('onetrade',
             broker='amqp://localhost',
             backend='redis://localhost')

@app.task(bind=True, max_retries=3)
def run_backtest_task(self, config: dict):
    try:
        result = execute_backtest(config)
        return result
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

# main.py (FastAPI)
@app.post("/api/v1/backtests")
async def create_backtest(config: BacktestConfig):
    task = run_backtest_task.delay(config.dict())
    return {"task_id": task.id, "status": "PENDING"}

@app.get("/api/v1/backtests/{task_id}")
async def get_backtest_status(task_id: str):
    task = AsyncResult(task_id)
    return {
        "status": task.state,
        "result": task.result if task.ready() else None
    }
```

### Consecuencias

**Positivas:**
- Backtests no bloquean requests
- Auto-retry en fallos transitorios
- Fácil escalar agregando workers

**Negativas:**
- Complejidad operacional (más servicios)
- Necesidad de monitoring (queue length, worker health)

---

## Decision #6: Arquitectura

### Contexto

¿Monolito vs Microservicios vs Modulith?

### Opciones Consideradas

**A. Monolito**
- ✅ Simple deploy
- ✅ Fácil debug
- ❌ No escala independientemente
- ❌ Un bug tira todo

**B. Microservicios puros**
- ✅ Escalado independiente
- ✅ Tecnologías mixtas
- ❌ Complejidad operacional alta
- ❌ Latencia de red entre servicios
- ❌ Overkill para MVP

**C. Modulith (Monolito Modular)**
- ✅ Módulos bien definidos
- ✅ Deploy simple
- ✅ Puede evolucionar a microservicios
- ⚠️ Requiere disciplina de boundaries

### Decisión

**Elegido: Modulith con path a Microservicios**

### Justificación

1. **Start simple**: MVP como monolito modular
2. **Bounded contexts**: Módulos con interfaces claras
3. **Evolutionary**: Extraer servicios cuando sea necesario
4. **Productividad**: Deploy y debug más rápidos

### Estructura de Módulos

```
onetrade/
├── api/                    # FastAPI app
│   ├── routers/            # Endpoints agrupados
│   └── dependencies.py     # Auth, DB connections
├── core/
│   ├── data_ingestion/     # Módulo 1
│   │   ├── connectors/
│   │   ├── validators/
│   │   └── interface.py    # Public API
│   ├── backtest/           # Módulo 2
│   │   ├── executor/
│   │   ├── strategies/
│   │   └── interface.py
│   ├── recommendation/     # Módulo 3
│   │   ├── condenser/
│   │   ├── generator/
│   │   └── interface.py
│   └── shared/             # Utils compartidos
│       ├── models.py
│       └── utils.py
├── workers/                # Celery tasks
└── tests/
```

**Reglas de Comunicación:**
- Módulos se comunican solo a través de interfaces públicas
- Sin imports directos de internals
- Eventos para comunicación asíncrona

### Migración Futura

Cuando sea necesario (>100k usuarios):
1. Extraer `recommendation/` a servicio independiente
2. Extraer `backtest/` a servicio con auto-scaling
3. `data_ingestion/` permanece acoplado (menos tráfico)

---

## Decision #7: Autenticación

### Contexto

Usuarios necesitan autenticarse para acceder a la app y sus datos.

### Opciones Consideradas

**A. JWT (JSON Web Tokens)**
- ✅ Stateless, escalable
- ✅ Standard (RFC 7519)
- ⚠️ No revocable fácilmente

**B. Session-based (cookies)**
- ✅ Revocación simple
- ❌ Stateful, requiere sesión en server
- ❌ No funciona bien con mobile

**C. OAuth 2.0 (terceros)**
- ✅ "Login with Google/GitHub"
- ❌ Dependencia de terceros
- ❌ Overkill para MVP

### Decisión

**Elegido: JWT con Refresh Tokens**

### Justificación

1. **Stateless**: API no necesita sesión
2. **Mobile-friendly**: Token en header
3. **Escalable**: Sin servidor de sesiones
4. **Revocation**: Refresh tokens en DB (blacklist)

### Implementación

```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"  # From env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    token_id = uuid4()
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
        "jti": str(token_id)
    }
    # Store token_id in DB for revocation
    store_refresh_token(user_id, token_id)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

### Flujo de Autenticación

```
1. Login → Access Token (15min) + Refresh Token (30d)
2. API calls → Enviar Access Token en header
3. Access Token expira → Usar Refresh Token para obtener nuevo Access Token
4. Logout → Blacklist Refresh Token en DB
```

### Consecuencias

**Positivas:**
- No state en API (escalable)
- Tokens autocontenidos (info en payload)

**Negativas:**
- Access tokens no revocables (mitigado con TTL corto)
- Necesidad de DB para refresh tokens

---

## Decision #8: Despliegue

### Contexto

¿Cómo deployar la aplicación en producción?

### Opciones Consideradas

**A. Docker + Kubernetes**
- ✅ Orquestación automática
- ✅ Auto-scaling
- ✅ Rolling updates sin downtime
- ⚠️ Complejidad operacional

**B. Docker Compose**
- ✅ Simple para apps pequeñas
- ❌ No escala automáticamente
- ❌ Single point of failure

**C. Serverless (AWS Lambda + API Gateway)**
- ✅ Zero ops, auto-scaling
- ❌ Vendor lock-in
- ❌ Cold starts
- ❌ Difícil para backtests largos

**D. VPS tradicional (sin containers)**
- ✅ Simple
- ❌ Difícil replicar entornos
- ❌ Deployment manual

### Decisión

**Elegido: Docker + Kubernetes (para producción)**

**Desarrollo local: Docker Compose**

### Justificación

1. **Portabilidad**: Mismo container en dev/staging/prod
2. **Escalabilidad**: K8s auto-scale basado en CPU/memoria
3. **Resiliencia**: Self-healing, auto-restart
4. **Observabilidad**: Integración con Prometheus/Grafana
5. **Industry standard**: Kubernetes es el estándar de facto

### Kubernetes Manifests (Ejemplo)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: onetrade/api:v1.0.0
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 3

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Consecuencias

**Positivas:**
- Deployment declarativo (GitOps)
- Auto-healing, auto-scaling
- Zero-downtime deployments

**Negativas:**
- Curva de aprendizaje de K8s
- Costos de infraestructura (cluster manager)

### Alternativa para MVP

Usar **Railway.app** o **Render.com**:
- Deploy con `git push`
- Managed Postgres, Redis
- Auto HTTPS, monitoring incluido
- $20-50/mes vs $100+ K8s

Migrar a K8s cuando sea necesario (>10k usuarios).

---

## Resumen de Decisiones

| Componente | Tecnología Elegida | Razón Principal |
|------------|-------------------|-----------------|
| Backend | Python + FastAPI | Reutilización código + ecosistema científico |
| Database | PostgreSQL + TimescaleDB | Balance ACID + time-series |
| Frontend | React + TypeScript | Ecosistema maduro + type safety |
| Cache | Redis | Versatilidad + performance |
| Job Queue | Celery + RabbitMQ | Confiabilidad + features |
| Architecture | Modulith | Start simple, evolucionar después |
| Auth | JWT + Refresh Tokens | Stateless + revocación |
| Deploy | Docker + K8s (Railway para MVP) | Portabilidad + escalabilidad |

---

## Próximos Pasos

1. **Setup inicial**: Crear repos, CI/CD básico
2. **PoC Recommendation Engine**: Validar viabilidad técnica
3. **Iteración**: Ajustar decisiones basadas en learnings

**Documento vivo**: Estas decisiones pueden cambiar según feedback y realidad del desarrollo.







