from app.models.user import User
from app.schemas.user import UserCreate
from app.core import security
# Mock environment if needed
import os

try:
    user_in = UserCreate(
        email="test@example.com",
        password="testpassword",
        full_name="Test User",
        phone_number="1234567890"
    )
    print("UserCreate created:", user_in)
    
    # Test 1: security hash
    print("Testing password hash...")
    hashed = security.get_password_hash(user_in.password)
    print(f"Hash success: {hashed[:10]}...")
    
    # Test 2: User.from_orm
    print("Testing User.from_orm...")
    # SQLModel 0.0.14+ deprecates from_orm but it might still exist
    # User is a SQLModel
    try:
        user_obj = User.from_orm(user_in)
        print("User.from_orm success:", user_obj)
    except Exception as e:
        print(f"User.from_orm FAILED: {e}")
        # Try expected replacement?
        user_obj = User.model_validate(user_in)
        print("User.model_validate success:", user_obj)

except Exception as e:
    print(f"GENERAL FAILURE: {e}")
