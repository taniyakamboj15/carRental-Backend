from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_alembic_version():
    engine = create_engine(str(settings.DATABASE_URL))
    with engine.connect() as connection:
        # Check if table exists
        result = connection.execute(text("SELECT * FROM alembic_version"))
        rows = result.fetchall()
        print(f"Current version: {rows}")
        
        # Update
        connection.execute(text("UPDATE alembic_version SET version_num = '10791b02b1d3'"))
        connection.commit()
        
        # Verify
        result = connection.execute(text("SELECT * FROM alembic_version"))
        print(f"New version: {result.fetchall()}")

if __name__ == "__main__":
    fix_alembic_version()
