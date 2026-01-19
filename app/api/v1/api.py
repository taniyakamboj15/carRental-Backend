from fastapi import APIRouter
from app.api.v1.endpoints import auth, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
from app.api.v1.endpoints import vehicles
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
from app.api.v1.endpoints import bookings
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
from app.api.v1.endpoints import payments
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
