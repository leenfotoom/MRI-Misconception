from __future__ import annotations

import html
import os

import httpx

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:3000").rstrip("/")
EMAIL_MODE = os.getenv("EMAIL_MODE", "console").lower()
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
MAIL_FROM = os.getenv("MAIL_FROM", "Misconception MRI <onboarding@example.com>")
EXPOSE_DEV_EMAIL_LINKS = os.getenv("EXPOSE_DEV_EMAIL_LINKS", "1") == "1"


def _send(to: str, subject: str, body_html: str) -> None:
    if EMAIL_MODE == "disabled":
        return
    if EMAIL_MODE == "console":
        print(f"[EMAIL PREVIEW] to={to} subject={subject}\n{body_html}")
        return
    if EMAIL_MODE != "resend":
        raise RuntimeError("Unsupported EMAIL_MODE")
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY is required when EMAIL_MODE=resend")
    response = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        json={"from": MAIL_FROM, "to": [to], "subject": subject, "html": body_html},
        timeout=20.0,
    )
    response.raise_for_status()


def verification_url(raw_token: str) -> str:
    return f"{APP_BASE_URL}/verify-email?token={raw_token}"


def reset_url(raw_token: str) -> str:
    return f"{APP_BASE_URL}/reset-password?token={raw_token}"


def send_verification(email: str, full_name: str, raw_token: str) -> str | None:
    url = verification_url(raw_token)
    _send(
        email,
        "Verify your Misconception MRI account",
        f"<p>Hello {html.escape(full_name)},</p><p>Verify your email to activate your learner profile.</p><p><a href='{html.escape(url)}'>Verify email</a></p>",
    )
    return url if EMAIL_MODE == "console" and EXPOSE_DEV_EMAIL_LINKS else None


def send_password_reset(email: str, full_name: str, raw_token: str) -> str | None:
    url = reset_url(raw_token)
    _send(
        email,
        "Reset your Misconception MRI password",
        f"<p>Hello {html.escape(full_name)},</p><p>A password reset was requested for your account.</p><p><a href='{html.escape(url)}'>Reset password</a></p>",
    )
    return url if EMAIL_MODE == "console" and EXPOSE_DEV_EMAIL_LINKS else None
