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

router = APIRouter()

@router.post("/", response_model=BookingRead)
def create_booking(
    *,
    session: Session = Depends(deps.get_session),
    booking_in: BookingCreate,
    current_user: User = Depends(deps.get_current_user),
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
