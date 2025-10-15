# 📚 Índice de Documentación - One Trade Decision-Centric App

Bienvenido a la documentación del proyecto. Este índice te ayudará a encontrar rápidamente la información que necesitas.

---

## 🚀 Inicio Rápido

**¿Primera vez aquí?** Empieza por:

1. [README Principal](../README.md) - Visión general del proyecto
2. [ARCHITECTURE.md](#architecture) - Entender cómo funciona el sistema
3. [TECHNICAL_DECISIONS.md](#decisions) - Por qué tomamos cada decisión técnica

---

## 📖 Documentos por Audiencia

### Para Product Managers / Stakeholders

| Documento | Qué Encontrarás | Tiempo de Lectura |
|-----------|----------------|-------------------|
| [README](../README.md) | Visión, features, roadmap | 10 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) § Visión General | Objetivo del sistema, casos de uso | 5 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) § Principios de Diseño | Decisiones de producto | 5 min |

**Total**: 20 minutos para entender el proyecto completo.

### Para Desarrolladores

| Documento | Qué Encontrarás | Cuándo Leer |
|-----------|----------------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Arquitectura completa, módulos, flujo de datos | Antes de escribir código |
| [TECHNICAL_DECISIONS.md](TECHNICAL_DECISIONS.md) | Justificación de stack y tecnologías | Cuando tengas dudas técnicas |
| [MIGRATION_PLAN.md](MIGRATION_PLAN.md) | Cómo migrar desde v2.0 | Al trabajar en migración |
| [API_CONTRACTS.md](API_CONTRACTS.md) | Specs de endpoints | Al integrar frontend/backend |

### Para DevOps / SRE

| Documento | Qué Encontrarás |
|-----------|----------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) § Infraestructura | Diagrama de despliegue, Docker, K8s |
| [ARCHITECTURE.md](ARCHITECTURE.md) § Seguridad y Rendimiento | SLOs, métricas, optimizaciones |

### Para QA / Testers

| Documento | Qué Encontrarás |
|-----------|----------------|
| [MIGRATION_PLAN.md](MIGRATION_PLAN.md) § Testing Strategy | Tests de paridad, integration tests |
| [ARCHITECTURE.md](ARCHITECTURE.md) § Casos de Uso | Flujos a testear end-to-end |

---

## 📁 Estructura de Documentos

```
decision_app/
├── README.md                       ← EMPIEZA AQUÍ
└── docs/
    ├── INDEX.md                    ← Este archivo (navegación)
    ├── ARCHITECTURE.md             ← Arquitectura completa (100+ páginas)
    ├── TECHNICAL_DECISIONS.md      ← ADRs y justificaciones
    ├── MIGRATION_PLAN.md           ← Cómo migrar desde v2.0
    └── API_CONTRACTS.md            ← Specs de API (TBD)
```

---

## 🎯 Documentos Principales

### <a name="architecture"></a> ARCHITECTURE.md

**Tema**: Arquitectura Completa del Sistema

**Secciones**:

1. **Visión General** - Objetivo, usuarios, casos de uso
2. **Principios de Diseño** - Filosofía del sistema
3. **Arquitectura de Alto Nivel** - Diagrama y componentes
4. **Módulos del Sistema** - Detalle de cada módulo:
   - Data Ingestion Service
   - Backtest Engine
   - Recommendation Engine (⭐ core feature)
   - API Gateway / BFF
   - Frontend Web App
5. **Flujo de Datos** - Cómo se mueven los datos
6. **Modelo de Datos** - Schemas de PostgreSQL + Redis
7. **Infraestructura y Despliegue** - Docker, K8s, CI/CD
8. **Seguridad y Rendimiento** - Auth, validación, optimizaciones

**Cuándo leer**: Antes de empezar a desarrollar cualquier feature.

**Destacados**:
- 📐 Diagrama ASCII de arquitectura completa
- 💡 Interfaces de código para cada módulo
- 🔄 Diagramas de flujo (actualización diaria, consulta manual, backtest)
- 🗄️ Schemas SQL completos
- 📊 Tabla de SLOs (latency, uptime, etc.)

---

### <a name="decisions"></a> TECHNICAL_DECISIONS.md

**Tema**: Decisiones Técnicas (ADR Style)

**Formato**: Cada decisión sigue:
- **Contexto**: Por qué necesitamos esto
- **Opciones Consideradas**: A, B, C con pros/cons
- **Decisión**: Qué elegimos
- **Justificación**: Por qué
- **Consecuencias**: Positivas y negativas

**Decisiones Documentadas**:

1. **Stack de Backend**: Python + FastAPI
2. **Base de Datos**: PostgreSQL + TimescaleDB
3. **Frontend**: React + TypeScript
4. **Cache Layer**: Redis
5. **Job Queue**: Celery + RabbitMQ
6. **Arquitectura**: Modulith → Microservicios
7. **Autenticación**: JWT con Refresh Tokens
8. **Despliegue**: Docker + Kubernetes

**Cuándo leer**: 
- Al cuestionar por qué usamos X tecnología
- Al proponer cambio de stack
- Al onboardear nuevo developer

**Valor**: Evita re-discutir decisiones ya tomadas. Si quieres cambiar algo, actualiza el ADR con nuevo contexto.

---

### MIGRATION_PLAN.md

**Tema**: Migración desde One Trade v2.0

**Secciones**:

1. **Análisis del Código Existente**
   - Inventario de módulos v2.0
   - Qué reutilizar vs reescribir
   - ~70% código reutilizable

2. **Estrategia de Migración**
   - Strangler Fig Pattern
   - Fases 1-5 de migración

3. **Migración Por Módulo**
   - DataStore: CSV → PostgreSQL
   - DataFetcher: Sync → Async
   - BacktestEngine: Single → Multi-symbol
   - Strategies: Agregar metadata
   - WebApp: Dash → React (reescritura)

4. **Testing Strategy**
   - Tests de paridad
   - Integration tests

5. **Timeline**
   - 12 semanas, detallado por semana

**Cuándo leer**: Al trabajar en migración de cualquier módulo.

**Destacados**:
- 📊 Tabla de inventario con LoC y acción para cada módulo
- 🔄 Diagramas de antes/después del código
- ✅ Checklist de go-live

---

### PRODUCT_BACKLOG.md ✅ NUEVO

**Tema**: Backlog Completo de Producto

**Contenido**:
- 58 User Stories distribuidas en 6 fases
- 379 Story Points totales
- Estimaciones y dependencias detalladas
- Priorización (P0/P1/P2/P3)
- Sprint planning sugerido
- Riesgos y mitigaciones

**Cuándo leer**: Al planificar sprints y asignar tareas

**Destacados**:
- 📊 Tabla resumen por fase
- 🔗 Diagrama de dependencias críticas
- ✅ Checklist de go-live
- 📈 Métricas de progreso

---

### STRATEGY_ROADMAP.md ✅ NUEVO

**Tema**: Roadmap de Implementación de Estrategias

**Contenido**:
- 10 estrategias a implementar (Wave 1-3)
- Arquitectura base de estrategias
- Detalles técnicos de cada estrategia
- Sistema de pesos dinámicos
- Benchmarking y optimización

**Cuándo leer**: Al implementar nuevas estrategias de trading

**Destacados**:
- 💻 Código completo de BaseStrategy
- 📊 Matriz estrategias vs condiciones de mercado
- 🧪 Templates de testing
- 🚀 Auto-tuning de parámetros

---

### API_CONTRACTS.md (Próximamente)

**Tema**: Especificación de API REST/GraphQL

**Contendrá**:
- Lista completa de endpoints
- Request/Response schemas (JSON)
- Códigos de error
- Ejemplos de uso con curl
- Rate limits
- Autenticación requerida

**Estado**: 📋 Pendiente (crear cuando API esté diseñada)

---

## 🔍 Búsqueda Rápida

### Por Tema

**Quiero entender...**

| Tema | Documento | Sección |
|------|-----------|---------|
| Cómo funciona el Recommendation Engine | [ARCHITECTURE.md](ARCHITECTURE.md) | § Módulos del Sistema → 3. Recommendation Engine |
| Por qué usamos PostgreSQL vs MongoDB | [TECHNICAL_DECISIONS.md](TECHNICAL_DECISIONS.md) | Decision #2: Base de Datos |
| Cómo migrar el DataStore | [MIGRATION_PLAN.md](MIGRATION_PLAN.md) | § Migración Por Módulo → 1. Data Store |
| Qué APIs expone el sistema | [ARCHITECTURE.md](ARCHITECTURE.md) | § Módulos → 4. API Gateway |
| Cómo deployar en producción | [ARCHITECTURE.md](ARCHITECTURE.md) | § Infraestructura y Despliegue |
| Roadmap de 12 semanas | [README](../README.md) | § Roadmap |
| Tareas de siguiente sprint | [PRODUCT_BACKLOG.md](../PRODUCT_BACKLOG.md) | § Sprint Planning Sugerido |
| Implementar nueva estrategia | [STRATEGY_ROADMAP.md](../STRATEGY_ROADMAP.md) | § Detalles de Implementación |
| Setup de infraestructura | [INFRASTRUCTURE_SETUP.md](../INFRASTRUCTURE_SETUP.md) | § Quick Start |
| Ver wireframes de UI | [UI_WIREFRAMES.md](../UI_WIREFRAMES.md) | § Pantallas Principales |
| Sistema de diseño | [DESIGN_SYSTEM.md](../DESIGN_SYSTEM.md) | § Paleta de Colores |
| Flujos de usuario | [USER_FLOWS.md](../USER_FLOWS.md) | § Flujos Principales |
| Componentes UI | [UI_COMPONENTS.md](../UI_COMPONENTS.md) | § Componentes Reutilizables |

### Por Rol

**Soy un...**

| Rol | Documentos Clave | Orden de Lectura |
|-----|-----------------|------------------|
| **Product Manager** | README, ARCHITECTURE § Visión | 1→2 |
| **Backend Developer** | ARCHITECTURE, TECHNICAL_DECISIONS, MIGRATION_PLAN | 1→2→3 |
| **Frontend Developer** | ARCHITECTURE § Frontend, API_CONTRACTS | 1→2 |
| **DevOps Engineer** | ARCHITECTURE § Infraestructura, TECHNICAL_DECISIONS | 1→2 |
| **QA Engineer** | ARCHITECTURE § Casos de Uso, MIGRATION_PLAN § Testing | 1→2 |

---

## 📝 Guías de Estilo

### Documentación

Todos los documentos siguen:

- **Formato**: Markdown
- **Diagramas**: ASCII art (para portabilidad)
- **Código**: Syntax highlighting con lenguaje
- **TOC**: Tabla de contenidos al inicio
- **Enlaces**: Relativos (no absolutos)

### Actualización

Estos documentos son **vivos**:

- Actualizar cuando cambie el diseño
- Agregar sección "Changelog" al final si hay cambios mayores
- Revisar una vez por sprint/iteración

---

## 🚦 Estado de Documentos

| Documento | Versión | Última Actualización | Estado | Próxima Revisión |
|-----------|---------|---------------------|--------|------------------|
| README | 1.0 | Oct 2025 | ✅ Completo | Semana 4 |
| ARCHITECTURE | 1.0 | Oct 2025 | ✅ Completo | Semana 4 |
| TECHNICAL_DECISIONS | 1.0 | Oct 2025 | ✅ Completo | Cuando cambie stack |
| MIGRATION_PLAN | 1.0 | Oct 2025 | ✅ Completo | Semana 3 |
| API_CONTRACTS | - | - | 📋 Pendiente | Semana 5 |
| SETUP_GUIDE | - | - | 📋 Pendiente | Semana 2 |
| CONTRIBUTING | - | - | 📋 Pendiente | Semana 2 |

---

## 💡 Tips de Navegación

### Atajos

- **Ctrl+F** en navegador para buscar término específico
- Usa los anchors (#section) para links directos
- Los diagramas ASCII se ven mejor en monospace font

### Formato de Enlaces

```markdown
<!-- Link a otro documento -->
Ver [ARCHITECTURE.md](ARCHITECTURE.md)

<!-- Link a sección específica -->
Ver [Recommendation Engine](ARCHITECTURE.md#3-recommendation-engine)

<!-- Link externo -->
Ver [FastAPI Docs](https://fastapi.tiangolo.com)
```

---

## 🤝 Contribuir a la Documentación

¿Encontraste algo confuso o desactualizado?

1. **Pequeños cambios**: Edita directamente y crea PR
2. **Grandes cambios**: Abre issue primero para discutir
3. **Nuevo documento**: Propón en issue, agrega a este índice

**Checklist** antes de commit:

- [ ] Markdown válido (no broken links)
- [ ] Actualizado índice si creaste nuevo doc
- [ ] Changelog agregado si cambio mayor
- [ ] Spelling checked

---

## 📞 Contacto

¿Preguntas sobre la documentación?

- **Slack**: #onetrade-docs
- **Email**: docs@onetrade.com
- **Issues**: [GitHub Issues](https://github.com/yourusername/onetrade-decision-app/issues)

---

## 🔗 Enlaces Útiles

- [One Trade v2.0 (sistema actual)](https://github.com/yourusername/one_trade)
- [Guía de Usuario v2.0](../../WEBAPP_USER_GUIDE.md)
- [Implementación de Estabilización](../../ESTABILIZACION_APP_INTERACTIVA_RESUMEN.md)

---

**Última actualización**: Octubre 2025  
**Mantenedor**: Equipo de Arquitectura





