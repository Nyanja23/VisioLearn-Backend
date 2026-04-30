# 🎓 How to Create Test Student Account (For Voice Session Testing)

## 3 Simple Steps

### Step 1️⃣: Get Admin Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "admin@visiolearn.org",
    "password": "YourPassword123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**➜ Save the `access_token` as `ADMIN_TOKEN`**

---

### Step 2️⃣: Create Student Account (Using Admin Token)

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H 'Authorization: Bearer ADMIN_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "teststudent@visiolearn.org",
    "full_name": "Test Student",
    "password": "TestPass123!",
    "role": "student",
    "school_id": "d1ae8f00-e0b0-40c7-9884-8c7611acc87a"
  }'
```

Replace `ADMIN_TOKEN` with your token from Step 1.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a976-c1ae67b64e19",
  "email": "teststudent@visiolearn.org",
  "full_name": "Test Student",
  "role": "student",
  "school_id": "d1ae8f00-e0b0-40c7-9884-8c7611acc87a"
}
```

**➜ Save the `id` as `STUDENT_ID`**

---

### Step 3️⃣: Use Student for Voice Session

Now you have a real student account! Use it in voice session:

```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H 'Authorization: Bearer ADMIN_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "student_id": "550e8400-e29b-41d4-a976-c1ae67b64e19",
    "note_id": "f6540ed3-1020-4713-b14b-c1bc853422a8",
    "unit_id": "a350a896-05be-458c-8090-2e690c86da20"
  }'
```

**Response (201 Created):**
```json
{
  "session_id": "660e8401-e29c-41d5-a897-c2bf68c65f2a",
  "student_id": "550e8400-e29b-41d4-a976-c1ae67b64e19",
  "note_id": "f6540ed3-1020-4713-b14b-c1bc853422a8",
  "unit_id": "a350a896-05be-458c-8090-2e690c86da20",
  "status": "ACTIVE",
  "started_at": "2026-04-19T16:54:38.820+03:00"
}
```

✅ **Voice session created for test student!**

---

## 🎯 Complete One-Liner (Paste All at Once)

```bash
# Step 1: Login as admin
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@visiolearn.org","password":"YourPassword123!"}' | jq -r '.access_token')

echo "Admin token: $TOKEN"

# Step 2: Create student
STUDENT=$(curl -s -X POST http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"email":"teststudent@visiolearn.org","full_name":"Test Student","password":"TestPass123!","role":"student","school_id":"d1ae8f00-e0b0-40c7-9884-8c7611acc87a"}' | jq -r '.id')

echo "Student ID: $STUDENT"

# Step 3: Get note and unit
NOTE=$(curl -s http://localhost:8000/api/v1/notes \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data[0].id')

UNIT=$(curl -s http://localhost:8000/api/v1/notes/$NOTE/units \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data[0].id')

echo "Note: $NOTE"
echo "Unit: $UNIT"

# Step 4: Start voice session
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"student_id\":\"$STUDENT\",\"note_id\":\"$NOTE\",\"unit_id\":\"$UNIT\"}" | jq '.'
```

---

## ✅ What You Get

After these steps:
- ✅ Test student account created with role="student"
- ✅ Voice session created for that student
- ✅ Ready to test interactions, pause, resume, end
- ✅ Admin can still manage/view everything

---

## 🔑 Variables You Need

| Variable | Get From |
|----------|----------|
| ADMIN_TOKEN | POST /auth/login (your admin account) |
| STUDENT_ID | POST /users response (id field) |
| NOTE_ID | GET /notes (first note's id) |
| UNIT_ID | GET /notes/{NOTE_ID}/units (first unit's id) |

---

## ⚠️ Important Notes

- **Role MUST be "student"** - this is what enables voice sessions
- **school_id is required** - use the default shown or your school's ID
- **Use ADMIN_TOKEN for all calls** - it has permission to create users
- **Test student doesn't need admin privileges** - it's just for testing

---

## 🚀 Next: Test Voice Session

Once you have the session_id from Step 3, you can:

```bash
# Log an interaction
curl -X POST http://localhost:8000/api/v1/voice/session/event \
  -H "Authorization: Bearer TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "RETURNED_SESSION_ID",
    "interaction_type": "answer",
    "command": "My answer here",
    "confidence": 0.95
  }'

# View session details
curl http://localhost:8000/api/v1/voice/session/RETURNED_SESSION_ID \
  -H "Authorization: Bearer TOKEN"

# List interactions
curl http://localhost:8000/api/v1/voice/session/RETURNED_SESSION_ID/interactions \
  -H "Authorization: Bearer TOKEN"

# End session
curl -X POST http://localhost:8000/api/v1/voice/session/end \
  -H "Authorization: Bearer TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "RETURNED_SESSION_ID",
    "duration_seconds": 300,
    "questions_answered": 3,
    "total_score": 2.5
  }'
```

---

**That's it! You now have a test student and can test voice sessions.** 🎉
