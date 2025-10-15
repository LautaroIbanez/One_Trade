# 🚀 Quick Start Guide - One Trade Decision App

**Para desarrolladores que quieren comenzar YA**

---

## ⚡ Setup en 10 Minutos

### 1. Clonar y Setup Básico

```bash
git clone <repo-url>
cd onetrade-decision-app

cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cd ../frontend
npm install
```

### 2. Levantar Servicios con Docker

```bash
docker-compose up -d postgres redis rabbitmq
```

### 3. Aplicar Migraciones

```bash
cd backend
alembic upgrade head
```

### 4. Correr Backend y Frontend

Terminal 1:
```bash
cd backend
uvicorn main:app --reload
```

Terminal 2:
```bash
cd frontend
npm run dev
```

### 5. Verificar

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000

---

## 🎯 Primera Tarea: ¿Por Dónde Empiezo?

### Si eres Backend Developer

**Task Recomendada**: SETUP-004 - Estructura de proyecto backend

1. Lee: [ARCHITECTURE.md](docs/ARCHITECTURE.md) § Módulos
2. Implementa: Estructura de carpetas según spec
3. Setup: FastAPI app base + Alembic
4. Crea: Primera migration
5. Tests: pytest básico funcionando

**Archivos a crear**:
```
backend/
├── main.py               # FastAPI app
├── routers/
│   └── recommendations.py
├── services/
│   └── recommendation_service.py
├── models/
│   └── recommendation.py
├── schemas/
│   └── recommendation.py
└── tests/
    └── test_recommendations.py
```

### Si eres Frontend Developer

**Task Recomendada**: SETUP-005 - Estructura de proyecto frontend

1. Lee: [ARCHITECTURE.md](docs/ARCHITECTURE.md) § Frontend
2. Implementa: React + Vite setup
3. Configura: Tailwind CSS + Shadcn/ui
4. Setup: React Router + Zustand
5. Crea: Primer componente

**Archivos a crear**:
```
frontend/
├── src/
│   ├── pages/
│   │   └── Dashboard.tsx
│   ├── components/
│   │   └── RecommendationCard.tsx
│   ├── hooks/
│   │   └── useRecommendations.ts
│   ├── stores/
│   │   └── recommendationStore.ts
│   └── lib/
│       └── api.ts
```

### Si eres DevOps

**Task Recomendada**: SETUP-002 - Docker Compose

1. Lee: [ARCHITECTURE.md](docs/ARCHITECTURE.md) § Infraestructura
2. Implementa: docker-compose.yml completo
3. Configura: PostgreSQL + TimescaleDB
4. Agrega: Redis, RabbitMQ
5. Verifica: Healthchecks

---

## 📋 Checklist Primera Semana

### Lunes - Setup

- [ ] Repositorio clonado
- [ ] Docker funcionando
- [ ] Servicios corriendo (postgres, redis, rabbitmq)
- [ ] Backend corre sin errores
- [ ] Frontend corre sin errores

### Martes - Estructura

- [ ] Backend: Carpetas creadas
- [ ] Frontend: Carpetas creadas
- [ ] Alembic configurado
- [ ] Primera migration creada
- [ ] Tests básicos pasando

### Miércoles - Primer Feature

- [ ] Endpoint /health implementado
- [ ] Página 404 en frontend
- [ ] CI/CD pipeline básico (lint)
- [ ] README con setup instructions

### Jueves - PoC Integration

- [ ] Recommendation Engine PoC integrado
- [ ] Primera API /api/recommendations/latest
- [ ] Tests de integración
- [ ] Documentación actualizada

### Viernes - Review

- [ ] Code review de lo hecho
- [ ] Retrospectiva de equipo
- [ ] Planning próxima semana
- [ ] Demo a stakeholders

---

## 🔥 Tasks Críticas (Prioridad P0)

Estas **DEBEN** completarse antes de avanzar:

| ID | Task | Bloqueador Para | Tiempo |
|----|------|----------------|--------|
| SETUP-001 | Crear repos | TODO | 2-4h |
| SETUP-002 | Docker Compose | Data, Jobs, Backend | 4-6h |
| SETUP-004 | Backend structure | Toda la lógica | 4-6h |
| SETUP-005 | Frontend structure | Todo el UI | 4-6h |
| POC-001 | Integrar Recommendation PoC | API de recomendaciones | 4-6h |
| DATA-001 | Conector Binance | Ingesta de datos | 6-8h |
| BT-001 | BacktestEngine async | Fase 2 y 3 completas | 1-2 días |
| REC-001 | API REST recommendations | Todo el frontend | 6-8h |
| AUTH-001 | Login básico | Seguridad del sistema | 1 día |

**Total estimado**: ~1 semana intensiva

---

## 📚 Documentos Esenciales

Lee en este orden:

1. [README.md](README.md) - Visión general (10 min)
2. [ARCHITECTURE.md](docs/ARCHITECTURE.md) § Visión General (15 min)
3. [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) - Tu fase específica (20 min)
4. [TECHNICAL_DECISIONS.md](docs/TECHNICAL_DECISIONS.md) - Stack elegido (30 min)

**Total**: 1.5 horas de lectura para estar al día

---

## 🧪 Testing Rápido

### Correr Tests

```bash
# Backend
cd backend
pytest tests/ -v --cov

# Frontend
cd frontend
npm test

# E2E
npm run test:e2e
```

### Crear Nuevo Test

```python
# backend/tests/test_recommendations.py

import pytest
from services.recommendation_service import RecommendationService

@pytest.mark.asyncio
async def test_get_latest_recommendation():
    service = RecommendationService()
    rec = await service.get_latest("BTC/USDT")
    
    assert rec is not None
    assert rec.symbol == "BTC/USDT"
    assert rec.action in ["BUY", "SELL", "HOLD"]
    assert 0 <= rec.confidence <= 1
```

---

## 🐛 Troubleshooting Común

### Error: "PostgreSQL connection failed"

```bash
# Verificar que Docker esté corriendo
docker ps | grep postgres

# Ver logs
docker logs <postgres-container-id>

# Reintentar
docker-compose restart postgres
```

### Error: "Module not found"

```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install

# Limpiar cache
rm -rf node_modules package-lock.json
npm install
```

### Error: "Port already in use"

```bash
# Encontrar proceso
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Matar proceso
kill -9 <PID>
```

---

## 💡 Tips de Productividad

### 1. Usa Aliases

```bash
# .bashrc o .zshrc
alias be='cd backend && source venv/bin/activate'
alias fe='cd frontend'
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
```

### 2. Configurar VS Code

```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### 3. Pre-commit Hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar
pre-commit install

# Correr manualmente
pre-commit run --all-files
```

---

## 🔄 Workflow Diario Recomendado

### Mañana (9am - 12pm)

1. **Standup** (15 min)
2. **Revisar PRs** pendientes (30 min)
3. **Coding** en task asignada (2h 15min)

### Tarde (1pm - 5pm)

4. **Coding** continuado (2h)
5. **Tests** de lo implementado (1h)
6. **Code review** de otros (30 min)
7. **Documentar** cambios (30 min)

### Fin de Día (5pm)

8. **Push** cambios a branch
9. **Crear PR** si task completa
10. **Actualizar** JIRA/backlog

---

## 🎯 Objetivos por Sprint

### Sprint 1 (Semanas 1-2): Foundation

**Goal**: Infraestructura lista

**Success Criteria**:
- [ ] Repos configurados
- [ ] CI/CD básico funcionando
- [ ] Docker Compose completo
- [ ] PoC Recommendation Engine integrado
- [ ] 1 endpoint funcionando
- [ ] 1 página en frontend

### Sprint 2 (Semanas 3-4): Data Pipeline

**Goal**: Datos fluyendo automáticamente

**Success Criteria**:
- [ ] Binance connector funcionando
- [ ] Datos en TimescaleDB
- [ ] Validación automática
- [ ] Job diario configurado
- [ ] Dashboard de data quality

### Sprint 3 (Semanas 5-6): Backtest Engine

**Goal**: Motor refactorizado y funcionando

**Success Criteria**:
- [ ] BacktestEngine async
- [ ] Multi-activo funcional
- [ ] Métricas avanzadas
- [ ] Comparador visual
- [ ] Cache funcionando

---

## 📞 Contactos del Equipo

| Rol | Persona | Canal |
|-----|---------|-------|
| **Tech Lead** | TBD | Slack @techlead |
| **Backend Lead** | TBD | Slack @backend |
| **Frontend Lead** | TBD | Slack @frontend |
| **DevOps** | TBD | Slack @devops |
| **Product Manager** | TBD | Slack @pm |

**Canales Slack**:
- #onetrade-dev - Desarrollo general
- #onetrade-backend - Backend específico
- #onetrade-frontend - Frontend específico
- #onetrade-alerts - Alertas de CI/CD

---

## 🔗 Enlaces Útiles

### Desarrollo

- [Backend API Docs](http://localhost:8000/docs) - Swagger local
- [Frontend Dev](http://localhost:3000) - Local dev server
- [PgAdmin](http://localhost:5050) - PostgreSQL UI
- [Flower](http://localhost:5555) - Celery monitoring

### Documentación

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitectura completa
- [TECHNICAL_DECISIONS.md](docs/TECHNICAL_DECISIONS.md) - Decisiones técnicas
- [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) - Backlog completo
- [STRATEGY_ROADMAP.md](STRATEGY_ROADMAP.md) - Roadmap de estrategias

### Recursos Externos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Shadcn/ui](https://ui.shadcn.com/)
- [TimescaleDB Docs](https://docs.timescale.com/)

---

## ⚡ Comandos Útiles

### Docker

```bash
# Levantar todo
docker-compose up -d

# Ver logs
docker-compose logs -f <service>

# Reiniciar servicio
docker-compose restart <service>

# Bajar todo
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

### Database

```bash
# Conectar a PostgreSQL
docker exec -it <postgres-container> psql -U postgres -d onetrade

# Backup
docker exec <postgres-container> pg_dump -U postgres onetrade > backup.sql

# Restore
docker exec -i <postgres-container> psql -U postgres onetrade < backup.sql

# Migrations
alembic revision --autogenerate -m "Add recommendations table"
alembic upgrade head
alembic downgrade -1
```

### Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_recommendations.py::test_get_latest

# With coverage
pytest --cov=backend --cov-report=html

# Watch mode
pytest-watch
```

---

## 🏁 Conclusión

Ya estás listo para comenzar. Recuerda:

1. **Lee la documentación** antes de codear
2. **Haz preguntas** si algo no está claro
3. **Escribe tests** desde el día 1
4. **Haz PRs pequeños** (< 400 líneas)
5. **Documenta** tus cambios

**¡Éxito! 🚀**

---

**Última actualización**: Octubre 2025 - Día 2
**Mantenedor**: Tech Team



