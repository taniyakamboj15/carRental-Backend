from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from sqlmodel import Session, select
from app.db.session import engine
from app.models.booking import Booking, BookingStatus
from datetime import date

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
    

    print("Checking for expired bookings...")
    
    today = date.today()
    
    with Session(engine) as session:
        # 1. Mark CONFIRMED bookings as COMPLETED if end_date < today
        statement_completed = select(Booking).where(
            Booking.status == BookingStatus.CONFIRMED,
            Booking.end_date < today
        )
        expired_active_bookings = session.exec(statement_completed).all()
        
        for booking in expired_active_bookings:
            print(f"Completing booking {booking.id} (End date: {booking.end_date})")
            booking.status = BookingStatus.COMPLETED
            session.add(booking)
            
        # 2. Mark PENDING bookings as CANCELLED if start_date < today (expired request)
        statement_cancelled = select(Booking).where(
            Booking.status == BookingStatus.PENDING,
            Booking.start_date < today
        )
        expired_pending_bookings = session.exec(statement_cancelled).all()
        
        for booking in expired_pending_bookings:
            print(f"Cancelling expired pending booking {booking.id} (Start date: {booking.start_date})")
            booking.status = BookingStatus.CANCELLED
            session.add(booking)

        session.commit()
        
        # 3. Mark PENDING bookings as CANCELLED if created_at < 15 mins ago (payment timeout)
        # Note: In a real app, successful payment would move status to CONFIRMED.
        # If it's still PENDING after 15 mins, they abandonned payment.
        from datetime import datetime, timedelta
        timeout_threshold = datetime.utcnow() - timedelta(minutes=15)
        
        statement_timeout = select(Booking).where(
            Booking.status == BookingStatus.PENDING,
            Booking.created_at < timeout_threshold
        )
        timeout_bookings = session.exec(statement_timeout).all()

        for booking in timeout_bookings:
            print(f"Cancelling timed-out booking {booking.id} (Created at: {booking.created_at})")
            booking.status = BookingStatus.CANCELLED
            session.add(booking)
            
        session.commit()
        
        count_completed = len(expired_active_bookings)
        count_cancelled = len(expired_pending_bookings) + len(timeout_bookings)

    return f"Checked bookings. Completed: {count_completed}, Cancelled: {count_cancelled}"

@celery_app.task
def send_tomorrow_reminders():
    print("Sending reminders...")
    return "Reminders sent"

@celery_app.task(acks_late=True)
def send_email_async(email: str, subject: str, message: str):
    import time
    time.sleep(2) 
    print(f"Sent email to {email}: {subject}")
    return True
