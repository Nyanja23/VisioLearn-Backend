# Production Database Initialization Guide

## Problem
The production database at Render was empty, so the test credentials didn't work.

## Solution
We created `seed_database.py` to initialize the database with test users.

---

## Test Credentials

After initialization, use these credentials to test:

### Admin User
```
Email: admin@visiolearn.org
Password: AdminPass123!@
Role: admin (all permissions)
```

### Teacher User
```
Email: teacher@visiolearn.org
Password: TeacherPass123!@
Role: teacher (can upload notes, view progress)
```

### Student User
```
Email: student@visiolearn.org
Password: StudentPass123!@
Role: student (can access lessons, voice sessions)
```

---

## How to Initialize Production Database

### Quick Setup (Recommended)

**Step 1: Reset Production Database**
1. Go to [Render.com Dashboard](https://dashboard.render.com)
2. Select your PostgreSQL database
3. Click **Settings** → **Data**
4. Click **Delete database**
5. Render auto-recreates an empty one (~2 minutes)

**Step 2: Trigger Backend Redeployment**
1. Go to Backend service settings
2. Click **Manual Deploy** → **Deploy latest commit**
3. Wait for deployment to complete (runs `alembic upgrade head`)

**Step 3: Run Seed Script**
Option A (SSH - if available):
```bash
ssh your-render-instance
python seed_database.py
```

Option B (Local with Render CLI):
```bash
# Pull the Render CLI
curl https://cli.render.com/install.sh | sh

# Connect to Render
render login

# Run seed script on production
render exec your-backend-service -- python seed_database.py
```

**Step 4: Test Login**
```bash
curl -X POST https://visiolearn-backend.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@visiolearn.org",
    "password": "AdminPass123!@"
  }'
```

---

## Advanced Setup (Automated)

If you want to auto-run migrations + seeding on deployment:

**Option 1: Add to Dockerfile**
```dockerfile
# After migrations in Dockerfile entrypoint
RUN alembic upgrade head
RUN python seed_database.py
```

**Option 2: Add to Render Build Command**
In render.yaml:
```yaml
buildCommand: "pip install -r requirements.txt && alembic upgrade head && python seed_database.py"
```

**Option 3: Add Post-Deployment Hook**
In render.yaml:
```yaml
preDeployCommand: "python seed_database.py"
```

---

## Troubleshooting

### Issue: "Database already seeded. Aborting..."
**Solution:** The seed script only runs on empty databases to prevent duplicates. If you need to reseed:
```bash
# Delete all records (careful!)
python -c "
from app.database import SessionLocal
from app import models
db = SessionLocal()
db.query(models.RefreshToken).delete()
db.query(models.VoiceSessionInteraction).delete()
db.query(models.VoiceSession).delete()
db.query(models.StudentProgress).delete()
db.query(models.LessonNote).delete()
db.query(models.User).delete()
db.query(models.School).delete()
db.commit()
db.close()
print('✓ Database cleared')
"
```

Then run seed again:
```bash
python seed_database.py
```

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution:** Run from project root:
```bash
cd /path/to/VisioLearn-Backend
python seed_database.py
```

### Issue: Connection refused to database
**Solution:** 
1. Verify Render database is running (check status in dashboard)
2. Verify DATABASE_URL environment variable is set
3. Check network connectivity (firewall rules)

---

## What the Seed Script Does

1. **Checks for existing users** - Prevents duplicate data
2. **Creates demo school** - School users belong to
3. **Creates three test users** - Admin, teacher, student
4. **Hashes passwords securely** - Uses bcrypt (same as production)
5. **Commits to database** - Transactional, all-or-nothing

---

## Production Authentication Flow

After seeding, the login flow works like this:

```
User enters email/password
    ↓
POST /api/v1/auth/login
    ↓
Backend queries User table by email
    ↓
Verifies password against hashed_password with bcrypt
    ↓
Generates JWT access_token (1 hour expiry)
    ↓
Generates JWT refresh_token (7 days expiry)
    ↓
Stores refresh_token in refresh_tokens table
    ↓
Returns tokens to frontend
    ↓
Frontend stores tokens (localStorage/cookies)
    ↓
All API calls include: Authorization: Bearer <access_token>
```

---

## Next Steps

1. ✅ Run seed script on production
2. ✅ Test login with admin credentials
3. ✅ Create additional users via POST /api/v1/users endpoint
4. ✅ Change default passwords after first login
5. ✅ Configure custom domain with name.com DNS

---

## Support

If you encounter issues:
1. Check Render service logs: Dashboard → Service → Logs
2. Verify migrations ran: `alembic current`
3. Check database connection: `psql $DATABASE_URL`
4. Review seed_database.py logs for errors

