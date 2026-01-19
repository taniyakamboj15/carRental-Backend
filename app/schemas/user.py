from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, KYCStatus
import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    phone_number: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    role: UserRole
    kyc_verified: bool
    kyc_status: KYCStatus
    kyc_document_url: Optional[str] = None
    phone_number: Optional[str] = None

class UserKYCSubmit(BaseModel):
    document_url: str

class UserKYCUpdate(BaseModel):
    kyc_status: KYCStatus

class UserLogin(BaseModel):
    email: EmailStr
    password: str
