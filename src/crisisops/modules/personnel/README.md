# Grupo C — Personal y brigadas

Este directorio es propiedad del **Grupo C**.

Estructura recomendada:

- `router.py`: recepción HTTP y traducción de errores.
- `service.py`: casos de uso y reglas de negocio.
- `repository.py`: persistencia.
- `models.py`: modelos ORM del dominio.
- `schemas.py`: contratos Pydantic.

No se debe implementar lógica de negocio de otros módulos aquí. La integración
se realiza mediante contratos explícitos.
