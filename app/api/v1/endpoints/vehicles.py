from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.api import deps
from app.db.session import get_session
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate

router = APIRouter()

@router.get("/", response_model=List[VehicleRead])
def read_vehicles(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(deps.get_session),
    
) -> Any:
    
    statement = select(Vehicle).offset(skip).limit(limit)
    vehicles = session.exec(statement).all()
    return vehicles

@router.post("/", response_model=VehicleRead)
def create_vehicle(
    *,
    session: Session = Depends(deps.get_session),
    vehicle_in: VehicleCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
   
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
