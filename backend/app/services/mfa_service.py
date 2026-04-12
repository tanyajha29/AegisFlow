"""MFA helper utilities for TOTP-based authentication."""
from __future__ import annotations

import base64
import hashlib
import json
import logging
import secrets
import time
from io import BytesIO
from typing import List, Tuple

import pyotp
import qrcode
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models.user_model import User

logger = logging.getLogger("dristi-scan")
settings = get_settings()


class OTPThrottle:
    """Simple in-memory throttling for OTP verification attempts."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = {}

    def check(self, key: str):
        now = time.time()
        window = [t for t in self._attempts.get(key, []) if now - t < self.window_seconds]
        if len(window) >= self.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP attempts. Please wait and try again.",
            )
        window.append(now)
        self._attempts[key] = window


otp_throttle = OTPThrottle()


def _fernet() -> Fernet:
    key = settings.fernet_key
    if not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FERNET_KEY not configured",
        )
    try:
        return Fernet(key)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Invalid FERNET_KEY: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid FERNET_KEY configured",
        ) from exc


def encrypt_secret(secret: str) -> str:
    return _fernet().encrypt(secret.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to decrypt MFA secret",
        )


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def build_provisioning_uri(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name="DristiScan")


def generate_qr_base64(otpauth_url: str) -> str:
    qr = qrcode.make(otpauth_url)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"


def generate_backup_codes(count: int = 5) -> Tuple[List[str], List[str]]:
    """Return (plain_codes, hashed_codes)."""
    plain_codes = [secrets.token_hex(4).upper() for _ in range(count)]
    hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in plain_codes]
    return plain_codes, hashed_codes


def _load_backup_codes(user: User) -> list[str]:
    if not user.backup_codes:
        return []
    try:
        return json.loads(user.backup_codes)
    except Exception:
        return []


def _store_backup_codes(user: User, hashed_codes: list[str]):
    user.backup_codes = json.dumps(hashed_codes)


def persist_secret(db: Session, user: User, secret: str, backup_codes_hashed: list[str] | None = None):
    user.mfa_secret_encrypted = encrypt_secret(secret)
    _store_backup_codes(user, backup_codes_hashed or [])
    user.mfa_enabled = False
    db.add(user)
    db.commit()
    db.refresh(user)


def verify_user_otp(db: Session, user: User, otp: str) -> str:
    """Verify OTP or backup code. Returns 'totp' or 'backup' on success."""
    otp_value = (otp or "").strip()
    otp_throttle.check(f"user:{user.id}")

    if not user.mfa_secret_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not initialized for this account",
        )

    secret = decrypt_secret(user.mfa_secret_encrypted)
    totp = pyotp.TOTP(secret)
    if totp.verify(otp_value, valid_window=1):
        return "totp"

    # backup codes fallback
    hashed_attempt = hashlib.sha256(otp_value.encode()).hexdigest()
    codes = _load_backup_codes(user)
    if hashed_attempt in codes:
        codes.remove(hashed_attempt)
        _store_backup_codes(user, codes)
        db.add(user)
        db.commit()
        db.refresh(user)
        return "backup"

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired OTP",
    )
