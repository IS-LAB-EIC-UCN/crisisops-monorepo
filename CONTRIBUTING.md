# Contribución a CrisisOps

Este repositorio es un **monorepo** compartido por los equipos del Proyecto
Integrador. Cada grupo es responsable de un subproyecto y debe respetar los
límites de código definidos en este documento y validados automáticamente por
GitHub Actions.

## 1. Ramas protegidas

Las ramas `main` y `develop` son ramas protegidas.

- No se trabaja directamente sobre `main`.
- No se trabaja directamente sobre `develop`.
- Todo cambio entra mediante Pull Request.
- Los Pull Requests de los grupos se dirigen a `develop`.
- El paso `develop -> main` se realiza únicamente como integración estable.
- No se permiten force-pushes sobre `main` ni `develop`.

## 2. Alcance por grupo

| Grupo | Prefijo de rama | Código propietario | Tests propietarios |
|---|---|---|---|
| A | `gA/` | `src/crisisops/modules/emergencies/**` | `tests/emergencies/**` |
| B | `gB/` | `src/crisisops/modules/resources/**` | `tests/resources/**` |
| C | `gC/` | `src/crisisops/modules/personnel/**` | `tests/personnel/**` |
| D | `gD/` | `src/crisisops/modules/operations/**` | `tests/operations/**` |
| E | `gE/` | `src/crisisops/modules/evacuation/**` | `tests/evacuation/**` |

Una rama de grupo solo puede modificar el código y los tests correspondientes a
su propio módulo. El workflow `Scope check` valida esta regla en cada Pull
Request hacia `develop`.

## 3. Convención de ramas

Toda rama debe crearse desde `develop` actualizado.

Formato:

```text
gA/<issue>-descripcion
gB/<issue>-descripcion
gC/<issue>-descripcion
gD/<issue>-descripcion
gE/<issue>-descripcion
common/<issue>-descripcion
```

Ejemplos:

```text
gA/23-register-emergency
gB/31-resource-availability
gC/18-person-certification
gD/42-create-mission
gE/27-shelter-admission
common/56-add-audit-fields
```

No se aceptan ramas sin descripción, por ejemplo `gA` o `gA/`.

## 4. Flujo normal de trabajo

1. Crear o seleccionar un Issue.
2. Actualizar la copia local de `develop`:

   ```bash
   git checkout develop
   git pull origin develop
   ```

3. Crear la rama de trabajo:

   ```bash
   git checkout -b gA/23-register-emergency
   ```

4. Implementar únicamente dentro del scope del grupo.
5. Agregar o actualizar pruebas.
6. Ejecutar localmente:

   ```bash
   ruff check src tests scripts
   pytest
   ```

7. Crear commits pequeños y descriptivos.
8. Hacer push de la rama.
9. Abrir Pull Request hacia `develop`.
10. Esperar que pasen los checks `quality` y `scope`.
11. Resolver observaciones y conversaciones del Pull Request.
12. Hacer merge solo cuando se cumplan las revisiones exigidas por el ruleset.

## 5. Commits

Se usa la convención **Conventional Commits**.

Ejemplos:

```text
feat(emergencies): add emergency validation
fix(resources): prevent double reservation
test(personnel): cover expired certification
feat(operations): create mission endpoint
fix(evacuation): prevent shelter overcapacity
docs(common): document cross-module contract
refactor(common): simplify database session handling
```

No usar mensajes genéricos como `cambios`, `avance`, `fix` o `update`.

## 6. Pull Requests

Todo Pull Request debe:

- estar asociado a un Issue;
- tener un objetivo acotado;
- indicar qué se cambió y por qué;
- incluir pruebas cuando corresponda;
- pasar `quality`;
- pasar `scope` cuando el destino sea `develop`;
- respetar `CODEOWNERS`;
- mantener las conversaciones de revisión resueltas antes del merge.

No se deben mezclar funcionalidades no relacionadas en un mismo Pull Request.

## 7. Cambios comunes

Los cambios transversales se realizan en ramas:

```text
common/<issue>-descripcion
```

El scope común incluye únicamente los artefactos autorizados por
`scripts/check_scope.py`, por ejemplo:

- `src/crisisops/core/**`;
- `src/crisisops/shared/**`;
- `migrations/**`;
- `docs/adr/**`;
- `docs/governance/**`;
- `ARCHITECTURE.md`;
- `alembic.ini`;
- `pyproject.toml`;
- `Dockerfile`;
- `docker-compose.yml`.

Los cambios comunes requieren revisión de `arquitectura` según `CODEOWNERS`.

No se debe usar una rama `common/*` para modificar libremente el código
propietario de otro grupo.

## 8. Cambios de base de datos

La base de datos es compartida y su esquema es un artefacto común.

Reglas:

1. Nunca modificar manualmente el esquema de la base de datos compartida.
2. Todo cambio de esquema debe tener una migración Alembic versionada.
3. Abrir un Issue `COMMON-*` explicando:
   - motivo del cambio;
   - tablas/columnas afectadas;
   - módulos afectados;
   - compatibilidad esperada;
   - estrategia de migración o reversión.
4. La migración se implementa en una rama `common/*`.
5. El cambio requiere revisión del equipo `arquitectura`.
6. Si el cambio de esquema también exige modificar código propietario de un
   módulo, crear Pull Requests coordinados y enlazados:
   - PR común para migración/contrato;
   - PR del grupo para el código del módulo.
7. Preferir cambios compatibles y aditivos. Para renombres o eliminaciones,
   aplicar una estrategia de expansión/migración/limpieza en pasos separados.

Consultar además `docs/governance/database-changes.md`.

## 9. Decisiones arquitectónicas

Una decisión que afecte a más de un módulo, un contrato compartido, la
persistencia, la infraestructura o el despliegue debe documentarse como ADR
cuando corresponda.

Los ADR se almacenan en:

```text
docs/adr/
```

y se modifican mediante ramas `common/*`.

## 10. Archivos de gobierno

Los estudiantes no deben modificar como parte de una feature:

```text
.github/**
scripts/check_scope.py
CONTRIBUTING.md
```

Estos archivos están bajo propiedad del equipo `profesor` mediante
`CODEOWNERS`.

## 11. Definición mínima de terminado

Una historia se considera lista para integrar cuando:

- cumple sus criterios de aceptación;
- tiene pruebas suficientes;
- `ruff` no reporta errores;
- `pytest` pasa;
- no modifica archivos fuera de su scope;
- el Pull Request está actualizado y revisado;
- los checks obligatorios están en verde;
- las conversaciones de revisión están resueltas.

## 12. Integración a `main`

Los equipos no integran directamente a `main`.

La ruta normal es:

```text
gA/... ─┐
gB/... ─┤
gC/... ─┼──> develop ───> main
gD/... ─┤
gE/... ─┘
common/ ─┘
```

`main` representa una versión estable e integrada del sistema.
