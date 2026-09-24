## Qué cambia

Describe brevemente el cambio.

## Alcance

- [ ] Solo modifica el módulo de mi grupo.
- [ ] Modifica código común (requiere revisión del Comité de Arquitectura).
- [ ] Modifica esquema/migración de base de datos (requiere etiqueta `db-change`).

## Trazabilidad

Issue / historia / requisito: #

## Evidencia

- [ ] Pruebas agregadas o actualizadas.
- [ ] `ruff check src tests` pasa.
- [ ] `pytest` pasa.
- [ ] OpenAPI/documentación actualizada si corresponde.

## Si hay cambio de BD

- [ ] La migración fue generada con Alembic.
- [ ] No modifica tablas propiedad de otro grupo sin acuerdo.
- [ ] Se documenta compatibilidad y rollback.
- [ ] Revisado por el Comité de Arquitectura.
