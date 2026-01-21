from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
from app.utils import validate_phone, validate_city

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    response: Response,
    session: Session = Depends(deps.get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    
    
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False 
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/logout")
def logout(response: Response):
   
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.post("/signup", response_model=UserRead)
def create_user(
    *,
    session: Session = Depends(deps.get_session),
    user_in: UserCreate,
) -> Any:
   
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    # Validate City & Phone
    if user_in.city and not validate_city(user_in.city):
        raise HTTPException(status_code=400, detail=f"Invalid city: {user_in.city}")
    
    if user_in.phone_number and not validate_phone(user_in.phone_number):
         raise HTTPException(status_code=400, detail="Invalid phone number format")

    user_data = user_in.dict(exclude={"password"})
    user_obj = User(**user_data, hashed_password=security.get_password_hash(user_in.password))
    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)
    return user_obj
