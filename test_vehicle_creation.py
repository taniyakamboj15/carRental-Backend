import logging
import sys
from sqlmodel import Session
from app.db.session import engine
from app.models.vehicle import Vehicle, VehicleStatus
from app.schemas.vehicle import VehicleCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_vehicle() -> None:
    try:
        vehicle_in = VehicleCreate(
            make="Toyota",
            model="Camry",
            year=2024,
            license_plate="TEST-123",
            daily_rate=50.0,
            status=VehicleStatus.AVAILABLE
        )
        logger.info(f"Schema validation passed: {vehicle_in}")
        
        with Session(engine) as session:
            vehicle = Vehicle.from_orm(vehicle_in)
            session.add(vehicle)
            session.commit()
            session.refresh(vehicle)
            logger.info(f"Created vehicle: {vehicle}")
            
    except Exception as e:
        logger.error(f"Error creating vehicle: {e}")

if __name__ == "__main__":
    create_test_vehicle()
