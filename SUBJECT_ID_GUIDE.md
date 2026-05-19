# How to Find and Use Subject IDs

## Quick Answer

**Subject IDs are NOT random strings** - they are automatically created when a subject teacher joins a class. Here's how to get them:

---

## The Complete Workflow

### Step 1️⃣ Class Teacher Creates Class

**Endpoint:** `POST /api/v1/auth/register/class-teacher`

```json
{
  "email": "classteacher@school.org",
  "full_name": "Mrs. Smith",
  "password": "SecurePass123!@",
  "class_name": "Biology 101"
}
```

**Response** includes:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "classteacher@school.org",
  "full_name": "Mrs. Smith",
  "role": "class_teacher",
  "class_id": "550e8400-e29b-41d4-a716-446655440001",
  "student_code": "SC-ABCD",
  "teacher_code": "TC-EFGH",
  "created_at": "2025-05-19T05:30:00Z"
}
```

✅ **Save the `teacher_code` (TC-EFGH)** - you'll need this for subject teachers

---

### Step 2️⃣ Subject Teacher Joins Class

**Endpoint:** `POST /api/v1/auth/register/subject-teacher`

```json
{
  "email": "biology.teacher@school.org",
  "full_name": "Mr. Johnson",
  "password": "SecurePass456!@",
  "teacher_code": "TC-EFGH",
  "subject_name": "Biology"
}
```

**Response** includes:
```json
{
  "user_id": "660e8400-e29b-41d4-a716-446655440002",
  "email": "biology.teacher@school.org",
  "full_name": "Mr. Johnson",
  "role": "subject_teacher",
  "subject_id": "770e8400-e29b-41d4-a716-446655440003",    ⭐ THIS IS WHAT YOU NEED!
  "subject_name": "Biology",
  "class_id": "550e8400-e29b-41d4-a716-446655440001",
  "created_at": "2025-05-19T05:32:00Z"
}
```

✅ **The `subject_id` is returned automatically!**

---

### Step 3️⃣ Subject Teacher Uploads Lesson Notes

**Endpoint:** `POST /api/v1/notes/upload-with-file`

Now you can use the `subject_id` from Step 2:

```
title: Photosynthesis Basics
subject_id: 770e8400-e29b-41d4-a716-446655440003  ← Use this
grade_level: 9
file: lesson_notes.pdf
description: Chapter 1: Light and Dark Reactions
```

---

## Where to Find Subject IDs

### Method 1: From Registration Response ⭐ Easiest
When you register as a subject teacher (Step 2 above), the response includes `subject_id`.

**Save it somewhere! You'll need it for uploading files.**

### Method 2: List Subjects in a Class
If you forget the subject ID, list all subjects in the class:

**Endpoint:** `GET /api/v1/classes/{class_id}/subjects`

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/classes/550e8400-e29b-41d4-a716-446655440001/subjects" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "class_id": "550e8400-e29b-41d4-a716-446655440001",
    "subject_name": "Biology",
    "subject_teacher_id": "660e8400-e29b-41d4-a716-446655440002",
    "subject_teacher_email": "biology.teacher@school.org"
  }
]
```

### Method 3: Get Your Own Subjects (Subject Teacher Only)
**Endpoint:** `GET /api/v1/users/me/subjects` (if available)

Lists all subjects you teach.

---

## Real-World Example with cURL

### Step 1: Register Class Teacher
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/class-teacher" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "classteacher@school.org",
    "full_name": "Mrs. Smith",
    "password": "SecurePass123!@",
    "class_name": "Biology 101"
  }'
```

Save from response:
- `teacher_code`: `TC-EFGH`
- `class_id`: `550e8400-e29b-41d4-a716-446655440001`

### Step 2: Register Subject Teacher
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/subject-teacher" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "biology.teacher@school.org",
    "full_name": "Mr. Johnson",
    "password": "SecurePass456!@",
    "teacher_code": "TC-EFGH",
    "subject_name": "Biology"
  }'
```

Save from response:
- `subject_id`: `770e8400-e29b-41d4-a716-446655440003` ⭐

### Step 3: Login as Subject Teacher
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "biology.teacher@school.org",
    "password": "SecurePass456!@"
  }'
```

Save from response:
- `access_token`: Your JWT token

### Step 4: Upload Lesson Notes
```bash
curl -X POST "http://localhost:8000/api/v1/notes/upload-with-file" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "title=Photosynthesis Basics" \
  -F "subject_id=770e8400-e29b-41d4-a716-446655440003" \
  -F "grade_level=9" \
  -F "file=@photosynthesis_notes.pdf" \
  -F "description=Chapter 1: Light and Dark Reactions"
```

---

## Subject ID Reference

| What | Where | Example |
|------|-------|---------|
| **Format** | UUID v4 | `770e8400-e29b-41d4-a716-446655440003` |
| **Created** | When subject teacher joins class | During Step 2 registration |
| **Returned** | Registration response | In `subject_id` field |
| **Retrieved** | List class subjects endpoint | `GET /api/v1/classes/{class_id}/subjects` |
| **Used** | File upload endpoint | `POST /api/v1/notes/upload-with-file` |
| **Scope** | Unique per subject teacher per class | Different for each subject in a class |

---

## In Swagger UI (What You're Seeing)

### To Find Subject ID in Swagger:

1. **Register as subject teacher first** (if not done)
   - Use `POST /api/v1/auth/register/subject-teacher`
   - **Copy the `subject_id` from the response** ✅

2. **List subjects** if you forgot
   - Use `GET /api/v1/classes/{class_id}/subjects`
   - **Copy the `id` field** ✅

3. **Paste into file upload form**
   - Use `POST /api/v1/notes/upload-with-file`
   - In the `subject_id` field, paste the UUID ✅

---

## Common Issues & Fixes

### ❌ "Subject not found"
**Cause:** Invalid subject_id
**Fix:** 
1. Check the UUID format (should be like `770e8400-e29b-41d4-a716-446655440003`)
2. Make sure you registered as a subject teacher first
3. Use `GET /api/v1/classes/{class_id}/subjects` to find correct ID

### ❌ "You don't have permission"
**Cause:** Logged in as wrong user
**Fix:**
1. Logout and login as the **subject teacher who created the subject**
2. OR use the correct `teacher_code` when registering

### ❌ "Teacher code not found"
**Cause:** Invalid teacher code format
**Fix:** 
1. Use the exact `teacher_code` from class teacher registration
2. Format must be `TC-XXXX` (exact length)
3. Make sure class teacher still exists

### ❌ "Subject ID is just asking for a string"
**Why:** The API doesn't validate until you submit
**Solution:** Follow the workflow above to get a real subject_id

---

## Best Practices

1. **Save immediately** - When you register as subject teacher, save the `subject_id` from the response
2. **Write it down** - Create a note with: email, password, subject_id, class_id
3. **Double-check format** - Subject IDs are always UUIDs (36 characters with hyphens)
4. **One subject per teacher per class** - If you need multiple subjects, register again with different subject_name
5. **Use the list endpoint** - If unsure, always use `GET /api/v1/classes/{class_id}/subjects` to verify

---

## API Endpoints Reference

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `POST /api/v1/auth/register/class-teacher` | Create class | `class_id`, `teacher_code` |
| `POST /api/v1/auth/register/subject-teacher` | Join class as subject teacher | **`subject_id`** ⭐ |
| `GET /api/v1/classes/{class_id}/subjects` | List subjects in class | All `subject_id`s |
| `POST /api/v1/notes/upload-with-file` | Upload lesson file | Uses `subject_id` |

