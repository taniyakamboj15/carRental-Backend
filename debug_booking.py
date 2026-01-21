from sqlmodel import Session, select
from app.db.session import engine
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.booking import Booking, BookingStatus
from app.services import booking_service
from datetime import date, timedelta
from app.schemas.booking import BookingCreate

# Mock data
start_date = date.today() + timedelta(days=1)
end_date = date.today() + timedelta(days=3)
vehicle_data = {
    "make": "Toyota", "model": "Camry", "year": 2022, 
    "license_plate": "TEST-123", "daily_rate": 50.0, 
    "status": VehicleStatus.AVAILABLE,
    "image_url": "http://example.com/car.jpg"
}

def test_create_booking():
    with Session(engine) as session:
        # 1. Get/Create User
        user = session.exec(select(User).where(User.email == "debug_user@example.com")).first()
        if not user:
            print("Creating debug user...")
            from app.core import security
            user = User(
                email="debug_user@example.com",
                hashed_password=security.get_password_hash("password"),
                full_name="Debug User",
                role="customer"
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        # 2. Get/Create Vehicle
        vehicle = session.exec(select(Vehicle).where(Vehicle.license_plate == "TEST-123")).first()
        if not vehicle:
            print("Creating debug vehicle...")
            vehicle = Vehicle(**vehicle_data)
            session.add(vehicle)
            session.commit()
            session.refresh(vehicle)

        print(f"Testing Booking for User {user.id} and Vehicle {vehicle.id}")

        # 3. Simulate Endpoint Logic
        try:
            # logic from endpoints/bookings.py
            booking_in = BookingCreate(
                vehicle_id=vehicle.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Service checks
            if not booking_service.check_availability(session, booking_in.vehicle_id, booking_in.start_date, booking_in.end_date):
                 print("Vehicle not available")
                 return

            total = booking_service.calculate_total(vehicle.daily_rate, booking_in.start_date, booking_in.end_date)
            
            print(f"Creating booking object... Total: {total}")
            booking = Booking(
                user_id=user.id,
                vehicle_id=vehicle.id,
                start_date=booking_in.start_date,
                end_date=booking_in.end_date,
                total_amount=total,
                status=BookingStatus.PENDING
            )
            session.add(booking)
            session.commit()
            session.refresh(booking)
            print("Booking created successfully:", booking)
            
        except Exception as e:
            print("BOOM! Failed to create booking:")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_create_booking()
