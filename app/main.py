import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

from .routers import auth, users, notes, voice

load_dotenv()

app = FastAPI(
    title="VisioLearn Backend",
    description="Offline-first interactive audio learning platform API for visually impaired students",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
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

# Mount nested routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)
app.include_router(voice.router)

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
