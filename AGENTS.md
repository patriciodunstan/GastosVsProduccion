# CLAUDE.md - Configuración Global

Instrucciones globales para Claude Code en todos los proyectos.

---

## Principios de Desarrollo

### Metodología

- **Arquitectura Limpia**: Separación clara de capas (domain, application, infrastructure)
- **Código Limpio**: Nombres descriptivos, funciones pequeñas, responsabilidad única
- **KISS**: Soluciones simples antes que complejas
- **SOLID**: Single responsibility, Open/closed, Liskov, Interface segregation, Dependency inversion
- **DRY**: No repetir código, abstraer patrones comunes

### Proceso de Desarrollo

1. **Entender necesidades** antes de proponer soluciones técnicas
2. **Plan inicial** con historias de usuario antes de codificar
3. **Elegir tecnología adecuada** al problema, no al revés
4. **Iteración incremental** con entregables pequeños y funcionales
5. **Tests** como parte del desarrollo, no como paso posterior

### Comunicación

- Usar lenguaje técnico de informática
- Explicar decisiones arquitectónicas con justificación
- Documentar trade-offs cuando existan alternativas
- Ser directo y conciso

---

## Stack Tecnológico Preferido

### Backend

| Opción | Tecnología | Uso |
|--------|------------|-----|
| Principal | Python + FastAPI | APIs REST, microservicios, ML |
| Alternativa | Node.js + NestJS | APIs tiempo real, ecosistema JS |

### Frontend

| Opción | Tecnología | Uso |
|--------|------------|-----|
| Principal | React + TypeScript | SPAs, dashboards |
| Alternativa | Angular | Aplicaciones enterprise |

### Base de Datos

| Tipo | Tecnología | Uso |
|------|------------|-----|
| Relacional | PostgreSQL | Datos estructurados, transacciones |
| NoSQL | MongoDB | Documentos flexibles, alta escritura |
| Cache | Redis | Sesiones, cache, colas |

### ORM/ODM

| Lenguaje | Tecnología |
|----------|------------|
| Python | SQLAlchemy (async) |
| Node.js | Prisma, TypeORM |

### Cloud/Deploy

| Plataforma | Uso |
|------------|-----|
| Railway | Prototipos, POCs rápidos |
| Azure | Enterprise, integración Microsoft |
| AWS | Escalabilidad, servicios variados |

### Contenedores

- Docker para desarrollo y producción
- Docker Compose para entornos locales multi-servicio

---

## Planificación de Features

### Formato de Plan Inicial

```markdown
## Contexto
[Descripción del problema o necesidad]

## Objetivo
[Qué se quiere lograr]

## Historias de Usuario
[Lista de historias priorizadas]

## Arquitectura Propuesta
[Decisiones técnicas con justificación]

## Fases de Implementación
[Entregables incrementales]
```

### Formato de Historia de Usuario

```markdown
### HU-001: [Título descriptivo]

**Como** [rol del usuario]
**Quiero** [acción o funcionalidad]
**Para** [beneficio o valor]

**Criterios de Aceptación:**
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

**Tareas Técnicas:**
- [ ] Tarea 1
- [ ] Tarea 2
- [ ] Tarea 3

**Estimación:** [S/M/L/XL]
```

---

## Patrones de Código

### Estructura de Proyecto (Python/FastAPI)

```text
project/
├── app/
│   ├── core/           # Config, security, exceptions
│   ├── api/            # Routers/endpoints
│   ├── services/       # Lógica de negocio
│   ├── models/         # Modelos de dominio
│   ├── schemas/        # Pydantic DTOs
│   ├── db/             # Database, repositories
│   └── main.py
├── tests/
├── scripts/
├── docs/
└── requirements.txt
```

### Estructura de Proyecto (Node/NestJS)

```text
project/
├── src/
│   ├── common/         # Shared utilities
│   ├── config/         # Configuration
│   ├── modules/        # Feature modules
│   │   └── feature/
│   │       ├── dto/
│   │       ├── entities/
│   │       ├── feature.controller.ts
│   │       ├── feature.service.ts
│   │       └── feature.module.ts
│   └── main.ts
├── test/
└── package.json
```

### Convenciones de Naming

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Archivos Python | snake_case | `user_service.py` |
| Archivos TS/JS | kebab-case o camelCase | `user-service.ts` |
| Clases | PascalCase | `UserService` |
| Funciones | snake_case (Py) / camelCase (JS) | `get_user()` / `getUser()` |
| Variables | snake_case (Py) / camelCase (JS) | `user_id` / `userId` |
| Constantes | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Tablas DB | snake_case plural | `users`, `order_items` |

---

## Testing

### Filosofía TDD (Test-Driven Development)

**Los tests PRIMERO, el código después.**

El ciclo TDD:
1. **Red**: Escribir un test que falla (porque la funcionalidad no existe)
2. **Green**: Implementar el código mínimo para pasar el test
3. **Refactor**: Mejorar el código manteniendo los tests verdes

### Por qué TDD

- **Tests como especificación**: El test documenta el comportamiento esperado
- **Regression testing**: Si un test existente falla, la nueva implementación rompió algo
- **Diseño guiado**: Pensar en el API antes de implementar fuerza mejor diseño
- **Seguridad en refactor**: Cambios seguros con red de tests

### Estrategia de Testing

1. **Unit tests**: Lógica de negocio aislada (mock de dependencias externas)
2. **Integration tests**: APIs con DB real/mock
3. **E2E tests**: Flujos completos (selectivos, solo críticos)

### Frameworks Recomendados

| Lenguaje | Framework | Uso |
|----------|-----------|-----|
| Python | pytest + pytest-asyncio | Unit/Integration tests |
| Python | pytest-mock | Mocking |
| TypeScript | vitest | Unit tests (rápido, nativo ESM) |
| TypeScript | jest | Alternativa tradicional |
| TypeScript | supertest | Integration tests HTTP |

### Cobertura Mínima

- Services: 80%+
- Utils/Helpers: 90%+
- Routers: 70%+ (integration)

### Pre-commit Requirements

Antes de hacer push de cambios, SIEMPRE:

1. **Ejecutar todos los tests**: `pytest` / `npm test`
2. **Verificar cobertura**: `pytest --cov` / `npm run test:cov`
3. **Linting**: `ruff check` / `eslint .`
4. **Type checking**: `mypy` / `tsc --noEmit`

Si algún test falla, no commitear. Fix primero.

### Regression Testing

Cuando un test existente falla tras un cambio:

- **No desactivar el test** - eso oculta un bug real
- **Investigar por qué falla**:
  - ¿El cambio rompió funcionalidad existente? → Fix del código
  - ¿El comportamiento requerido cambió intencionalmente? → Actualizar el test
  - ¿El test estaba mal escrito? → Corregir el test

### Impact Analysis

Antes de implementar cambios:

1. **Identificar dependientes**: ¿Qué otros servicios/componentes usan este código?
2. **Tests de integración**: Verificar que los contratos no se rompan
3. **Versionado**: Si el cambio es breaking, actualizar versión y comunicar

```bash
# Ejemplo de pre-commit hook (pytest)
pytest --cov=app --cov-fail-under=80
```

---

## Git

### Commits

Formato: `tipo(scope): descripción`

Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

Ejemplos:
- `feat(auth): add JWT refresh token`
- `fix(api): handle null response from external service`
- `refactor(db): extract repository pattern`

### Branches

- `main` / `master`: Producción
- `develop`: Integración
- `feature/HU-001-descripcion`: Features
- `fix/issue-descripcion`: Bugfixes
- `hotfix/descripcion`: Fixes urgentes a producción

---

## Seguridad

### Principios OWASP Top 10

- Validación de inputs en todos los endpoints
- Sanitización de datos para prevenir XSS, SQL Injection
- Autenticación robusta (JWT, OAuth2)
- Autorización por roles/resources (RBAC)
- Gestión segura de secrets (environment variables, vault)
- Headers de seguridad (CORS, CSP, HSTS)

### Autenticación/Authorization Patterns

| Patrón | Uso |
|--------|-----|
| JWT + Refresh tokens | APIs stateless, microservicios |
| Session + Redis | APIs tradicionales, monolitos |
| OAuth2 / OIDC | Integración con terceros, SSO |
| API Keys | Servicios internos, webhooks |

### Secret Management

- Nunca commitear secrets en el repo
- Usar `.env` files para desarrollo (en `.gitignore`)
- Usar vault services para producción (Azure Key Vault, AWS Secrets Manager)
- Rotar credentials regularmente

---

## Debug & Producción

### Logging Strategy

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| DEBUG | Desarrollo, tracing detallado | Variable values, execution flow |
| INFO | Eventos importantes de negocio | User login, order created |
| WARNING | Situaciones anómalas no críticas | Retry attempt, deprecated usage |
| ERROR | Errores que no requieren intervención | API timeout, DB connection lost |
| CRITICAL | Errores que requieren intervención inmediata | Service down, data corruption |

### Error Handling Patterns

```python
# Python/FastAPI
try:
    # operación
except BusinessLogicException as e:
    raise HTTPException(status_code=400, detail=str(e))
except DatabaseError as e:
    logger.error(f"DB error: {e}")
    raise HTTPException(status_code=503, detail="Service unavailable")
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal error")
```

```typescript
// Node/NestJS
try {
  // operación
} catch (error) {
  if (error instanceof BusinessLogicException) {
    throw new BadRequestException(error.message);
  }
  logger.error(`Unexpected error: ${error}`);
  throw new InternalServerErrorException('Internal error');
}
```

### Observability

- **Metrics**: Prometheus + Grafana (latencia, throughput, errores)
- **Tracing**: OpenTelemetry / Jaeger (distributed tracing)
- **Logs**: Structured logging (JSON) + ELK / Loki
- **Alerts**: PagerDuty / OpsGenie para incidentes críticos

---

## Configuración de Modelos AI

### Estrategia de Uso de Modelos (GLM Coding Lite - z.ai)

Plan Lite ($3/mes): ~120 prompts cada 5 horas

| Tipo de Tarea | Modelo | Uso |
|---------------|--------|-----|
| Planificación arquitectónica | `glm-4.7` | Máximo razonamiento para decisiones críticas |
| Desarrollo principal | `glm-4.7` | Coding, debugging, refactor |
| Code review | `glm-4.7` | Calidad y capacidad de procesamiento |
| Review de PRs | `glm-4.7` | Análisis de cambios |
| Exploración de codebase | `glm-4.5-Air` | Búsquedas rápidas |
| Comandos CLI | `glm-4.7` | Buen razonamiento para ops críticas |
| Tareas triviales (commit, docs) | `glm-4.5-Air` | Mínimo costo para operaciones simples |

### Consideraciones

- Solo 2 modelos disponibles: `glm-4.7` y `glm-4.5-Air`
- `glm-4.7` para tareas que requieren razonamiento complejo
- `glm-4.5-Air` para tareas simples y operaciones rápidas
- Límite de 120 prompts cada 5 horas (resetea automáticamente)
