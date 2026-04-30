# 🎤 Phase 3 Week 1: Voice Session Management - QUICK START

**Status: ✅ READY TO TEST**

---

## 📦 What's Implemented

```
5 NEW ENDPOINTS:
├── POST   /api/v1/voice/session/start              → Create session
├── POST   /api/v1/voice/session/event              → Log interaction
├── POST   /api/v1/voice/session/end                → End session
├── GET    /api/v1/voice/session/{session_id}       → Get details
└── GET    /api/v1/voice/session/{session_id}/interactions → List all interactions

DATABASE:
├── voice_sessions (with status: ACTIVE, PAUSED, COMPLETED)
└── voice_interactions (with 5+ fields tracked per interaction)

SCHEMA FILES:
├── app/routers/voice.py (13.3 KB, 5 endpoints + schemas)
└── Fixed all ORM field mappings to actual database columns
```

---

## 🚀 Start Testing (5 Minutes)

### 1️⃣ Get Token
```bash
TOKEN=$(curl -s http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@visiolearn.org","password":"YOUR_PASSWORD"}' | jq '.access_token')
echo $TOKEN
```

### 2️⃣ Get IDs (Lesson + Unit + Student)
```bash
# Get note ID
curl http://localhost:8000/api/v1/notes -H "Authorization: Bearer $TOKEN" | jq '.data[0].id'

# Get unit ID (replace NOTE_ID)
curl http://localhost:8000/api/v1/notes/NOTE_ID/units -H "Authorization: Bearer $TOKEN" | jq '.data[0].id'

# Get student ID (use your admin ID for testing)
curl http://localhost:8000/api/v1/users -H "Authorization: Bearer $TOKEN" | jq '.data[0].id'
```

### 3️⃣ Create Voice Session
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STUDENT_ID",
    "note_id": "NOTE_ID",
    "unit_id": "UNIT_ID"
  }' | jq '.session_id'
```
**Save session_id for next steps!**

### 4️⃣ Test Interaction
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/event \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "interaction_type": "answer",
    "command": "My answer here",
    "confidence": 0.95
  }' | jq '.'
```

### 5️⃣ Get Session Details
```bash
curl http://localhost:8000/api/v1/voice/session/SESSION_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.status'
```

### 6️⃣ List Interactions
```bash
curl http://localhost:8000/api/v1/voice/session/SESSION_ID/interactions \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {sequence: .sequence_number, type: .detected_intent}'
```

### 7️⃣ End Session
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/end \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "duration_seconds": 300,
    "questions_answered": 3,
    "total_score": 2.5
  }' | jq '.status'
```
**Expected output: `"COMPLETED"`**

---

## 🧪 Full Testing Guide

See **PHASE3_WEEK1_TESTING.md** for:
- Detailed setup instructions
- Complete test flow with all 5 endpoints
- Expected responses for each endpoint
- Different interaction types (answer, next, repeat, free_ask, pause)
- Swagger UI testing (easier alternative)
- Database verification queries
- Troubleshooting

---

## 📋 Files Created/Modified

**Created:**
- ✅ `app/routers/voice.py` (13.3 KB) - Full voice session implementation
- ✅ `PHASE3_WEEK1_TESTING.md` (10.5 KB) - Complete testing guide

**Modified:**
- ✅ `app/main.py` - Registered voice router
- ✅ `app/dependencies.py` - HTTPBearer auth (already done in Phase 2)

**Schema Fixed:**
- ✅ All VoiceSession/VoiceInteraction ORM fields mapped correctly
- ✅ Status transitions: ACTIVE → PAUSED → COMPLETED
- ✅ Request/response schemas aligned with actual database columns

---

## 🎯 Success Criteria

**Week 1 Complete When:**
- [ ] All 5 endpoints tested and responding correctly
- [ ] Session creation with ACTIVE status
- [ ] Interactions logged with auto-incrementing sequence_number
- [ ] Session details retrieval working
- [ ] Interactions list returns data in order
- [ ] Session completion with score calculation
- [ ] Database records persisting correctly

---

## ⚙️ Technical Details

### Implemented Endpoints

**POST /api/v1/voice/session/start**
- Creates new VoiceSession
- Sets status = "ACTIVE"
- Returns session_id + start time

**POST /api/v1/voice/session/event**
- Logs VoiceInteraction
- Supports: answer, next, repeat, free_ask, pause
- Auto-increments sequence_number
- Updates session.last_activity_at

**POST /api/v1/voice/session/end**
- Marks session COMPLETED
- Calculates average_score
- Stores ended_at timestamp
- Returns session summary

**GET /api/v1/voice/session/{id}**
- Returns full session details
- Includes current status
- Safe for students to check own sessions

**GET /api/v1/voice/session/{id}/interactions**
- Lists all interactions in order (by sequence_number)
- Returns full transcript + AI responses
- Pagination ready

---

## 🔄 Flow Example

```
Student → POST /start
         ↓
         Session (ACTIVE)
         ↓
         POST /event (answer)
         ↓
         Interaction 1 recorded
         ↓
         POST /event (next)
         ↓
         Interaction 2 recorded
         ↓
         POST /event (pause)
         ↓
         Session (PAUSED)
         ↓
         POST /event (resume would go here in Week 2)
         ↓
         POST /end
         ↓
         Session (COMPLETED) + Score calculated
```

---

## 🚀 Next Phase

**Week 2: Voice Transcription & Intent Detection**
- Whisper API integration
- Intent classifier
- Two new endpoints: /transcribe, /interpret

**Week 3: RAG Pipeline & Delta Sync**
- pgvector embeddings
- Semantic search
- Offline data sync

**Week 4: Testing & Polish**
- Integration tests
- Analytics logging
- Documentation

---

*Ready to test? See PHASE3_WEEK1_TESTING.md for step-by-step instructions! 🎉*
