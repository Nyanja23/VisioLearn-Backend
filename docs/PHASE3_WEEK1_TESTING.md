# Phase 3 Week 1: Voice Session Management - Testing Guide

**Status:** ✅ **IMPLEMENTED & READY TO TEST**

---

## 📋 What We Built

**5 New Voice Endpoints:**

1. ✅ `POST /api/v1/voice/session/start` - Create voice session
2. ✅ `POST /api/v1/voice/session/event` - Log interaction
3. ✅ `POST /api/v1/voice/session/end` - End session
4. ✅ `GET /api/v1/voice/session/{id}` - Get session details
5. ✅ `GET /api/v1/voice/session/{id}/interactions` - List interactions

---

## 🧪 Testing Instructions

### Setup

1. **Ensure backend is running:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Ensure Celery is running** (in separate terminal):
   ```bash
   celery -A app.worker worker --loglevel=info --pool=solo
   ```

3. **Get your access token** (if you don't have one):
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@visiolearn.org","password":"YourPassword123!"}'
   ```
   Save the `access_token` value.

4. **Open Swagger UI** at http://localhost:8000/docs
   - Click "Authorize"
   - Paste your access token
   - Click "Authorize"

---

## 🧑‍🎓 Complete Test Flow

### Step 1: Get Your Lesson Note ID

Use the existing **GET `/api/v1/notes`** endpoint to list your lessons:

```bash
curl http://localhost:8000/api/v1/notes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Save the first note's `id`. Example: `3abe4bef-df2a-4e56-89e7-970e97ee9a67`

### Step 2: Get a Learning Unit ID

Use **GET `/api/v1/notes/{id}/units`** to list units:

```bash
curl http://localhost:8000/api/v1/notes/3abe4bef-df2a-4e56-89e7-970e97ee9a67/units \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Save the first unit's `id`. Example: `1bd01836-b6af-482e-b80a-ae47ae24cd81`

### Step 3: Get a Student ID

Use **GET `/api/v1/users`** to list users (if you have admin access):

```bash
curl http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Or create a student user first. For testing, use your own admin ID if needed.

---

## 🎤 Test Endpoint 1: Start Voice Session

**What it does:** Student starts learning → creates a voice session

```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "a6b83342-94f9-4f1d-a0f0-26efc7942277",
    "note_id": "3abe4bef-df2a-4e56-89e7-970e97ee9a67",
    "unit_id": "1bd01836-b6af-482e-b80a-ae47ae24cd81"
  }'
```

**Expected Response (201 Created):**
```json
{
  "session_id": "550e8400-e29b-41d4-...",
  "student_id": "a6b83342-94f9-4f1d-...",
  "note_id": "3abe4bef-df2a-4e56-...",
  "unit_id": "1bd01836-b6af-482e-...",
  "status": "ACTIVE",
  "started_at": "2026-04-19T15:30:00.123456+03:00"
}
```

✅ **Save the `session_id`** - you'll need it for the next tests!

---

## 🎤 Test Endpoint 2: Log Voice Interaction

**What it does:** Student answers question → logs the interaction

```bash
curl -X POST http://localhost:8000/api/v1/voice/session/event \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-...",
    "interaction_type": "answer",
    "command": "The cell nucleus is the powerhouse of the cell",
    "confidence": 0.92,
    "response": "Good try! The nucleus is the control center, not the powerhouse. The mitochondria is the powerhouse."
  }'
```

**Expected Response (201 Created):**
```json
{
  "interaction_id": "660e8401-e29c-41d5-...",
  "session_id": "550e8400-e29b-41d4-...",
  "sequence_number": 1,
  "student_transcript": "The cell nucleus is the powerhouse of the cell",
  "detected_intent": "answer",
  "ai_response_text": "Good try! The nucleus is the control center...",
  "confidence_score": 0.92,
  "created_at": "2026-04-19T15:30:15.234567+03:00"
}
```

### Test Different Interaction Types

Try these other intents:

**Next Unit:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/event \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-...",
    "interaction_type": "next",
    "command": "Next unit",
    "confidence": 0.98
  }'
```

**Repeat:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/event \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-...",
    "interaction_type": "repeat",
    "command": "Can you say that again?",
    "confidence": 0.95
  }'
```

**Free Ask:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/event \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-...",
    "interaction_type": "free_ask",
    "command": "What is photosynthesis?",
    "confidence": 0.87
  }'
```

**Pause:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/event \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-...",
    "interaction_type": "pause",
    "command": "Pause",
    "confidence": 0.99
  }'
```

✅ After `pause`, the session status changes to PAUSED

---

## 🎤 Test Endpoint 3: Get Session Details

**What it does:** Check current session status

```bash
curl http://localhost:8000/api/v1/voice/session/550e8400-e29b-41d4-... \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-...",
  "student_id": "a6b83342-94f9-4f1d-...",
  "note_id": "3abe4bef-df2a-4e56-...",
  "unit_id": "1bd01836-b6af-482e-...",
  "status": "PAUSED",
  "started_at": "2026-04-19T15:30:00.123456+03:00"
}
```

---

## 🎤 Test Endpoint 4: List Session Interactions

**What it does:** Get all interactions in chronological order

```bash
curl http://localhost:8000/api/v1/voice/session/550e8400-e29b-41d4-.../interactions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
[
  {
    "interaction_id": "660e8401-e29c-41d5-...",
    "session_id": "550e8400-e29b-41d4-...",
    "sequence_number": 1,
    "student_transcript": "The cell nucleus is the powerhouse of the cell",
    "detected_intent": "answer",
    "ai_response_text": "Good try!...",
    "confidence_score": 0.92,
    "created_at": "2026-04-19T15:30:15.234567+03:00"
  },
  {
    "interaction_id": "770e8402-e29d-41d6-...",
    "session_id": "550e8400-e29b-41d4-...",
    "sequence_number": 2,
    "student_transcript": "Next unit",
    "detected_intent": "next",
    "ai_response_text": "",
    "confidence_score": 0.98,
    "created_at": "2026-04-19T15:30:22.345678+03:00"
  }
]
```

✅ Notice `sequence_number` increments automatically!

---

## 🎤 Test Endpoint 5: End Voice Session

**What it does:** Student finishes learning → closes session

```bash
curl -X POST http://localhost:8000/api/v1/voice/session/end \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-...",
    "duration_seconds": 720,
    "questions_answered": 5,
    "total_score": 4.1
  }'
```

**Expected Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-...",
  "status": "COMPLETED",
  "duration_seconds": 720,
  "questions_answered": 5,
  "average_score": 0.82,
  "ended_at": "2026-04-19T15:42:00.456789+03:00"
}
```

✅ Session is now COMPLETED!

---

## 🧪 Using Swagger UI (Easier)

**Preferred method for testing:**

1. Open http://localhost:8000/docs

2. Click "Authorize" → paste your token

3. **Test POST /voice/session/start:**
   - Find the endpoint
   - Click "Try it out"
   - Fill in request body (copy from examples above)
   - Click "Execute"
   - See response and save session_id

4. **Test POST /voice/session/event:**
   - Paste the session_id from previous response
   - Fill in interaction details
   - Click "Execute"
   - See interaction details

5. **Test GET /voice/session/{id}:**
   - Paste session_id in path
   - Click "Execute"
   - See current session status

6. **Test GET /voice/session/{id}/interactions:**
   - Paste session_id in path
   - Click "Execute"
   - See list of all interactions in order

7. **Test POST /voice/session/end:**
   - Paste session_id
   - Fill in duration and score
   - Click "Execute"
   - See completion summary

---

## ✅ Success Criteria

Phase 3 Week 1 is complete when:

- [x] All 5 voice endpoints created
- [x] All endpoints registered in main.py
- [ ] All endpoints tested successfully
- [ ] Can create voice session
- [ ] Can log multiple interactions
- [ ] Can retrieve session details
- [ ] Can list interactions in order
- [ ] Can end session and see summary
- [ ] Session status transitions work (ACTIVE → PAUSED → COMPLETED)

---

## 🐛 Troubleshooting

**Error: "Student not found"**
- Make sure student_id exists in database
- For testing, use your own admin ID

**Error: "Lesson note not ready"**
- Make sure the note has `status: READY`
- Upload a test note with Phase 2 and wait for processing

**Error: "Learning unit not found in this lesson"**
- Make sure unit_id belongs to the note_id
- Get correct unit_id from GET /notes/{id}/units

**Error: "Session not found"**
- Make sure you're using the correct session_id from the start response

---

## 📊 Database Verification

**Check voice tables created:**

```bash
psql -U postgres -d visiolearn -c "SELECT * FROM voice_sessions LIMIT 5;"
psql -U postgres -d visiolearn -c "SELECT * FROM voice_interactions LIMIT 10;"
```

**Check session details:**

```bash
psql -U postgres -d visiolearn -c "
SELECT id, student_id, status, started_at, completed_at 
FROM voice_sessions 
ORDER BY started_at DESC LIMIT 3;
"
```

---

## 🚀 Next: Phase 3 Week 2

Once Week 1 is fully tested, proceed to:

**Phase 3 Week 2: Voice Transcription & Intent Detection**
- `POST /voice/transcribe` - Whisper API fallback
- `POST /voice/interpret` - Intent classification

See **PHASE3_PLAN.md** Section 2-3 for implementation details.

---

*Phase 3 Week 1 Complete - Ready for Testing! 🎉*
