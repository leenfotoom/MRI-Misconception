from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Cookie, Depends, Header, HTTPException, Request, Response, status
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, UserSession, utcnow

password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
DUMMY_HASH = password_hasher.hash("Dummy-Password-For-Timing-Only-91!")

SESSION_COOKIE = os.getenv("SESSION_COOKIE_NAME", "mri_session")
SESSION_DAYS = int(os.getenv("SESSION_DAYS", "14"))
COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "lax").lower()
COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN") or None


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def validate_password(password: str) -> None:
    if len(password) < 10:
        raise HTTPException(status_code=400, detail="Password must be at least 10 characters.")
    groups = [
        any(c.islower() for c in password),
        any(c.isupper() for c in password),
        any(c.isdigit() for c in password),
        any(not c.isalnum() for c in password),
    ]
    if sum(groups) < 3:
        raise HTTPException(status_code=400, detail="Password must use at least three character groups.")


def token_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def new_token(nbytes: int = 48) -> str:
    return secrets.token_urlsafe(nbytes)


def new_csrf() -> str:
    return secrets.token_urlsafe(32)


def client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:80]
    return request.client.host[:80] if request.client else None


def create_session(db: Session, user: User, request: Request) -> tuple[UserSession, str]:
    raw = new_token()
    session = UserSession(
        user_id=user.id,
        token_hash=token_hash(raw),
        csrf_token=new_csrf(),
        session_version=user.session_version,
        user_agent=(request.headers.get("user-agent") or "")[:500] or None,
        ip_address=client_ip(request),
        expires_at=utcnow() + timedelta(days=SESSION_DAYS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session, raw


def set_session_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=raw_token,
        max_age=SESSION_DAYS * 86400,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=SESSION_COOKIE,
        domain=COOKIE_DOMAIN,
        path="/",
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
    )


@dataclass
class AuthContext:
    user: User
    session: UserSession


def get_auth_context(
    db: Session = Depends(get_db),
    raw_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> AuthContext:
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    now = utcnow()
    session = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == token_hash(raw_token),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
        )
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid.")
    user = db.get(User, session.user_id)
    if not user or session.session_version != user.session_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid.")
    session.last_seen_at = now
    db.commit()
    return AuthContext(user=user, session=session)


def get_optional_auth_context(
    db: Session = Depends(get_db),
    raw_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> AuthContext | None:
    if not raw_token:
        return None
    try:
        return get_auth_context(db=db, raw_token=raw_token)
    except HTTPException:
        return None


def require_csrf(
    auth: AuthContext = Depends(get_auth_context),
    csrf: str | None = Header(default=None, alias="X-CSRF-Token"),
) -> AuthContext:
    if not csrf or not secrets.compare_digest(csrf, auth.session.csrf_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed.")
    return auth
