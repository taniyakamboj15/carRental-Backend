from typing import Optional
from pydantic import BaseModel
from app.models.vehicle import VehicleStatus

class VehicleCreate(BaseModel):
    make: str
    model: str
    year: int
    license_plate: str
    daily_rate: float
    location: str
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    status: VehicleStatus = VehicleStatus.AVAILABLE
    image_url: Optional[str] = None

class VehicleUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    license_plate: Optional[str] = None
    daily_rate: Optional[float] = None
    location: Optional[str] = None
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    status: Optional[VehicleStatus] = None
    image_url: Optional[str] = None

class VehicleRead(BaseModel):
    id: int
    make: str
    model: str
    year: int
    license_plate: str
    daily_rate: float
    location: str
    driver_name: Optional[str] = None
    status: VehicleStatus
    image_url: Optional[str] = None
