# Contribución

## Alcance por grupo

| Grupo | Código propietario | Tests propietarios |
|---|---|---|
| A | `src/crisisops/modules/emergencies/**` | `tests/emergencies/**` |
| B | `src/crisisops/modules/resources/**` | `tests/resources/**` |
| C | `src/crisisops/modules/personnel/**` | `tests/personnel/**` |
| D | `src/crisisops/modules/operations/**` | `tests/operations/**` |
| E | `src/crisisops/modules/evacuation/**` | `tests/evacuation/**` |

Los demás paths se consideran comunes.

## Flujo normal

1. Crear issue.
2. Actualizar `develop`.
3. Crear rama `gX/<issue>-descripcion`.
4. Implementar solo dentro del scope del grupo.
5. Agregar pruebas.
6. `ruff check src tests` y `pytest`.
7. Push y Pull Request hacia `develop`.
8. Esperar CI y revisión.
9. Merge solo cuando los checks y revisiones requeridas estén aprobados.

## Commits

Convención sugerida (Conventional Commits):

- `feat(emergencies): add emergency validation`
- `fix(resources): prevent double reservation`
- `test(personnel): cover expired certification`
- `docs(common): document cross-module contract`
- `refactor(operations): isolate dispatch service`

## Cambios comunes

No mezclar un cambio común grande dentro de un PR funcional de un grupo.

1. Abrir issue `COMMON-*`.
2. Explicar impacto en módulos.
3. Si cambia arquitectura/contrato, agregar ADR.
4. Rama `common/<issue>-descripcion`.
5. Revisión obligatoria del Comité de Arquitectura.
6. Si cambia BD, seguir `docs/governance/database-changes.md`.
