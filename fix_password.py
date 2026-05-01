from app.security import verify_password, get_password_hash
from app.models import User
from app.database import SessionLocal

session = SessionLocal()

# Get the first user
user = session.query(User).first()

if user:
    print(f"\nUser: {user.email}")
    print(f"Stored hash: {user.hashed_password[:50]}...\n")
    
    # Test password
    password = "BootstrapPass123!@"
    is_correct = verify_password(password, user.hashed_password)
    print(f"Testing password: '{password}'")
    print(f"Match: {is_correct}\n")
    
    if not is_correct:
        print("Password doesn't match. Regenerating hash...\n")
        new_hash = get_password_hash(password)
        print(f"New hash: {new_hash[:50]}...")
        print(f"Test new hash: {verify_password(password, new_hash)}\n")
        
        # Update in database
        user.hashed_password = new_hash
        session.commit()
        print("Database updated with correct password hash!")

session.close()
