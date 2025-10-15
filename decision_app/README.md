# One Trade Decision-Centric App

Sistema inteligente de recomendaciones de trading que proporciona decisiones diarias claras y accionables basadas en análisis automatizado de múltiples estrategias y datos de mercado.

## 🚀 Quick Start

### Requisitos Previos

- **Docker** y **Docker Compose** (recomendado)
- **Python 3.11+** (para desarrollo backend)
- **Node.js 18+** y **npm/pnpm** (para desarrollo frontend)
- **Git**

### Instalación con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd decision_app

# 2. Copiar archivos de entorno
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Iniciar servicios de infraestructura
docker-compose up -d

# 4. Verificar que los servicios estén corriendo
docker-compose ps

# Los siguientes servicios deberían estar activos:
# - PostgreSQL (TimescaleDB): localhost:5432
# - Redis: localhost:6379
# - RabbitMQ: localhost:5672 (Management UI: localhost:15672)
```

### Setup Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor de desarrollo
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# El backend estará disponible en:
# - API: http://localhost:8000
# - Documentación interactiva: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Setup Frontend

```bash
cd frontend

# Instalar dependencias
npm install
# o con pnpm:
# pnpm install

# Iniciar servidor de desarrollo
npm run dev

# El frontend estará disponible en:
# - http://localhost:5173
```

## 📁 Estructura del Proyecto

```
decision_app/
├── backend/                    # API FastAPI
│   ├── alembic/               # Database migrations
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   └── v1/            # API version 1
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # Configuration
│   │   │   ├── database.py    # Database setup
│   │   │   └── logging.py     # Logging setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── strategies/        # Trading strategies
│   ├── tests/                 # Backend tests
│   ├── .env.example           # Environment template
│   ├── main.py                # Application entry point
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React + TypeScript
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── layout/        # Layout components
│   │   │   └── ui/            # Shadcn/ui components
│   │   ├── hooks/             # Custom hooks
│   │   ├── lib/               # Utilities
│   │   ├── pages/             # Page components
│   │   ├── App.tsx            # Main app component
│   │   └── main.tsx           # Entry point
│   ├── .env.example           # Environment template
│   ├── package.json           # Dependencies
│   └── vite.config.ts         # Vite configuration
│
├── recommendation_engine/      # Core recommendation logic
├── integration/               # Adapters
├── tests/                     # Integration tests
├── docker-compose.yml         # Docker services
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_recommendation_engine.py -v
```

### Frontend Tests

```bash
cd frontend

# Ejecutar tests
npm run test

# Con UI
npm run test:ui

# Con coverage
npm run test:coverage
```

## 🔧 Desarrollo

### Linting y Formateo

**Backend:**
```bash
cd backend

# Formatear código
black .
isort .

# Linting
flake8
mypy .
```

**Frontend:**
```bash
cd frontend

# Linting
npm run lint

# Auto-fix
npm run lint:fix

# Type checking
npm run type-check
```

### Migraciones de Base de Datos

```bash
cd backend

# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history
```

### Workers de Celery

```bash
cd backend

# Iniciar worker
celery -A app.core.celery_app worker --loglevel=info

# Iniciar beat scheduler (para tareas programadas)
celery -A app.core.celery_app beat --loglevel=info

# Monitoring con Flower (opcional)
celery -A app.core.celery_app flower
```

## 📊 Servicios de Infraestructura

### PostgreSQL + TimescaleDB

- **Puerto:** 5432
- **Base de datos:** onetrade
- **Usuario:** onetrade
- **Contraseña:** onetrade_dev (cambiar en producción)

### Redis

- **Puerto:** 6379
- **Uso:** Cache y resultado de tareas Celery

### RabbitMQ

- **Puerto:** 5672 (AMQP)
- **Management UI:** http://localhost:15672
- **Usuario:** onetrade
- **Contraseña:** onetrade_dev

### PgAdmin (Desarrollo)

```bash
# Iniciar PgAdmin
docker-compose --profile dev up pgadmin

# Acceder en: http://localhost:5050
# Email: admin@onetrade.local
# Password: admin
```

## 🚀 Despliegue

### Build para Producción

**Backend:**
```bash
cd backend

# Build con Docker
docker build -t onetrade-backend:latest .

# O con gunicorn directamente
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
cd frontend

# Build optimizado
npm run build

# Los archivos estarán en frontend/dist/
# Servir con nginx, Vercel, Netlify, etc.
```

## 📚 Documentación Adicional

- [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - Resumen ejecutivo del proyecto
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitectura detallada
- [PRODUCT_BACKLOG.md](PRODUCT_BACKLOG.md) - Backlog completo
- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Guía rápida para developers
- [API Documentation](http://localhost:8000/docs) - Swagger UI (cuando el backend esté corriendo)

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Haz commit de tus cambios: `git commit -m 'feat: agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

### Convenciones de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Cambios en documentación
- `style:` Formateo, sin cambios de código
- `refactor:` Refactorización de código
- `test:` Agregar o modificar tests
- `chore:` Tareas de mantenimiento

## ❓ Troubleshooting

### El backend no inicia

1. Verificar que PostgreSQL esté corriendo: `docker-compose ps`
2. Verificar variables de entorno en `backend/.env`
3. Verificar migraciones: `alembic current`

### El frontend no conecta con el backend

1. Verificar que `VITE_API_URL` en `frontend/.env` apunte a `http://localhost:8000`
2. Verificar CORS en backend (config.py)
3. Verificar que el backend esté corriendo en puerto 8000

### Errores de base de datos

1. Recrear base de datos:
   ```bash
   docker-compose down -v
   docker-compose up -d
   alembic upgrade head
   ```

2. Verificar conexión:
   ```bash
   psql -h localhost -U onetrade -d onetrade
   ```

## 📄 Licencia

Este proyecto es propietario. Todos los derechos reservados.

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/yourusername/onetrade-decision-app/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/onetrade-decision-app/discussions)
- **Email:** team@onetrade.com

---

**Última actualización:** Octubre 2025
**Versión:** 1.0.0
**Estado:** Development
