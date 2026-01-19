from sqlmodel import create_engine, Session
from app.core.config import settings

# echo=True is useful for debugging to see generated SQL
engine = create_engine(str(settings.DATABASE_URL), echo=True)

def get_session():
    with Session(engine) as session:
        yield session
