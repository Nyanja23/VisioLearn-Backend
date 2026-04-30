# 🎯 Quick Reference: IDs and Artefacts

## 📊 The Hierarchy (Visual)

```
┌─────────────────────────────────────────────────────────┐
│ Lesson Note (e.g., "Food and Nutrition")                │
│ ID: f6540ed3-1020-4713-b14b-c1bc853422a8 ← note_id     │
│ Status: READY                                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Unit 0: "Types of Food" [seq: 0]                        │
│ ID: a350a896-05be-458c-8090-2e690c86da20 ← unit_id     │
│ Content: "Food can be grouped into..."                  │
│ Artefacts:                                              │
│   • MCQ: "Which is a protein?"                          │
│   • Short Answer: "Name 3 foods"                        │
│   • Fill Blank: "Proteins give ___ to body"            │
│   • Summary: "Key points about food types"             │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Unit 1: "Balanced Diet" [seq: 1]                        │
│ ID: b460b907-05cf-459d-8091-2e780f87da21 ← unit_id     │
│ Content: "A balanced diet has all food types..."       │
│ Artefacts:                                              │
│   • MCQ: "What makes a balanced diet?"                  │
│   • Summary: "Balanced diet requirements"              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 Getting IDs - Command Sequence

### Step 1: Get note_id

```bash
curl http://localhost:8000/api/v1/notes \
  -H "Authorization: Bearer TOKEN" | jq '.data[] | {id, title, status}'
```

**Output:**
```json
{
  "id": "f6540ed3-1020-4713-b14b-c1bc853422a8",
  "title": "Food and Nutrition",
  "status": "READY"
}
```

**→ Copy this `id` as your `note_id`**

---

### Step 2: Get unit_id from note_id

```bash
curl http://localhost:8000/api/v1/notes/f6540ed3-1020-4713-b14b-c1bc853422a8/units \
  -H "Authorization: Bearer TOKEN" | jq '.data[] | {id, sequence_number, content_text}'
```

**Output:**
```json
{
  "id": "a350a896-05be-458c-8090-2e690c86da20",
  "sequence_number": 0,
  "content_text": "Food can be grouped into..."
}
```

**→ Copy this `id` as your `unit_id`**

---

### Step 3: Use both in voice session

```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STUDENT_ID",
    "note_id": "f6540ed3-1020-4713-b14b-c1bc853422a8",
    "unit_id": "a350a896-05be-458c-8090-2e690c86da20"
  }'
```

---

## 🎓 Artefact Types

| Type | Use Case | Example |
|------|----------|---------|
| `mcq` | Multiple choice question | Question + 4 options + correct answer |
| `short_answer` | Open-ended question | Question + expected answer + rubric |
| `fill_blank` | Complete the sentence | Sentence with ___ + correct word |
| `summary_extractive` | Key sentences from lesson | 3-5 most important sentences |
| `summary_key_points` | Bullet point summary | • Point 1<br>• Point 2<br>• Point 3 |
| `learning_objectives` | What student will learn | "By end of unit you will..." |

---

## 📥 Getting Artefacts for a Unit

### Option A: Direct Database Query

```bash
# Get ALL artefacts for a unit
psql -U postgres -d visiolearn -c "
SELECT id, artefact_type, created_at 
FROM ai_artefacts 
WHERE unit_id = 'a350a896-05be-458c-8090-2e690c86da20'
ORDER BY created_at;
"
```

### Option B: Get Specific Type

```bash
# Get only MCQ questions
psql -U postgres -d visiolearn -c "
SELECT content FROM ai_artefacts 
WHERE unit_id = 'a350a896-05be-458c-8090-2e690c86da20' 
AND artefact_type = 'mcq';
"
```

### Option C: Future API Endpoint (Phase 3 Week 2+)
```bash
# These endpoints don't exist yet, but will be:
GET /api/v1/notes/{note_id}/units/{unit_id}/questions
GET /api/v1/notes/{note_id}/units/{unit_id}/summaries
GET /api/v1/notes/{note_id}/units/{unit_id}/objectives
```

---

## ❌ Admin Account CANNOT Start Voice Session

### ❌ This WILL FAIL
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "student_id": "ADMIN_USER_ID",  ← Wrong! Role = "admin"
    "note_id": "...",
    "unit_id": "..."
  }'

# Response:
# 400 Bad Request
# "Can only create voice sessions for student users"
```

### ✅ This WILL WORK
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "student_id": "STUDENT_USER_ID",  ← Correct! Role = "student"
    "note_id": "...",
    "unit_id": "..."
  }'

# Response:
# 201 Created
# Session started for the student
```

---

## 📋 Complete Flow Checklist

- [ ] Get admin token: `POST /api/v1/auth/login`
- [ ] Get all notes: `GET /api/v1/notes` → save **note_id**
- [ ] Get units: `GET /api/v1/notes/{note_id}/units` → save **unit_id**
- [ ] Get student ID (create test student if needed)
- [ ] Start session: `POST /api/v1/voice/session/start` with **student_id**, **note_id**, **unit_id**
- [ ] Log interaction: `POST /api/v1/voice/session/event`
- [ ] View session: `GET /api/v1/voice/session/{session_id}`
- [ ] List interactions: `GET /api/v1/voice/session/{session_id}/interactions`
- [ ] End session: `POST /api/v1/voice/session/end`

---

## 🔗 File References

See these for more details:
- **VOICE_SESSION_FAQ.md** - Detailed Q&A
- **PHASE3_WEEK1_TESTING.md** - Complete testing guide
- **PHASE3_WEEK1_QUICK_START.md** - 5-minute rapid test
- **app/routers/voice.py** - Source code

