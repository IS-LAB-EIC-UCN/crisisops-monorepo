# CrisisOps — Monorepo inicial

Proyecto común para **ECIN-00619 — Proyecto Integrador de Software**.

La arquitectura inicial es un **monolito modular** en Python/FastAPI. Cada grupo es propietario de un
módulo, pero todos construyen un único producto integrado.

## Módulos

| Grupo | Módulo | Ruta |
|---|---|---|
| A | Emergencias y evaluación | `src/crisisops/modules/emergencies/` |
| B | Recursos y equipamiento | `src/crisisops/modules/resources/` |
| C | Personal y brigadas | `src/crisisops/modules/personnel/` |
| D | Operaciones y despacho | `src/crisisops/modules/operations/` |
| E | Evacuación, refugios y alertas | `src/crisisops/modules/evacuation/` |

Código común: `src/crisisops/core/`, `src/crisisops/shared/`, `migrations/` y configuración raíz.

## Requisitos

- Python 3.11+
- Docker / Docker Compose (recomendado para PostgreSQL)

## Inicio rápido local

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\\Scripts\\activate      # Windows
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn crisisops.main:app --reload
```

Abrir:

- API: `http://localhost:8000`
- OpenAPI/Swagger: `http://localhost:8000/docs`

## Inicio con Docker

```bash
docker compose up --build
```

## Calidad

```bash
ruff check src tests
pytest --cov=crisisops --cov-report=term-missing
```

## Base de datos

```bash
alembic revision --autogenerate -m "GA-123 descripcion"
alembic upgrade head
```

Lea antes: `docs/governance/database-changes.md`.

## Gobierno GitHub

Lea `docs/governance/github-setup.md` y `CONTRIBUTING.md`. El archivo
`.github/CODEOWNERS.template` debe adaptarse al nombre real de la organización.

## Regla principal

Un grupo modifica su módulo. Los cambios transversales no se hacen informalmente: issue común + PR +
revisión del Comité de Arquitectura; si alteran contratos/arquitectura, ADR; si alteran la BD, Alembic.
