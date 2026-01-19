from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.api import deps
from app.db.session import get_session
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate, BookingRead
from app.services import booking_service
from app.helpers import idempotency

router = APIRouter()

@router.post("/", response_model=BookingRead)
def create_booking(
    *,
    session: Session = Depends(deps.get_session),
    booking_in: BookingCreate,
    current_user: User = Depends(deps.get_current_user),
    idempotency_key: str = Depends(idempotency.check_idempotency)
) -> Any:
    """
    Create a booking.
    """
    vehicle = session.get(Vehicle, booking_in.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    if not booking_service.check_availability(session, booking_in.vehicle_id, booking_in.start_date, booking_in.end_date):
         raise HTTPException(status_code=400, detail="Vehicle not available for these dates")

    total = booking_service.calculate_total(vehicle.daily_rate, booking_in.start_date, booking_in.end_date)
    
    booking = Booking(
        user_id=current_user.id,
        vehicle_id=vehicle.id,
        start_date=booking_in.start_date,
        end_date=booking_in.end_date,
        total_amount=total,
        status=BookingStatus.PENDING
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)

    # Save Idempotency Key
    if idempotency_key:
        idempotency.save_idempotency_key(idempotency_key, {"status": "success", "booking_id": booking.id})

    return booking

@router.get("/", response_model=List[BookingRead])
def read_bookings(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List bookings (User sees own, Admin sees all).
    """
    if current_user.is_superuser:
        statement = select(Booking).offset(skip).limit(limit)
    else:
        statement = select(Booking).where(Booking.user_id == current_user.id).offset(skip).limit(limit)
    
    bookings = session.exec(statement).all()
    return bookings
@router.post("/{booking_id}/cancel", response_model=BookingRead)
def cancel_booking(
    *,
    session: Session = Depends(deps.get_session),
    booking_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Cancel a booking (Policy: Can only cancel if start_date is more than 24 hours away).
    """
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Authorization: Only Admin or Owner can cancel
    if not current_user.is_superuser and booking.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not authorized to cancel this booking")

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    
    if booking.status == BookingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel a completed booking")

    # Cancellation Policy Check (e.g., 24 hours notice)
    # For now, simple: Start Date must be in future (tomorrow or later) to avoid same-day cancellation issues
    from datetime import date, timedelta
    if not current_user.is_superuser: # Admins can bypass policy
        if booking.start_date <= date.today():
             raise HTTPException(status_code=400, detail="Cancellation policy violation: Cannot cancel on or after start date.")

    booking.status = BookingStatus.CANCELLED
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking
