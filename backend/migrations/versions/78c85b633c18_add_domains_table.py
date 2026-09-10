"""add domains table

Revision ID: 78c85b633c18
Revises: 0001_identity_and_scans
Create Date: 2026-08-29 17:24:48.946924
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '78c85b633c18'
down_revision: Union[str, Sequence[str], None] = '0001_identity_and_scans'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "domains",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_domains_name", "domains", ["name"], unique=True)

def downgrade() -> None:
    op.drop_index("ix_domains_name", table_name="domains")
    op.drop_table("domains")
