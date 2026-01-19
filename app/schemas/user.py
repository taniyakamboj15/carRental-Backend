from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
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
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
