from celery import Celery
from celery.schedules import crontab
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.core.config import settings
from app.db.session import engine
from app.models.booking import Booking, BookingStatus

celery_app = Celery("worker", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "check-expired-bookings-every-15-min": {
        "task": "app.worker.check_expired_bookings",
        "schedule": crontab(minute="*/15"),
    },
    "daily-reminder": {
        "task": "app.worker.send_tomorrow_reminders",
        "schedule": crontab(hour=7, minute=0),
    }
}

@celery_app.task
def check_expired_bookings():
    """
    Cancel bookings that are PENDING and older than 30 minutes.
    """
    print("Checking for expired bookings...")
    with Session(engine) as session:
        # 30 minutes ago
        threshold_time = datetime.utcnow() - timedelta(minutes=30)
        
        statement = select(Booking).where(
            Booking.status == BookingStatus.PENDING,
            Booking.created_at < threshold_time
        )
        expired_bookings = session.exec(statement).all()
        
        for booking in expired_bookings:
            print(f"Expiring booking {booking.id}")
            booking.status = BookingStatus.CANCELLED
            session.add(booking)
        
        session.commit()
    return f"Checked {len(expired_bookings) if 'expired_bookings' in locals() else 0} expired bookings"

@celery_app.task
def send_tomorrow_reminders():
    """
    Send reminders for bookings starting tomorrow.
    """
    print("Sending reminders...")
    # Logic: Find bookings with start_date == tomorrow
    with Session(engine) as session:
        tomorrow = datetime.utcnow().date() + timedelta(days=1)
        statement = select(Booking).where(
            Booking.start_date == tomorrow,
            Booking.status == BookingStatus.CONFIRMED
        )
        upcoming_bookings = session.exec(statement).all()
        for booking in upcoming_bookings:
            # In a real app, query User email and send email
            print(f"Reminder: Booking {booking.id} starts tomorrow for User {booking.user_id}")
            
    return "Reminders sent"

@celery_app.task
def generate_invoice(booking_id: int):
    """
    Generate PDF Invoice (Simulation).
    """
    import time
    time.sleep(3) # Simulate PDF generation
    print(f"Generated Invoice PDF for Booking {booking_id}")
    return f"Invoice_{booking_id}.pdf"

@celery_app.task(acks_late=True)
def send_welcome_email_task(email: str, full_name: str):
    """
    Send Welcome Email via Celery.
    """
    # Simply call the logic from the service, or inline it.
    # Inlining is fine for simplicity given the previous discussions.
    # Or cleaner: import email_service
    # Let's inline the logging for clarity in worker logs.
    import time
    time.sleep(1) # Simulate network delay
    print(f"=======================================================")
    print(f"Subject: Welcome to Car Rental System (via Celery)!")
    print(f"To: {full_name} <{email}>")
    print(f"")
    print(f"Hello {full_name}, thanks for signing up!")
    print(f"=======================================================")
    return True

