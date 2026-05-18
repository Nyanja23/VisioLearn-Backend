# Lesson Notes Upload Guide

## Overview

VisioLearn supports TWO methods for uploading lesson notes:

1. **Metadata-Only** (Simple) - For descriptions and metadata
2. **File Upload** (Recommended) - For actual files (PDF, DOCX, TXT)

---

## Method 1: Metadata-Only Upload (Simplest)

Use this if you want to create a note entry without uploading a file yet.

**Endpoint:** `POST /api/v1/notes/upload`

**Request Body:**
```json
{
  "title": "Introduction to Photosynthesis",
  "subject_id": "550e8400-e29b-41d4-a716-446655440000",
  "grade_level": "9",
  "description": "Students will learn the process of photosynthesis, including light-dependent and light-independent reactions.",
  "duration_seconds": 1200
}
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Introduction to Photosynthesis",
  "subject": "Biology",
  "grade_level": "9",
  "description": "Students will learn the process of photosynthesis...",
  "duration_seconds": 1200,
  "teacher_id": "660e8400-e29b-41d4-a716-446655440002",
  "class_id": "660e8400-e29b-41d4-a716-446655440003",
  "subject_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_url": null,
  "original_file_name": null,
  "status": "READY",
  "created_at": "2025-05-18T12:34:56Z",
  "updated_at": "2025-05-18T12:34:56Z"
}
```

**When to use:**
- ✅ Quick note creation with just descriptions
- ✅ When content is audio/video (no file needed)
- ✅ Content will be added later through another system
- ✅ Testing API workflows

---

## Method 2: File Upload (Recommended for Textual Content)

Upload actual lesson files along with metadata. **Supported formats:** PDF, DOCX, TXT

**Endpoint:** `POST /api/v1/notes/upload-with-file`

**Request Type:** `multipart/form-data`

**Form Fields:**
- `title` (string, required) - Lesson title
- `subject_id` (string, required) - UUID of the ClassSubject
- `grade_level` (string, required) - Target grade level
- `file` (file, required) - The lesson file (PDF, DOCX, or TXT)
- `description` (string, optional) - Additional description
- `duration_seconds` (integer, optional) - Duration in seconds

### Example with cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/notes/upload-with-file" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "title=Introduction to Photosynthesis" \
  -F "subject_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "grade_level=9" \
  -F "file=@lesson_notes.pdf" \
  -F "description=Students will learn photosynthesis basics" \
  -F "duration_seconds=1200"
```

### Example with Python:

```python
import requests

url = "http://localhost:8000/api/v1/notes/upload-with-file"
headers = {"Authorization": "Bearer YOUR_JWT_TOKEN"}

files = {
    'file': open('lesson_notes.pdf', 'rb')
}

data = {
    'title': 'Introduction to Photosynthesis',
    'subject_id': '550e8400-e29b-41d4-a716-446655440000',
    'grade_level': '9',
    'description': 'Students will learn photosynthesis basics',
    'duration_seconds': 1200
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### Example with JavaScript/Fetch:

```javascript
const formData = new FormData();
formData.append('title', 'Introduction to Photosynthesis');
formData.append('subject_id', '550e8400-e29b-41d4-a716-446655440000');
formData.append('grade_level', '9');
formData.append('description', 'Students will learn photosynthesis basics');
formData.append('duration_seconds', 1200);
formData.append('file', fileInput.files[0]); // From <input type="file">

fetch('/api/v1/notes/upload-with-file', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`
  },
  body: formData
})
.then(res => res.json())
.then(data => console.log(data))
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Introduction to Photosynthesis",
  "subject": "Biology",
  "grade_level": "9",
  "description": "Students will learn photosynthesis basics",
  "duration_seconds": 1200,
  "teacher_id": "660e8400-e29b-41d4-a716-446655440002",
  "class_id": "660e8400-e29b-41d4-a716-446655440003",
  "subject_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_url": "/uploads/notes/lesson_notes_550e8400.pdf",
  "original_file_name": "lesson_notes.pdf",
  "status": "READY",
  "created_at": "2025-05-18T12:34:56Z",
  "updated_at": "2025-05-18T12:34:56Z"
}
```

**When to use:**
- ✅ Uploading PDF lesson notes
- ✅ Uploading DOCX/Word documents
- ✅ Uploading TXT transcripts
- ✅ Content needs to be accessible for students
- ✅ Files need to be processed/indexed

---

## Workflow Example

### Step 1: Create a Class (Class Teacher)
```json
POST /api/v1/auth/register/class-teacher
{
  "email": "teacher@school.org",
  "full_name": "Mrs. Smith",
  "password": "SecurePass123!@",
  "class_name": "Biology 101"
}
```

Response includes:
- `student_code` - For students to join
- `teacher_code` - For subject teachers to join

### Step 2: Register Subject Teacher

```json
POST /api/v1/auth/register/subject-teacher
{
  "email": "biology.teacher@school.org",
  "full_name": "Mr. Johnson",
  "password": "SecurePass456!@",
  "teacher_code": "TC-ABCD",  // From step 1
  "subject_name": "Biology"
}
```

### Step 3: Get Subject ID

First, retrieve the subject ID created for this subject teacher in the class.

```bash
GET /api/v1/classes/{class_id}/subjects
Authorization: Bearer YOUR_TOKEN
```

Response will include the subject with its UUID.

### Step 4: Upload Lesson Notes

Using the subject ID from step 3:

```bash
curl -X POST "http://localhost:8000/api/v1/notes/upload-with-file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Photosynthesis Basics" \
  -F "subject_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "grade_level=9" \
  -F "file=@photosynthesis_notes.pdf" \
  -F "description=Chapter 1: Light and Dark Reactions"
```

### Step 5: Student Accesses Notes

Student joins class with `student_code`, then:

```bash
GET /api/v1/notes
Authorization: Bearer STUDENT_TOKEN
```

Students see all lesson notes from their class subjects.

---

## Supported File Formats

| Format | Extension | MIME Type | Max Size |
|--------|-----------|-----------|----------|
| PDF | .pdf | application/pdf | 25 MB |
| Word (2007+) | .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | 25 MB |
| Word (97-2003) | .doc | application/msword | 25 MB |
| Plain Text | .txt | text/plain | 25 MB |

---

## Error Handling

### File Too Large
```json
{
  "detail": "File size exceeds maximum (25 MB)"
}
```

### Unsupported File Type
```json
{
  "detail": "File type not supported. Allowed: .pdf, .docx, .txt, .doc"
}
```

### Invalid Subject ID
```json
{
  "detail": "Invalid subject_id format. Must be a valid UUID."
}
```

### No Permission
```json
{
  "detail": "You don't have permission to upload content for this subject"
}
```

---

## Best Practices

1. **Always provide meaningful titles** - Students use these to find content
2. **Include description** - Brief summary helps students know what to expect
3. **Set grade_level** - Helps with content organization
4. **Use files for documents** - PDFs preserve formatting and are widely supported
5. **Test with metadata first** - Verify your workflow before adding file uploads

---

## Troubleshooting

**Q: I'm getting a 404 for subject_id**
- A: Verify the subject was created. Use `GET /api/v1/classes/{class_id}/subjects` to list subjects.

**Q: My file upload fails silently**
- A: Check file size (must be < 25 MB) and format (must be PDF, DOCX, TXT, or DOC).

**Q: Can students download the files?**
- A: Yes, files are stored and accessible. Use `GET /api/v1/notes/{note_id}/file` to retrieve.

---

## API Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/notes/upload` | Metadata-only note creation |
| POST | `/api/v1/notes/upload-with-file` | File upload with metadata |
| GET | `/api/v1/notes` | List all notes (role-based) |
| GET | `/api/v1/notes/{note_id}` | Get note details |
| GET | `/api/v1/notes/{note_id}/file` | Download note file |
| PUT | `/api/v1/notes/{note_id}` | Update note metadata |
| DELETE | `/api/v1/notes/{note_id}` | Delete note |

