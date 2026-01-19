from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlmodel import Session
from app.core import security
from app.core.config import settings
from app.db.session import get_session
from app.models.user import User
from app.schemas.token import TokenPayload

# OAuth2PasswordBearer is required for Swagger UI to show the Authorize button
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
    token: Optional[str] = Depends(reusable_oauth2)
) -> User:
    # Hybrid Auth: Check Cookie first, then Header (handled by depends reusable_oauth2)
    # Note: depends reusable_oauth2 extracts from Authorization header
    
    # If header auth failed or wasn't provided, reusable_oauth2 yields None or throws if auto_error=True (default)
    # But wait, auto_error=True means it throws 401. 
    # To support cookie fallback properly, we should set auto_error=False on OAuth2PasswordBearer 
    # OR we handle the logic carefully.
    
    # Better approach for hybrid:
    # 1. Try to get token from cookie.
    # 2. If no cookie, rely on Header (via OAuth2PasswordBearer).
    
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        # If verify works, return user
        # Note: If cookie is present, we prioritize it or treat it as the token.
         if cookie_token.startswith("Bearer "):
             token = cookie_token.split(" ")[1]
         else:
             token = cookie_token
    
    # dependencies are executed. 'token' arg comes from reusable_oauth2
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = session.get(User, int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
