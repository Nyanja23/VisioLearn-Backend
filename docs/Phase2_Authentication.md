# Phase 2: Authentication & Role-Based Access Control (RBAC)

## Overview
Based on PRD Section 6.1 and 8.1, the VisioLearn backend requires secure authentication tailored for offline sync. The API issues short-lived JWTs (1 hour) and long-lived Refresh Tokens (90 days) configured perfectly for intermittent Android connectivity. 

Access to the system relies on Role-Based Access Control (RBAC) strictly segmented into `ADMIN`, `TEACHER`, and `STUDENT` roles. 

## What Was Completed
1.  **Security Foundations**:
    - Installed `PyJWT` for token encoding mapping to PRD constraints and `passlib` for `bcrypt` password hashing.
    - Set up a utility layer `app/security.py` spanning password hashing, JWT encoding/decoding, and verification checks.
2.  **API Structure Initialization**:
    - Created `app/main.py` configuring our `FastAPI` instance.
    - Set up `app/schemas.py` containing Pydantic models for request validation (e.g. `UserCreate`, `Token`, `LoginRequest`).
3.  **Authentication Routing (`POST /api/v1/auth/*`)**:
    - Added login endpoint: Generates paired access + refresh tokens upon verified credentials.
    - Created utility for refreshing access credentials relying tightly on database-tracked `rf_tokens`.
4.  **RBAC Dependency System**:
    - Formed `app/dependencies.py` enabling secure router mounting via `get_current_user`.
    - Added Role checker classes testing endpoints tightly against `role == "teacher"` or `role == "admin"`.

## Next Steps for Validation
1.  Boot the API locally using:
    ```bash
    .\venv\Scripts\uvicorn.exe app.main:app --reload
    ```
2.  Navigate to swagger documentation: `http://localhost:8000/docs` to test user registration and JWT claims.

Once verified, we shift securely into **Phase 3: File Upload & Task Queuing**!