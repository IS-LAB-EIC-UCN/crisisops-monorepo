from fastapi import APIRouter

router = APIRouter(prefix="/emergencies", tags=["Grupo A - Emergencias y evaluación"])


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "emergencies"}
