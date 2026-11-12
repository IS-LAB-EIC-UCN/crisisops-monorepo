# Grupo A — Emergencias y evaluación

Este directorio es propiedad del **Grupo A**.

## Panel temporal y consulta (HU-02)

Con la API en ejecución, abrir `http://localhost:8000/api/v1/emergencies/panel`.
La sección «Consultar Emergencia» consulta un identificador real mediante
`GET /api/v1/emergencies/{id}` y muestra estado, severidad y última actualización.
Si no hay severidad asignada, muestra «Sin asignar».

Abrir el panel mediante esa ruta, no directamente como archivo: así comparte
origen con la API y no necesita una configuración CORS adicional.
El formulario de registro y validación sigue siendo una demostración local;
sus identificadores `LOCAL-*` no corresponden a registros de la base de datos.
Para probar la consulta, registrar primero una emergencia mediante la API
(por ejemplo, desde `/docs`) y utilizar el identificador numérico devuelto.

Estructura recomendada:

- `router.py`: recepción HTTP y traducción de errores.
- `service.py`: casos de uso y reglas de negocio.
- `repository.py`: persistencia.
- `models.py`: modelos ORM del dominio.
- `schemas.py`: contratos Pydantic.

No se debe implementar lógica de negocio de otros módulos aquí. La integración
se realiza mediante contratos explícitos.
