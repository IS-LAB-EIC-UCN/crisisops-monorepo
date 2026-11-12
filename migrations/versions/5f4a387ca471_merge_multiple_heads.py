"""merge multiple heads

Revision ID: 5f4a387ca471
Revises: bc10ef008022, d233560baa9d
Create Date: 2026-11-12 12:01:07.975036
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5f4a387ca471'
down_revision: Union[str, Sequence[str], None] = ('bc10ef008022', 'd233560baa9d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
