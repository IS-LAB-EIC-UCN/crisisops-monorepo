from fastapi import APIRouter

router = APIRouter(prefix="/operations", tags=["Grupo D - Operaciones y despacho"])


@router.get("/health")
def module_health() -> dict[str, str]:
    """Endpoint mínimo para verificar que el módulo quedó integrado."""
    return {"status": "ok", "module": "operations"}
