import uuid
from app.models.payment import PaymentStatus

def process_payment(amount: float) -> tuple[bool, str]:
  
    return True, str(uuid.uuid4())
