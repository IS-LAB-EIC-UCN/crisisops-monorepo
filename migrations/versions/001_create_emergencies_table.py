"""create emergencies table

Revision ID: 0001
Revises:
Create Date: 2026-10-28

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "emergencies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "FIRE", "FLOOD", "EARTHQUAKE", "LANDSLIDE", "MAJOR_ACCIDENT", "HAZMAT", "OTHER",
                name="emergencytype", native_enum=False, length=30,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=150), nullable=True),
        sa.Column("type_detail", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location_description", sa.String(length=250), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "REPORTED", "VALIDATED", "REJECTED", "ACTIVE", "CONTROLLED", "CLOSED", "CANCELLED",
                name="emergencystatus", native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum(
                "LOW", "MEDIUM", "HIGH", "CRITICAL",
                name="severity", native_enum=False, length=30,
            ),
            nullable=True,
        ),
        sa.Column("date_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reported_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("emergencies")