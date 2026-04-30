# 📚 Phase 3 Week 1 - Complete Documentation Index

## 🎯 Your Questions Answered

### Question 1: Can Admin Use Voice Session?
**Answer:** ❌ **STRICTLY NO**

The endpoint validates that `student_id` must have `role="student"`. Admins have `role="admin"` and will get a 400 error: `"Can only create voice sessions for student users"`

**What admins CAN do:**
- Create sessions **for** students
- Create a test student account and use that
- Query/view student sessions

### Question 2: What Are note_id and unit_id?

**Hierarchy:**
```
Lesson Note (note_id) 
  └─ Learning Units (unit_id) [0...N]
       └─ Artefacts (questions, summaries)
```

**How to get them:**
1. Get note_id: `GET /api/v1/notes`
2. Get unit_id: `GET /api/v1/notes/{note_id}/units`
3. Use both in voice session request

**Artefacts:** AI-generated content (questions, summaries, objectives) stored in `ai_artefacts` table by `unit_id`

---

## 📖 Documentation Files

### Quick References (Read First)
- **QUICK_REF_IDS_ARTEFACTS.md** - Visual reference for IDs and artefacts (5 min)
- **VOICE_SESSION_FAQ.md** - Detailed Q&A (10 min)

### Implementation & Testing
- **PHASE3_WEEK1_README.md** - Overview (2 min)
- **PHASE3_WEEK1_QUICK_START.md** - 5-minute rapid test
- **PHASE3_WEEK1_TESTING.md** - Complete testing guide (15-30 min)
- **PHASE3_WEEK1_STATUS.md** - Technical details and schemas
- **PHASE3_WEEK1_DELIVERY.md** - Final summary

### Architecture & Planning
- **PHASE3_PLAN.md** - Full 4-week Phase 3 roadmap
- **PHASE3_QUICK_REFERENCE.md** - Features overview

### Source Code
- **app/routers/voice.py** - 5 voice session endpoints (13.3 KB)

---

## 🚀 Quick Start

### Test in 5 Minutes (Easiest)
```bash
# 1. Run backend
uvicorn app.main:app --reload

# 2. Go to Swagger
http://localhost:8000/docs

# 3. Click Authorize → paste token
# 4. Test voice endpoints
```

### Test with Commands (5 min)
Follow: **PHASE3_WEEK1_QUICK_START.md**

### Complete Testing (15-30 min)
Follow: **PHASE3_WEEK1_TESTING.md**

---

## 📊 Current State

| Component | Status | File |
|-----------|--------|------|
| Voice Session Endpoints | ✅ Complete | app/routers/voice.py |
| Testing Guide | ✅ Complete | PHASE3_WEEK1_TESTING.md |
| Documentation | ✅ Complete | Multiple files |
| Code | ✅ Verified | Syntax OK |
| Database | ✅ Compatible | Models ready |
| API | ✅ Registered | In main.py |

---

## 🎤 The 5 Endpoints

1. **POST /api/v1/voice/session/start** (201 Created)
   - Creates new voice session
   - Returns: session_id, status (ACTIVE), started_at
   - Requires: student_id (role="student"), note_id, unit_id

2. **POST /api/v1/voice/session/event** (201 Created)
   - Logs student interaction
   - Supports: answer, next, repeat, free_ask, pause
   - Returns: interaction_id, sequence_number, confidence_score

3. **POST /api/v1/voice/session/end** (200 OK)
   - Closes session
   - Calculates average_score
   - Returns: status (COMPLETED), score, duration

4. **GET /api/v1/voice/session/{id}** (200 OK)
   - Get session details
   - Shows: current status, timestamps, unit info

5. **GET /api/v1/voice/session/{id}/interactions** (200 OK)
   - List all interactions in order
   - Sorted by sequence_number
   - Shows: transcript, intent, AI response, confidence

---

## 📚 Understanding the Data

### LearningUnit Structure
```json
{
  "id": "unit_id_here",
  "note_id": "note_id_here",
  "sequence_number": 0,
  "content_text": "The actual lesson content...",
  "created_at": "2026-04-19T16:29:22.305577+03:00"
}
```

### AiArtefact Types
| Type | Purpose |
|------|---------|
| `mcq` | Multiple choice questions |
| `short_answer` | Open-ended questions |
| `fill_blank` | Complete the sentence |
| `summary_extractive` | Key sentences |
| `summary_key_points` | Bullet points |
| `learning_objectives` | Learning goals |

### Query Artefacts
```sql
-- Get all for a unit
SELECT * FROM ai_artefacts WHERE unit_id = '...';

-- Get specific type
SELECT * FROM ai_artefacts WHERE unit_id = '...' AND artefact_type = 'mcq';
```

---

## 🔐 Authentication

All endpoints require Bearer token:
```bash
-H "Authorization: Bearer YOUR_TOKEN"
```

Get token: `POST /api/v1/auth/login`

---

## ⚠️ Important Rules

### Voice Session Creation
- ✅ Student role MUST be "student" (strict validation)
- ✅ student_id must be a valid student user
- ✅ note_id must have status="READY"
- ✅ unit_id must belong to that note_id

### Admin Testing
- Create test student account with role="student"
- Use that account for voice session testing
- Admin can view/manage all sessions via admin token

---

## 🧪 Test Checklist

- [ ] All 5 endpoints respond with correct status codes
- [ ] Session creation returns session_id
- [ ] Interactions auto-increment sequence_number
- [ ] Status transitions work (ACTIVE → PAUSED → COMPLETED)
- [ ] Session details retrieval works
- [ ] All interactions can be listed
- [ ] Score calculation works on completion
- [ ] Database records persist after testing
- [ ] Bearer token auth works
- [ ] Invalid IDs return 404

---

## 🎯 Next Phases

**Phase 3 Week 2 (Ready to start):**
- Voice transcription (Whisper API)
- Intent classification
- New endpoints: /transcribe, /interpret

**Phase 3 Week 3:**
- RAG pipeline with pgvector
- Delta sync for offline
- Semantic search

**Phase 3 Week 4:**
- Integration tests
- Analytics logging
- Polish & documentation

---

## 📞 Quick Help

**Q: How do I get IDs?**
```bash
# note_id
curl /notes → copy id

# unit_id  
curl /notes/{note_id}/units → copy id
```

**Q: Can I use admin account?**
No, only student accounts. Create a test student.

**Q: Where are questions stored?**
`ai_artefacts` table, query by unit_id and artefact_type

**Q: API endpoints for artefacts?**
Not yet. Use SQL queries for now. Coming in Week 2+.

---

## 🔗 File Locations

```
/Backend
├── QUICK_REF_IDS_ARTEFACTS.md       ← START HERE for visual ref
├── VOICE_SESSION_FAQ.md              ← Detailed Q&A
├── PHASE3_WEEK1_README.md            ← Overview
├── PHASE3_WEEK1_QUICK_START.md       ← 5-min test
├── PHASE3_WEEK1_TESTING.md           ← Complete test guide
├── PHASE3_WEEK1_STATUS.md            ← Technical details
├── PHASE3_WEEK1_DELIVERY.md          ← Final summary
├── PHASE3_PLAN.md                    ← 4-week roadmap
└── app/routers/voice.py              ← Source code
```

---

## ✅ Summary

| What | Where |
|------|-------|
| Quick visual reference | QUICK_REF_IDS_ARTEFACTS.md |
| Detailed Q&A | VOICE_SESSION_FAQ.md |
| 5-minute test | PHASE3_WEEK1_QUICK_START.md |
| Complete test | PHASE3_WEEK1_TESTING.md |
| Technical details | PHASE3_WEEK1_STATUS.md |
| All answers | This file |

---

**🎉 Phase 3 Week 1 Complete & Documented!**

Start with QUICK_REF_IDS_ARTEFACTS.md or VOICE_SESSION_FAQ.md for answers to your questions.
