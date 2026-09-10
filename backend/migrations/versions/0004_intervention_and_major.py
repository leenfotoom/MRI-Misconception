"""add misconception intervention and academic major fields

Revision ID: 0004_intervention_and_major
Revises: 0003_stem_scan_context
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_intervention_and_major"
down_revision = "0003_stem_scan_context"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("academic_major", sa.String(60), nullable=False, server_default="undecided"),
    )
    op.create_index("ix_users_academic_major", "users", ["academic_major"])
    op.add_column("scans", sa.Column("intervention_started_at", sa.DateTime(timezone=True)))
    op.add_column("scans", sa.Column("intervention_completed_at", sa.DateTime(timezone=True)))
    op.add_column("scans", sa.Column("intervention_status", sa.String(20)))
    op.add_column("scans", sa.Column("intervention_answer", sa.String(40)))
    op.add_column("scans", sa.Column("intervention_reasoning", sa.Text()))
    op.add_column("scans", sa.Column("post_misconception_probability", sa.Float()))
    op.create_index("ix_scans_intervention_status", "scans", ["intervention_status"])


def downgrade() -> None:
    op.drop_index("ix_scans_intervention_status", table_name="scans")
    op.drop_column("scans", "post_misconception_probability")
    op.drop_column("scans", "intervention_reasoning")
    op.drop_column("scans", "intervention_answer")
    op.drop_column("scans", "intervention_status")
    op.drop_column("scans", "intervention_completed_at")
    op.drop_column("scans", "intervention_started_at")
    op.drop_index("ix_users_academic_major", table_name="users")
    op.drop_column("users", "academic_major")
