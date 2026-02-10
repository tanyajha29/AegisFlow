from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    # Accepts "email" in the payload, but allows "username" for compatibility.
    username: str = Field(..., alias="email")
    password: str

    class Config:
        populate_by_name = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        from_attributes = True
