from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.exceptions import http_exception_handler, validation_exception_handler
import time
import logging

# Setup basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
    )
    # Global Exception Handlers
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Middleware
    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Path: {request.url.path} Method: {request.method} Status: {response.status_code} Duration: {process_time:.4f}s")
        return response

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:8000"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=settings.API_V1_STR)
    return application

app = create_application()

@app.on_event("startup")
def on_startup():
    from app.db.session import engine
    from sqlmodel import Session, select
    from app.models.user import User
    from app.core import security
    
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == "admin@example.com")).first()
        if not user:
            user = User(
                email="admin@example.com",
                hashed_password=security.get_password_hash("admin123"),
                full_name="Super Admin",
                is_superuser=True,
                is_active=True,
                role="admin" # Enum string value
            )
            session.add(user)
            session.commit()
            print("----------------------------------------------------------------")
            print("Superuser created: admin@example.com / admin123")
            print("----------------------------------------------------------------")

