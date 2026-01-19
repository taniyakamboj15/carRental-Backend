from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.models.booking import BookingStatus

class BookingCreate(BaseModel):
    vehicle_id: int
    start_date: date
    end_date: date

class BookingRead(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    start_date: date
    end_date: date
    total_amount: float
    status: BookingStatus
    created_at: datetime
