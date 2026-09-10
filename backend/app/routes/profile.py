from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import UserSession, utcnow
from ..security import AuthContext, clear_session_cookie, get_auth_context, require_csrf, verify_password
from ..study_plan import MAJORS

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    preferred_language: str | None = None
    preferred_theme: str | None = None
    academic_major: str | None = None


class DeleteAccountRequest(BaseModel):
    password: str


def payload(auth: AuthContext) -> dict:
    user = auth.user
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "preferred_language": user.preferred_language,
        "preferred_theme": user.preferred_theme,
        "academic_major": user.academic_major,
        "is_email_verified": user.is_email_verified,
        "created_at": user.created_at.isoformat(),
    }


@router.get("")
def get_profile(auth: AuthContext = Depends(get_auth_context)) -> dict:
    return payload(auth)


@router.patch("")
def update_profile(req: ProfileUpdate, auth: AuthContext = Depends(require_csrf), db: Session = Depends(get_db)) -> dict:
    if req.full_name is not None:
        auth.user.full_name = req.full_name.strip()
    if req.preferred_language is not None:
        if req.preferred_language not in {"en", "ar"}:
            raise HTTPException(status_code=400, detail="Unsupported language.")
        auth.user.preferred_language = req.preferred_language
    if req.preferred_theme is not None:
        if req.preferred_theme not in {"light", "dark", "system"}:
            raise HTTPException(status_code=400, detail="Unsupported theme.")
        auth.user.preferred_theme = req.preferred_theme
    if req.academic_major is not None:
        if req.academic_major not in MAJORS or req.academic_major == "undecided":
            raise HTTPException(status_code=400, detail="Unsupported academic major.")
        auth.user.academic_major = req.academic_major
    db.commit()
    db.refresh(auth.user)
    return payload(auth)


@router.delete("")
def delete_account(
    req: DeleteAccountRequest,
    response: Response,
    auth: AuthContext = Depends(require_csrf),
    db: Session = Depends(get_db),
) -> dict:
    if not verify_password(req.password, auth.user.password_hash):
        raise HTTPException(status_code=400, detail="Password is incorrect.")
    db.delete(auth.user)
    db.commit()
    clear_session_cookie(response)
    return {"message": "Account deleted."}
