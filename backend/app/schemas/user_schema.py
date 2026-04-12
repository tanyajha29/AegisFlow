from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    mfa_enabled: bool = False

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    mfa_required: bool = False
    challenge_token: str | None = None


class TokenData(BaseModel):
    user_id: int | None = None
    email: EmailStr | None = None


class MFAVerifyRequest(BaseModel):
    otp: str


class MFAVerifyLoginRequest(BaseModel):
    challenge_token: str
    otp: str


class MFASetupResponse(BaseModel):
    qr_code_base64: str
    otpauth_url: str
    backup_codes: list[str] | None = None


class MFAStatus(BaseModel):
    mfa_enabled: bool
    backup_codes_remaining: int | None = None
