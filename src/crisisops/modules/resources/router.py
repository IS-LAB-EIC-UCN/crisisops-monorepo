from fastapi import APIRouter

router = APIRouter(prefix="/resources", tags=["Grupo B - Recursos y equipamiento"])


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "resources"}
