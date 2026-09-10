from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")
    preferred_theme: Mapped[str] = mapped_column(String(10), default="system")
    academic_major: Mapped[str] = mapped_column(String(60), default="undecided", index=True)
    session_version: Mapped[int] = mapped_column(Integer, default=1)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    auth_tokens: Mapped[list["AuthToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    scans: Mapped[list["Scan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )

    purpose: Mapped[str] = mapped_column(String(40), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )

    user: Mapped[User] = relationship(back_populates="auth_tokens")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )

    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    csrf_token: Mapped[str] = mapped_column(String(128))
    session_version: Mapped[int] = mapped_column(Integer)

    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    user: Mapped[User] = relationship(back_populates="sessions")


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )

    scenario_id: Mapped[str] = mapped_column(String(40), index=True)
    scenario_title: Mapped[str] = mapped_column(String(240))

    domain: Mapped[str] = mapped_column(String(40), default="science", index=True)

    topic: Mapped[str] = mapped_column(String(120), default="Electricity")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        index=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    answer: Mapped[str] = mapped_column(String(20))
    reasoning: Mapped[str] = mapped_column(Text)

    parser: Mapped[str] = mapped_column(String(120))

    top_misconception_id: Mapped[str] = mapped_column(
        String(40),
        index=True
    )

    top_misconception_name: Mapped[str] = mapped_column(
        String(240)
    )

    before_probability: Mapped[float] = mapped_column(Float)

    experiment_id: Mapped[str] = mapped_column(String(40))
    experiment_name: Mapped[str] = mapped_column(String(240))

    information_gain: Mapped[float] = mapped_column(Float)

    actual_outcome: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True
    )

    after_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    posterior_before: Mapped[dict] = mapped_column(JSON)

    posterior_after: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    intervention_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    intervention_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    intervention_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    intervention_answer: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    intervention_reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    post_misconception_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    user: Mapped[User] = relationship(back_populates="scans")


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=new_id
    )

    name: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    icon: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow
    )
