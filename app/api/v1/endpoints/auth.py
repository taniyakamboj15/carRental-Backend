from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from app.core.limiter import limiter
from sqlmodel import Session, select
from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.worker import send_welcome_email_task


router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login_access_token(
    request: Request,
    response: Response,
    user_in: UserLogin,
    session: Session = Depends(deps.get_session),
) -> Any:
    """
    Login via Email/Password (JSON) -> Sets HttpOnly Cookie.
    """
    # Use select statement for SQLModel
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    
    if not user or not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Set HttpOnly Cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False # Set to True in production with HTTPS
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/logout")
def logout(response: Response):
    """
    Logout the user by clearing the cookie.
    """
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.post("/signup", response_model=UserRead)
@limiter.limit("5/minute")
def create_user(
    request: Request,
    *,
    session: Session = Depends(deps.get_session),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    user_obj = User.from_orm(user_in, update={"hashed_password": security.get_password_hash(user_in.password)})


    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)

    # Send Welcome Email via Celery
   
    send_welcome_email_task.delay(
        email=user_obj.email, 
        full_name=user_obj.full_name or "User"
    )

    return user_obj


