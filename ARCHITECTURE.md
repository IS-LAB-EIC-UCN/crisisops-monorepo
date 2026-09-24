# Arquitectura inicial

CrisisOps comienza como **monolito modular**: una aplicación FastAPI y una base PostgreSQL, con límites
explícitos por dominio.

```text
FastAPI
  |
  +-- Grupo A: emergencies
  +-- Grupo B: resources
  +-- Grupo C: personnel
  +-- Grupo D: operations
  +-- Grupo E: evacuation
  |
  +-- core/shared (gobierno común)
  |
PostgreSQL
```

Dentro de cada módulo:

```text
router -> service -> repository -> SQLAlchemy/PostgreSQL
```

## Reglas

1. El `router` no contiene reglas de negocio.
2. Cada módulo es dueño de sus tablas y reglas.
3. Un módulo no reutiliza directamente el repository de otro módulo.
4. Integraciones mediante servicios/contratos explícitos.
5. Código común pequeño y deliberado; no usar `shared` como cajón de sastre.
6. Toda decisión transversal significativa se documenta en un ADR.
