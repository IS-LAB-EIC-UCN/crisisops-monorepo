"""create personnel tables

Revision ID: 38b56a7bd496
Revises:
Create Date: 2026-10-24 15:15:29.106771
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '38b56a7bd496'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('responders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('badge_number', sa.String(length=20), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('badge_number')
    )
    op.create_table('skills',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('requires_certification', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('certifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('responder_id', sa.Integer(), nullable=False),
    sa.Column('skill_code', sa.String(length=50), nullable=False),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['responder_id'], ['responders.id'], ),
    sa.ForeignKeyConstraint(['skill_code'], ['skills.code'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('responder_skills',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('responder_id', sa.Integer(), nullable=False),
    sa.Column('skill_code', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['responder_id'], ['responders.id'], ),
    sa.ForeignKeyConstraint(['skill_code'], ['skills.code'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('responder_id', 'skill_code')
    )
    op.create_table('shifts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('responder_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['responder_id'], ['responders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('personnel_assignments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('responder_id', sa.Integer(), nullable=False, index=True),
    sa.Column('mission_id', sa.Integer(), nullable=True),
    sa.Column('start_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.CheckConstraint('start_at < end_at', name='ck_assignment_start_before_end'),
    sa.ForeignKeyConstraint(['responder_id'], ['responders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('personnel_assignments')
    op.drop_table('shifts')
    op.drop_table('responder_skills')
    op.drop_table('certifications')
    op.drop_table('skills')
    op.drop_table('responders')
