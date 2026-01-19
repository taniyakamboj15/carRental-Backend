from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, model_validator
from app.models.booking import BookingStatus

class BookingCreate(BaseModel):
    vehicle_id: int
    start_date: date
    end_date: date

    @model_validator(mode='after')
    def check_dates(self) -> 'BookingCreate':
        if self.start_date < date.today():
            raise ValueError('Start date cannot be in the past')
        if self.end_date <= self.start_date:
            raise ValueError('End date must be after start date')
        return self

class BookingRead(BaseModel):
    id: int
    user_id: int
    vehicle_id: int
    start_date: date
    end_date: date
    total_amount: float
    status: BookingStatus
    created_at: datetime
