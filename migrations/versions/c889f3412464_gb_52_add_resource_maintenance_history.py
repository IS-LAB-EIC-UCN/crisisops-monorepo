"""GB-52 add resource maintenance history

Revision ID: c889f3412464
Revises: 5f4a387ca471
Create Date: 2026-11-12 12:28:32.501622
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c889f3412464'
down_revision: Union[str, Sequence[str], None] = '5f4a387ca471'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'historial_mantenimiento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_recursos', sa.Integer(), nullable=False),
        sa.Column('estado_anterior', sa.String(length=30), nullable=False),
        sa.Column('estado_nuevo', sa.String(length=30), nullable=False),
        sa.Column('fecha_mantenimiento', sa.DateTime(timezone=True), nullable=False),
        sa.Column('descripcion', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['id_recursos'], ['recursos.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('historial_mantenimiento')
