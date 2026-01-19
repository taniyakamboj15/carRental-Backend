from datetime import date
from sqlmodel import Session, select, and_, or_
from app.models.booking import Booking, BookingStatus

def check_availability(session: Session, vehicle_id: int, start_date: date, end_date: date) -> bool:
    # Query for any bookings that overlap
    # Overlap logic: (StartA <= EndB) and (EndA >= StartB)
    statement = select(Booking).where(
        Booking.vehicle_id == vehicle_id,
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
        and_(
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        )
    )
    conflicting_booking = session.exec(statement).first()
    return conflicting_booking is None

def calculate_total(daily_rate: float, start_date: date, end_date: date) -> float:
    days = (end_date - start_date).days
    if days < 1: days = 1 # Minimum 1 day
    return days * daily_rate
