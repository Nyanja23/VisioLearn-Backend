from app.models import User
from app.database import SessionLocal

session = SessionLocal()

print("\n=== USERS IN DATABASE ===\n")
users = session.query(User).all()
if users:
    for user in users:
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"ID: {user.id}")
        print()
else:
    print("NO USERS FOUND")

session.close()
