# 🎯 VisioLearn Backend - Frontend Integration Reference

**Version:** 1.0  
**Date:** April 19, 2026  
**Audience:** Frontend Development Team  
**Backend Status:** Phase 3 Week 1 Complete ✅

---

## 📖 Table of Contents

1. [Quick Start](#quick-start)
2. [API Overview](#api-overview)
3. [Authentication](#authentication)
4. [Data Models](#data-models)
5. [API Endpoints](#api-endpoints)
6. [Error Handling](#error-handling)
7. [Integration Examples](#integration-examples)
8. [Testing & Debugging](#testing--debugging)
9. [Deployment Notes](#deployment-notes)

---

## 🚀 Quick Start

### Backend URL
```
http://localhost:8000  (development)
https://api.visiolearn.org (production - TBD)
```

### Base API Path
```
/api/v1/
```

### Example Endpoint
```
POST http://localhost:8000/api/v1/auth/login
```

### Prerequisites
- Backend running (see SETUP_AND_RUN.md)
- PostgreSQL database initialized
- Redis running (for Celery tasks)
- Admin account created

---

## 📊 API Overview

### Implemented & Ready (Phase 2-3 Week 1)

| Feature | Status | Endpoints |
|---------|--------|-----------|
| **Authentication** | ✅ Ready | POST /auth/login, POST /auth/refresh |
| **User Management** | ✅ Ready | POST /users, GET /users |
| **Lesson Upload** | ✅ Ready | POST /notes/upload, GET /notes |
| **Content Retrieval** | ✅ Ready | GET /notes/{id}, GET /notes/{id}/units |
| **Voice Sessions** | ✅ Ready | POST /voice/session/start, /event, /end |
| **Session Details** | ✅ Ready | GET /voice/session/{id}, /{id}/interactions |

### Coming Soon (Phase 3 Weeks 2-4)

| Feature | Status | Endpoints |
|---------|--------|-----------|
| **Voice Transcription** | 🔄 In Development | POST /voice/transcribe |
| **Intent Classification** | 🔄 In Development | POST /voice/interpret |
| **Free Ask (RAG)** | 🔄 In Development | POST /voice/ask |
| **Offline Sync** | 🔄 In Development | GET /sync/pull, POST /sync/push |
| **Progress Tracking** | 🔄 In Development | GET /progress, POST /progress |
| **Analytics** | 🔄 In Development | POST /analytics/event |

---

## 🔐 Authentication

### Login Flow

**Step 1: Get Access Token**

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@visiolearn.org",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using Access Token

**All protected endpoints require Authorization header:**

```bash
-H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

### Token Expiration

- **Access Token:** 60 minutes (default)
- **Refresh Token:** 90 days

### Refresh Token Flow

```bash
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGci..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

## 📋 Data Models

### User Model

```json
{
  "id": "UUID",
  "email": "user@school.org",
  "full_name": "Full Name",
  "role": "admin|teacher|student",
  "school_id": "UUID",
  "created_at": "2026-04-19T00:00:00Z",
  "last_login_at": "2026-04-19T17:00:00Z"
}
```

**Roles:**
- `admin` - Full system access, user management
- `teacher` - Can upload lessons, view student progress
- `student` - Can access lessons, participate in voice sessions

---

### LessonNote Model

```json
{
  "id": "UUID",
  "title": "Living Things",
  "subject": "Science",
  "grade_level": "P3",
  "teacher_id": "UUID",
  "school_id": "UUID",
  "original_file_name": "science_notes.txt",
  "file_url": "notes/UUID/science_notes.txt",
  "status": "PENDING_PROCESSING|READY|ERROR",
  "created_at": "2026-04-19T16:00:00Z",
  "updated_at": "2026-04-19T16:30:00Z"
}
```

**Status Meanings:**
- `PENDING_PROCESSING` - File uploaded, waiting for AI processing
- `READY` - Fully processed, ready for student learning
- `ERROR` - Processing failed, check with teacher

---

### LearningUnit Model

```json
{
  "id": "UUID",
  "note_id": "UUID",
  "sequence_number": 0,
  "content_text": "The lesson content for this unit...",
  "created_at": "2026-04-19T14:10:00Z"
}
```

**Key Points:**
- One lesson has multiple units
- Units are in sequence order (0, 1, 2, ...)
- Each unit is ~500 words of content

---

### VoiceSession Model

```json
{
  "id": "UUID",
  "student_id": "UUID",
  "note_id": "UUID",
  "current_unit_id": "UUID",
  "status": "ACTIVE|PAUSED|COMPLETED",
  "current_state": "LISTENING_UNIT|ANSWERING|REVIEWING|...",
  "started_at": "2026-04-19T17:00:00Z",
  "last_activity_at": "2026-04-19T17:05:00Z",
  "completed_at": "2026-04-19T17:20:00Z"
}
```

**Status Flow:**
```
ACTIVE → (user pauses) → PAUSED → (user resumes) → ACTIVE → (user ends) → COMPLETED
```

---

### VoiceInteraction Model

```json
{
  "id": "UUID",
  "session_id": "UUID",
  "sequence_number": 1,
  "student_transcript": "My answer to the question",
  "detected_intent": "answer|next|repeat|free_ask|pause",
  "ai_response_text": "That's correct! The cell nucleus...",
  "confidence_score": 0.92,
  "created_at": "2026-04-19T17:05:00Z"
}
```

**Intent Types:**
- `answer` - Student answered a question
- `next` - Student wants to move to next unit
- `repeat` - Student wants content repeated
- `free_ask` - Student asked a free question
- `pause` - Student paused session

---

## 🔌 API Endpoints

### Authentication Endpoints

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@visiolearn.org",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJh...",
  "refresh_token": "eyJh...",
  "token_type": "bearer"
}
```

---

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJh..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJh...",
  "token_type": "bearer"
}
```

---

### User Endpoints

#### Create User (Admin Only)
```http
POST /api/v1/users
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "email": "newuser@school.org",
  "full_name": "New User",
  "password": "SecurePass123!",
  "role": "student|teacher|admin",
  "school_id": "UUID"
}
```

**Response (201 Created):**
```json
{
  "id": "UUID",
  "email": "newuser@school.org",
  "full_name": "New User",
  "role": "student"
}
```

---

#### Get All Users
```http
GET /api/v1/users
Authorization: Bearer TOKEN
```

**Response (200 OK):**
```json
[
  {
    "id": "UUID",
    "email": "user1@school.org",
    "full_name": "User One",
    "role": "student"
  },
  ...
]
```

---

### Lesson Notes Endpoints

#### Get All Lessons
```http
GET /api/v1/notes
Authorization: Bearer TOKEN
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "UUID",
      "title": "Living Things",
      "subject": "Science",
      "grade_level": "P3",
      "status": "READY",
      "created_at": "2026-04-19T14:00:00Z"
    }
  ]
}
```

---

#### Get Lesson Details
```http
GET /api/v1/notes/{note_id}
Authorization: Bearer TOKEN
```

**Response (200 OK):**
```json
{
  "id": "UUID",
  "title": "Living Things",
  "subject": "Science",
  "grade_level": "P3",
  "status": "READY",
  "teacher_name": "John Doe",
  "school_name": "Sample School",
  "created_at": "2026-04-19T14:00:00Z"
}
```

---

#### Get Learning Units
```http
GET /api/v1/notes/{note_id}/units
Authorization: Bearer TOKEN
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "UUID",
      "note_id": "UUID",
      "sequence_number": 0,
      "content_text": "Living things are...",
      "created_at": "2026-04-19T14:10:00Z"
    },
    {
      "id": "UUID",
      "note_id": "UUID",
      "sequence_number": 1,
      "content_text": "Non-living things are...",
      "created_at": "2026-04-19T14:10:00Z"
    }
  ]
}
```

---

### Voice Session Endpoints

#### Start Voice Session
```http
POST /api/v1/voice/session/start
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "student_id": "UUID",
  "note_id": "UUID",
  "unit_id": "UUID"
}
```

**Response (201 Created):**
```json
{
  "session_id": "UUID",
  "student_id": "UUID",
  "note_id": "UUID",
  "unit_id": "UUID",
  "status": "ACTIVE",
  "started_at": "2026-04-19T17:00:00Z"
}
```

**Errors:**
- `400` - Student doesn't have role="student"
- `404` - Student, note, or unit not found
- `400` - Note status is not "READY"

---

#### Log Voice Interaction
```http
POST /api/v1/voice/session/event
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "session_id": "UUID",
  "interaction_type": "answer|next|repeat|free_ask|pause",
  "command": "The nucleus controls the cell",
  "confidence": 0.92
}
```

**Response (201 Created):**
```json
{
  "interaction_id": "UUID",
  "session_id": "UUID",
  "sequence_number": 1,
  "student_transcript": "The nucleus controls the cell",
  "detected_intent": "answer",
  "ai_response_text": "Correct! The nucleus is the control center...",
  "confidence_score": 0.92,
  "created_at": "2026-04-19T17:05:00Z"
}
```

---

#### Get Session Details
```http
GET /api/v1/voice/session/{session_id}
Authorization: Bearer TOKEN
```

**Response (200 OK):**
```json
{
  "session_id": "UUID",
  "student_id": "UUID",
  "note_id": "UUID",
  "current_unit_id": "UUID",
  "status": "ACTIVE",
  "started_at": "2026-04-19T17:00:00Z",
  "last_activity_at": "2026-04-19T17:05:00Z"
}
```

---

#### Get All Interactions in Session
```http
GET /api/v1/voice/session/{session_id}/interactions
Authorization: Bearer TOKEN
```

**Response (200 OK):**
```json
[
  {
    "interaction_id": "UUID",
    "session_id": "UUID",
    "sequence_number": 1,
    "student_transcript": "...",
    "detected_intent": "answer",
    "ai_response_text": "...",
    "confidence_score": 0.92,
    "created_at": "2026-04-19T17:05:00Z"
  }
]
```

---

#### End Voice Session
```http
POST /api/v1/voice/session/end
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "session_id": "UUID",
  "duration_seconds": 720,
  "questions_answered": 5,
  "total_score": 4.1
}
```

**Response (200 OK):**
```json
{
  "session_id": "UUID",
  "status": "COMPLETED",
  "duration_seconds": 720,
  "questions_answered": 5,
  "average_score": 0.82,
  "ended_at": "2026-04-19T17:20:00Z"
}
```

---

## ❌ Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | Success | GET request successful |
| **201** | Created | POST request successful, resource created |
| **400** | Bad Request | Invalid input, student is not role="student" |
| **401** | Unauthorized | Missing or invalid token |
| **403** | Forbidden | User doesn't have permission |
| **404** | Not Found | Resource doesn't exist |
| **422** | Validation Error | Invalid request body |
| **500** | Server Error | Backend error |

### Common Errors

#### Authentication Error
```json
{
  "detail": "Not authenticated"
}
```
**Fix:** Include valid Authorization header with Bearer token

#### Student Role Error
```json
{
  "detail": "Can only create voice sessions for student users"
}
```
**Fix:** Use user with role="student"

#### Note Not Ready
```json
{
  "detail": "Lesson note not ready for learning (status: PENDING_PROCESSING)"
}
```
**Fix:** Wait for lesson processing to complete (status becomes READY)

#### Resource Not Found
```json
{
  "detail": "Student not found: uuid"
}
```
**Fix:** Use correct IDs from GET endpoints

---

## 💡 Integration Examples

### Example 1: Complete Voice Learning Flow

```javascript
// 1. Login
const login = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@visiolearn.org',
    password: 'SecurePass123!'
  })
});
const { access_token } = await login.json();

// 2. Get lessons
const notes = await fetch('http://localhost:8000/api/v1/notes', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const { data: lessons } = await notes.json();
const lesson = lessons.find(l => l.status === 'READY');

// 3. Get units
const units = await fetch(`http://localhost:8000/api/v1/notes/${lesson.id}/units`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const { data: unitList } = await units.json();

// 4. Start voice session
const session = await fetch('http://localhost:8000/api/v1/voice/session/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    student_id: 'cfcfc13e-52bd-46e2-85c5-b6390d7d6cbc',
    note_id: lesson.id,
    unit_id: unitList[0].id
  })
});
const { session_id } = await session.json();

// 5. Log an interaction
const interaction = await fetch('http://localhost:8000/api/v1/voice/session/event', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    session_id: session_id,
    interaction_type: 'answer',
    command: 'Living things are alive',
    confidence: 0.95
  })
});
const result = await interaction.json();

// 6. End session
const end = await fetch('http://localhost:8000/api/v1/voice/session/end', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    session_id: session_id,
    duration_seconds: 300,
    questions_answered: 1,
    total_score: 1.0
  })
});
```

---

### Example 2: Create Test Student

```javascript
// Create student user
const createUser = await fetch('http://localhost:8000/api/v1/users', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${admin_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'student@school.org',
    full_name: 'Test Student',
    password: 'StudentPass123!',
    role: 'student',
    school_id: 'd1ae8f00-e0b0-40c7-9884-8c7611acc87a'
  })
});
const { id: student_id } = await createUser.json();
```

---

## 🧪 Testing & Debugging

### Using Swagger UI

1. Go to `http://localhost:8000/docs`
2. Click "Authorize" button
3. Paste your access token
4. Click endpoint to test
5. Click "Try it out"
6. Fill in request body
7. Click "Execute"

### Using cURL

```bash
curl -X POST http://localhost:8000/api/v1/voice/session/start \
  -H 'Authorization: Bearer eyJhbGci...' \
  -H 'Content-Type: application/json' \
  -d '{
    "student_id": "cfcfc13e-52bd-46e2-85c5-b6390d7d6cbc",
    "note_id": "3abe4bef-df2a-4e56-89e7-970e97ee9a67",
    "unit_id": "1bd01836-b6af-482e-b80a-ae47ae24cd81"
  }'
```

### Debugging Checklist

- [ ] Token is valid (not expired)
- [ ] Authorization header has "Bearer " prefix
- [ ] All required fields in request body
- [ ] IDs exist in database (use GET endpoints to verify)
- [ ] Student has role="student"
- [ ] Note status is "READY"
- [ ] Unit belongs to that note

---

## 🚀 Deployment Notes

### Environment Variables Frontend Needs

```env
BACKEND_URL=http://localhost:8000          # Development
BACKEND_URL=https://api.visiolearn.org     # Production
API_VERSION=v1
```

### CORS Configuration

Frontend can be at:
- `http://localhost:3000` (development)
- `http://localhost:8080` (alternative dev)
- `https://visiolearn.org` (production - TBD)

### Token Storage

**Recommendation:** Store tokens securely
- Access token: Session storage (cleared on browser close)
- Refresh token: Secure HTTP-only cookie (if backend supports)

### Error Handling Strategy

```javascript
try {
  const res = await fetch(url, { headers, body });
  if (!res.ok) {
    const error = await res.json();
    console.error(`Error ${res.status}: ${error.detail}`);
  }
  return await res.json();
} catch (e) {
  console.error('Network error:', e);
}
```

---

## 📞 Support & Questions

**For API issues:**
1. Check this documentation first
2. Review Swagger UI at http://localhost:8000/docs
3. Check backend logs for errors

**For phase 3 features (coming soon):**
- Voice transcription
- Intent classification
- RAG for free questions
- Offline synchronization
- Progress tracking

See **PHASE3_PLAN.md** for implementation timeline.

---

## ✅ Checklist for Frontend Development

- [ ] Read this entire document
- [ ] Test at least 3 endpoints in Swagger UI
- [ ] Implement login & token management
- [ ] Create lesson list view
- [ ] Create unit list view
- [ ] Implement voice session flow
- [ ] Handle all error cases
- [ ] Test with different user roles
- [ ] Implement token refresh logic
- [ ] Test offline scenarios

---

**Backend Status:** Production-ready for Phase 2-3 Week 1  
**Last Updated:** April 19, 2026  
**Next Update:** When Phase 3 Weeks 2-4 complete

