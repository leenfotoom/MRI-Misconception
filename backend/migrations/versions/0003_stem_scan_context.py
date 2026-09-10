"""add STEM domain and topic context to scans

Revision ID: 0003_stem_scan_context
Revises: 78c85b633c18
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_stem_scan_context"
down_revision = "78c85b633c18"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scans",
        sa.Column("domain", sa.String(40), nullable=False, server_default="science"),
    )
    op.add_column(
        "scans",
        sa.Column("topic", sa.String(120), nullable=False, server_default="Electricity"),
    )
    op.create_index("ix_scans_domain", "scans", ["domain"])


def downgrade() -> None:
    op.drop_index("ix_scans_domain", table_name="scans")
    op.drop_column("scans", "topic")
    op.drop_column("scans", "domain")
