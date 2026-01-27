from app.db.session import engine
from sqlalchemy import text

def check_column():
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='city';"
        ))
        row = result.fetchone()
        if row:
            print("SUCCESS: Column 'city' found in table 'user'.")
        else:
            print("FAILURE: Column 'city' NOT found in table 'user'.")

if __name__ == "__main__":
    check_column()
