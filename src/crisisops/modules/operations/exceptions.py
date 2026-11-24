from crisisops.core.exceptions import DomainError


class EmergencyNotFound(DomainError):
    """La emergencia indicada no existe en Grupo A."""

    status_code = 422


class EmergencyNotActive(DomainError):
    """La emergencia existe, pero su estado no permite crear operaciones."""

    status_code = 409


class EmergencyUnavailable(DomainError):
    """No se pudo consultar a Grupo A (caído o aún no integrado)."""

    status_code = 503


class OperationNotFound(DomainError):
    """No existe una operación con el id consultado."""

    status_code = 404


class MissionNotFound(DomainError):
    """No existe una misión con el id consultado."""

    status_code = 404


class InvalidCatalogItem(DomainError):
    """El tipo de recurso o perfil no existe en el catálogo de Grupo B o C."""

    status_code = 422


class CatalogUnavailable(DomainError):
    """No se pudo consultar el catálogo de Grupo B o C."""

    status_code = 503
