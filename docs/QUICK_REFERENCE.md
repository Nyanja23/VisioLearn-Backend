# VisioLearn Backend - Quick Reference Card

## Start Backend (Copy & Paste)
```powershell
cd C:\Users\josep\OneDrive\Documents\Project\Backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Quick Links
| Link | Purpose |
|------|---------|
| http://localhost:8000 | API Base URL |
| http://localhost:8000/docs | Swagger Interactive Docs |
| http://localhost:8000/redoc | ReDoc Documentation |

## Test Credentials
```
Email:    admin@visiolearn.org
Password: SecurePass123!
```

## Common curl Commands

### 1. Health Check
```powershell
curl http://localhost:8000
```

### 2. Login (Get Tokens)
```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@visiolearn.org","password":"SecurePass123!"}'
```

### 3. Use Access Token
```powershell
$token = "eyJhbGc..." # Replace with actual token from login
curl -H "Authorization: Bearer $token" http://localhost:8000/api/v1/users/
```

### 4. Refresh Token
```powershell
curl -X POST http://localhost:8000/api/v1/auth/refresh `
  -H "Content-Type: application/json" `
  -d '{"refresh_token":"eyJhbGc..."}'  # Replace with actual token
```

## Database Verification
```powershell
.\venv\Scripts\Activate.ps1
python -c "
from app.database import SessionLocal
from app import models

db = SessionLocal()
users = db.query(models.User).all()
print(f'Users: {len(users)}')
for u in users:
    print(f'  - {u.email}: {u.role}')
db.close()
"
```

## Port Already in Use?
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID with number from above)
taskkill /PID <PID> /F

# Or use different port
uvicorn app.main:app --port 8001 --reload
```

## Check PostgreSQL Service
```powershell
Get-Service postgresql-x64-18

# If not running, start it
Start-Service postgresql-x64-18
```

## Module Import Error?
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## API Endpoints
```
POST   /api/v1/auth/login      - Login with email/password
POST   /api/v1/auth/refresh    - Get new tokens
POST   /api/v1/auth/logout     - Logout (revoke token)
POST   /api/v1/users/          - Create new user (admin only)
POST   /api/v1/users/bootstrap - Create first admin (disabled)
GET    /                       - Health check
```

## File Locations
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app entry point |
| `app/routers/auth.py` | Login/logout endpoints |
| `app/routers/users.py` | User management endpoints |
| `app/models.py` | Database tables |
| `.env` | Configuration (secrets) |
| `alembic/` | Database migrations |

## Troubleshooting in 30 Seconds
1. **API won't start?** → Check Python version: `python --version`
2. **Database won't connect?** → Start service: `Start-Service postgresql-x64-18`
3. **Port 8000 in use?** → Kill with: `taskkill /PID <PID> /F` (from netstat output)
4. **Login fails?** → Try password: `SecurePass123!` (include special chars)
5. **Module not found?** → Reinstall: `pip install -r requirements.txt`

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `ALLOWED_ORIGINS` - CORS allowed domains
- `ENVIRONMENT` - "development" or "production"
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token TTL (default: 60)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token TTL (default: 90)

## Status Check (All at Once)
```powershell
# Run comprehensive test
.\TEST_BACKEND.ps1
```

## Need to Reset Database?
```powershell
# WARNING: This deletes all data!
# Drop and recreate database:
#   1. Stop the backend server
#   2. In PostgreSQL pgAdmin: right-click database → drop
#   3. Create new empty database named "visiolearn"
#   4. Restart backend (alembic will auto-migrate)
```

## Documentation
- **Setup:** See `SETUP_AND_RUN.md` (detailed guide)
- **Status:** See `STATUS_REPORT.md` (comprehensive report)
- **API Docs:** http://localhost:8000/docs (interactive)
- **Code Comments:** Check `app/` folder for inline docs

---

**Backend Status:** ✅ Operational  
**Last Verified:** 2024-12-20  
**Test Credentials Work:** ✅ Yes
