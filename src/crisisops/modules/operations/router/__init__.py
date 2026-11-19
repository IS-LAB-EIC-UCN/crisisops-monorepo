from fastapi import APIRouter

from crisisops.modules.operations.router import missions, operations

router = APIRouter()
router.include_router(operations.router)
router.include_router(missions.router)
