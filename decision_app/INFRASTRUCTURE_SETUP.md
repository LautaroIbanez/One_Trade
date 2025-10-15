# 🏗️ Infrastructure Setup - One Trade Decision App

**Epic**: 0.1 - Setup de Proyecto  
**Story Points**: 17  
**Duración**: 3-4 días  
**Status**: 🚧 EN PROGRESO

---

## 📋 Tasks del Epic 0.1

| ID | Task | Story Points | Prioridad | Dependencias |
|----|------|-------------|-----------|--------------|
| SETUP-001 | Crear repositorios separados | 2 | P0 | Ninguna |
| SETUP-002 | Docker Compose con servicios | 3 | P0 | SETUP-001 |
| SETUP-003 | CI/CD pipeline básico | 5 | P1 | SETUP-001 |
| SETUP-004 | Estructura backend | 3 | P0 | SETUP-002 |
| SETUP-005 | Estructura frontend | 3 | P0 | SETUP-001 |
| SETUP-006 | Variables de entorno | 1 | P1 | SETUP-004, SETUP-005 |

**Total**: 17 puntos

---

## 🎯 Objetivo

Crear la infraestructura base para el desarrollo del proyecto One Trade Decision App, incluyendo repositorios, Docker, CI/CD y estructuras de proyecto.

---

## 📁 Estructura de Repositorios

### Repositorio Principal (Monorepo)

```
onetrade-decision-app/
├── README.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-staging.yml
│       └── deploy-prod.yml
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ...
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── ...
├── docs/
│   ├── api/
│   ├── deployment/
│   └── development/
└── scripts/
    ├── setup.sh
    ├── dev.sh
    └── deploy.sh
```

### Alternativa: Repositorios Separados

```
onetrade-decision-backend/
├── app/
├── tests/
├── requirements.txt
├── Dockerfile
└── ...

onetrade-decision-frontend/
├── src/
├── public/
├── package.json
├── Dockerfile
└── ...
```

**Recomendación**: Monorepo para facilitar desarrollo y deployment coordinado.

---

## 🐳 Docker Configuration

### docker-compose.yml (Base)

```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: timescale/timescaledb:latest-pg15
    container_name: onetrade-postgres
    environment:
      POSTGRES_DB: onetrade
      POSTGRES_USER: onetrade
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-onetrade_dev}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U onetrade"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Cache
  redis:
    image: redis:7-alpine
    container_name: onetrade-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Message Queue
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: onetrade-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: onetrade
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD:-onetrade_dev}
    ports:
      - "5672:5672"
      - "15672:15672"  # Management UI
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Database Admin (Development only)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: onetrade-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@onetrade.local
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
    ports:
      - "5050:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres
    profiles:
      - dev

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
  pgadmin_data:

networks:
  default:
    name: onetrade-network
```

### docker-compose.dev.yml (Development)

```yaml
version: '3.8'

services:
  # Backend Development
  backend-dev:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: onetrade-backend-dev
    environment:
      - DATABASE_URL=postgresql://onetrade:onetrade_dev@postgres:5432/onetrade
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://onetrade:onetrade_dev@rabbitmq:5672/
      - ENVIRONMENT=development
      - DEBUG=true
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - /app/__pycache__
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend Development
  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: onetrade-frontend-dev
    environment:
      - VITE_API_URL=http://localhost:8000
      - VITE_WS_URL=ws://localhost:8000/ws
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  # Celery Worker
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: onetrade-celery-worker
    environment:
      - DATABASE_URL=postgresql://onetrade:onetrade_dev@postgres:5432/onetrade
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://onetrade:onetrade_dev@rabbitmq:5672/
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
      - rabbitmq
    command: celery -A app.celery worker --loglevel=info

  # Celery Beat (Scheduler)
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: onetrade-celery-beat
    environment:
      - DATABASE_URL=postgresql://onetrade:onetrade_dev@postgres:5432/onetrade
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://onetrade:onetrade_dev@rabbitmq:5672/
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
      - rabbitmq
    command: celery -A app.celery beat --loglevel=info
```

### docker-compose.prod.yml (Production)

```yaml
version: '3.8'

services:
  # Backend Production
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: onetrade-backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - RABBITMQ_URL=${RABBITMQ_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - rabbitmq
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend Production
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: onetrade-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: onetrade-nginx
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
```

---

## 🏗️ Backend Structure

### backend/Dockerfile

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### backend/Dockerfile.dev

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### backend/requirements.txt

```txt
# FastAPI and ASGI
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Cache and Queue
redis==5.0.1
celery==5.3.4
kombu==5.3.4

# Data Processing
pandas==2.1.3
numpy==1.25.2
pydantic==2.5.0
pydantic-settings==2.1.0

# HTTP Client
httpx==0.25.2
aiohttp==3.9.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Monitoring and Logging
structlog==23.2.0
prometheus-client==0.19.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1

# Production
sentry-sdk[fastapi]==1.38.0
```

### backend/app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.exceptions import setup_exception_handlers

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="One Trade Decision-Centric App API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up trusted hosts
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.BACKEND_CORS_ORIGINS
    )

# Set up exception handlers
setup_exception_handlers(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "One Trade Decision App API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
```

### backend/app/core/config.py

```python
from typing import List, Optional
from pydantic import BaseSettings, validator
import secrets

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "One Trade Decision App"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # Database
    DATABASE_URL: str = "postgresql://onetrade:onetrade_dev@localhost:5432/onetrade"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://onetrade:onetrade_dev@localhost:5672/"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"
    
    # External APIs
    BINANCE_API_URL: str = "https://api.binance.com"
    COINBASE_API_URL: str = "https://api.exchange.coinbase.com"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### backend/app/core/database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

# Sync database
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async database
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.ENVIRONMENT == "development"
)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### backend/app/core/celery_app.py

```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "onetrade",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.data_ingestion",
        "app.tasks.recommendations",
        "app.tasks.metrics",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
```

### backend/app/api/v1/api.py

```python
from fastapi import APIRouter
from app.api.v1.endpoints import (
    recommendations,
    backtests,
    strategies,
    assets,
    auth,
    health
)

api_router = APIRouter()

api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["recommendations"]
)
api_router.include_router(
    backtests.router, prefix="/backtests", tags=["backtests"]
)
api_router.include_router(
    strategies.router, prefix="/strategies", tags=["strategies"]
)
api_router.include_router(
    assets.router, prefix="/assets", tags=["assets"]
)
api_router.include_router(
    auth.router, prefix="/auth", tags=["auth"]
)
api_router.include_router(
    health.router, prefix="/health", tags=["health"]
)
```

### backend/app/api/v1/endpoints/health.py

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@router.get("/db")
async def database_health(db: Session = Depends(get_db)):
    """Database health check"""
    try:
        # Simple query to test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
```

### backend/alembic.ini

```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format
version_num_format = %04d

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = postgresql://onetrade:onetrade_dev@localhost:5432/onetrade


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### backend/alembic/env.py

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.core.database import Base
from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    return settings.DATABASE_URL

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## ⚛️ Frontend Structure

### frontend/Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### frontend/Dockerfile.dev

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev"]
```

### frontend/package.json

```json
{
  "name": "onetrade-decision-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directs --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "type-check": "tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.18.0",
    "@tanstack/react-query": "^5.8.4",
    "zustand": "^4.4.6",
    "axios": "^1.6.0",
    "recharts": "^2.8.0",
    "lucide-react": "^0.292.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "class-variance-authority": "^0.7.0",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-tooltip": "^1.0.7",
    "framer-motion": "^10.16.4"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@typescript-eslint/eslint-plugin": "^6.10.0",
    "@typescript-eslint/parser": "^6.10.0",
    "@vitejs/plugin-react": "^4.1.0",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.53.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.4",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.3.5",
    "typescript": "^5.2.2",
    "vite": "^4.5.0",
    "vitest": "^0.34.6",
    "@vitest/ui": "^0.34.6",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^6.1.4",
    "@testing-library/user-event": "^14.5.1"
  }
}
```

### frontend/vite.config.ts

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
```

### frontend/tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        signal: {
          buy: '#10B981',
          sell: '#EF4444',
          hold: '#F59E0B',
        },
        brand: {
          primary: '#3B82F6',
          secondary: '#8B5CF6',
          accent: '#06B6D4',
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
        "slide-in-right": {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        "slide-in-left": {
          "0%": { transform: "translateX(-100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
        "slide-in-left": "slide-in-left 0.3s ease-out",
        "fade-in": "fade-in 0.3s ease-in",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

### frontend/src/main.tsx

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './index.css'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
```

### frontend/src/App.tsx

```typescript
import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { Dashboard } from '@/pages/Dashboard'
import { History } from '@/pages/History'
import { Backtests } from '@/pages/Backtests'
import { Settings } from '@/pages/Settings'
import { Layout } from '@/components/Layout'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/backtests" element={<Backtests />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
      <Toaster />
    </div>
  )
}

export default App
```

---

## 🔄 CI/CD Pipeline

### .github/workflows/ci.yml

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint with flake8
      run: |
        cd backend
        flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Type check with mypy
      run: |
        cd backend
        mypy app --ignore-missing-imports
    
    - name: Format check with black
      run: |
        cd backend
        black --check app
    
    - name: Test with pytest
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
      run: |
        cd backend
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
        name: backend-coverage

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Lint
      run: |
        cd frontend
        npm run lint
    
    - name: Type check
      run: |
        cd frontend
        npm run type-check
    
    - name: Test
      run: |
        cd frontend
        npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info
        flags: frontend
        name: frontend-coverage

  build:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
    
    - name: Build and push Docker images
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

### .github/workflows/deploy-staging.yml

```yaml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # Add your deployment script here
        # Example: kubectl apply -f k8s/staging/
```

### .github/workflows/deploy-prod.yml

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      run: |
        echo "Deploying to production environment..."
        # Add your deployment script here
        # Example: kubectl apply -f k8s/production/
```

---

## 🔧 Scripts de Desarrollo

### scripts/setup.sh

```bash
#!/bin/bash

# One Trade Decision App - Setup Script
set -e

echo "🚀 Setting up One Trade Decision App..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database
POSTGRES_PASSWORD=onetrade_dev
DATABASE_URL=postgresql://onetrade:onetrade_dev@localhost:5432/onetrade

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_PASSWORD=onetrade_dev
RABBITMQ_URL=amqp://onetrade:onetrade_dev@localhost:5672/

# PgAdmin
PGADMIN_PASSWORD=admin

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Environment
ENVIRONMENT=development
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis rabbitmq

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️ Running database migrations..."
cd backend
python -m pip install -r requirements.txt
alembic upgrade head
cd ..

echo "✅ Setup complete!"
echo ""
echo "🌐 Services available at:"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - PgAdmin: http://localhost:5050"
echo "  - RabbitMQ Management: http://localhost:15672"
echo ""
echo "📚 Next steps:"
echo "  1. Run 'npm install' in frontend directory"
echo "  2. Run 'python -m pip install -r requirements.txt' in backend directory"
echo "  3. Start development with 'docker-compose -f docker-compose.dev.yml up'"
```

### scripts/dev.sh

```bash
#!/bin/bash

# One Trade Decision App - Development Script
set -e

echo "🚀 Starting One Trade Decision App in development mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run setup.sh first."
    exit 1
fi

# Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### scripts/deploy.sh

```bash
#!/bin/bash

# One Trade Decision App - Deployment Script
set -e

ENVIRONMENT=${1:-staging}

echo "🚀 Deploying One Trade Decision App to $ENVIRONMENT..."

# Build and push images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy based on environment
case $ENVIRONMENT in
    staging)
        echo "📦 Deploying to staging..."
        # Add staging deployment commands
        ;;
    production)
        echo "📦 Deploying to production..."
        # Add production deployment commands
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        echo "Usage: $0 [staging|production]"
        exit 1
        ;;
esac

echo "✅ Deployment to $ENVIRONMENT complete!"
```

---

## 📝 Environment Variables

### .env.example

```bash
# Project
PROJECT_NAME=One Trade Decision App
VERSION=1.0.0
ENVIRONMENT=development

# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://onetrade:your_secure_password@localhost:5432/onetrade

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_PASSWORD=your_secure_password
RABBITMQ_URL=amqp://onetrade:your_secure_password@localhost:5672/

# PgAdmin (Development only)
PGADMIN_PASSWORD=admin

# Security
SECRET_KEY=your_secret_key_here

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# External APIs
BINANCE_API_URL=https://api.binance.com
COINBASE_API_URL=https://api.exchange.coinbase.com

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Monitoring (Production)
SENTRY_DSN=your_sentry_dsn_here
```

---

## 🧪 Testing Setup

### backend/pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

### frontend/vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

---

## 📊 Monitoring Setup

### backend/app/core/monitoring.py

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

def setup_metrics_middleware(app):
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## ✅ Checklist de Implementación

### SETUP-001: Repositorios ✅
- [ ] Crear repositorio principal (monorepo)
- [ ] Configurar .gitignore
- [ ] Setup branch protection rules
- [ ] Configurar README principal

### SETUP-002: Docker Compose ✅
- [ ] docker-compose.yml base
- [ ] docker-compose.dev.yml
- [ ] docker-compose.prod.yml
- [ ] Health checks configurados
- [ ] Volumes persistentes

### SETUP-003: CI/CD Pipeline ✅
- [ ] GitHub Actions workflows
- [ ] Tests automáticos (backend + frontend)
- [ ] Linting y type checking
- [ ] Build y push de imágenes
- [ ] Deploy a staging/production

### SETUP-004: Backend Structure ✅
- [ ] Estructura de carpetas
- [ ] Dockerfile + Dockerfile.dev
- [ ] requirements.txt
- [ ] FastAPI app básica
- [ ] Database setup (SQLAlchemy + Alembic)
- [ ] Celery configuration
- [ ] API router structure

### SETUP-005: Frontend Structure ✅
- [ ] Estructura de carpetas
- [ ] Dockerfile + Dockerfile.dev
- [ ] package.json con dependencias
- [ ] Vite configuration
- [ ] Tailwind CSS setup
- [ ] React app básica
- [ ] Router configuration

### SETUP-006: Environment Variables ✅
- [ ] .env.example
- [ ] Configuración en backend
- [ ] Configuración en frontend
- [ ] Scripts de setup

---

## 🚀 Quick Start

### 1. Clone y Setup

```bash
git clone <repo-url>
cd onetrade-decision-app

# Make scripts executable
chmod +x scripts/*.sh

# Run setup
./scripts/setup.sh
```

### 2. Start Development

```bash
# Start all services
./scripts/dev.sh

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 3. Access Services

- **Backend API**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **PgAdmin**: http://localhost:5050
- **RabbitMQ Management**: http://localhost:15672

---

## 📈 Próximos Pasos

### Inmediato (Días 4-5)
1. ✅ Implementar estructura completa
2. ✅ Validar que todos los servicios funcionan
3. ✅ Tests básicos pasando
4. ✅ CI/CD pipeline funcionando

### Semana 1
1. Integrar PoC Recommendation Engine
2. Crear primeros endpoints API
3. Implementar primeros componentes React
4. Setup de testing completo

---

**Status**: 🚧 EN PROGRESO  
**Epic**: 0.1 - Setup de Proyecto (17 puntos)  
**ETA**: 3-4 días

**Próximo**: Implementar estructura completa y validar funcionamiento


