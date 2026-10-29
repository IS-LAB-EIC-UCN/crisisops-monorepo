"""add shelter admissions table

Revision ID: e4c22f40d573
Revises: 2d58f8e2ed86
Create Date: 2026-10-28 19:36:34.807432
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e4c22f40d573'
down_revision: Union[str, Sequence[str], None] = '2d58f8e2ed86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('shelter_admissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shelter_id', sa.Integer(), nullable=False),
    sa.Column('evacuee_code', sa.String(length=50), nullable=False),
    sa.Column('people_count', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('admitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('departed_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('people_count > 0', name='ck_shelter_admissions_people_count_positive'),
    sa.ForeignKeyConstraint(['shelter_id'], ['shelters.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shelter_admissions_id'), 'shelter_admissions', ['id'], unique=False)
    op.create_index(op.f('ix_shelter_admissions_shelter_id'), 'shelter_admissions', ['shelter_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_shelter_admissions_shelter_id'), table_name='shelter_admissions')
    op.drop_index(op.f('ix_shelter_admissions_id'), table_name='shelter_admissions')
    op.drop_table('shelter_admissions')
