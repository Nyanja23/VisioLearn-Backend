# File Upload Endpoint Fix

## Issue
When uploading lesson notes via `POST /api/v1/notes/upload-with-file`, the endpoint returned:
```json
{
  "detail": "File upload failed: type object 'FileManager' has no attribute 'save_file'"
}
```

## Root Cause
The `upload_lesson_note_with_file()` endpoint was calling the **wrong method name**:
- ❌ Called: `FileManager.save_file(file)` 
- ✅ Correct: `FileManager.save_upload_file(file, note_id)` (async method)

## Changes Made

### app/routers/notes.py
1. **Made endpoint async**: Changed `def` to `async def` (line 402)
2. **Fixed method call**: Changed to `await FileManager.save_upload_file(file, str(note_id))`
3. **Reordered logic**: Generate `note_id` before calling file save (so it can be passed as parameter)
4. **Simplified file path**: Removed unnecessary `str()` cast (save_upload_file already returns string)

### Summary of Changes
```python
# Before (WRONG)
file_path = FileManager.save_file(file)

# After (CORRECT)
file_path = await FileManager.save_upload_file(file, str(note_id))
```

## What Now Works
✅ File upload endpoint accepts PDF, DOCX, TXT files
✅ Files are validated (extension, MIME type, magic bytes)
✅ Files are stored in `./uploads/notes/{note_id}/` directory structure
✅ LessonNote records are created with file metadata
✅ Subject teachers can upload notes for their classes

## Testing the Fix

### Via cURL
```bash
# 1. Register subject teacher (get subject_id from response)
curl -X POST "http://localhost:8000/api/v1/auth/register/subject-teacher" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@school.org",
    "full_name": "Mr. Smith",
    "password": "StrongPass123!@",
    "teacher_code": "TC-ABCD",
    "subject_name": "Biology"
  }'

# 2. Login to get JWT token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teacher@school.org",
    "password": "StrongPass123!@"
  }'

# 3. Upload lesson file
curl -X POST "http://localhost:8000/api/v1/notes/upload-with-file" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "title=Lesson 1: Photosynthesis" \
  -F "subject_id=<UUID_FROM_STEP_1>" \
  -F "grade_level=9" \
  -F "file=@lesson_notes.pdf" \
  -F "description=Chapter 1"
```

### Via Swagger UI
1. Navigate to `/docs`
2. Register as subject teacher → save `subject_id`
3. Login with the teacher account
4. Use POST `/api/v1/notes/upload-with-file`
5. Fill in the form:
   - title: "Photosynthesis Basics"
   - subject_id: `<UUID from registration>`
   - grade_level: "9"
   - file: Choose your PDF/DOCX/TXT file
   - description: Optional

## Success Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Lesson 1: Photosynthesis",
  "class_id": "550e8400-e29b-41d4-a716-446655440001",
  "subject_id": "550e8400-e29b-41d4-a716-446655440002",
  "file_url": "550e8400-e29b-41d4-a716-446655440000/lesson_notes.pdf",
  "original_file_name": "lesson_notes.pdf",
  "status": "READY",
  "created_at": "2025-05-19T05:30:00Z"
}
```

## Files Modified
- `app/routers/notes.py` - Fixed upload endpoint (lines 397-509)

## Commit
```
Fix file upload endpoint method call and make async
- Changed FileManager.save_file() to FileManager.save_upload_file()
- Made endpoint async to support await
- Reordered to create note_id before file upload
```

## Next Steps
1. Test file upload locally with a sample PDF
2. Deploy to Render
3. Test complete workflow end-to-end on production
