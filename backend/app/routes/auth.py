from __future__ import annotations

import os
from datetime import timedelta

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..database import get_db
from ..email_service import send_password_reset, send_verification
from ..models import AuthToken, User, UserSession, utcnow
from ..security import (
    AuthContext,
    DUMMY_HASH,
    clear_session_cookie,
    create_session,
    get_auth_context,
    get_optional_auth_context,
    hash_password,
    new_token,
    require_csrf,
    set_session_cookie,
    token_hash,
    validate_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
VERIFY_TTL_MINUTES = int(os.getenv("EMAIL_VERIFICATION_TTL_MINUTES", "1440"))
RESET_TTL_MINUTES = int(os.getenv("PASSWORD_RESET_TTL_MINUTES", "30"))
LOGIN_LOCK_MINUTES = int(os.getenv("LOGIN_LOCK_MINUTES", "15"))
MAX_FAILED_LOGINS = int(os.getenv("MAX_FAILED_LOGINS", "5"))


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=10, max_length=200)
    preferred_language: str = "en"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenRequest(BaseModel):
    token: str = Field(min_length=20, max_length=500)


class EmailRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


def normalize_email(raw: str) -> str:
    try:
        return validate_email(raw, check_deliverability=False).normalized.lower()
    except EmailNotValidError as exc:
        raise HTTPException(status_code=400, detail="Invalid email address.") from exc


def user_payload(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "is_email_verified": user.is_email_verified,
        "preferred_language": user.preferred_language,
        "preferred_theme": user.preferred_theme,
        "academic_major": user.academic_major,
        "created_at": user.created_at.isoformat(),
    }


def create_auth_token(db: Session, user: User, purpose: str, minutes: int) -> tuple[AuthToken, str]:
    raw = new_token()
    db.execute(
        update(AuthToken)
        .where(AuthToken.user_id == user.id, AuthToken.purpose == purpose, AuthToken.used_at.is_(None))
        .values(used_at=utcnow())
    )
    record = AuthToken(
        user_id=user.id,
        purpose=purpose,
        token_hash=token_hash(raw),
        expires_at=utcnow() + timedelta(minutes=minutes),
    )
    db.add(record)
    db.commit()
    return record, raw


@router.post("/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    email = normalize_email(req.email)
    validate_password(req.password)
    if req.preferred_language not in {"en", "ar"}:
        raise HTTPException(status_code=400, detail="Unsupported language.")
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(
        full_name=req.full_name.strip(),
        email=email,
        password_hash=hash_password(req.password),
        preferred_language=req.preferred_language,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _, raw = create_auth_token(db, user, "verify_email", VERIFY_TTL_MINUTES)
    try:
        preview = send_verification(user.email, user.full_name, raw)
    except Exception:
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=503, detail="Verification email could not be sent.")
    return {
        "message": "Account created. Verify your email to continue.",
        "dev_verification_url": preview,
    }


@router.post("/verify-email")
def verify_email(req: TokenRequest, db: Session = Depends(get_db)) -> dict:
    now = utcnow()
    record = db.scalar(
        select(AuthToken).where(
            AuthToken.token_hash == token_hash(req.token),
            AuthToken.purpose == "verify_email",
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > now,
        )
    )
    if not record:
        raise HTTPException(status_code=400, detail="Verification link is invalid or expired.")
    user = db.get(User, record.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Verification link is invalid or expired.")
    record.used_at = now
    user.is_email_verified = True
    user.email_verified_at = now
    db.commit()
    return {"message": "Email verified. You can now sign in."}


@router.post("/resend-verification")
def resend_verification(req: EmailRequest, db: Session = Depends(get_db)) -> dict:
    email = normalize_email(req.email)
    user = db.scalar(select(User).where(User.email == email))
    preview = None
    if user and not user.is_email_verified:
        _, raw = create_auth_token(db, user, "verify_email", VERIFY_TTL_MINUTES)
        try:
            preview = send_verification(user.email, user.full_name, raw)
        except Exception:
            pass
    return {"message": "If the account needs verification, a new link has been sent.", "dev_verification_url": preview}


@router.post("/login")
def login(req: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    email = normalize_email(req.email)
    user = db.scalar(select(User).where(User.email == email))
    now = utcnow()

    if not user:
        verify_password(req.password, DUMMY_HASH)
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if user.locked_until and user.locked_until > now:
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again later.")
    if not verify_password(req.password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= MAX_FAILED_LOGINS:
            user.locked_until = now + timedelta(minutes=LOGIN_LOCK_MINUTES)
            user.failed_login_count = 0
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Email verification required.")

    user.failed_login_count = 0
    user.locked_until = None
    db.commit()
    session, raw = create_session(db, user, request)
    set_session_cookie(response, raw)
    return {"user": user_payload(user), "csrf_token": session.csrf_token}


@router.get("/me")
def me(auth: AuthContext = Depends(get_auth_context)) -> dict:
    return {"user": user_payload(auth.user), "csrf_token": auth.session.csrf_token}


@router.get("/status")
def auth_status(auth: AuthContext | None = Depends(get_optional_auth_context)) -> dict:
    if auth is None:
        return {"authenticated": False}
    return {"authenticated": True, "user": user_payload(auth.user), "csrf_token": auth.session.csrf_token}


@router.post("/logout")
def logout(response: Response, auth: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)) -> dict:
    auth.session.revoked_at = utcnow()
    db.commit()
    clear_session_cookie(response)
    return {"message": "Signed out."}


@router.get("/sessions")
def sessions(auth: AuthContext = Depends(get_auth_context), db: Session = Depends(get_db)) -> dict:
    rows = db.scalars(
        select(UserSession)
        .where(UserSession.user_id == auth.user.id, UserSession.revoked_at.is_(None), UserSession.expires_at > utcnow())
        .order_by(UserSession.last_seen_at.desc())
    ).all()
    return {
        "items": [
            {
                "id": row.id,
                "current": row.id == auth.session.id,
                "user_agent": row.user_agent,
                "ip_address": row.ip_address,
                "created_at": row.created_at.isoformat(),
                "last_seen_at": row.last_seen_at.isoformat(),
                "expires_at": row.expires_at.isoformat(),
            }
            for row in rows
        ]
    }


@router.delete("/sessions/{session_id}")
def revoke_session(session_id: str, response: Response, auth: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)) -> dict:
    session = db.scalar(select(UserSession).where(UserSession.id == session_id, UserSession.user_id == auth.user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    is_current = session.id == auth.session.id
    session.revoked_at = utcnow()
    db.commit()
    if is_current:
        clear_session_cookie(response)
    return {"message": "Session revoked.", "current_session": is_current}


@router.post("/logout-all")
def logout_all(response: Response, auth: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)) -> dict:
    now = utcnow()
    db.execute(update(UserSession).where(UserSession.user_id == auth.user.id, UserSession.revoked_at.is_(None)).values(revoked_at=now))
    db.commit()
    clear_session_cookie(response)
    return {"message": "All sessions revoked."}


@router.post("/forgot-password")
def forgot_password(req: EmailRequest, db: Session = Depends(get_db)) -> dict:
    email = normalize_email(req.email)
    user = db.scalar(select(User).where(User.email == email, User.is_email_verified.is_(True)))
    preview = None
    if user:
        _, raw = create_auth_token(db, user, "reset_password", RESET_TTL_MINUTES)
        try:
            preview = send_password_reset(user.email, user.full_name, raw)
        except Exception:
            pass
    return {"message": "If the account exists, password reset instructions have been sent.", "dev_reset_url": preview}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, response: Response, db: Session = Depends(get_db)) -> dict:
    validate_password(req.new_password)
    now = utcnow()
    record = db.scalar(
        select(AuthToken).where(
            AuthToken.token_hash == token_hash(req.token),
            AuthToken.purpose == "reset_password",
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > now,
        )
    )
    if not record:
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired.")
    user = db.get(User, record.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired.")
    user.password_hash = hash_password(req.new_password)
    user.session_version += 1
    record.used_at = now
    db.execute(update(UserSession).where(UserSession.user_id == user.id, UserSession.revoked_at.is_(None)).values(revoked_at=now))
    db.commit()
    clear_session_cookie(response)
    return {"message": "Password updated. Sign in with your new password."}


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    request: Request,
    response: Response,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> dict:
    if not verify_password(req.current_password, auth.user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    validate_password(req.new_password)
    auth.user.password_hash = hash_password(req.new_password)
    auth.user.session_version += 1
    now = utcnow()
    db.execute(update(UserSession).where(UserSession.user_id == auth.user.id, UserSession.revoked_at.is_(None)).values(revoked_at=now))
    db.commit()
    new_session, raw = create_session(db, auth.user, request)
    set_session_cookie(response, raw)
    return {"message": "Password changed.", "csrf_token": new_session.csrf_token}
