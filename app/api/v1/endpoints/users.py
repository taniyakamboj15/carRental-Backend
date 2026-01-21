from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.api import deps
from app.core import security
from app.db.session import get_session
from app.models.user import User, KYCStatus
from app.schemas.user import UserRead, UserUpdate, UserKYCSubmit, UserKYCUpdate

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
   
    return current_user

@router.put("/me", response_model=UserRead)
def update_user_me(
    *,
    session: Session = Depends(deps.get_session),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user.
    """
    user_data = user_in.dict(exclude_unset=True)
    if "password" in user_data:
        password = user_data.pop("password")
        current_user.hashed_password = security.get_password_hash(password)
        
    for key, value in user_data.items():
        setattr(current_user, key, value)
        
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@router.post("/kyc", response_model=UserRead)
def submit_kyc(
    *,
    session: Session = Depends(deps.get_session),
    kyc_in: UserKYCSubmit,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Submit KYC document.
    """
    current_user.kyc_document_url = kyc_in.document_url
    current_user.kyc_status = KYCStatus.SUBMITTED
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@router.put("/{user_id}/kyc", response_model=UserRead)
def update_kyc_status(
    *,
    session: Session = Depends(deps.get_session),
    user_id: int,
    kyc_in: UserKYCUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Admin: Approve or Reject KYC.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.kyc_status != KYCStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="KYC is not submitted")
    
    user.kyc_status = kyc_in.kyc_status
    # Update kyc_verified based on kyc_status

    
    # If kyc_status is VERIFIED, set kyc_verified to True
    # If kyc_status is REJECTED, set kyc_verified to False
    if user.kyc_status == KYCStatus.VERIFIED:
        user.kyc_verified = True
    else:
        user.kyc_verified = False
        
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
