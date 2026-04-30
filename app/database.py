import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# Default to a local postgres DB if not set
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/visiolearn"
)

# Environment check for pool configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Configure connection pool for production resilience
if ENVIRONMENT == "production":
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,           # Number of connections to keep open
        max_overflow=20,        # Max extra connections when pool is exhausted
        pool_timeout=30,        # Seconds to wait for a connection
        pool_recycle=1800,      # Recycle connections after 30 minutes
        pool_pre_ping=True,     # Verify connection health before use
    )
else:
    # Development: simpler pool settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,     # Still verify connection health
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
