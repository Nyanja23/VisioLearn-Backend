# 🎤 Voice Session FAQ - Critical Questions

## ❓ Q1: Can I Use Admin Account to Start Voice Session?

**STRICT ANSWER: ❌ NO** 

The endpoint enforces that `student_id` must be a user with `role="student"`.

### Code Validation (voice.py, lines 121-125)

```python
if student.role != "student":
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Can only create voice sessions for student users"
    )
```

### What You'll Get if You Try

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "student_id": "ADMIN_USER_ID",
    "note_id": "...",
    "unit_id": "..."
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Can only create voice sessions for student users"
}
```

### What Admins CAN Do

✅ Create sessions **for** students (by passing their student_id)
✅ Create a test student account and test with that
✅ Query/view student sessions
✅ Manage lesson notes for students

### Recommended Approach for Testing

1. Create a student user first
2. Pass that student's ID in the voice session request
3. Admin can then manage/view that student's sessions

---

## ❓ Q2: What Are note_id and unit_id? How Do I Get "Artefacts"?

### The Data Hierarchy

```
Lesson Note (uploaded file - e.g., "Living Things")
│
├── note_id = "f6540ed3-1020-4713-b14b-c1bc853422a8"
│
└── Learning Units (content chunks)
    │
    ├── unit_id[0] = "a350a896-05be-458c-8090-2e690c86da20" (sequence 0)
    │   ├── content_text: "What are living things..."
    │   └── Artefacts:
    │       ├── Questions (MCQ, short answer, fill-in)
    │       ├── Summary (extractive, key points)
    │       └── Learning objectives
    │
    ├── unit_id[1] = "b460b907-05cf-459d-8091-2e780f87da21" (sequence 1)
    │   ├── content_text: "What are non-living things..."
    │   └── Artefacts: ...
    │
    └── unit_id[N] = "..." (sequence N)
```

### IDs Explained

| ID | Meaning | Example | Where to Get |
|---|---|---|---|
| **note_id** | ID of the uploaded lesson file | `f6540ed3-1020-4713-b14b-c1bc853422a8` | `GET /api/v1/notes` |
| **unit_id** | ID of one content chunk in the lesson | `a350a896-05be-458c-8090-2e690c86da20` | `GET /api/v1/notes/{note_id}/units` |

### Step-by-Step to Get All IDs

#### Step 1: Get All Lesson Notes
```bash
curl http://localhost:8000/api/v1/notes \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
[
  {
    "id": "f6540ed3-1020-4713-b14b-c1bc853422a8",  ← note_id
    "title": "Food and Nutrition",
    "subject": "Science",
    "grade_level": "P4",
    "status": "READY",
    "created_at": "2026-04-19T16:29:22.305577+03:00"
  },
  ...
]
```

**Save:** `f6540ed3-1020-4713-b14b-c1bc853422a8` as your note_id

#### Step 2: Get All Learning Units in That Note
```bash
curl http://localhost:8000/api/v1/notes/f6540ed3-1020-4713-b14b-c1bc853422a8/units \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
[
  {
    "id": "a350a896-05be-458c-8090-2e690c86da20",  ← unit_id
    "note_id": "f6540ed3-1020-4713-b14b-c1bc853422a8",
    "sequence_number": 0,
    "content_text": "Food is anything we eat or drink...",
    "created_at": "2026-04-19T16:29:22.305577+03:00"
  },
  {
    "id": "b460b907-05cf-459d-8091-2e780f87da21",  ← another unit_id
    "note_id": "f6540ed3-1020-4713-b14b-c1bc853422a8",
    "sequence_number": 1,
    "content_text": "Types of food include proteins...",
    "created_at": "2026-04-19T16:29:22.305577+03:00"
  }
]
```

**Save:** `a350a896-05be-458c-8090-2e690c86da20` as your unit_id

#### Step 3: Now You Can Start Voice Session
```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "YOUR_STUDENT_ID",
    "note_id": "f6540ed3-1020-4713-b14b-c1bc853422a8",
    "unit_id": "a350a896-05be-458c-8090-2e690c86da20"
  }'
```

---

## 📦 What Are "Artefacts"?

**Artefacts** = Questions, summaries, and other AI-generated content for a learning unit

### Artefact Types (Stored in `ai_artefacts` table)

| Type | Purpose | Example |
|------|---------|---------|
| `mcq` | Multiple choice question | "Which of these is a protein?" |
| `short_answer` | Open-ended question | "What is photosynthesis?" |
| `fill_blank` | Fill in the blank | "Mitochondria is the ___ of the cell" |
| `summary_extractive` | Key sentences from content | 5 most important sentences |
| `summary_key_points` | Bullet points | • Point 1<br>• Point 2 |
| `learning_objectives` | Learning goals | "By end of unit, student will know..." |

### Database Schema: ai_artefacts

```sql
CREATE TABLE ai_artefacts (
    id UUID PRIMARY KEY,
    unit_id UUID NOT NULL,  -- FK to learning_units
    artefact_type VARCHAR(50),  -- mcq, short_answer, etc.
    content JSONB,  -- structured question/answer data
    created_at DATETIME
);
```

### How to Query Artefacts for a Unit

```sql
-- Get all artefacts for a unit
SELECT * FROM ai_artefacts WHERE unit_id = 'a350a896-...';

-- Get only MCQ questions
SELECT * FROM ai_artefacts 
WHERE unit_id = 'a350a896-...' 
AND artefact_type = 'mcq';

-- Get all summaries
SELECT * FROM ai_artefacts 
WHERE unit_id = 'a350a896-...' 
AND artefact_type LIKE 'summary%';
```

### Example MCQ Artefact Content

```json
{
  "id": "d574c018-...",
  "unit_id": "a350a896-05be-458c-8090-2e690c86da20",
  "artefact_type": "mcq",
  "content": {
    "question": "Which of these is a protein?",
    "options": [
      "Water",
      "Meat",
      "Sugar",
      "Carbohydrate"
    ],
    "correct_answer": "Meat",
    "explanation": "Proteins are found in meat, eggs, beans..."
  }
}
```

### Example Short Answer Artefact

```json
{
  "id": "e685d129-...",
  "unit_id": "a350a896-05be-458c-8090-2e690c86da20",
  "artefact_type": "short_answer",
  "content": {
    "question": "Name three types of food in Uganda",
    "expected_answer": "Matoke, beans, rice",
    "rubric": "Award points for each valid Ugandan food mentioned"
  }
}
```

---

## 🧠 Understanding the Full Flow

### For Learning (Student Perspective)

```
1. Student logs in → authenticated
2. Browse lessons → GET /notes
3. Pick lesson → GET /notes/{note_id}/units
4. Start learning unit:
   → POST /voice/session/start
   → Session created (ACTIVE)
   → Unit loaded for studying
5. Student answers questions:
   → POST /voice/session/event (answer)
   → Interaction logged with confidence score
6. Student continues or pauses:
   → POST /voice/session/event (next/pause/repeat)
7. Student finishes:
   → POST /voice/session/end
   → Score calculated
   → Session closed (COMPLETED)
```

### For Content (Backend Perspective)

```
Teacher uploads file
    ↓
Phase 2 Processing:
    • Extracts text from file
    • Chunks into learning units → LearningUnit table
    • Generates questions → ai_artefacts table (type=mcq, etc.)
    • Generates summaries → ai_artefacts table (type=summary_*)
    • Marks note as READY
    ↓
Phase 3 (Voice Sessions):
    Student can now start voice sessions
    Each interaction is logged and scored
```

---

## 📋 Common Scenarios

### Scenario 1: Test Voice Session with Admin

**Goal:** Admin wants to test voice session functionality

```bash
# 1. Create a test student
POST /api/v1/users
{
  "email": "teststudent@school.org",
  "password": "Pass123!",
  "full_name": "Test Student",
  "role": "student"
}
# Save response: test_student_id

# 2. Get note and unit IDs
GET /api/v1/notes
# Save: note_id

GET /api/v1/notes/{note_id}/units
# Save: unit_id

# 3. Start session as test student
POST /api/v1/voice/session/start
{
  "student_id": "test_student_id",
  "note_id": "note_id",
  "unit_id": "unit_id"
}

# 4. Admin can now view the session
GET /api/v1/voice/session/{session_id}
```

### Scenario 2: Get All Questions for a Unit

**Goal:** Retrieve MCQ questions to display in UI

```bash
# 1. Get unit details
GET /api/v1/notes/{note_id}/units
# Save unit_id you want

# 2. Query questions (raw SQL or future endpoint)
SELECT * FROM ai_artefacts 
WHERE unit_id = 'YOUR_UNIT_ID' 
AND artefact_type = 'mcq';

# This returns all MCQ questions for that unit
```

### Scenario 3: Get Summary for a Unit

**Goal:** Display lesson summary to student

```bash
# Get extractive summary
SELECT * FROM ai_artefacts 
WHERE unit_id = 'YOUR_UNIT_ID' 
AND artefact_type = 'summary_extractive';

# Get key points
SELECT * FROM ai_artefacts 
WHERE unit_id = 'YOUR_UNIT_ID' 
AND artefact_type = 'summary_key_points';
```

---

## ⚠️ Important Notes

### Authentication
- Student sessions **must** have `role="student"` ❌ Admin/teacher cannot use own account
- But admin **can** create session **for** student
- All endpoints require valid Bearer token

### Data Integrity
- A unit_id **must** belong to the note_id you specify
- Endpoint validates: `WHERE unit_id = ? AND note_id = ?`
- If mismatched, you get 404 error

### Artefacts
- Currently stored but **no dedicated endpoint** yet to retrieve them
- You can query directly from `ai_artefacts` table
- Or wait for Phase 3 Week 2+ to add endpoints

---

## 🔗 Quick Command Reference

```bash
# Get all lessons
curl http://localhost:8000/api/v1/notes \
  -H "Authorization: Bearer TOKEN"

# Get units in a lesson
curl http://localhost:8000/api/v1/notes/{NOTE_ID}/units \
  -H "Authorization: Bearer TOKEN"

# Start voice session (MUST use student_id)
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"student_id":"...","note_id":"...","unit_id":"..."}'

# Query artefacts directly (psql)
psql -c "SELECT * FROM ai_artefacts WHERE unit_id='...';"
```

---

## ✅ Summary

| Question | Answer |
|----------|--------|
| **Can admin use voice session?** | ❌ No (role must be "student") |
| **Can admin create session for student?** | ✅ Yes |
| **Where to get note_id?** | `GET /notes` |
| **Where to get unit_id?** | `GET /notes/{note_id}/units` |
| **What are artefacts?** | Questions, summaries, learning objectives |
| **Where are artefacts stored?** | `ai_artefacts` table |
| **Artefact types?** | mcq, short_answer, fill_blank, summary_extractive, summary_key_points, learning_objectives |

---

*Phase 3 Week 1 - Voice Session FAQ*
