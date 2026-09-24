# Configuración recomendada en GitHub

## Equipos de la organización

Crear:

- `grupo-a`, `grupo-b`, `grupo-c`, `grupo-d`, `grupo-e`
- `arquitectura` (un representante por grupo + docentes)
- `docentes`

Todos los estudiantes necesitan lectura del repositorio. Los equipos de estudiantes pueden tener
permiso `Write`; la protección real se implementa con PR, CODEOWNERS y reglas.

## Ramas

- `main`: versión estable / hitos.
- `develop`: integración del semestre.
- `gA/<issue>-descripcion`, ..., `gE/<issue>-descripcion`: trabajo de grupos.
- `common/<issue>-descripcion`: cambios transversales aprobados.

No se permite push directo a `main` ni `develop`.

## Ruleset para `main` y `develop`

Activar:

- Require a pull request before merging.
- Require at least 1 approval (2 para cambios comunes si se desea).
- Require review from Code Owners.
- Dismiss stale approvals when new commits are pushed.
- Require status checks: `quality` y `scope`.
- Block force pushes.
- Block deletions.

## CODEOWNERS

Copiar `.github/CODEOWNERS.template` a `.github/CODEOWNERS` y sustituir `TU_ORG`.

CODEOWNERS controla quién debe aprobar un cambio antes del merge; no es, por sí solo, una
restricción de escritura por carpeta.

## Restricción fuerte por carpeta (si el plan de GitHub la ofrece)

Usar **push rulesets** por módulo:

- proteger `src/crisisops/modules/emergencies/**` y `tests/emergencies/**`; bypass: `grupo-a`, `docentes`;
- proteger `resources/**`; bypass: `grupo-b`, `docentes`;
- repetir para C, D y E;
- proteger `core/**`, `shared/**`, `migrations/**`, `.github/**` y archivos raíz comunes; bypass:
  `arquitectura`, `docentes`.

Así un integrante de A no puede empujar cambios al módulo B. Los cambios comunes se realizan mediante
el flujo `common/*` y aprobación del Comité de Arquitectura.

Si el plan no dispone de push rulesets para el repositorio privado, mantenga la restricción a nivel de
merge con ramas protegidas + CODEOWNERS. GitHub no ofrece permisos de escritura por carpeta mediante
los permisos normales del repositorio.

## Check automático de alcance

El repositorio incluye el workflow `Scope check`. En PRs con ramas `gA/*` ... `gE/*`, el check falla
si el diff contiene archivos fuera del módulo y tests del grupo. Márquelo también como **required
status check** en `main` y `develop`.

Este check controla lo que puede **integrarse** aunque un estudiante pueda crear commits locales o en
una rama. La restricción física del push por carpeta requiere push rulesets; ambas medidas se pueden
usar juntas.
