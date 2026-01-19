from pydantic import BaseModel
from app.models.payment import PaymentStatus

class PaymentCreate(BaseModel):
    booking_id: int
    amount: float

class PaymentRead(BaseModel):
    id: int
    booking_id: int
    amount: float
    status: PaymentStatus
    transaction_id: str
