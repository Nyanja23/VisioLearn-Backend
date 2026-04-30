> **PRODUCT** **REQUIREMENTS** **DOCUMENT**
>
> **BACKEND** **SYSTEM**
>
> *Interactive* *Audio* *Learning* *Platform* *for* *Visually*
> *Impaired* *Students*

||
||
||
||
||
||
||
||
||

> **CONFIDENTIAL** **—** **INTERNAL** **DEVELOPMENT** **USE** **ONLY**

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

**1.** **Executive** **Summary**

This document is the authoritative Product Requirements Document (PRD)
for the complete backend system of VisioLearn — an offline-first,
interactive audio learning platform designed to empower visually
impaired students in Uganda. The backend serves as the central
intelligence and data hub of the platform, powering teacher content
management, AI-driven question and summary generation (content-bound
RAG), student progress synchronisation, push notifications, analytics,
and administration.

The backend must be engineered for maximum performance given the
constraint that end devices are basic Android phones operating
predominantly offline in low-bandwidth environments. Every API response
must be optimised for minimum latency, minimum payload size, and
graceful degradation when connectivity is unstable.

The system is built with Python FastAPI on PostgreSQL. It exposes a
RESTful API consumed by the Android client, and an administrative web
interface for school administrators and research staff. All AI
processing happens server-side, and AI-generated artefacts (questions,
summaries, feedback) are pushed to the device for completely offline
student use.

||
||
||
||
||
||
||
||
||
||
||

**2.** **Document** **Conventions** **&** **Terminology**

||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

**3.** **Project** **Context** **&** **Problem** **Being** **Solved**

**3.1** **Research** **Background**

Visually impaired students in Uganda are passive learners. Existing
tools (Blind Assistant, Yee FM, JAWS) provide audio access to text but
offer zero interaction: no questions, no feedback, no progress tracking.
Under Uganda's new competency-based curriculum, this gap is academically
fatal — 112 visually impaired candidates appeared in the 2026 UACE with
disproportionately low pass rates.

VisioLearn transforms the paradigm. Teachers upload lesson notes once;
the backend processes them, generates curriculum-aligned questions and
summaries through constrained AI, and pushes the artefacts to students'
devices for completely offline learning. Students listen, answer,
receive feedback, and accumulate tracked progress — all without
internet.

**3.2** **The** **Backend's** **Role** **in** **the** **Platform**

The Android client is entirely offline during student learning sessions.
The backend is engaged in two windows:

> • Teacher window: when a teacher has internet connectivity to upload a
> note.
>
> • Sync window: when a student or teacher briefly connects to internet
> to sync progress up and pull new artefacts down.

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

Everything the student experiences during learning — audio content,
questions, answer feedback, progress records — originates from the
backend but lives on-device. The backend must therefore process notes
thoroughly, generate high-quality artefacts, and deliver them
efficiently during the brief sync windows available on limited data
connections.

**3.3** **Non-Negotiable** **Constraints**

> • All AI generation MUST be strictly content-bound (no external
> knowledge sources). • All generated artefacts MUST be storable
> on-device for fully offline use.
>
> • API responses MUST be lean and fast — target devices are low-end
> Android phones. • The backend MUST handle intermittent sync — partial
> uploads, retry, resumption.
>
> • The system MUST be deployable on a free or low-cost cloud tier for
> the pilot phase.
>
> • All personal data MUST be handled in compliance with applicable data
> protection norms.

**4.** **System** **Architecture** **Overview**

**4.1** **High-Level** **Architecture**

The backend is structured as a layered, asynchronous system composed of
the following components:

||
||
||
||
||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

**4.2** **Technology** **Stack** **Specification**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

**4.3** **Data** **Flow:** **Note** **Upload** **to** **Offline**
**Artefact**

The following describes the complete data flow from a teacher uploading
a note to a student using AI artefacts fully offline:

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

> 1\. Teacher uploads note file via POST /api/v1/notes with file
> attachment and metadata (subject, topic, grade level).
>
> 2\. FastAPI validates file type, size, and user permissions. File is
> saved to blob storage. Note record created in DB with status
> PENDING_PROCESSING.
>
> 3\. A Celery task (process_note) is enqueued with high priority.
>
> 4\. Celery worker picks up the task: (a) extracts raw text from file,
> (b) segments into Learning Units (paragraphs/sections), (c) stores
> units in DB.
>
> 5\. A follow-on task (generate_artefacts) runs the AI pipeline per
> Learning Unit: generates questions (MCQ + short answer), a summary,
> and feedback templates — ALL strictly from the unit's text.
>
> 6\. AI artefacts are stored in DB linked to their Learning Unit. Note
> status updated to READY.
>
> 7\. Next time the student's Android app syncs, GET /api/v1/sync
> returns a payload containing all new/updated Learning Units and AI
> Artefacts since the device's last_synced_at timestamp.
>
> 8\. Android client stores everything in Room DB. Student now learns
> entirely offline. 9. Student answers questions offline; responses are
> stored in Room DB.
>
> 10\. On next sync, Android client POSTs student progress (answers,
> scores, completion) to POST /api/v1/sync/progress. Backend stores
> records in PostgreSQL for analytics.

**5.** **Data** **Models** **&** **Database** **Schema**

All tables use PostgreSQL. UUID primary keys throughout for security and
scalability. All timestamps are stored in UTC. Soft-delete pattern used
on all critical entities (is_deleted flag + deleted_at timestamp).

**5.1** **Entity:** **schools**

||
||
||
||
||
||
||
||
||
||
||

**5.2** **Entity:** **users**

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

**5.3** **Entity:** **refresh_tokens**

||
||
||
||
||
||
||
||
||
||

**5.4** **Entity:** **lesson_notes**

||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **Index:** CREATE INDEX idx_notes_school_subject ON
> lesson_notes(school_id, subject);
>
> **Index:** CREATE INDEX idx_notes_status ON lesson_notes(status) WHERE
> status = 'uploaded' OR status = 'processing';

**5.5** **Entity:** **learning_units**

||
||
||
||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||

> **Index:** CREATE INDEX idx_units_note_seq ON learning_units(note_id,
> sequence_number);

**5.6** **Entity:** **ai_artefacts**

||
||
||
||
||
||
||
||
||
||
||
||

**JSONB** **Schema:** **mcq_question**

||
||
||
||
||
||
||
||

**JSONB** **Schema:** **summary**

||
||
||
||
||

**5.7** **Entity:** **student_progress**

||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **Index:** CREATE INDEX idx_progress_student_unit ON
> student_progress(student_id, unit_id);
>
> **Index:** CREATE INDEX idx_progress_student_time ON
> student_progress(student_id, offline_recorded_at DESC);

**5.8** **Entity:** **note_assignments**

Links a note to students or grade groups within a school, giving
teachers control over who receives which content.

||
||
||
||
||
||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

**5.9** **Entity:** **analytics_events**

Anonymised aggregate analytics for research and policymakers. No
personally identifiable information in this table.

||
||
||
||
||
||
||
||
||
||
||
||

**6.** **REST** **API** **Specification**

Base URL: /api/v1. All responses return JSON. All authenticated
endpoints require Authorization: Bearer \<access_token\>. All endpoints
return standard envelope: { success, data, error, pagination }.

**6.1** **Authentication** **Endpoints**

||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||

**6.2** **User** **Management** **Endpoints**

||
||
||
||
||
||
||
||
||

**6.3** **School** **Management** **Endpoints**

||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

**6.4** **Lesson** **Note** **Endpoints**

||
||
||
||
||
||
||
||
||
||
||
||

**6.5** **Note** **Assignment** **Endpoints**

||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||

**6.6** **Sync** **Endpoints** **(Core** **Offline-First** **API)**

These endpoints are the heartbeat of the offline-first architecture.
They are optimised for minimal payload size and bandwidth.

||
||
||
||
||
||
||

**Sync** **Pull** **Response** **Schema**

||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||

**6.7** **Progress** **&** **Analytics** **Endpoints**

||
||
||
||
||
||
||

**6.8** **Admin** **Endpoints**

||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||

**7.** **AI** **Processing** **Pipeline** **—** **Content-Bound**
**Architecture**

This section defines the complete AI pipeline that runs server-side as
Celery tasks after a note is uploaded. The pipeline is architecturally
constrained: it MUST ONLY generate questions, summaries, and feedback
from the text of the uploaded note. No external knowledge, no internet
lookups, no language model hallucinations.

**7.1** **Stage** **1:** **Document** **Parsing**

||
||
||
||
||
||
||
||
||
||

**7.2** **Stage** **2:** **Text** **Chunking** **into** **Learning**
**Units**

||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||

**7.3** **Stage** **3:** **Question** **Generation**

Questions are generated per Learning Unit using a pipeline of NLP
techniques. All questions are strictly grounded in the unit text.

**MCQ** **Generation** **Algorithm**

> 11\. Parse unit text with spaCy (en_core_web_sm).
>
> 12\. Extract candidate fact sentences: sentences containing named
> entities (PERSON, ORG, GPE, DATE, CARDINAL, PRODUCT) or sentences with
> subject-verb-object triples.
>
> 13\. For each candidate sentence, apply cloze transformation: mask the
> key entity/noun phrase to form the question stem.
>
> 14\. Generate 3 distractor options using: (a) other entities of the
> same type from the same unit text, (b) semantically similar terms from
> sentence-transformers nearest-neighbor search within the unit corpus.
>
> 15\. Shuffle options; assign random option IDs (A/B/C/D).
>
> 16\. Store correct_option_id server-side ONLY; excluded from sync-pull
> payload.
>
> 17\. Generate 1-sentence explanation by extracting the surrounding
> context of the source sentence.
>
> 18\. Target: 3–6 MCQ questions per Learning Unit. Skip generation if
> unit has fewer than 4 candidate sentences.

**Short** **Answer** **Question** **Generation**

> 19\. Identify the 2–3 most information-dense sentences in the unit
> using TF-IDF scoring.
>
> 20\. Transform each into a 'What / Who / When / How' question by
> replacing the subject or key predicate.
>
> 21\. Store the source sentence as the model answer for scoring. 22.
> Target: 1–2 short answer questions per Learning Unit.

**Answer** **Scoring** **for** **Short** **Answers**

> 23\. On sync/answers endpoint call, compare student's text answer
> against model answer.
>
> 24\. Compute cosine similarity using sentence-transformers
> (paraphrase-MiniLM-L6-v2, quantised for server efficiency).
>
> 25\. Score: \>= 0.75 = correct (1.0), 0.50–0.74 = partial (0.5), \<
> 0.50 = incorrect (0.0). 26. Return score and the model answer text for
> student learning feedback.

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

**7.4** **Stage** **4:** **Summary** **Generation**

||
||
||
||
||
||
||

**7.5** **Stage** **5:** **Quality** **Control** **&** **Approval**

||
||
||
||
||
||
||

**8.** **Authentication** **&** **Authorisation**

**8.1** **JWT** **Strategy**

||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||

**8.2** **Role-Based** **Access** **Control** **(RBAC)**

||
||
||
||
||
||
||
||
||
||
||
||
||

**8.3** **Security** **Requirements**

> • All endpoints MUST be served over HTTPS. HTTP requests MUST be
> redirected to HTTPS. • Passwords MUST be hashed with bcrypt, minimum
> cost factor 12.
>
> • Login endpoint MUST implement rate limiting: max 10 failed attempts
> per 15 minutes per IP. Lock account after 20 failed attempts.
>
> • Refresh token MUST be validated against DB hash on every use — not
> just signature. • All API inputs MUST be validated by Pydantic models
> before processing.
>
> • File uploads MUST be validated for MIME type (not just extension),
> scanned for malformed structure.
>
> • File paths MUST use content-addressed naming (UUID/hash) — no
> user-controlled file path components.

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

> • SQL queries MUST use parameterised statements via SQLAlchemy ORM —
> no raw string interpolation.
>
> • Sensitive environment variables (DB URL, JWT secret, storage keys)
> MUST be stored in environment/.env and NEVER in source code.
>
> • CORS MUST be configured to whitelist only the Android app's declared
> origins in production.

**9.** **Performance** **Requirements** **&** **Optimisation**
**Strategy**

Performance is critical. Students sync over mobile data (often GPRS/EDGE
in rural Uganda). Teachers upload over Wi-Fi or 3G. Every millisecond
and every byte counts.

**9.1** **Response** **Time** **Targets** **(P99)**

||
||
||
||
||
||
||
||
||
||
||
||
||
||

**9.2** **Payload** **Optimisation**

> • Learning unit text_content fields MUST be compressed with gzip at
> the HTTP layer (Accept-Encoding: gzip in all client requests).
>
> • Sync pull endpoint MUST use delta sync (only records changed since
> last_synced_at) — never return full data set.
>
> • AI artefact payloads MUST omit correct_option_id in sync-pull
> responses — served separately via /sync/answers.

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

> • All list endpoints MUST support cursor-based pagination (default
> page_size: 50, max: 200).
>
> • Response envelopes MUST NOT include null fields (exclude_none=True
> in Pydantic models).
>
> • Note metadata endpoints MUST NOT return file binary data — only
> paths and metadata.

**9.3** **Database** **Optimisation**

> • All foreign key columns MUST have indexes.
>
> • Composite indexes MUST be created for all common query patterns (see
> Section 5 for index specifications).
>
> • PostgreSQL connection pooling MUST be configured: min_connections=5,
> max_connections=20 (asyncpg pool via SQLAlchemy async).
>
> • Heavy read queries (analytics, aggregated progress) MUST use
> PostgreSQL materialized views refreshed on schedule.
>
> • N+1 query patterns MUST be eliminated: use SQLAlchemy
> selectinload/joinedload for all relationship loading.
>
> • EXPLAIN ANALYZE MUST be run on all critical path queries during
> development; slow queries (\> 50ms) MUST be optimised before
> deployment.

**9.4** **Caching** **Strategy**

||
||
||
||
||
||
||
||

**9.5** **Async** **&** **Concurrency**

> • FastAPI endpoints MUST use async def for all I/O-bound operations
> (DB queries, file reads, Redis).
>
> • SQLAlchemy async sessions MUST be used throughout — no synchronous
> DB calls in async context.
>
> • Celery worker concurrency MUST be set to min(4, CPU_count \* 2) for
> the pilot deployment.
>
> • Celery task priority queues: high (document parsing, artefact
> delivery), medium (question generation), low (analytics aggregation).

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

> • Celery tasks MUST implement exponential backoff retry:
> max_retries=3, retry_backoff=True, retry_backoff_max=300.

**10.** **File** **Management** **&** **Storage**

||
||
||
||
||
||
||
||
||
||
||

**11.** **Background** **Job** **Specifications**

**11.1** **Task:** **process_note**

||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||

**11.2** **Task:** **generate_artefacts**

||
||
||
||
||
||
||
||

**11.3** **Scheduled** **Jobs** **(Celery** **Beat)**

||
||
||
||
||
||
||
||

**12.** **Error** **Handling** **&** **API** **Error** **Codes**

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

All errors return a standardised envelope: { success: false, error: {
code, message, details? } }. HTTP status codes are used semantically.

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

**13.** **Observability,** **Logging** **&** **Monitoring**

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

**13.1** **Structured** **Logging**

> • All log output MUST be structured JSON (using structlog or loguru
> with JSON sink).
>
> • Every HTTP request MUST be logged with: request_id (UUID injected by
> middleware), method, path, status_code, duration_ms, user_id (if
> authenticated), school_id.
>
> • Every Celery task MUST log: task_name, task_id, note_id, status,
> duration_ms, error (on failure).
>
> • Log levels: DEBUG (local dev only), INFO (request logs, task
> completion), WARNING (recoverable errors, rate limit hits), ERROR
> (exceptions, task failures), CRITICAL (DB down, queue full).
>
> • Sensitive data (passwords, tokens, file content) MUST NEVER appear
> in logs.

**13.2** **Metrics**

||
||
||
||
||
||
||
||
||
||

**13.3** **Alerting**

> • ALERT: 5xx error rate \> 1% over 5 minutes → page on-call (Grafana /
> Uptime Robot for pilot).
>
> • ALERT: Celery queue depth \> 100 tasks for \> 10 minutes → scale
> workers. • ALERT: DB connection pool exhausted → immediate
> investigation.
>
> • ALERT: Note stuck in 'processing' for \> 30 minutes → auto-retry +
> notify system_admin. • ALERT: Disk usage \> 80% → notify system_admin.

**14.** **Testing** **Requirements**

**14.1** **Unit** **Tests**

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

> • Every service function (note parsing, text chunking, question
> generation, scoring) MUST have unit tests with mocked DB.
>
> • Test document parsing with: valid .txt, valid .docx, valid text PDF,
> image PDF (must fail gracefully), corrupted file (must fail
> gracefully), empty file (must fail gracefully).
>
> • Test question generation with: short unit (\< 100 words), typical
> unit (300 words), maximum unit (600 words), unit with no named
> entities.
>
> • Test JWT logic: valid token, expired token, revoked refresh token,
> tampered token.

**14.2** **Integration** **Tests**

> • Test full note upload → processing → sync-pull cycle using httpx
> AsyncClient against test DB.
>
> • Test delta sync: upload 3 notes, sync, upload 2 more notes, sync
> again — verify only 2 new notes returned.
>
> • Test answer reveal endpoint: verify correct_option_id not present in
> sync-pull; verify it IS present after /sync/answers.
>
> • Test role-based access: student attempting teacher endpoint returns
> 403; teacher attempting admin endpoint returns 403.

**14.3** **Performance** **Tests**

> • Simulate 50 concurrent sync-pull requests with 200-item deltas each
> — P99 must stay under 2500ms.
>
> • Simulate 10 concurrent note uploads — verify all are processed
> without queue blockage within 5 minutes.
>
> • Test DB query plans with EXPLAIN ANALYZE for all endpoints in the
> critical path.

**14.4** **Coverage** **Target**

> • Minimum 80% code coverage for all service and repository layers
> (pytest-cov). • 100% coverage on authentication and file validation
> logic.
>
> • CI pipeline MUST block merge if coverage drops below 80%.

**15.** **Deployment** **&** **Infrastructure**

**15.1** **Containerisation**

||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||

**15.2** **Environment** **Configuration**

All environment-specific values MUST be configured via environment
variables. A .env.example file with all required keys (no values) MUST
be committed to the repository.

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

**15.3** **Pilot** **Deployment** **(Recommended)**

> • Platform: Railway.app or Render.com (free tier supports PostgreSQL +
> Redis + web service).
>
> • Alternatively: single low-cost VPS (e.g. Hetzner CX11 €3.79/month)
> running Docker Compose.
>
> • SSL: Let's Encrypt via Certbot (automated renewal).
>
> • Domain: subdomain of project domain e.g. api.visiolearn.ug
>
> • Backups: pg_dump to file daily; upload to Backblaze B2 (free tier
> 10GB).

**16.** **Recommended** **Project** **Structure**

The following directory structure is prescribed for the backend
repository. Deviations must be documented and justified.

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||
||
||
||
||
||

**17.** **Acceptance** **Criteria**

The backend is considered feature-complete and ready for pilot when ALL
of the following conditions are met:

> 27\. A teacher can register, log in, upload a .txt/.docx/.pdf lesson
> note, and the note transitions to 'ready' status within 5 minutes.
>
> 28\. At least 3 MCQ questions and 1 summary are generated for every
> learning unit with \>= 150 words.
>
> 29\. Correct answers are NOT present in the sync-pull payload and ARE
> correctly returned by /sync/answers after completion is submitted.
>
> 30\. A student can sync-pull their assigned content in \< 800ms (P99)
> on a 3G-simulated network test.
>
> 31\. A student's offline progress can be sync-pushed successfully
> after 48 hours of offline use, with no duplicate records in DB.
>
> 32\. Delta sync is verified: syncing twice without any new content
> returns an empty payload in \< 150ms.
>
> 33\. A teacher can mark an AI artefact as unapproved, and it is absent
> from subsequent student sync-pulls.
>
> 34\. All RBAC rules defined in Section 8.2 are enforced — verified by
> integration tests.
>
> 35\. Rate limiting on /auth/login blocks accounts with 10+ failed
> attempts within 15 minutes. 36. All unit and integration tests pass
> with \>= 80% coverage.
>
> 37\. POST /notes with an image-only PDF returns a 422 INVALID_FILE
> error.
>
> 38\. The system handles 50 concurrent sync-pull requests without error
> (load test verified).
>
> 39\. Docker Compose starts the full stack (API + DB + Redis + Worker)
> with docker compose up on a fresh machine.
>
> 40\. OpenAPI documentation is accessible at /docs and accurately
> reflects all endpoints.

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

**18.** **Development** **Phases** **&** **Priorities**

||
||
||
||
||
||
||
||
||
||

**19.** **Open** **Questions** **&** **Decisions** **Required**

||
||
||
||

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||

**20.** **Reference** **Documents**

> • Original Research Proposal: VisioLearn — Interactive Audio Learning
> Platform for Visually Impaired Students (Uganda), UTAMU, 2026.
>
> • FastAPI Official Documentation: https://fastapi.tiangolo.com
>
> • SQLAlchemy 2.0 Async Documentation:
> https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
>
> • Celery Documentation: https://docs.celeryq.dev • spaCy
> Documentation: https://spacy.io/usage
>
> • PDFMiner.six Documentation: https://pdfminersix.readthedocs.io •
> python-docx Documentation: https://python-docx.readthedocs.io •
> sentence-transformers: https://www.sbert.net
>
> • PostgreSQL 15 Documentation: https://www.postgresql.org/docs/15/
>
> • OWASP API Security Top 10:
> https://owasp.org/www-project-api-security/
>
> **—** **END** **OF** **DOCUMENT** **—**

Interactive Audio Learning Platform — Backend PRDPage

VisioLearn Backend PRD \| v1.0 \| March 2026**CONFIDENTIAL**

> VisioLearn Backend PRD v1.0 \| Prepared March 2026

Interactive Audio Learning Platform — Backend PRDPage
