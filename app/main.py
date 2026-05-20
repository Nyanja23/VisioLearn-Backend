import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text

from .routers import auth, users, notes, voice, schools, internal, progress, classes
from .database import SessionLocal, engine
from . import models
from .security import get_password_hash, PASSWORD_HASHING_VERSION

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[*] VisioLearn Backend starting - Password hashing: {PASSWORD_HASHING_VERSION}")
    print("[*] Initializing database...")
    
    # Run Alembic migrations
    try:
        print("[*] Running database migrations...")
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations
        
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", "sqlite:///visiolearn.db"))
        
        with engine.begin() as connection:
            ctx = MigrationContext.configure(connection)
            op = Operations(ctx)
            
            # Get current revision
            current_rev = ctx.get_current_revision()
            print(f"[*] Current revision: {current_rev}")
            
            # Get target revision
            script = ScriptDirectory.from_config(alembic_cfg)
            target_rev = script.get_current_head()
            print(f"[*] Target revision: {target_rev}")
            
            if current_rev != target_rev:
                print(f"[*] Running migrations from {current_rev} to {target_rev}...")
                from alembic.command import upgrade
                upgrade(alembic_cfg, 'head')
                print("[+] Migrations completed")
            else:
                print("[+] Database is up to date")
    except Exception as e:
        print(f"[!] Migration error: {e}")
        import traceback
        traceback.print_exc()
        print("[*] Continuing despite migration errors...")
    
    try:
        # Create only the tables we need (skip analytics_events and ai_artefacts which have JSONB)
        # for SQLite compatibility
        tables_to_create = [
            models.User,
            models.RefreshToken,
            models.Class,
            models.ClassSubject,
            models.ClassMembership,
            models.LessonNote,
            models.LearningUnit,
            models.StudentProgress,
            models.ContentProgress,
        ]
        
        # Create all necessary tables
        try:
            # Create all tables at once using SQLAlchemy's metadata
            print("[*] Creating all tables...")
            models.Base.metadata.create_all(bind=engine)
            print("[+] Database tables created")
            
            # Verify by trying to query
            print("[*] Verifying table creation...")
            with engine.begin() as conn:
                # Try a simple query to each table to verify they exist
                conn.execute(text("SELECT 1 FROM users LIMIT 0"))
                print("[+] Users table verified")
        except Exception as e:
            print(f"[!] Table creation/verification error: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - try to continue anyway
            print("[*] Continuing despite table creation errors...")
        
        # Seed admin user if no users exist
        db = SessionLocal()
        try:
            existing_users = db.query(models.User).first()
            if not existing_users:
                print("[*] Creating admin user...")
                admin = models.User(
                    email="admin@visiolearn.org",
                    full_name="System Administrator",
                    role="admin",
                    hashed_password=get_password_hash("AdminPass123!@")
                )
                db.add(admin)
                db.commit()
                db.refresh(admin)
                print(f"[+] Admin user created: {admin.email}")
            else:
                user_count = db.query(models.User).count()
                print(f"[+] Users already exist ({user_count} total)")
        except Exception as e:
            print(f"[!] Error creating admin user: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"[!] Startup error: {e}")
        import traceback
        traceback.print_exc()
    
    yield
    
    # Shutdown
    print("[-] App shutting down...")

app = FastAPI(
    title="VisioLearn Backend",
    description="Offline-first interactive audio learning platform API for visually impaired students",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS configuration - use environment variable for allowed origins
def get_allowed_origins() -> list[str]:
    origins_str = os.getenv("ALLOWED_ORIGINS", "")
    if not origins_str:
        # Default to localhost only in development
        return ["http://localhost:3000", "http://localhost:8080"]
    return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

allowed_origins = get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "VisioLearn Backend API is online", "status": "success"}

# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint that verifies database connection and admin user exists.
    """
    try:
        db = SessionLocal()
        
        # Check database connection using text() wrapper for SQLAlchemy
        db.execute(text("SELECT 1"))
        
        # Check if admin exists
        admin = db.query(models.User).filter(models.User.role == "admin").first()
        
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "admin_exists": admin is not None,
            "admin_email": admin.email if admin else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Mount nested routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(schools.router)
app.include_router(notes.router)
app.include_router(progress.router)
app.include_router(classes.router)
app.include_router(voice.router)
app.include_router(internal.router)

# Configure Swagger UI security scheme for Bearer token
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="VisioLearn Backend",
        version="2.0.0",
        description="Offline-first interactive audio learning platform API for visually impaired students",
        routes=app.routes,
    )
    
    # Add Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT access token from the /login endpoint"
        }
    }
    
    # Mark all protected endpoints as requiring Bearer token
    if "paths" in openapi_schema:
        for path in openapi_schema["paths"].values():
            for operation in path.values():
                if isinstance(operation, dict) and "tags" in operation:
                    # Add security to protected endpoints
                    if any(tag in ["notes", "users"] for tag in operation.get("tags", [])):
                        operation["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
