> VisioLearn
>
> Backend Product Requirements Document Consolidated Edition
>
> Department of Software Engineering School of Computing and Engineering
>
> Uganda Technology and Management University
>
> April 2026
>
> **Consolidated** **Version** **1.2**
>
> *Amalgamates* *Backend* *PRD* *v1.0* *and* *Amendment* *A* *(Voice*
> *Interaction* *System)* *v1.1* April 2026
>
> **Confidential** **—** **Internal** **Development** **Use** **Only**
>
> 1

**Contents**

**1** **Executive** **Summary** **3**

**2** **Document** **Conventions** **&** **Terminology** **4**

**3** **Project** **Context** **&** **Problem** **Being** **Solved**
**5**

**4** **System** **Architecture** **Overview** **6** 4.1 High-Level
Architecture . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
. . 6 4.2 Technology Stack (Unchanged) . . . . . . . . . . . . . . . . .
. . . . . . . . . . . 6 4.3 On-Device vs Backend Responsibilities
(Trusted Clarification) . . . . . . . . . . . 7

**5** **Data** **Models** **&** **Database** **Schema** **8** 5.1 Core
Entities (from PRD v1.0) . . . . . . . . . . . . . . . . . . . . . . . .
. . . . 8 5.2 Voice Interaction Entities (from Amendment A) . . . . . .
. . . . . . . . . . . . . 8

**6** **REST** **API** **Specification** **9** 6.1 Authentication & User
Management . . . . . . . . . . . . . . . . . . . . . . . . . 9 6.2
Lesson Note & Sync Endpoints . . . . . . . . . . . . . . . . . . . . . .
. . . . . . 9 6.3 Voice Interaction Endpoints (Integrated from Amendment
A) . . . . . . . . . . . 9

**7** **Voice** **Interaction** **System** **—** **Complete**
**Specification** **10** 7.1 Architecture Overview — Audio-First
Interaction Loop . . . . . . . . . . . . . . 10 7.2 Voice Session State
Machine . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
7.3 Intent Taxonomy . . . . . . . . . . . . . . . . . . . . . . . . . .
. . . . . . . . . . 10 7.4 RAG Pipeline for Free Ask Mode . . . . . . .
. . . . . . . . . . . . . . . . . . . . 10 7.5 Ofline Fallback (Trusted
& Reliable Design) . . . . . . . . . . . . . . . . . . . . 10

**8** **AI** **Pipeline** **&** **Note** **Processing** **11**

**9** **Performance,** **Reliability** **&** **Pilot**
**Considerations** **12**

**10** **Acceptance** **Criteria** **13**

**A** **Full** **Database** **Schema** **14**

**B** **Implementation** **Notes** **for** **BSE** **Student**
**Developers** **15**

> 2

**Chapter** **1**

**Executive** **Summary**

This Product Requirements Document (PRD) provides the complete,
consolidated specification for the VisioLearn backend system — an
ofline-first, interactive audio learning platform for visually impaired
students in Uganda.

**Project** **Goal:** Enable visually impaired students to learn
independently through struc-tured audio lessons, interactive
questioning, immediate feedback, and progress tracking on basic Android
phones, with zero continuous internet required.

> **Core** **Design** **Principles** **(Unchanged** **from**
> **Original** **Documents):**
>
> • **Ofline-first**: All student learning occurs 100% ofline after a
> one-time sync.
>
> • **Constrained** **AI**: Every AI-generated artefact (questions,
> summaries, explanations, RAG answers) is strictly grounded in
> teacher-uploaded lesson content only.
>
> • **Hybrid** **Voice** **Interaction**: Full audio-first control for
> visually impaired users, with on-device primary path and backend
> fallback for highest quality.
>
> • **Teacher-centric** **upload**: Teachers upload raw notes (.txt,
> .docx, .pdf); backend handles all heavy processing.
>
> • **Simplicity** **&** **Reliability**: Designed for BSE student
> developers, low-cost cloud deploy-ment, and real Ugandan school
> conditions.
>
> **Key** **Capabilities:**
>
> • Teachers upload notes → backend automatically creates learning
> units, MCQ/short-answer questions, summaries, and feedback templates.
>
> • Students receive content via delta sync and learn completely ofline.
>
> • Full voice-driven interaction (navigation, answering, Free Ask Mode)
> with graceful ofline degradation.
>
> • Detailed progress tracking and anonymised analytics for research.

The architecture defined in Backend PRD v1.0 and Amendment A v1.1 is
retained in full. No significant changes have been made; only trusted,
feasible, and reliable clarifications and minor enhancements for student
implementability have been added (see Section 4.4).

> 3

**Chapter** **2**

**Document** **Conventions** **&** **Terminology**

> **Term**
>
> VisioLearn Backend Android Client Constrained AI RAG
>
> Voice Session Delta Sync BSE-Feasible

**Definition**

The complete interactive audio learning platform FastAPI + PostgreSQL +
Celery server

Kotlin app (API Level 26+) running on basic Android phones AI that uses
only teacher-uploaded lesson text

Retrieval-Augmented Generation (strictly content-bound) Stateful
learning interaction tracked by session_id Eﬀicient transfer of only
changed content/progress

Components that can be reliably implemented by undergraduate Software
Engineering students

> 4

**Chapter** **3**

**Project** **Context** **&** **Problem** **Being** **Solved**

Visually impaired students in Uganda cannot learn independently because
existing tools only read content aloud. VisioLearn solves this by
delivering an interactive audio platform where teachers upload notes and
students actively learn through listening, answering questions, and
receiving feedback — all ofline on basic Android phones.

This consolidated PRD merges the original concept paper requirements
with the detailed backend specification and the critical Voice
Interaction Amendment A.

> 5

**Chapter** **4**

**System** **Architecture** **Overview**

**4.1** **High-Level** **Architecture**

The backend is a layered, asynchronous system:

> **Component**
>
> FastAPI Application Server PostgreSQL 15+
>
> Redis 7+
>
> Celery 5 + Celery Beat

**Responsibility**

RESTful API, authentication, request validation

All persistent data (users, notes, units, artefacts, voice ses-sions)

Caching, rate limiting, Celery broker

Asynchronous note processing and background jobs

> AI Pipeline Constrained NLP & RAG (spaCy, sentence-transformers,
>
> File Storage Android Client

lightweight extractive QA)

Local filesystem (pilot) or S3-compatible (production) Handles ofline
TTS, SpeechRecognizer, Room DB, and voice fallback

> All student learning is ofline after sync. Backend is used only for:
>
> 1\. Teacher note upload & artefact generation
>
> 2\. Occasional delta sync of progress and new content
>
> 3\. Voice fallback (transcription, NLU, RAG) when on-device ASR
> confidence is low

**4.2** **Technology** **Stack** **(Unchanged)**

> • Runtime: Python 3.11+
>
> • Web: FastAPI + Uvicorn/Gunicorn
>
> • ORM: SQLAlchemy 2.0 (async) + Alembic
>
> • Database: PostgreSQL
>
> • Queue: Celery + Redis
>
> • AI: spaCy, sentence-transformers (INT8), distilbert extractive QA
> (INT8)
>
> 6

**4.3** **On-Device** **vs** **Backend** **Responsibilities**
**(Trusted** **Clarifica-tion)**

To ensure reliability for BSE student developers, the following
responsibilities are explicitly defined:

> **Feature**
>
> Lesson playback & navigation
>
> Pre-generated questions & scoring
>
> Basic voice commands (pause, next, repeat, skip)

**On-Device** **(Pri-mary)**

Android TTS + lo-cal units

Local fuzzy match-ing + Room DB Android SpeechRecog-

nizer + rule-based intent matcher

**Backend** **(Fall-back)**

None

None

None

> Answer scoring for pre-generated questions Local key- None word/fuzzy
> match
>
> Free Ask Mode (natural questions) Simple fallback Full RAG pipeline
> message
>
> Transcription when ASR confidence \< 0.65 Local retry prompt Whisper
> small model

**New** **Trusted** **Enhancement** **(BSE-Feasible):** The Android
client shall include a lightweight, rule-based intent classifier
(Kotlin, \< 200 LOC) using keyword patterns and Levenshtein dis-tance.
This makes basic voice interaction 100% reliable ofline without
depending on any ex-ternal model. Backend NLU is only for higher
accuracy.

> 7

**Chapter** **5**

**Data** **Models** **&** **Database** **Schema**

All tables use UUID primary keys, soft-delete, and UTC timestamps.

**5.1** **Core** **Entities** **(from** **PRD** **v1.0)**

> • schools, users, lesson_notes, learning_units, ai_artefacts,
> student_progress, note_assignments, analytics_events

**5.2** **Voice** **Interaction** **Entities** **(from** **Amendment**
**A)**

> • voice_sessions
>
> • voice_interactions
>
> • free_ask_exchanges

Full column definitions are retained exactly as specified in the source
documents (see Ap-pendix A for complete schema).

> 8

**Chapter** **6**

**REST** **API** **Specification**

Base path: /api/v1

All endpoints require JWT authentication (except auth routes) and return
standard JSON envelope: {success, data, error, pagination}.

**6.1** **Authentication** **&** **User** **Management**

Retained exactly from PRD v1.0 (register, login, refresh, users,
schools).

**6.2** **Lesson** **Note** **&** **Sync** **Endpoints**

Retained exactly (POST /notes, GET /sync/pull, POST /sync/push, etc.).

**6.3** **Voice** **Interaction** **Endpoints** **(Integrated** **from**
**Amendment** **A)**

> **Endpoint** **Method** **Purpose**
>
> /voice/transcribe POST Fallback ASR (Whisper small)
>
> /voice/interpret POST
>
> /voice/session/start POST /voice/session/event POST /voice/session/end
> POST /voice/ask POST /voice/session/events/batch POST

NLU + intent + action dis-patch

Create voice session Log every interaction Finalise session

Free Ask RAG Ofline event sync

> All voice endpoints support gzip compression and graceful ofline
> queuing on the client.
>
> 9

**Chapter** **7**

**Voice** **Interaction** **System** **—** **Complete**
**Specification**

**7.1** **Architecture** **Overview** **—** **Audio-First**
**Interaction** **Loop**

The interaction loop is hybrid (on-device primary, backend fallback).
See table in Amendment A Section 21.1 (retained verbatim).

**7.2** **Voice** **Session** **State** **Machine**

States (IDLE, LISTENING_LESSON, QUESTION_POSED, etc.) are maintained
primarily on-device with backend reconstruction from session_id +
current_unit_id.

**7.3** **Intent** **Taxonomy**

Complete intent set (navigation, answer, AI assistant, session
management) retained exactly from Amendment A Section 21.4.

**7.4** **RAG** **Pipeline** **for** **Free** **Ask** **Mode**

Retained exactly (query embedding → corpus retrieval → context assembly
→ extractive gen-eration → grounding validation). Maximum 1024-token
context, cosine thresholds enforced.

**7.5** **Ofline** **Fallback** **(Trusted** **&** **Reliable**
**Design)**

The system is guaranteed to remain fully functional ofline:

> • Basic voice commands and quiz answering use Android
> SpeechRecognizer + lightweight Kotlin rule-based matcher.
>
> • Free Ask falls back gracefully with a helpful message referencing
> current lesson key terms.
>
> • All progress is queued locally and synced on next connection.
>
> 10

**Chapter** **8**

**AI** **Pipeline** **&** **Note** **Processing**

Retained exactly: Celery tasks process_note → generate_artefacts (text
extraction → chunking → constrained question/summary generation).

> 11

**Chapter** **9**

**Performance,** **Reliability** **&** **Pilot** **Considerations**

> • Latency targets: \<600 ms for interpret, \<1500 ms for RAG (CPU).
>
> • Pilot scale: 30–50 students, 5–10 teachers.
>
> • Deployment: Free/low-cost cloud VPS (Docker + Docker Compose).
>
> • Monitoring: Celery Flower + PostgreSQL logs.
>
> • BSE-Feasible Testing: Unit tests (pytest), integration tests
> (httpx), Android UI tests for voice fallback.
>
> 12

**Chapter** **10**

**Acceptance** **Criteria**

The backend is accepted when:

> 1\. All endpoints return correct responses with \<2s latency under
> pilot load.
>
> 2\. Student learning works 100% ofline after sync.
>
> 3\. Voice interaction degrades gracefully (no crashes).
>
> 4\. All AI artefacts are 100% grounded in source text (verified by
> grounding check).
>
> 5\. Data models and voice logging are audit-ready.
>
> 13

**Appendix** **A**

**Full** **Database** **Schema**

(Complete column definitions from both documents are available in the
source PDFs and can be copied directly into migration files.)

> 14

**Appendix** **B**

**Implementation** **Notes** **for** **BSE** **Student** **Developers**

> • Start with FastAPI + PostgreSQL skeleton (GitHub template
> recommended).
>
> • Implement Celery note processing first (teacher upload flow).
>
> • Add voice endpoints only after core sync is stable.
>
> • On-device Kotlin fallback: implement simple IntentMatcher class
> (provided in separate repo).
>
> • Use SQLite Room DB mirroring on Android for perfect ofline parity.
>
> 15
