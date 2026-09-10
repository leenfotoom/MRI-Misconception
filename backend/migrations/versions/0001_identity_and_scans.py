"""identity and account-scoped scan history

Revision ID: 0001_identity_and_scans
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_identity_and_scans"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("email_verified_at", sa.DateTime(timezone=True)),
        sa.Column("preferred_language", sa.String(5), nullable=False, server_default="en"),
        sa.Column("preferred_theme", sa.String(10), nullable=False, server_default="system"),
        sa.Column("session_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_verified", "users", ["is_email_verified"])

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.String(40), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_tokens_hash", "auth_tokens", ["token_hash"], unique=True)
    op.create_index("ix_auth_tokens_user", "auth_tokens", ["user_id"])

    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("csrf_token", sa.String(128), nullable=False),
        sa.Column("session_version", sa.Integer(), nullable=False),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("ip_address", sa.String(80)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_user_sessions_hash", "user_sessions", ["token_hash"], unique=True)
    op.create_index("ix_user_sessions_user", "user_sessions", ["user_id"])

    op.create_table(
        "scans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario_id", sa.String(40), nullable=False),
        sa.Column("scenario_title", sa.String(240), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("answer", sa.String(20), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("parser", sa.String(120), nullable=False),
        sa.Column("top_misconception_id", sa.String(40), nullable=False),
        sa.Column("top_misconception_name", sa.String(240), nullable=False),
        sa.Column("before_probability", sa.Float(), nullable=False),
        sa.Column("experiment_id", sa.String(40), nullable=False),
        sa.Column("experiment_name", sa.String(240), nullable=False),
        sa.Column("information_gain", sa.Float(), nullable=False),
        sa.Column("actual_outcome", sa.String(120)),
        sa.Column("after_probability", sa.Float()),
        sa.Column("posterior_before", sa.JSON(), nullable=False),
        sa.Column("posterior_after", sa.JSON()),
    )
    op.create_index("ix_scans_user_created", "scans", ["user_id", "created_at"])
    op.create_index("ix_scans_scenario", "scans", ["scenario_id"])


def downgrade() -> None:
    op.drop_table("scans")
    op.drop_table("user_sessions")
    op.drop_table("auth_tokens")
    op.drop_table("users")
