import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL, use SQLite for development
if not DATABASE_URL:
    # Use SQLite for development without PostgreSQL
    DATABASE_URL = "sqlite:///./visiolearn.db"
    print("[*] No DATABASE_URL provided - using SQLite: visiolearn.db")

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
    if DATABASE_URL.startswith("sqlite"):
        # SQLite-specific configuration
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
        )
        # Enable foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        # PostgreSQL configuration
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
