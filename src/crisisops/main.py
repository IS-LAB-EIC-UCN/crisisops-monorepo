from fastapi import FastAPI

from crisisops.core.config import get_settings
from crisisops.modules.emergencies.router import router as emergencies_router
from crisisops.modules.evacuation.router import router as evacuation_router
from crisisops.modules.operations.router import router as operations_router
from crisisops.modules.personnel.router import router as personnel_router
from crisisops.modules.resources.router import router as resources_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API común del proyecto académico CrisisOps.",
)


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok", "application": settings.app_name}


for module_router in (
    emergencies_router,
    resources_router,
    personnel_router,
    operations_router,
    evacuation_router,
):
    app.include_router(module_router, prefix=settings.api_v1_prefix)
