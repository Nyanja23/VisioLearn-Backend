# VisioLearn Backend - Setup & Running Guide

## ✅ Status: BACKEND IS RUNNING & FUNCTIONAL

**Current State:** FastAPI backend is successfully running on `http://localhost:8000`
- ✅ Python 3.14.3 installed
- ✅ Virtual environment (`venv`) active  
- ✅ Dependencies installed via pip
- ✅ PostgreSQL database connected (Service: postgresql-x64-18 - Running)
- ✅ Database schema initialized (Alembic migrations applied)
- ✅ Authentication system functional (JWT + Refresh tokens)
- ✅ Admin user created and verified

---

## Quick Start (Windows)

### 1. Activate Virtual Environment
```powershell
cd C:\Users\josep\OneDrive\Documents\Project\Backend
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies (if needed)
```powershell
pip install -r requirements.txt
```

### 3. Start the Backend Server
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 4. Access the API
- **API Root:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc Docs:** http://localhost:8000/redoc

---

## API Endpoints Overview

### Authentication Endpoints (`/api/v1/auth`)
```
POST /api/v1/auth/login
  - Login with email and password
  - Returns: access_token, refresh_token, token_type
  - Test: {"email":"admin@visiolearn.org","password":"SecurePass123!"}

refresh: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODQzNzE0OTYsInN1YiI6ImE2YjgzMzQyLTk0ZjktNGYxZC1hMGYwLTI2ZWZjNzk0MjI3NyIsInR5cGUiOiJyZWZyZXNoIn0.0buAKL1YjWeQV10zxwFTQvkjWp75bAPgdkEoIAV5hMc

access: 
POST /api/v1/auth/refresh
  - Refresh an expired access token
  - Request: {"refresh_token":"..."}
  - Returns: New access_token and refresh_token pair

POST /api/v1/auth/logout
  - Logout and revoke refresh token
  - Requires: Authorization header with Bearer token
```

### User Management Endpoints (`/api/v1/users`)
```
POST /api/v1/users/bootstrap
  - Create first admin account (only works when no users exist)
  - Status: DISABLED (Users already exist in DB)

POST /api/v1/users/
  - Create new user (requires admin authentication)
  - Requires: Bearer token of admin user
  - Request: {"email":"...", "password":"...", "full_name":"...", "role":"...", "school_id":null}
```

### Root Endpoint
```
GET /
  - Health check
  - Returns: {"message":"VisioLearn Backend API is online","status":"success"}
```

---

## Testing Guide

### Test 1: Health Check
```powershell
curl http://localhost:8000
```

**Expected:** `{"message":"VisioLearn Backend API is online","status":"success"}`

### Test 2: Login
```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@visiolearn.org","password":"SecurePass123!"}'
```

**Expected:** Returns access_token, refresh_token, and token_type="bearer"

### Test 3: Use Access Token (Protected Endpoint)
```powershell
# First, get a token
$response = curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@visiolearn.org","password":"SecurePass123!"}' | ConvertFrom-Json

$token = $response.access_token

# Use token in Authorization header
curl -H "Authorization: Bearer $token" http://localhost:8000/api/v1/users/
```

### Test 4: Refresh Token
```powershell
# Get tokens from login
$login = curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@visiolearn.org","password":"SecurePass123!"}' | ConvertFrom-Json

# Use refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh `
  -H "Content-Type: application/json" `
  -d "{`"refresh_token`":`"$($login.refresh_token)`"}"
```

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3ODQzNjQ1MzAsInN1YiI6ImE2YjgzMzQyLTk0ZjktNGYxZC1hMGYwLTI2ZWZjNzk0MjI3NyIsInR5cGUiOiJyZWZyZXNoIn0.LICfuJRLWHSH4q9TmWGojtViX7xJVTMJu8opRdqjFe4

---

## Default Test Credentials

**Admin Account:**
- Email: `admin@visiolearn.org`
- Password: `SecurePass123!`
- Role: `admin`

**Secondary Admin:**
- Email: `admin2@visiolearn.org`
- Password: `SecurePass123!`
- Role: `admin`

---

## Database Information

### PostgreSQL Connection
- **Host:** localhost
- **Port:** 5432
- **Database:** visiolearn
- **User:** postgres
- **Service Status:** ✅ Running (postgresql-x64-18)

### Database Schema
Managed by **Alembic** (SQL migration tool)
- Migrations are in: `./alembic/`
- Configuration: `./alembic.ini`
- Status: ✅ All migrations applied

**Current Tables:**
- `users` - User accounts with JWT tokens
- `refresh_tokens` - Token rotation and revocation
- Additional tables TBD (Phase 3+)

### Verify Database Connection
```powershell
# Using Python in venv
.\venv\Scripts\Activate.ps1
python -c "
from app.database import SessionLocal
from app import models

db = SessionLocal()
users = db.query(models.User).all()
print(f'Users in database: {len(users)}')
db.close()
"
```

---

## Environment Variables (.env)

**Required for Backend to Run:**
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/visiolearn
SECRET_KEY=<auto-generated or set to strong random string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=90
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
ENVIRONMENT=development
```

**Check Current Values:**
```powershell
# View .env file (Windows)
Get-Content .env
```

---

## Common Issues & Troubleshooting

### Issue: "Cannot connect to PostgreSQL"
**Solution:**
```powershell
# Check if PostgreSQL service is running
Get-Service postgresql-x64-18

# If not running, start it
Start-Service postgresql-x64-18
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:**
```powershell
# Activate venv and install
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue: "Incorrect email or password" on Login
**Check:**
- Email is exact match: `admin@visiolearn.org` (lowercase)
- Password is exact: `SecurePass123!`
- Database user exists (see: Verify Database Connection above)

### Issue: Server won't start on port 8000
**Solution:**
```powershell
# Check if port is in use
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Try different port
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Issue: "CORS error" from frontend
**Solution:** Update `.env`
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://your-frontend-url
```
Then restart server.

---

## Project Structure

```
Backend/
├── app/
│   ├── main.py              ← FastAPI app setup + CORS config
│   ├── database.py          ← SQLAlchemy engine & session setup
│   ├── models.py            ← Database ORM models (User, RefreshToken)
│   ├── schemas.py           ← Pydantic validation schemas
│   ├── security.py          ← Password hashing, JWT token creation
│   ├── dependencies.py      ← FastAPI dependency functions (auth)
│   └── routers/
│       ├── auth.py          ← Login, refresh, logout endpoints
│       └── users.py         ← User creation, bootstrap endpoints
├── alembic/                 ← Database migrations
├── docs/                    ← Previous documentation (Phase 1-3)
├── venv/                    ← Python virtual environment
├── requirements.txt         ← Python dependencies
├── .env                     ← Environment config (secrets)
├── .env.example             ← Environment template
└── alembic.ini              ← Alembic configuration
```

---

## Performance & Features

### Current Capabilities
- ✅ User authentication with JWT tokens
- ✅ Token refresh for offline-first app
- ✅ Role-based access control (RBAC): admin, teacher, student
- ✅ Password hashing with bcrypt
- ✅ Email validation
- ✅ CORS configuration
- ✅ Error handling with detailed messages
- ✅ Transaction management with rollback

### AI/ML Features (Not Yet Tested)
- `spacy` - Natural Language Processing
- `sentence-transformers` - Semantic embeddings
- `PyPDF2` - PDF content extraction
- `python-docx` - Word document extraction

These are installed in `requirements.txt` but endpoints to use them are in **Phase 3** planning.

### Background Jobs (Celery)
- Redis queue installed but not yet tested
- Celery tasks not yet implemented

---

## Next Steps

### Phase 1: ✅ COMPLETE
- [x] Backend setup and running
- [x] Authentication system
- [x] User management
- [x] Database connectivity

### Phase 2: 🔄 IN PROGRESS
- [ ] Content processing (PDF/Word uploads)
- [ ] AI-powered content summarization
- [ ] Audio generation endpoints

### Phase 3: 📋 PLANNED
- [ ] Celery background job implementation
- [ ] Content recommendation engine
- [ ] Student progress tracking
- [ ] Teacher dashboard

---

## Support & Documentation

### API Documentation
- **Interactive (Swagger):** http://localhost:8000/docs
- **API Schema (ReDoc):** http://localhost:8000/redoc

### Code Documentation
- See: `./docs/` folder for:
  - `Phase1_Database_Setup.md` - Schema design
  - `Phase2_Authentication.md` - Auth flow explanation
  - `Phase3_Planning.md` - Future roadmap
  - `CODE_REVIEW_FIXES.md` - Security fixes applied

### PRD (Product Requirements)
- `VisioLearn_Backend_PRD.docx.pdf` - Full requirements
- `VisioLearn_Backend_PRD_Amendment_A_Voice.docx.pdf` - Voice feature spec
- `prd_consolidated.md` - Markdown summary

---

## Version Information

- **Python:** 3.14.3
- **FastAPI:** ≥0.100.0
- **SQLAlchemy:** ≥2.0.0
- **PostgreSQL:** 18
- **Alembic:** ≥1.11.0

---

**Last Updated:** 2024-12-XX  
**Status:** ✅ Backend Operational  
**Next Review:** After Phase 2 implementation



