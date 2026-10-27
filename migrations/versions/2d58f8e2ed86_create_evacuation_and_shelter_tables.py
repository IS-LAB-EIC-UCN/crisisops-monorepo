"""create evacuation and shelter tables

Revision ID: 2d58f8e2ed86
Revises:
Create Date: 2026-10-26 22:39:32.790518
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2d58f8e2ed86'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('evacuation_orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('emergency_id', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('people_in_motion', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evacuation_orders_emergency_id'), 'evacuation_orders', ['emergency_id'], unique=False)
    op.create_index(op.f('ix_evacuation_orders_id'), 'evacuation_orders', ['id'], unique=False)
    op.create_table('shelters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('location', sa.String(length=150), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('current_occupancy', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shelters_id'), 'shelters', ['id'], unique=False)
    op.create_table('people_movement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('emergency_id', sa.Integer(), nullable=True),
    sa.Column('shelter_id', sa.Integer(), nullable=True),
    sa.Column('people_count', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=150), nullable=False),
    sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['shelter_id'], ['shelters.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_people_movement_id'), 'people_movement', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_people_movement_id'), table_name='people_movement')
    op.drop_table('people_movement')
    op.drop_index(op.f('ix_shelters_id'), table_name='shelters')
    op.drop_table('shelters')
    op.drop_index(op.f('ix_evacuation_orders_id'), table_name='evacuation_orders')
    op.drop_index(op.f('ix_evacuation_orders_emergency_id'), table_name='evacuation_orders')
    op.drop_table('evacuation_orders')
