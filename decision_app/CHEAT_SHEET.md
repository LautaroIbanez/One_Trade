# ⚡ One Trade Decision App - Cheat Sheet

**Referencia rápida de 1 página**

---

## 📂 Documentos Principales

| Necesito... | Documento | Tiempo |
|------------|-----------|--------|
| Visión general | [README.md](README.md) | 10 min |
| Empezar a codear | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) | 15 min |
| Ver arquitectura | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 30 min |
| Próxima tarea | [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) | 5 min |
| Implementar estrategia | [STRATEGY_ROADMAP.md](STRATEGY_ROADMAP.md) | 20 min |
| Decisiones técnicas | [docs/TECHNICAL_DECISIONS.md](docs/TECHNICAL_DECISIONS.md) | 30 min |

---

## 🚀 Setup Rápido

```bash
# 1. Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Frontend
cd frontend && npm install

# 3. Docker
docker-compose up -d postgres redis rabbitmq

# 4. Migrations
cd backend && alembic upgrade head

# 5. Run
# Terminal 1: cd backend && uvicorn main:app --reload
# Terminal 2: cd frontend && npm run dev
```

---

## 📊 Stack Tecnológico

**Backend**: Python 3.11+ | FastAPI | PostgreSQL + TimescaleDB | Redis | Celery
**Frontend**: React 18 | TypeScript | Tailwind CSS | Shadcn/ui | Zustand
**Infra**: Docker | Kubernetes | GitHub Actions | Prometheus + Grafana

---

## 🎯 Tasks Críticas (P0)

| ID | Task | Tiempo | Bloqueador |
|----|------|--------|-----------|
| SETUP-001 | Repos | 2-4h | TODO |
| SETUP-002 | Docker Compose | 4-6h | Backend/Data |
| SETUP-004 | Backend structure | 4-6h | Lógica |
| SETUP-005 | Frontend structure | 4-6h | UI |
| POC-001 | Integrar PoC | 4-6h | API |
| REC-001 | API recommendations | 6-8h | Frontend |

---

## 📅 Sprints (12 Semanas)

| Sprint | Semanas | Goal | Story Points |
|--------|---------|------|--------------|
| 1 | 1-2 | Foundation | 38 |
| 2 | 3-4 | Data Pipeline | 53 |
| 3 | 5-6 | Backtest Engine | 60 |
| 4 | 7-8 | Recommendations | 61 |
| 5 | 9-10 | Dashboard | 84 |
| 6 | 11-12 | QA & Deploy | 83 |

---

## 🔧 Comandos Útiles

```bash
# Docker
docker-compose up -d              # Levantar todo
docker-compose logs -f <service>  # Ver logs
docker-compose restart <service>  # Reiniciar

# Tests
pytest tests/ -v --cov           # Backend
npm test                         # Frontend

# Database
alembic revision --autogenerate -m "msg"  # Nueva migration
alembic upgrade head                      # Aplicar migrations

# Linting
black .                          # Format Python
eslint src/                      # Lint TS/React
```

---

## 🧪 Arquitectura BaseStrategy

```python
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    @property
    @abstractmethod
    def metadata(self) -> StrategyMetadata:
        pass
    
    @abstractmethod
    def calculate_signal(self, data: pd.DataFrame) -> SignalStrength:
        pass
```

---

## 📈 Estrategias Planeadas

**Wave 1** (Semana 7): RSI Pure | Bollinger Bands | MACD Histogram
**Wave 2** (Semana 8): Volume Profile | Mean Reversion | Support/Resistance
**Wave 3** (Semanas 9-10): Ichimoku | ADX | Fibonacci | Harmonic

---

## 🔗 APIs Principales

```python
# GET /api/recommendations/latest/{symbol}
# GET /api/recommendations/history/{symbol}
# POST /api/recommendations/generate
# GET /api/backtests/{id}
# POST /api/backtests/run
```

---

## 🐛 Troubleshooting

| Error | Solución |
|-------|----------|
| PostgreSQL connection failed | `docker-compose restart postgres` |
| Module not found | `pip install -r requirements.txt` |
| Port 8000 in use | `lsof -i :8000` → `kill -9 <PID>` |
| Alembic migration fail | `alembic downgrade -1` |

---

## 📞 Contactos

**Tech Lead**: @techlead (Slack #onetrade-dev)
**Backend**: @backend (Slack #onetrade-backend)
**Frontend**: @frontend (Slack #onetrade-frontend)
**DevOps**: @devops (Slack #onetrade-infra)

---

## ✅ Checklist Go-Live

- [ ] P0 y P1 completados
- [ ] Coverage > 80%
- [ ] E2E tests pasando
- [ ] Monitoring configurado
- [ ] Backups automáticos
- [ ] Rollback plan documentado
- [ ] Security audit completo
- [ ] User docs lista

---

## 📊 Métricas de Éxito

| Métrica | Target |
|---------|--------|
| API Latency (P95) | < 200ms |
| Backtest Duration (1 año) | < 10s |
| Uptime | > 99.5% |
| Win Rate Recomendaciones | > 60% |
| Code Coverage | > 80% |

---

## 🎓 Recursos

**Docs**: [README](README.md) | [Architecture](docs/ARCHITECTURE.md) | [Backlog](PRODUCT_BACKLOG.md)
**Code**: [PoC](demo_recommendation_engine.py) | [Tests](tests/)
**External**: [FastAPI](https://fastapi.tiangolo.com) | [React](https://react.dev) | [TimescaleDB](https://docs.timescale.com)

---

**Última actualización**: Octubre 2025 - Día 2
**Imprime esta página para referencia rápida** 📋



