from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class KYCStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REJECTED = "rejected"

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    role: UserRole = Field(default=UserRole.CUSTOMER)
    kyc_verified: bool = False
    kyc_status: KYCStatus = Field(default=KYCStatus.PENDING)
    kyc_document_url: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
