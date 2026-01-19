import uuid
from app.models.payment import PaymentStatus

def process_payment(amount: float) -> tuple[bool, str]:
    # Simulate payment processing
    # Always success for dummy
    return True, str(uuid.uuid4())
