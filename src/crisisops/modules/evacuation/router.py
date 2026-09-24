from fastapi import APIRouter

router = APIRouter(prefix="/evacuation", tags=["Grupo E - Evacuación, refugios y alertas"])


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "evacuation"}
