from datetime import timedelta
import json
import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user_model import User
from ..schemas.user_schema import (
    LoginResponse,
    MFASetupResponse,
    MFAStatus,
    MFAVerifyLoginRequest,
    MFAVerifyRequest,
    RegisterChallengeResponse,
    RegisterVerifyRequest,
    Token,
    UserCreate,
    UserLogin,
    UserProfile,
)
from ..services.mfa_service import (
    build_provisioning_uri,
    generate_backup_codes,
    generate_qr_base64,
    generate_totp_secret,
    persist_secret,
    verify_user_otp,
)
from ..utils.security_utils import create_access_token, decode_token, hash_password, verify_password
from ..config import get_settings
from ..middleware.auth_middleware import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
logger = logging.getLogger("dristi-scan")


@router.post("/register", response_model=RegisterChallengeResponse, status_code=status.HTTP_200_OK)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Step 1 of registration: validate credentials, create inactive user,
    generate TOTP secret + QR, return challenge token.
    Account is NOT active until /auth/register/verify succeeds.
    """
    t0 = time.perf_counter()
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Create user in inactive state
    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        is_active=False,
        mfa_enabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate TOTP secret and QR
    secret = generate_totp_secret()
    otpauth_url = build_provisioning_uri(secret, user.email)
    qr_code = generate_qr_base64(otpauth_url)
    backup_plain, backup_hashed = generate_backup_codes()

    # Persist encrypted pending secret (mfa_enabled stays False until verified)
    user.mfa_secret_encrypted = __import__('app.services.mfa_service', fromlist=['encrypt_secret']).encrypt_secret(secret)
    user.backup_codes = json.dumps(backup_hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Issue short-lived registration challenge token (10 min)
    challenge_token = create_access_token(
        {"user_id": user.id, "email": user.email, "registration_pending": True},
        expires_delta=timedelta(minutes=10),
    )

    elapsed = time.perf_counter() - t0
    logger.info("[register] User created (inactive) email=%s user_id=%d elapsed=%.3fs", user.email, user.id, elapsed)

    return RegisterChallengeResponse(
        challenge_token=challenge_token,
        qr_code_base64=qr_code,
        otpauth_url=otpauth_url,
        backup_codes=backup_plain,
    )


@router.post("/register/verify", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_verify(payload: RegisterVerifyRequest, db: Session = Depends(get_db)):
    """
    Step 2 of registration: verify OTP, activate account, enable MFA.
    Returns a full access token on success.
    """
    t0 = time.perf_counter()
    token_payload = decode_token(payload.challenge_token)
    if not token_payload or not token_payload.get("registration_pending") or not token_payload.get("user_id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired registration challenge")

    user = db.query(User).filter(User.id == token_payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already activated")

    # Verify OTP against the pending secret
    verify_user_otp(db, user, payload.otp)

    # Activate account and enable MFA
    user.is_active = True
    user.mfa_enabled = True
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        {"user_id": user.id, "email": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    elapsed = time.perf_counter() - t0
    logger.info("[register/verify] Account activated email=%s user_id=%d elapsed=%.3fs", user.email, user.id, elapsed)
    return Token(access_token=access_token)


@router.post("/login", response_model=LoginResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    t0 = time.perf_counter()
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Block inactive (unverified) accounts
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated. Complete MFA setup during registration.",
        )

    # MFA required for all active users (new users always have it; legacy users may not)
    if user.mfa_enabled:
        challenge_token = create_access_token(
            {"user_id": user.id, "email": user.email, "mfa_pending": True},
            expires_delta=timedelta(minutes=10),
        )
        elapsed = time.perf_counter() - t0
        logger.info("[login] MFA challenge issued email=%s elapsed=%.3fs", user.email, elapsed)
        return LoginResponse(mfa_required=True, challenge_token=challenge_token)

    # Legacy users without MFA: issue token but flag for enrollment
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token({"user_id": user.id, "email": user.email}, expires_delta=access_token_expires)
    elapsed = time.perf_counter() - t0
    logger.info("[login] Direct login (no MFA) email=%s elapsed=%.3fs", user.email, elapsed)
    return LoginResponse(access_token=access_token, mfa_required=False)


@router.get("/profile", response_model=UserProfile)
def profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/setup-mfa", response_model=MFASetupResponse)
def setup_mfa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Legacy endpoint: allows existing users without MFA to set it up from Settings."""
    secret = generate_totp_secret()
    otpauth_url = build_provisioning_uri(secret, current_user.email)
    qr_code = generate_qr_base64(otpauth_url)
    backup_plain, backup_hashed = generate_backup_codes()
    persist_secret(db, current_user, secret, backup_hashed)
    logger.info("[setup-mfa] Secret generated for user=%s", current_user.email)
    return MFASetupResponse(qr_code_base64=qr_code, otpauth_url=otpauth_url, backup_codes=backup_plain)


@router.post("/verify-mfa", response_model=MFAStatus)
def verify_mfa(payload: MFAVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    method = verify_user_otp(db, current_user, payload.otp)
    if not current_user.mfa_enabled:
        current_user.mfa_enabled = True
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        logger.info("[verify-mfa] MFA enabled for user=%s via %s", current_user.email, method)
    remaining_backups = None
    if current_user.backup_codes:
        try:
            codes = json.loads(current_user.backup_codes)
            remaining_backups = len(codes)
        except Exception:
            remaining_backups = None
    return MFAStatus(mfa_enabled=current_user.mfa_enabled, backup_codes_remaining=remaining_backups)


@router.post("/verify-login-mfa", response_model=Token)
def verify_login_mfa(payload: MFAVerifyLoginRequest, db: Session = Depends(get_db)):
    t0 = time.perf_counter()
    token_payload = decode_token(payload.challenge_token)
    if not token_payload or not token_payload.get("mfa_pending") or not token_payload.get("user_id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired challenge")

    user = db.query(User).filter(User.id == token_payload["user_id"]).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or MFA disabled")

    verify_user_otp(db, user, payload.otp)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token({"user_id": user.id, "email": user.email}, expires_delta=access_token_expires)
    elapsed = time.perf_counter() - t0
    logger.info("[verify-login-mfa] MFA login success email=%s elapsed=%.3fs", user.email, elapsed)
    return Token(access_token=access_token)


@router.post("/disable-mfa", response_model=MFAStatus)
def disable_mfa(payload: MFAVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.mfa_enabled:
        return MFAStatus(mfa_enabled=False)
    verify_user_otp(db, current_user, payload.otp)
    current_user.mfa_enabled = False
    current_user.mfa_secret_encrypted = None
    current_user.backup_codes = None
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    logger.info("[disable-mfa] MFA disabled for user=%s", current_user.email)
    return MFAStatus(mfa_enabled=False, backup_codes_remaining=0)
