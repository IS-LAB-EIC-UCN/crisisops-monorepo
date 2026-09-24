from fastapi import APIRouter

router = APIRouter(prefix="/personnel", tags=["Grupo C - Personal y brigadas"])


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "personnel"}
