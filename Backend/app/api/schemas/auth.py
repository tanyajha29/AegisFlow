from pydantic import BaseModel, Field, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Accepts "email" in the payload, but allows "username" for compatibility.
    username: str = Field(..., alias="email")
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_active: bool
