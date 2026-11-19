def get_emergency_status_from_group_a(emergency_id: int) -> str | None:
    """Consulta el estado en Grupo A. Mientras A no esté integrado en develop, no responde."""
    raise ConnectionError("El módulo de emergencias (Grupo A) aún no está integrado.")


def get_resource_types_from_group_b() -> set[str]:
    """Consulta los tipos de recurso de Grupo B. Mientras B no los exponga, no responde."""
    raise ConnectionError("El catálogo de tipos de recurso (Grupo B) aún no está disponible.")


def get_personnel_profiles_from_group_c() -> set[str]:
    """Consulta los perfiles (skills) de Grupo C. Mientras C no los exponga, no responde."""
    raise ConnectionError("El catálogo de perfiles de personal (Grupo C) aún no está disponible.")
