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
    vehicle = session.get(Vehicle, booking_in.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    if not booking_service.check_availability(session, booking_in.vehicle_id, booking_in.start_date, booking_in.end_date):
         raise HTTPException(status_code=400, detail="Vehicle not available for these dates")

    # Verify Location Match
    # "when user book car in fleet then use depend to check and verify that user location enter and vehicle base location are same"
    vehicle_loc = vehicle.location.lower().strip()
    pickup_loc = booking_in.pickup_location.lower().strip()
    
    # Check if vehicle location is part of pickup location (e.g. "Mumbai" in "Andheri, Mumbai")
    # or exact match
    if vehicle_loc not in pickup_loc and pickup_loc not in vehicle_loc:
         raise HTTPException(status_code=400, detail=f"Pickup location must be within {vehicle.location}. You selected: {booking_in.pickup_location}")

    total = booking_service.calculate_total(vehicle.daily_rate, booking_in.start_date, booking_in.end_date)
    
    try:
        booking = Booking(
            user_id=current_user.id,
            vehicle_id=vehicle.id,
            start_date=booking_in.start_date,
            end_date=booking_in.end_date,
            pickup_location=booking_in.pickup_location,
            total_amount=total,
            status=BookingStatus.PENDING
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        print(f"Booking created: {booking}")
        session.commit()
        session.refresh(booking)
        print(f"Booking created: {booking}")
        
        # Enrich for response
        return _enrich_booking_with_driver_info(session, booking)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

@router.get("/", response_model=List[BookingRead])
def read_bookings(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(deps.get_session),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
   
    if current_user.is_superuser:
        statement = select(Booking).offset(skip).limit(limit)
    else:
        statement = select(Booking).where(Booking.user_id == current_user.id).offset(skip).limit(limit)
    
    bookings = session.exec(statement).all()
    
    # Enrich all bookings
    enriched_bookings = [_enrich_booking_with_driver_info(session, b) for b in bookings]
    return enriched_bookings

def _enrich_booking_with_driver_info(session: Session, booking: Booking) -> BookingRead:
    vehicle = session.get(Vehicle, booking.vehicle_id)
    driver_name = None
    driver_contact = None
    
    if vehicle:
        driver_name = vehicle.driver_name
        # Only show contact if confirmed
        if booking.status == BookingStatus.CONFIRMED:
            driver_contact = vehicle.driver_contact
            
    # Create a dict from the booking to satisfy the Pydantic model (since we are adding fields)
    booking_dict = booking.dict()
    booking_dict['driver_name'] = driver_name
    booking_dict['driver_contact'] = driver_contact
    
    return BookingRead(**booking_dict)

@router.patch("/{booking_id}/cancel", response_model=BookingRead)
def cancel_booking(
    *,
    session: Session = Depends(deps.get_session),
    booking_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Cancel a booking.
    """
    booking = session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if not current_user.is_superuser and booking.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not authorized")
        
    if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail="Cannot cancel a completed or already cancelled booking")

    booking.status = BookingStatus.CANCELLED
    session.add(booking)
    session.commit()
    session.refresh(booking)
    session.refresh(booking)
    return _enrich_booking_with_driver_info(session, booking)
