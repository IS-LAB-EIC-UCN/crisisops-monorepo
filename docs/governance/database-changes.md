# Convención de cambios de base de datos

La base de datos es infraestructura común, aunque cada tabla tenga un módulo propietario.

## Propiedad

- Grupo A: tablas de `emergencies`.
- Grupo B: tablas de `resources`.
- Grupo C: tablas de `personnel`.
- Grupo D: tablas de `operations`.
- Grupo E: tablas de `evacuation` / `shelters` / `alerts`.
- `core`, `shared`, autenticación, auditoría y decisiones transversales: Comité de Arquitectura.

## Regla Importante

Un grupo puede cambiar sus propios modelos. No debe cambiar directamente modelos o tablas de otro
módulo. Una referencia entre módulos se hace mediante identificadores y contratos explícitos; una
FK/relación ORM cruzada requiere acuerdo documentado.

## Flujo para una migración

1. Crear/relacionar un issue.
2. Si el cambio afecta más de un módulo, crear ADR o propuesta `common-change`.
3. Actualizar `develop` antes de generar la migración.
4. Modificar el modelo ORM propietario.
5. Generar migración:
   `alembic revision --autogenerate -m "GA-123 add emergency status"`.
6. Revisar manualmente `upgrade()` y `downgrade()`. No aceptar autogenerate a ciegas.
7. Ejecutar `alembic upgrade head` en una BD limpia y correr las pruebas.
8. Abrir PR con etiqueta `db-change`.
9. Toda modificación de `migrations/**` requiere revisión del Comité de Arquitectura.
10. Antes de mergear, actualizar nuevamente desde `develop`.

## Migraciones concurrentes

Si dos PR crean migraciones desde el mismo `down_revision`, Alembic puede producir múltiples heads.
La política del curso será **evitarlos antes del merge**: el segundo PR se actualiza con `develop` y
regenera/ajusta su migración sobre el head vigente. Si no es razonable, el Comité de Arquitectura
decide si corresponde crear una migración de merge (`alembic merge`).

## Nombres

Mensaje recomendado:

`G<grupo>-<issue> <verbo> <objeto>`

Ejemplos:

- `GA-42 add affected_zone table`
- `GB-18 add resource availability index`
- `COMMON-7 add audit actor columns`

## Prohibido

- editar la BD manualmente y no registrar migración;
- borrar/reescribir una migración que ya llegó a `develop`;
- cambiar tablas de otro grupo sin aprobación;
- subir datos reales o secretos.
