from functools import partial
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from crisisops.core.database import get_db
from crisisops.modules.operations.integrations import (
    get_emergency_status_from_group_a,
    get_personnel_profiles_from_group_c,
    get_resource_types_from_group_b,
)
from crisisops.modules.operations.repository.mission import MissionsRepository
from crisisops.modules.operations.repository.operation import OperationsRepository
from crisisops.modules.operations.service.mission import MissionsService
from crisisops.modules.operations.service.operation import OperationsService


def get_operations_service(
    db: Annotated[Session, Depends(get_db)],
) -> OperationsService:
    """Crea el caso de uso para cada petición usando el repositorio local."""
    repository = OperationsRepository(db)
    return OperationsService(
        partial(get_emergency_status_from_group_a, db),
        repository,
        get_resource_types=get_resource_types_from_group_b,
        get_personnel_profiles=get_personnel_profiles_from_group_c,
    )


def get_missions_service(
    db: Annotated[Session, Depends(get_db)],
) -> MissionsService:
    """Igual que get_operations_service, pero con el service y repositorio de misiones."""
    repository = MissionsRepository(db)
    return MissionsService(
        partial(get_emergency_status_from_group_a, db),
        repository,
        get_resource_types=get_resource_types_from_group_b,
        get_personnel_profiles=get_personnel_profiles_from_group_c,
    )


ServiceDEP = Annotated[OperationsService, Depends(get_operations_service)]
MissionsServiceDEP = Annotated[MissionsService, Depends(get_missions_service)]
