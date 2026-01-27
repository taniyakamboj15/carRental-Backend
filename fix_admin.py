"""
Quick script to fix admin user - set is_superuser=True
"""
from sqlmodel import Session, select
from app.db.session import engine
from app.models.user import User

with Session(engine) as session:
    # Find admin user
    admin = session.exec(select(User).where(User.email == "admin@example.com")).first()
    
    if admin:
        print(f"Found admin: {admin.email}")
        print(f"Current is_superuser: {admin.is_superuser}")
        print(f"Current role: {admin.role}")
        
        # Update to superuser
        admin.is_superuser = True
        admin.role = "admin"
        
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        print(f"\n✅ Updated!")
        print(f"New is_superuser: {admin.is_superuser}")
        print(f"New role: {admin.role}")
    else:
        print("❌ Admin user not found!")
