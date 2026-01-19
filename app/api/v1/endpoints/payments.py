from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.api import deps
from app.db.session import get_session
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentRead
from app.services import payment_service
from app.helpers import idempotency
from app.worker import generate_invoice

router = APIRouter()

@router.post("/process", response_model=PaymentRead)
def process_payment(
    *,
    session: Session = Depends(deps.get_session),
    payment_in: PaymentCreate,
    current_user: Any = Depends(deps.get_current_user),
    idempotency_key: str = Depends(idempotency.check_idempotency)
) -> Any:
    """
    Process payment for a booking.
    """
    booking = session.get(Booking, payment_in.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not authorized")
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Booking already processed or cancelled")

    success, txn_id = payment_service.process_payment(payment_in.amount)
    
    payment = Payment(
        booking_id=booking.id,
        amount=payment_in.amount,
        status=PaymentStatus.COMPLETED if success else PaymentStatus.FAILED,
        transaction_id=txn_id
    )
    session.add(payment)
    
    if success:
        booking.status = BookingStatus.CONFIRMED
        session.add(booking)
        
        # Trigger Invoice Generation Task
        from app.worker import generate_invoice
        generate_invoice.delay(booking.id)
        
        # Save Idempotency Key to prevent re-play
        if idempotency_key:
            idempotency.save_idempotency_key(idempotency_key, {"status": "success", "payment_id": payment.id})
        
    session.commit()
    session.refresh(payment)
    return payment
