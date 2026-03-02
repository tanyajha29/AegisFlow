from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Code Upload Schemas ---
class CodeUpload(BaseModel):
    title: str
    code_content: str
    filename: str

# --- Scan Result Schemas ---
class VulnerabilityGenerate(BaseModel):
    vulnerability_name: str
    severity: str
    file_name: str
    line_number: int
    code_snippet: str
    explanation: str
    remediation_steps: str
    cwe_mapping: str

class VulnerabilityResponse(VulnerabilityGenerate):
    id: int
    scan_id: int

    class Config:
        from_attributes = True

class ScanResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    status: str
    risk_score: float
    owner_id: int
    vulnerabilities: List[VulnerabilityResponse] = []

    class Config:
        from_attributes = True
