from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentBase(SQLModel):
    booking_id: int = Field(foreign_key="booking.id")
    amount: float
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    transaction_id: Optional[str] = None

class Payment(PaymentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
