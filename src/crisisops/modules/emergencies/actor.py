"""
Identifica el actor que ejecuta una acción sin autentificación
El cliente envía su usuario mediante la cabacera 'X-Actor'.
Este dato no se verifica, por lo que solo sirve para auditoría.
"""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Header

from crisisops.modules.emergencies.enums import Role

ACTOR_PATTERN = r"^[A-Za-z0-9_.-]{3,50}$"

@dataclass(frozen=True)
class CurrentUser:
    username: str
    role: Role

def get_current_user(
        x_actor: Annotated[
            str, 
            Header(
                pattern=ACTOR_PATTERN,
                description="Usuario que ejecuta la acción (sin verificar; solo para\
                solo para auditoría).",
            ),
        ], 
        x_actor_role: Annotated[
            Role, 
            Header(
                description="Rol con el que actuá (sin verificar): OPERATOR, COORDINATOR o \
                SUPERVISOR"
            ),
        ],
) -> CurrentUser:
    return CurrentUser(username=x_actor, role=x_actor_role)