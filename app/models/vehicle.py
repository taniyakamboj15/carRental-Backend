from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum

class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"

class VehicleBase(SQLModel):
    make: str
    model: str
    year: int
    license_plate: str = Field(unique=True)
    daily_rate: float
    location: str
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE)
    image_url: Optional[str] = None

class Vehicle(VehicleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
