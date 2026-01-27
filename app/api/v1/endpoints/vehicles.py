from typing import Any, List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, and_, or_
from app.api import deps
from app.db.session import get_session
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.booking import Booking, BookingStatus
from app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate

from app.utils import validate_phone, validate_city

router = APIRouter()


@router.get("/", response_model=List[VehicleRead])
def read_vehicles(
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    session: Session = Depends(deps.get_session),
) -> Any:
    """
    Public endpoint - no auth required to browse vehicles
    """
    query = select(Vehicle)

    if location:
        # Case-insensitive location filtering
        query = query.where(Vehicle.location.ilike(f"%{location}%"))

    if start_date and end_date:
        # Find busy vehicles
        busy_subquery = select(Booking.vehicle_id).where(
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            and_(
                Booking.start_date <= end_date,
                Booking.end_date >= start_date
            )
        )
        query = query.where(Vehicle.id.not_in(busy_subquery))

    query = query.offset(skip).limit(limit)
    vehicles = session.exec(query).all()
    return vehicles

@router.post("/", response_model=VehicleRead)
def create_vehicle(
    *,
    session: Session = Depends(deps.get_session),
    vehicle_in: VehicleCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
   
    # Validate Phone
    if vehicle_in.driver_contact:
        if not validate_phone(vehicle_in.driver_contact):
             raise HTTPException(status_code=400, detail="Invalid driver contact number")

    # Validate City
    if not validate_city(vehicle_in.location):
         raise HTTPException(status_code=400, detail=f"Location '{vehicle_in.location}' not found. Please enter a valid city.")

    vehicle = Vehicle.from_orm(vehicle_in)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle

@router.get("/{vehicle_id}", response_model=VehicleRead)
def read_vehicle_by_id(
    vehicle_id: int,
    session: Session = Depends(deps.get_session),
) -> Any:
  
    vehicle = session.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.put("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(
    *,
    session: Session = Depends(deps.get_session),
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
  
    vehicle = session.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle_data = vehicle_in.dict(exclude_unset=True)
    for key, value in vehicle_data.items():
        setattr(vehicle, key, value)
        
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle

@router.delete("/{vehicle_id}", response_model=VehicleRead)
def delete_vehicle(
    *,
    session: Session = Depends(deps.get_session),
    vehicle_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    
    vehicle = session.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    session.delete(vehicle)
    session.commit()
    return vehicle
