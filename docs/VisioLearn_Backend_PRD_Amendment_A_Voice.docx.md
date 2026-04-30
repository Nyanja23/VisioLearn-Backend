VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

> **PRD** **AMENDMENT** **A**
>
> **Voice** **Interaction** **System**
>
> *Full* *Audio-First* *Student* *Interaction* *—* *Backend*
> *Requirements*

||
||
||
||
||
||
||
||
||

> **CRITICAL** **DESIGN** **PRINCIPLE:** Visually impaired students
> cannot see buttons, menus, or text on screen. Every single student
> interaction with the learning system — navigation, answering
> questions, requesting help, controlling playback, asking the AI — MUST
> be achievable through voice alone. The backend must be architected to
> receive, interpret, and respond to voice input as a first-class
> interaction channel, not as an afterthought.

**21.** **Voice** **Interaction** **System** **—** **Complete**
**Specification**

This chapter defines the complete backend architecture for audio-first
student interaction. It covers: voice data reception, speech-to-text
transcription, natural language understanding (intent classification +
entity extraction), dialogue state management, AI response generation
(constrained to lesson content), and audio response delivery. It also
defines the fallback pipeline ensuring the system remains functional
when voice quality is poor.

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

**21.1** **Architecture** **Overview** **—** **Audio-First**
**Interaction** **Loop**

The interaction loop runs as follows. Every step either happens
on-device (Android client) or backend-side. The backend's
responsibilities are bolded:

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

> **OFFLINE** **FIRST** **—** **VOICE:** Voice interaction MUST degrade
> gracefully offline. Steps 1–4 (capture + transcription + basic intent
> matching) MUST work fully offline using on-device Android
> SpeechRecognizer and a downloaded intent model. Backend voice
> endpoints are only called when connectivity is available. The system
> must NOT become non-functional when offline — see Section 21.9 for
> full offline fallback specification.

**21.2** **Voice** **Session** **Concept** **&** **State** **Machine**

A Voice Session is the stateful context of a student's current learning
interaction. It tracks where in the lesson the student is, what question
they are on, and what the AI last said, so the backend can interpret
follow-up voice inputs correctly (e.g. 'repeat that' or 'I said B'
requires knowing what was just asked).

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

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

The current session state is maintained on the Android device
(in-memory + Room DB). The backend is stateless per-request but
reconstructs context from the session_id and the current_unit_id /
current_artefact_id passed with every voice API request. The backend
MUST validate that the incoming request is consistent with a valid state
transition.

**21.3** **New** **Database** **Entities** **for** **Voice**
**Interaction**

**21.3.1** **Entity:** **voice_sessions**

Tracks the lifecycle of each student's learning session at a note level.

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

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||

**21.3.2** **Entity:** **voice_interactions**

Detailed log of every voice exchange — the raw transcript, interpreted
intent, action taken, and response delivered. This is the core audit
trail for research and model improvement.

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

Index: CREATE INDEX idx_voice_interactions_session ON
voice_interactions(session_id, sequence_number);

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

**21.3.3** **Entity:** **free_ask_exchanges**

Dedicated table for student free-form questions posed to the AI
assistant during Free Ask Mode. Stores the question, the matched lesson
context, and the answer — critical for research analysis of what
students are confused about.

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

**21.4** **Intent** **Taxonomy** **—** **Complete** **Voice**
**Command** **Set**

The NLU classifier MUST recognise and correctly route all of the
following intents. Intents are grouped by the session state they are
valid in. The backend must reject (with a helpful clarification
response) intents that arrive in invalid states.

**21.4.1** **Navigation** **Intents** **(valid** **in**
**LISTENING_LESSON** **state)**

||
||
||
||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||
||

**21.4.2** **Answer** **Intents** **(valid** **in** **QUESTION_POSED**
**state)**

||
||
||
||
||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||

**21.4.3** **AI** **Assistant** **Intents** **(Free** **Ask** **Mode**
**—** **any** **state)**

||
||
||
||
||
||
||
||
||

**21.4.4** **Session** **Management** **Intents** **(any** **state)**

||
||
||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||
||
||
||

**21.5** **New** **Voice** **API** **Endpoints**

> **BASE** **PATH:** All voice endpoints are under /api/v1/voice. All
> require JWT authentication (student role minimum). All support gzip
> compression.

**21.5.1** **POST** **/voice/transcribe**

Used only as fallback when on-device ASR confidence is below 0.65, or
when the student is offline and has queued audio for transcription
during next sync. Accepts raw audio and returns transcription.

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

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||
||
||

**21.5.2** **POST** **/voice/interpret**

Takes a transcript (from on-device ASR or from /voice/transcribe) and
the current interaction context, and returns the classified intent,
extracted entities, and the backend action + response text. This is the
central NLU endpoint.

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

**21.5.3** **POST** **/voice/session/start**

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

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

**21.5.4** **POST** **/voice/session/event**

Lightweight endpoint for logging voice interaction events. Called after
every voice exchange. Designed for minimal payload and maximum
throughput.

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

**21.5.5** **POST** **/voice/session/end**

||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||
||
||

**21.5.6** **POST** **/voice/ask** **(Free** **Ask** **Mode** **—**
**RAG** **Endpoint)**

This is the most complex voice endpoint. It powers Free Ask Mode: the
student asks any natural language question about the lesson, and the
backend answers strictly from the uploaded lesson text using
Retrieval-Augmented Generation.

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

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

**21.5.7** **GET** **/voice/session/{session_id}/progress**

||
||
||
||
||
||
||
||
||

**21.5.8** **POST** **/voice/session/events/batch** **(Offline**
**Sync)**

Used during sync window to flush all voice interaction events that were
recorded offline.

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

**21.6** **Free** **Ask** **Mode** **—** **RAG** **Pipeline**
**Specification**

This pipeline is triggered by the ASK_QUESTION intent. It retrieves the
most relevant portions of the uploaded lesson content and generates a
grounded, spoken-language answer. It is strictly content-bound — the
system cannot use any knowledge outside the uploaded note.

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

**Step** **1:** **Query** **Embedding**

> • Normalise student question: lowercase, remove filler words, correct
> common ASR errors (via a small phonetic correction dictionary).
>
> • Embed the normalised question using sentence-transformers
> (paraphrase-MiniLM-L6-v2, INT8 quantised). This model runs entirely
> server-side.
>
> • Question embedding is a 384-dimension vector.

**Step** **2:** **Corpus** **Retrieval**

> • All learning units for the note are pre-embedded at index time
> (during generate_artefacts task) and stored as JSONB embedding vectors
> in the learning_units table.
>
> • Compute cosine similarity between question embedding and all unit
> embeddings for the note.
>
> • Retrieve top-3 units by cosine similarity score. Minimum similarity
> threshold: 0.40. If no unit meets threshold → answer_found=false.
>
> • If top unit score \> 0.75: use only top-1 unit (highly targeted
> answer). If top score 0.40–0.75: use top-3 units (broader context).

**Step** **3:** **Context** **Window** **Assembly**

> • Concatenate retrieved unit texts in similarity-rank order, separated
> by a blank line.
>
> • Prepend an instruction prefix: 'Answer the following question using
> ONLY the text below. If the answer is not in the text, say so.
> Question: \[question_text\]. Text: \[retrieved units\].'
>
> • Total context window MUST NOT exceed 1024 tokens (enforced by
> truncation of lower-ranked units).

**Step** **4:** **Answer** **Generation**

> • Pass assembled context to a lightweight extractive-abstractive
> generator: first attempt pure extraction (select the most
> answer-relevant sentence from retrieved units using a BERT extractive
> QA model — distilbert-base-cased-distilled-squad, INT8 quantised).
>
> • If extractive span confidence \>= 0.70: use extracted span as the
> answer base. Expand to include the surrounding 1–2 sentences for
> context.
>
> • If extractive confidence \< 0.70: fall back to template: 'Based on
> the lesson, \[most relevant sentence from top unit\].'
>
> • Answer MUST be converted to conversational spoken form: no markdown,
> no bullet points, written in complete sentences suitable for TTS. Max
> 3 sentences.

**Step** **5:** **Grounding** **Validation**

> • Split generated answer into sentences. For each sentence, compute
> cosine similarity to all retrieved unit sentences.
>
> • If any answer sentence has maximum similarity \< 0.40 to all unit
> sentences → remove that sentence from the answer (hallucination
> guard).
>
> • If grounding check removes all sentences → return no-answer
> fallback.

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

**Step** **6:** **Response** **Packaging**

> • Return answer_text (spoken-form, grounded), source_unit_ids (list of
> units used), confidence (top similarity score), answer_found: true.
>
> • Store exchange in free_ask_exchanges table for research analytics.

**21.7** **NLU** **Model** **Specification**

The NLU pipeline runs entirely on the backend server. No external AI API
calls are made. All models are downloaded at deployment time and stored
on the server.

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

**21.8** **Answer** **Scoring** **via** **Voice** **Input**

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

When a student answers a question by voice, the scoring pipeline must
handle both MCQ and short-answer types from a natural language voice
transcript.

**21.8.1** **MCQ** **Voice** **Answer** **Scoring**

> 1\. Receive transcript_text from /voice/interpret request.
>
> 2\. Normalise: lowercase, strip filler words, apply ASR error
> corrections.
>
> 3\. Extract answer entity: look for patterns — single letter
> ('a','b','c','d'), ordinal ('first','second','third','fourth'), or
> phrase match to option text.
>
> 4\. Entity extraction confidence: if pattern matched → confidence 1.0.
> If fuzzy match to option text (cosine similarity \>= 0.70) →
> confidence = similarity score.
>
> 5\. If no answer entity extracted with confidence \>= 0.60: return
> UNKNOWN intent → ask student to repeat ('I did not catch your answer.
> Say A, B, C, or D.').
>
> 6\. Compare extracted answer_choice to correct_option_id. Compute:
> is_correct (boolean), score (1.0 or 0.0 for MCQ).
>
> 7\. Generate feedback response_text: if correct → 'Correct!
> \[explanation text from artefact\]'. If incorrect → 'Not quite. The
> correct answer is \[option text\]. \[explanation text\].'
>
> 8\. Store in student_progress via voice_interactions record.

**21.8.2** **Short** **Answer** **Voice** **Scoring**

> 9\. Receive full transcript_text as the student's answer. 10. Embed
> transcript using paraphrase-MiniLM-L6-v2.
>
> 11\. Embed model_answer (the source sentence stored in artefact).
>
> 12\. Cosine similarity score → 0.75+ = correct (1.0), 0.50–0.74 =
> partial (0.5), \< 0.50 = incorrect (0.0).
>
> 13\. Generate voice feedback: correct → 'Well done! That is
> correct.' + encouragement. Partial → 'You are on the right track. A
> more complete answer would be: \[model answer\].' Incorrect → 'Not
> quite. The answer is: \[model answer\]. Let us read that part again.'
> (trigger re-read of source unit).
>
> 14\. Log score, student_answer (transcript), and is_correct in
> student_progress.

**21.9** **Offline** **Voice** **Interaction** **Fallback**
**Specification**

The backend cannot be reached when the student is offline. The Android
client must continue to provide a fully functional audio learning
experience. The backend's responsibility here is to

pre-deliver everything the client needs to operate voice interaction
without a connection.

> **DESIGN** **RULE:** The sync-pull payload (GET /api/v1/sync/pull)
> MUST include all data required for offline voice interaction. The
> Android client must never need to call a backend endpoint during a
> learning session. Backend voice endpoints are only called when online.

**Additional** **Data** **in** **Sync-Pull** **for** **Voice**
**Interaction**

||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

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

**Offline** **Intent** **Matching** **Flow**

> 15\. Android SpeechRecognizer produces transcript (offline ASR, always
> available).
>
> 16\. Run on-device intent model (TFLite). If confidence \>= 0.65 →
> dispatch intent locally. 17. If confidence \< 0.65 → fall back to
> navigation_phrases_map keyword lookup.
>
> 18\. If still unmatched → play clarification prompt from static audio
> file: 'I did not understand. You can say: next, repeat, answer A, or
> stop.'
>
> 19\. All interactions are logged in Room DB. Voice interactions and
> session events are queued for sync.
>
> 20\. Answer scoring (MCQ only) runs fully offline: correct_option_id
> is revealed after completion via /sync/answers; until then, Android
> stores answer_choice and defers scoring to next sync.

**21.10** **Performance** **Requirements** **—** **Voice** **Endpoints**

||
||
||
||
||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

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

**Voice** **Performance** **Optimisation** **Rules**

> • All NLP models MUST be loaded into memory at Celery worker startup —
> NOT per-request. Cold load penalty is paid once per worker lifecycle.
>
> • POST /voice/interpret MUST execute synchronously within the HTTP
> request — no task queue for navigation or answer intents. Latency must
> be felt in real-time conversation.
>
> • POST /voice/ask MAY be dispatched to a high-priority Celery task if
> server load is high — but MUST complete and return within 1500ms. Use
> async HTTP long-poll or WebSocket upgrade if needed.
>
> • Voice endpoints MUST have their own Uvicorn worker pool separate
> from general API workers — isolate model memory from REST endpoints.
>
> • Intent model inference MUST run on a dedicated thread pool
> (ThreadPoolExecutor) to avoid blocking the async event loop.
>
> • Whisper transcription MUST run in a subprocess or thread — it is
> CPU-bound and must not block the async event loop.

**21.11** **Amendments** **to** **Existing** **Data** **Models**

The following columns are added to existing tables defined in the
original PRD (Section 5) to support voice interaction:

**Additions** **to:** **learning_units**

||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||
||

**Additions** **to:** **ai_artefacts**

||
||
||
||
||
||
||
||

**Additions** **to:** **student_progress**

||
||
||
||
||
||
||
||

**21.12** **New** **Background** **Jobs** **for** **Voice** **System**

||
||
||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||
||
||
||
||

**21.13** **Voice-Specific** **Security** **Requirements**

> • Audio files received by POST /voice/transcribe MUST be validated for
> actual audio format using python-magic before processing. Reject
> non-audio files with 400 INVALID_AUDIO.
>
> • Audio files MUST be stored in a temporary directory (/tmp/voice/)
> with a random UUID filename. The file MUST be deleted immediately
> after transcription. Audio is never persisted.
>
> • Transcripts ARE stored in voice_interactions.transcript_text.
> Developers must be aware this is personal data (the student's own
> spoken words). It MUST be excluded from any data exports not
> explicitly consented to by the user.
>
> • The voice/ask RAG endpoint MUST enforce a rate limit of 20
> ASK_QUESTION requests per student per hour to prevent abuse of the NLP
> pipeline.
>
> • POST /voice/interpret and POST /voice/ask MUST validate that the
> provided note_id is actually assigned to the authenticated student. A
> student MUST NOT be able to query lesson content from notes not
> assigned to them.
>
> • Intent model bundles distributed to Android clients MUST be signed
> with a server private key. The Android client MUST verify the
> signature before loading a new bundle.

**21.14** **Testing** **Requirements** **—** **Voice** **System**

**Unit** **Tests**

> • Test intent classifier with: 20 correctly-classified utterances per
> intent (all intents in Section 21.4). Target: \>= 90% accuracy on
> held-out test set.
>
> • Test MCQ answer entity extraction with: 'A', 'option A', 'I think
> A', 'the answer is A', 'first option', 'see' (phonetic for C), 'dee'
> (phonetic for D).

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

> • Test short-answer scorer with: exact match, strong paraphrase
> (expect correct), weak paraphrase (expect partial), completely wrong
> answer (expect incorrect).
>
> • Test RAG pipeline with: factual question answerable from unit,
> factual question NOT answerable from unit, question that requires
> combining two units, nonsense question.
>
> • Test grounding validation: inject a synthetic hallucinated sentence;
> verify it is removed by grounding check.

**Integration** **Tests**

> • Full session simulation: POST /voice/session/start → 3x POST
> /voice/interpret (navigation) → 2x POST /voice/interpret (answer MCQ)
> → 1x POST /voice/ask → POST /voice/session/end. Verify all DB records
> created correctly.
>
> • Offline batch sync: create 100 voice events in local format; POST to
> /voice/session/events/batch; verify all inserted with correct
> deduplication.
>
> • State validation: submit ANS_MCQ intent while in LISTENING_LESSON
> state; verify backend returns clarification error (not an answer
> score).

**Performance** **Tests**

> • POST /voice/transcribe: test with 10 concurrent 15-second audio
> clips; all must complete in \< 1200ms P99.
>
> • POST /voice/ask: test with 20 concurrent RAG requests against a
> 10-unit note; all must complete in \< 1500ms P99.
>
> • Model startup time: verify all NLP models loaded and warm within 30
> seconds of worker start.

**21.15** **Acceptance** **Criteria** **—** **Voice** **System**

The voice interaction system is considered complete when ALL of the
following pass:

> 21\. A student can start a learning session, navigate through all
> units, and complete all questions using ONLY voice commands — zero
> screen touches required.
>
> 22\. MCQ answer intents correctly extract the answer choice from 'A',
> 'option B', 'I think it is C', and phonetic variants 'see', 'dee',
> 'ay', 'bee' with \>= 90% accuracy on a 50-utterance test set.
>
> 23\. Short answer scoring returns correct / partial / incorrect
> feedback with appropriate TTS response text for each.
>
> 24\. The UNKNOWN intent is returned for any utterance with
> intent_confidence \< 0.60, and the clarification response_text lists
> valid commands.
>
> 25\. Free Ask Mode answers a factual question from lesson text within
> 1500ms and the answer contains no content not present in the uploaded
> note (grounding check passes).
>
> 26\. Free Ask Mode correctly returns answer_found=false for a question
> with no relevant content in the lesson.
>
> 27\. POST /voice/session/event responds in \< 100ms P99 under 50
> concurrent requests.
>
> 28\. The sync-pull payload includes the intent_model_bundle,
> asr_correction_map, and all TTS feedback texts for offline use.

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

> 29\. A full simulated offline session (50 events) is successfully
> batch-synced via /voice/session/events/batch with zero data loss.
>
> 30\. Audio files are confirmed deleted from /tmp/voice/ within 5
> seconds of transcription completion.
>
> 31\. A student cannot call /voice/ask on a note not assigned to them —
> returns 403.

**21.16** **Updated** **Development** **Phases** **—** **Voice**
**System** **Integration**

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

**21.17** **Open** **Questions** **—** **Voice** **System**

||
||
||
||
||

VisioLearn — Voice Interaction System AmendmentPage

VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
\| March 2026**CONFIDENTIAL**

||
||
||
||
||
||

> **—** **END** **OF** **AMENDMENT** **A** **—**
>
> VisioLearn Backend PRD — Amendment A: Voice Interaction System \| v1.1
> \| March 2026
>
> *This* *document* *should* *be* *read* *alongside* *and* *supersedes*
> *relevant* *sections* *of* *VisioLearn* *Backend* *PRD* *v1.0*

VisioLearn — Voice Interaction System AmendmentPage
