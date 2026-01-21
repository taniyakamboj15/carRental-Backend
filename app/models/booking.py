from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class BookingBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    vehicle_id: int = Field(foreign_key="vehicle.id")
    pickup_location: str
    start_date: date
    end_date: date
    total_amount: float
    status: BookingStatus = Field(default=BookingStatus.PENDING)

class Booking(BookingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
