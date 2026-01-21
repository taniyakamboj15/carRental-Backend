from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

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
  
    return "Checked expired bookings"

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
