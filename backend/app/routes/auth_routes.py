from datetime import timedelta
import json
import logging

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


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=user_in.email, password_hash=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"user_id": user.id, "email": user.email})
    logger.info("User registered: %s", user.email)
    return Token(access_token=access_token)


@router.post("/login", response_model=LoginResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # If MFA is enabled, issue a short-lived challenge token and require OTP verification
    if user.mfa_enabled:
        challenge_token = create_access_token(
            {"user_id": user.id, "email": user.email, "mfa_pending": True},
            expires_delta=timedelta(minutes=10),
        )
        logger.info("MFA challenge issued for user: %s", user.email)
        return LoginResponse(mfa_required=True, challenge_token=challenge_token)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token({"user_id": user.id, "email": user.email}, expires_delta=access_token_expires)
    logger.info("User login: %s", user.email)
    return LoginResponse(access_token=access_token)


@router.get("/profile", response_model=UserProfile)
def profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/setup-mfa", response_model=MFASetupResponse)
def setup_mfa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = generate_totp_secret()
    otpauth_url = build_provisioning_uri(secret, current_user.email)
    qr_code = generate_qr_base64(otpauth_url)
    backup_plain, backup_hashed = generate_backup_codes()
    persist_secret(db, current_user, secret, backup_hashed)
    logger.info("MFA secret generated for user: %s", current_user.email)
    return MFASetupResponse(qr_code_base64=qr_code, otpauth_url=otpauth_url, backup_codes=backup_plain)


@router.post("/verify-mfa", response_model=MFAStatus)
def verify_mfa(payload: MFAVerifyRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    method = verify_user_otp(db, current_user, payload.otp)
    if not current_user.mfa_enabled:
        current_user.mfa_enabled = True
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        logger.info("MFA enabled for user: %s via %s", current_user.email, method)
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
    token_payload = decode_token(payload.challenge_token)
    if not token_payload or not token_payload.get("mfa_pending") or not token_payload.get("user_id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired challenge")

    user = db.query(User).filter(User.id == token_payload["user_id"]).first()
    if not user or not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or MFA disabled")

    verify_user_otp(db, user, payload.otp)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token({"user_id": user.id, "email": user.email}, expires_delta=access_token_expires)
    logger.info("User MFA login successful: %s", user.email)
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
    logger.info("MFA disabled for user: %s", current_user.email)
    return MFAStatus(mfa_enabled=False, backup_codes_remaining=0)
