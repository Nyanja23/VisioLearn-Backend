# VisioLearn Backend - Final Year Project

> **AI-powered interactive audio learning platform for visually impaired students**

## 🎯 Status: ✅ OPERATIONAL

The backend is fully set up, tested, and ready for Phase 2 development.

```
FastAPI Server ✅ | PostgreSQL ✅ | Authentication ✅ | API Docs ✅
```

---

## 🚀 Quick Start (30 seconds)

```powershell
# 1. Navigate to project
cd C:\Users\josep\OneDrive\Documents\Project\Backend

# 2. Activate environment
.\venv\Scripts\Activate.ps1

# 3. Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Then open:** http://localhost:8000/docs

---

## 📚 Documentation Guide

**Start here based on your need:**

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **QUICK_REFERENCE.md** | Copy-paste commands & common tasks | 2 min |
| **SETUP_AND_RUN.md** | Complete setup guide with troubleshooting | 10 min |
| **STATUS_REPORT.md** | Detailed system status & architecture | 15 min |
| **Phase 1-3 docs** | Previous phase documentation & planning | 5-10 min each |

**API Documentation:**
- **Interactive (Swagger):** http://localhost:8000/docs ← **Start here!**
- **Static (ReDoc):** http://localhost:8000/redoc

---

## 🔐 Test Account

```
Email:    admin@visiolearn.org
Password: SecurePass123!
Role:     admin
```

Try logging in at: http://localhost:8000/docs → Click "Authorize" → Paste token

---

## 📋 What's Included

### ✅ Working Features
- User authentication (JWT + refresh tokens)
- Role-based access control (admin, teacher, student)
- Password hashing with bcrypt
- Token refresh for offline capability
- User account management
- PostgreSQL database with migrations
- Comprehensive error handling
- CORS configuration for development

### 🔄 In Progress (Phase 2)
- Content processing (PDF/Word uploads)
- AI summarization endpoints
- Text-to-speech integration

### 📦 Installed but Not Yet Used
- spacy (NLP)
- sentence-transformers (embeddings)
- Celery + Redis (background jobs)
- PyPDF2 + python-docx (document processing)

---

## 🔗 API Endpoints

### Authentication
```
POST   /api/v1/auth/login     - Login with email/password
POST   /api/v1/auth/refresh   - Get new access token
POST   /api/v1/auth/logout    - Logout and revoke token
```

### User Management
```
POST   /api/v1/users/         - Create new user (admin only)
POST   /api/v1/users/bootstrap - Create first admin (disabled)
```

### Health
```
GET    /                      - API health check
GET    /docs                  - Swagger interactive docs
GET    /redoc                 - ReDoc documentation
```

All details in: http://localhost:8000/docs

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.14.3 |
| **Web Framework** | FastAPI | ≥0.100.0 |
| **Server** | Uvicorn | ≥0.23.0 |
| **Database** | PostgreSQL | 18 |
| **ORM** | SQLAlchemy | ≥2.0.0 |
| **Auth** | PyJWT + passlib | 2.8.0 + 1.7.4 |
| **Migration** | Alembic | ≥1.11.0 |

---

## 🏗️ Project Structure

```
Backend/
├── README.md                    ← You are here
├── QUICK_REFERENCE.md           ← Copy-paste commands
├── SETUP_AND_RUN.md             ← Detailed setup guide
├── STATUS_REPORT.md             ← System status
├── TEST_BACKEND.ps1             ← Run tests
│
├── app/                         ← Application code
│   ├── main.py                  ← FastAPI app
│   ├── database.py              ← Database setup
│   ├── models.py                ← Database models
│   ├── schemas.py               ← Pydantic schemas
│   ├── security.py              ← Auth functions
│   ├── dependencies.py          ← Auth middleware
│   └── routers/
│       ├── auth.py              ← Login/logout
│       └── users.py             ← User management
│
├── alembic/                     ← Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                ← Migration history
│
├── docs/                        ← Phase documentation
│   ├── Phase1_Database_Setup.md
│   ├── Phase2_Authentication.md
│   ├── Phase2_API_Test_Data.txt
│   ├── Phase3_Planning.md
│   └── CODE_REVIEW_FIXES.md
│
├── venv/                        ← Python environment
├── requirements.txt             ← Dependencies list
├── .env                         ← Configuration (ignored)
├── .env.example                 ← Config template
├── .gitignore                   ← Git exclusions
└── alembic.ini                  ← Migration config
```

---

## ⚡ Common Tasks

### Run the backend
```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Test all endpoints
```powershell
.\TEST_BACKEND.ps1
```

### Check database users
```powershell
.\venv\Scripts\Activate.ps1
python -c "from app.database import SessionLocal; from app import models; db = SessionLocal(); print([(u.email, u.role) for u in db.query(models.User).all()]); db.close()"
```

### Install dependencies
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Restart PostgreSQL service
```powershell
Get-Service postgresql-x64-18 | Restart-Service
```

---

## 🔍 Troubleshooting

**Backend won't start?**
- Check: `python --version` (need 3.8+)
- Check: PostgreSQL service running
- Check: Port 8000 not in use

**Login fails?**
- Password is exactly: `SecurePass123!` (with punctuation!)
- Email is lowercase: `admin@visiolearn.org`

**Database won't connect?**
- Start PostgreSQL: `Start-Service postgresql-x64-18`
- Verify connection string in `.env`

See **SETUP_AND_RUN.md** for more solutions.

---

## 📖 Documentation by Phase

### ✅ Phase 1: Setup & Authentication
- [x] Python environment configuration
- [x] FastAPI setup
- [x] PostgreSQL integration
- [x] User authentication (JWT)
- [x] User management endpoints
- [x] Security hardening
- [x] API documentation

**Read:** `docs/Phase1_Database_Setup.md` and `docs/Phase2_Authentication.md`

### 🔄 Phase 2: Content Processing & AI
- [ ] Content upload endpoints (PDF, Word)
- [ ] Document processing (text extraction)
- [ ] AI summarization integration
- [ ] Text-to-speech generation
- [ ] Background job implementation (Celery)

**See:** `docs/Phase3_Planning.md`

### 📋 Phase 3: Advanced Features
- [ ] Student progress tracking
- [ ] Teacher dashboard
- [ ] Content recommendation engine
- [ ] Analytics and reporting
- [ ] Mobile app integration

---

## 🧪 Testing

### Quick Test (30 seconds)
```powershell
curl http://localhost:8000  # Should return: {"message":"VisioLearn Backend API is online","status":"success"}
```

### Full Test Suite
```powershell
.\TEST_BACKEND.ps1
```

### Using Swagger UI
1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Paste an access token from login
4. Try endpoints directly in the UI

---

## 🔒 Security Notes

### Current Implementation
✅ Passwords hashed with bcrypt
✅ JWT tokens with expiration
✅ Refresh token rotation
✅ Token revocation on logout
✅ Email validation
✅ Role-based access control
✅ CORS configured for development

### For Production
⚠️ Change `SECRET_KEY` to a strong random value
⚠️ Use HTTPS only
⚠️ Set `ENVIRONMENT=production` in `.env`
⚠️ Update `ALLOWED_ORIGINS` to your domain
⚠️ Configure database backup strategy
⚠️ Set up monitoring and logging

See: `docs/CODE_REVIEW_FIXES.md` for security details

---

## 📞 Getting Help

1. **Can't start?** → See "Troubleshooting" section above
2. **API not responding?** → Check http://localhost:8000 (health check)
3. **Login not working?** → Try credentials from "Test Account" section
4. **Need more detail?** → Read `SETUP_AND_RUN.md`
5. **Want status info?** → Read `STATUS_REPORT.md`
6. **Quick commands?** → See `QUICK_REFERENCE.md`

---

## 📝 Notes

- This is a **Final Year Project** - handle changes carefully
- All security issues from Phase 1 code review have been fixed
- Database is PostgreSQL 18 running as Windows Service
- Python environment is properly isolated in `./venv/`
- All credentials/secrets are in `.env` (excluded from git)

---

## ✅ Verification Checklist

- [x] Backend server running on port 8000
- [x] PostgreSQL database operational
- [x] Authentication system working
- [x] API documentation accessible
- [x] Test account credentials valid
- [x] All endpoints responding
- [x] Documentation complete
- [x] Security issues resolved

---

## 🚀 Next Steps

1. **Understand the system** → Read SETUP_AND_RUN.md
2. **Test the API** → Visit http://localhost:8000/docs
3. **Review status** → Read STATUS_REPORT.md
4. **Plan Phase 2** → Read docs/Phase3_Planning.md
5. **Start development** → Begin Phase 2 work

---

**Backend Status:** ✅ **READY FOR PHASE 2**

Questions? Check the documentation files or visit http://localhost:8000/docs for interactive API testing.

**Proceed with confidence - all foundations are in place!**

---

*Last Updated: 2024-12-20*  
*Maintained by: Copilot CLI Agent*  
*Project: VisioLearn Final Year Project*
