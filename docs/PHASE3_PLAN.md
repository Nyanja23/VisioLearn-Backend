# VisioLearn Backend - Phase 3 Roadmap

**Status:** 📋 Planning Phase  
**Reference:** PRD Consolidated v1.2, Amendment A v1.1  
**Phase 2 Completion:** ✅ VERIFIED & WORKING  

---

## 📋 Executive Summary

Phase 3 focuses on **student-facing features**: voice interaction, progress tracking, and offline synchronization. Students will interact with lessons through voice commands, answer questions, and use "Free Ask Mode" for questions beyond lesson content.

### Key Deliverables
1. **Voice Session Management** - Track student interactions
2. **Voice Transcription & Interpretation** - Convert speech to intent
3. **RAG Pipeline** - Answer free questions from lesson content
4. **Delta Sync Protocol** - Efficient offline/online sync
5. **Progress Tracking** - Score and time tracking per student
6. **Analytics Logging** - Anonymous research data collection

---

## 🗓️ Phase 3 Timeline (4 Weeks Estimated)

### Week 1: Voice Foundation
- [ ] Voice Session Management (POST /voice/session/start, /event, /end)
- [ ] Database voice_sessions & voice_interactions tables verified
- [ ] Session state machine implemented (ACTIVE → PAUSED → COMPLETED)

### Week 2: Voice Processing
- [ ] Voice Transcription endpoint (POST /voice/transcribe) using Whisper
- [ ] Voice Intent Interpretation (POST /voice/interpret)
- [ ] Intent taxonomy mapping (answer, next-unit, repeat, free-ask, pause)

### Week 3: Advanced Features
- [ ] RAG Pipeline for Free Ask (POST /voice/ask)
- [ ] Embeddings storage & semantic search setup
- [ ] Delta Sync Protocol (GET /sync/pull, POST /sync/push)

### Week 4: Polish & Testing
- [ ] Student Progress Tracking endpoints
- [ ] Analytics Logging (POST /analytics/event)
- [ ] Integration tests covering full flow
- [ ] Documentation & deployment guide

---

## 🎯 Detailed Implementation Guide

### 1. Voice Session Management

**What it does:**
- Student starts lesson → creates voice_session
- Student answers questions, navigates units → logs voice_interactions
- Each interaction captures: intent, command, response, timestamp

**Endpoints to Create:**

```http
POST /api/v1/voice/session/start
Request: {
  "student_id": "uuid",
  "note_id": "uuid",
  "unit_id": "uuid"
}
Response: {
  "session_id": "uuid",
  "status": "ACTIVE",
  "started_at": "2026-04-19T15:00:00Z"
}

POST /api/v1/voice/session/event
Request: {
  "session_id": "uuid",
  "interaction_type": "answer|next|repeat|free_ask|pause",
  "command": "What is a cell?",
  "confidence": 0.92
}
Response: {
  "interaction_id": "uuid",
  "action": "play_question"
}

POST /api/v1/voice/session/end
Request: {
  "session_id": "uuid",
  "duration_seconds": 1200,
  "questions_answered": 5
}
Response: {
  "session_id": "uuid",
  "status": "COMPLETED",
  "summary": {...}
}
```

**Database Impact:**
- Insert into `voice_sessions` (student_id, note_id, status, started_at, ended_at)
- Insert into `voice_interactions` (session_id, sequence_number, interaction_type, command, response, confidence)

**Reference:** PRD Section 7.2 Voice Session State Machine, Amendment A Section 21.2

---

### 2. Voice Transcription Fallback

**What it does:**
- When Android app's ASR confidence < 0.65, falls back to server
- Sends raw audio → receives transcribed text
- Uses OpenAI Whisper small model (~1GB)

**Endpoint:**

```http
POST /api/v1/voice/transcribe
Content-Type: audio/wav (or audio/mp3)
Request: <binary audio data>
Response: {
  "text": "What is a cell?",
  "confidence": 0.95,
  "language": "en"
}
```

**Implementation:**
```python
# app/processing/whisper_transcriber.py
from openai import OpenAI

class WhisperTranscriber:
    @staticmethod
    async def transcribe(audio_bytes: bytes) -> dict:
        """Transcribe audio using Whisper"""
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Save bytes to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        try:
            # Call Whisper API
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=open(temp_path, "rb")
            )
            return {
                "text": transcript.text,
                "confidence": 0.95  # Whisper doesn't provide confidence
            }
        finally:
            os.unlink(temp_path)
```

**Cost Note:** ~$0.001 per minute of audio. Consider caching repeated questions.

**Reference:** PRD Section 4.3, Amendment A Section 21.3

---

### 3. Voice Intent Interpretation

**What it does:**
- Takes transcribed text → extracts intent
- Maps to action: `answer_question`, `next_unit`, `repeat_audio`, `free_ask`, `pause`
- Returns structured intent with confidence

**Endpoint:**

```http
POST /api/v1/voice/interpret
Request: {
  "text": "What is a cell?",
  "session_id": "uuid",
  "context": {"unit_id": "uuid", "question_id": "uuid"}
}
Response: {
  "intent": "free_ask",  # or answer_question, next_unit, repeat, pause
  "confidence": 0.92,
  "entities": {
    "question_text": "What is a cell?",
    "unit_id": "uuid"
  },
  "action": "retrieve_rag_answer"
}
```

**Intent Taxonomy:**

| Intent | Triggers | Action |
|--------|----------|--------|
| `answer_question` | User provides answer to current question | Score answer, show feedback |
| `next_unit` | "next", "continue", "skip" | Load next learning unit |
| `repeat_audio` | "repeat", "again", "say that again" | Replay current unit audio |
| `free_ask` | Any question not matching current unit | Invoke RAG pipeline |
| `pause` | "pause", "stop", "break" | Pause session, save state |

**Implementation:**

```python
# app/processing/intent_classifier.py
import spacy
from fuzzywuzzy import fuzz

class IntentClassifier:
    @staticmethod
    def classify(text: str, context: dict) -> dict:
        """Classify voice command intent"""
        text_lower = text.lower()
        
        # Rule-based patterns (for BSE simplicity)
        if any(word in text_lower for word in ["next", "continue", "skip"]):
            return {"intent": "next_unit", "confidence": 0.95}
        
        if any(word in text_lower for word in ["repeat", "again", "once more"]):
            return {"intent": "repeat_audio", "confidence": 0.95}
        
        if any(word in text_lower for word in ["pause", "stop", "break"]):
            return {"intent": "pause", "confidence": 0.95}
        
        # If within context of a question, likely an answer
        if context.get("question_id"):
            return {"intent": "answer_question", "confidence": 0.90, "answer_text": text}
        
        # Default: free ask
        return {"intent": "free_ask", "confidence": 0.85, "question_text": text}
```

**Reference:** PRD Section 7.3 Intent Taxonomy, Amendment A Section 21.4

---

### 4. RAG Pipeline for Free Ask

**What it does:**
- Student asks question not in lesson → RAG retrieves relevant content
- Generates answer from lesson material only (constrained AI)
- Returns answer with source unit reference

**Endpoint:**

```http
POST /api/v1/voice/ask
Request: {
  "question": "What is photosynthesis?",
  "note_id": "uuid",
  "session_id": "uuid"
}
Response: {
  "answer": "Photosynthesis is the process by which plants...",
  "source_unit_id": "uuid",
  "confidence": 0.87,
  "relevant_chunks": [
    {"unit_id": "uuid", "text": "..."}
  ]
}
```

**Implementation Steps:**

1. **Embed lesson content** (from Phase 2):
   - During note processing, generate embeddings for each learning unit
   - Store in `learning_units.embedding` (vector column via pgvector)

2. **Semantic search**:
   ```python
   # app/processing/rag_pipeline.py
   from sentence_transformers import SentenceTransformer
   from pgvector.sqlalchemy import Vector
   
   class RAGPipeline:
       def __init__(self):
           self.model = SentenceTransformer('all-MiniLM-L6-v2')
       
       @staticmethod
       async def answer_free_ask(question: str, note_id: str, db: Session) -> dict:
           # Embed question
           question_embedding = self.model.encode(question)
           
           # Retrieve top 3 most similar units
           similar_units = db.query(LearningUnit).filter(
               LearningUnit.note_id == note_id
           ).order_by(
               LearningUnit.embedding.cosine_distance(question_embedding)
           ).limit(3).all()
           
           # Generate answer from top match
           best_unit = similar_units[0]
           answer = self._generate_answer(question, best_unit.content_text)
           
           return {
               "answer": answer,
               "source_unit_id": best_unit.id,
               "relevant_chunks": [u.content_text[:200] for u in similar_units]
           }
   ```

3. **Answer generation** (heuristic):
   - Extract sentences from top unit that best answer the question
   - Combine into coherent paragraph
   - Or: Call LLM (Claude/GPT) with lesson text for polish (optional)

**Database Setup Required:**
```sql
-- Add pgvector extension (one-time)
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to learning_units
ALTER TABLE learning_units ADD COLUMN embedding vector(384);

-- Add index for fast similarity search
CREATE INDEX idx_unit_embedding ON learning_units USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

**Reference:** PRD Section 7.4 RAG Pipeline, Amendment A Section 21.5

---

### 5. Delta Sync Protocol

**What it does:**
- Student syncs only **changed** content/progress since last sync
- Efficient for offline-first apps on slow networks
- Pull: new content from teachers
- Push: student progress to backend

**Endpoints:**

```http
GET /api/v1/sync/pull
Query params: 
  - student_id: uuid
  - last_sync_timestamp: ISO8601
  - note_ids: comma-separated uuids (notes student has)

Response: {
  "new_notes": [...],           # Notes uploaded after last_sync
  "updated_units": [...],       # Updated learning units
  "new_artefacts": [...],       # New questions/summaries
  "server_timestamp": "2026-04-19T15:00:00Z"
}

POST /api/v1/sync/push
Request: {
  "student_id": "uuid",
  "progress_updates": [
    {
      "unit_id": "uuid",
      "question_id": "uuid",
      "answer": "...",
      "score": 0.85,
      "time_seconds": 45,
      "timestamp": "2026-04-19T14:55:00Z"
    }
  ]
}
Response: {
  "status": "synced",
  "progress_saved": 5,
  "server_timestamp": "2026-04-19T15:00:00Z"
}
```

**Implementation:**

```python
# app/routers/sync.py
@router.get("/api/v1/sync/pull")
async def pull_sync(
    student_id: UUID,
    last_sync: datetime,
    note_ids: str,  # comma-separated
    db: Session = Depends(get_db),
    student: User = Depends(require_student)
):
    note_list = [UUID(nid) for nid in note_ids.split(",")]
    
    # Get notes assigned to this student after last_sync
    new_notes = db.query(LessonNote).filter(
        LessonNote.id.in_(note_list),
        LessonNote.created_at > last_sync
    ).all()
    
    # Get updated learning units
    updated_units = db.query(LearningUnit).filter(
        LearningUnit.note_id.in_(note_list),
        LearningUnit.updated_at > last_sync
    ).all()
    
    # Get new artefacts
    new_artefacts = db.query(AiArtefact).join(
        LearningUnit
    ).filter(
        LearningUnit.note_id.in_(note_list),
        AiArtefact.created_at > last_sync
    ).all()
    
    return {
        "new_notes": [schemas.LessonNoteResponse.from_orm(n) for n in new_notes],
        "updated_units": [schemas.LearningUnitResponse.from_orm(u) for u in updated_units],
        "new_artefacts": [schemas.AiArtefactResponse.from_orm(a) for a in new_artefacts],
        "server_timestamp": datetime.now(timezone.utc)
    }

@router.post("/api/v1/sync/push")
async def push_sync(
    request: SyncPushRequest,
    db: Session = Depends(get_db),
    student: User = Depends(require_student)
):
    # Validate student owns these progress records
    saved_count = 0
    
    for update in request.progress_updates:
        progress = StudentProgress(
            student_id=request.student_id,
            unit_id=update.unit_id,
            question_answered_id=update.question_id,
            score=update.score,
            time_spent_seconds=update.time_seconds,
            answered_at=update.timestamp
        )
        db.add(progress)
        saved_count += 1
    
    db.commit()
    return {"status": "synced", "progress_saved": saved_count}
```

**Reference:** PRD Section 6.2 Sync Endpoints, Amendment A Section 21.6

---

### 6. Student Progress Tracking

**What it does:**
- Record every question answered by student
- Calculate score, time spent, completion percentage
- Show learning analytics (questions right/wrong per unit)

**Endpoints:**

```http
GET /api/v1/students/{student_id}/progress?note_id=uuid
Response: {
  "note_id": "uuid",
  "total_units": 6,
  "units_started": 5,
  "units_completed": 3,
  "completion_percentage": 50,
  "questions_answered": [
    {
      "unit_id": "uuid",
      "question_id": "uuid",
      "answer": "...",
      "score": 0.85,
      "time_seconds": 45,
      "answered_at": "2026-04-19T14:55:00Z"
    }
  ],
  "summary": {
    "total_score": 0.78,
    "average_time_per_question": 42,
    "most_difficult_unit": "uuid"
  }
}

GET /api/v1/students/{student_id}/progress/{unit_id}
Response: {
  "unit_id": "uuid",
  "content_text": "...",
  "questions": [
    {
      "id": "uuid",
      "question_text": "...",
      "student_answer": "...",
      "score": 0.85,
      "feedback": "Good understanding of living things!"
    }
  ]
}
```

**Database Queries:**

```python
# Get progress for a note
progress = db.query(StudentProgress).filter(
    StudentProgress.student_id == student_id,
    LearningUnit.note_id == note_id
).join(LearningUnit).all()

completion = len([p for p in progress if p.score >= 0.7]) / total_units * 100
average_score = sum(p.score for p in progress) / len(progress)
```

**Reference:** PRD Section 5 Data Models, StudentProgress entity

---

### 7. Analytics Logging

**What it does:**
- Log every student interaction for research
- Anonymous: no personally identifiable info
- Tracks: question answered, time, score, session duration

**Endpoint:**

```http
POST /api/v1/analytics/event
Request: {
  "event_type": "question_answered|unit_started|unit_completed|session_ended",
  "session_id": "uuid",
  "student_id": "uuid",
  "unit_id": "uuid",
  "question_id": "uuid",
  "score": 0.85,
  "time_seconds": 45,
  "timestamp": "2026-04-19T14:55:00Z"
}
Response: {"status": "logged"}
```

**Storage:** Use `analytics_events` table with:
- event_type, session_id, student_id, unit_id, score, time_spent_seconds

**Research Queries:**
```sql
-- Average time per unit by difficulty
SELECT unit_id, AVG(time_seconds) FROM analytics_events
WHERE event_type = 'question_answered'
GROUP BY unit_id ORDER BY AVG(time_seconds) DESC;

-- Question success rate by type
SELECT artefact_type, AVG(score) FROM analytics_events
JOIN ai_artefacts ON ... GROUP BY artefact_type;
```

---

## 🔧 Setup Checklist for Phase 3

### Before Starting Implementation

- [ ] **pgvector Extension**
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

- [ ] **OpenAI API Key**
  - Register at https://platform.openai.com
  - Get API key
  - Add to `.env`: `OPENAI_API_KEY=sk-...`

- [ ] **Update Models** (app/models.py):
  ```python
  class LearningUnit(Base):
      embedding = Column(Vector(384), nullable=True)  # Add this
  
  class StudentProgress(Base):  # Already exists from Phase 2
      student_id = Column(UUID, ForeignKey("users.id"))
      unit_id = Column(UUID, ForeignKey("learning_units.id"))
      score = Column(Float)
      time_spent_seconds = Column(Integer)
  ```

- [ ] **New Tables** (if not already present):
  ```python
  # Already in models.py from Phase 2:
  # - VoiceSession
  # - VoiceInteraction
  # - FreeAskExchange (for RAG)
  ```

- [ ] **Dependencies** (requirements.txt):
  ```
  openai>=1.0.0          # Whisper API
  pgvector>=0.2.0        # Vector DB support
  sentence-transformers  # Already installed
  fuzzywuzzy>=0.21.0     # For fuzzy matching
  python-Levenshtein     # For edit distance
  ```

---

## 📊 Architecture Diagram - Phase 3

```
┌─────────────────────────────────────────┐
│      Android Client (Offline-First)     │
│  • Local lesson playback (Phase 2 data)  │
│  • Local question scoring                │
│  • On-device ASR (Android SpeechRecognizer)
│  • Voice interaction queue               │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        │ When ASR < 0.65     │ When free ask needed
        │ (Fallback)          │ (RAG required)
        │                     │
        ▼                     ▼
┌───────────────────────────────────────────┐
│         FastAPI Backend (Phase 3)         │
│                                           │
│  Voice Endpoints:                         │
│  • POST /voice/transcribe (Whisper)       │
│  • POST /voice/interpret (Intent)         │
│  • POST /voice/ask (RAG)                  │
│  • POST /voice/session/* (State)          │
│                                           │
│  Sync Endpoints:                          │
│  • GET /sync/pull (New content)           │
│  • POST /sync/push (Progress)             │
│                                           │
│  Analytics:                               │
│  • POST /analytics/event (Research)       │
└──────────┬───────────────┬────────────────┘
           │               │
    ┌──────▼──────┐  ┌─────▼──────┐
    │ PostgreSQL  │  │ Redis/Cache│
    │ • voice_*   │  │ (Optional) │
    │ • progress  │  │            │
    │ • embeddings│  │            │
    └─────────────┘  └────────────┘
```

---

## 🧪 Testing Strategy

### Unit Tests
- Intent classification (answer, next, free_ask, etc.)
- RAG retrieval and ranking
- Delta sync timestamp filtering
- Progress score calculation

### Integration Tests
1. **Voice Flow**: Student logs in → starts voice session → answers question → gets feedback → navigates
2. **RAG Flow**: Ask free question → retrieve relevant content → generate answer → log analytics
3. **Sync Flow**: Download new notes → answer questions offline → sync progress back to server
4. **Edge Cases**: Network fails during sync, ASR fails, question answered wrong multiple times

### Manual Testing (with Android app)
- Complete lesson playback (Phase 2)
- Voice commands (next, repeat, pause)
- Free ask with actual question
- Offline sync and progress restore

---

## 📚 Success Criteria

✅ Phase 3 is complete when:

1. **All endpoints deployed and tested** (7 voice + sync endpoints)
2. **Voice interaction fully functional** (transcription, intent, RAG)
3. **Offline sync working** (pull new content, push progress)
4. **Progress tracking accurate** (scores, times, completion %)
5. **Analytics logging enabled** (for research)
6. **Integration tests passing** (100% coverage of flows)
7. **Documentation complete** (API, architecture, troubleshooting)
8. **Android client integration verified** (end-to-end test with real device)

---

## 🚀 Quick Start for Phase 3

```bash
# 1. Create Alembic migration for Phase 3 tables/columns
alembic revision --autogenerate -m "Phase 3: add embeddings, voice endpoints"
alembic upgrade head

# 2. Install Phase 3 dependencies
pip install openai pgvector sentence-transformers fuzzywuzzy python-Levenshtein

# 3. Start backend with Celery
uvicorn app.main:app --reload
celery -A app.worker worker --loglevel=info --pool=solo

# 4. Begin implementation
# Start with voice session management (easiest)
# Then voice transcription (requires OpenAI)
# Then RAG (complex, requires embeddings)
```

---

## 📞 Questions?

**Refer to:**
- PRD Consolidated v1.2 (Sections 6-7)
- Amendment A v1.1 (Voice Interaction System)
- Phase 2 Implementation docs (architecture patterns)
- Code comments in Phase 2 for patterns to follow

**Next Phase:** Phase 4 (Android Client) - depends on Phase 3 backend completion

---

*Phase 3 Plan Complete - Ready for Implementation*
