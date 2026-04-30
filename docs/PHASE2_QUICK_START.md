# Phase 2 Quick Start Guide

**Status:** ✅ Implementation Complete  
**Last Updated:** April 19, 2026

---

## 🚀 Getting Started (5 Minutes)

### Step 1: Activate Virtual Environment

```powershell
cd C:\Users\josep\OneDrive\Documents\Project\Backend
.\venv\Scripts\Activate.ps1
```

### Step 2: Update .env File

The `.env` file has been updated with Phase 2 configuration:

```bash
# Already configured:
UPLOAD_DIR=./uploads/notes
MAX_FILE_SIZE=26214400  # 25 MB
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

✅ **No changes needed** - just verify these values match your environment.

### Step 3: Download Required NLP Model

```powershell
# One-time setup (required for question generation)
python -m spacy download en_core_web_sm
```

This downloads the English language model for entity recognition (~50 MB, takes 1-2 minutes).

### Step 4: Start Redis Server

Choose one option:

**Option A: Docker** (Recommended)
```powershell
docker run --name visiolearn-redis -p 6379:6379 -d redis:7
```

**Option B: Windows (Chocolatey)**
```powershell
choco install redis-64
redis-server
```

**Option C: WSL**
```powershell
wsl apt-get install redis-server
redis-server
```

**Verify Redis is running:**
```powershell
redis-cli ping
# Should output: PONG
```

### Step 5: Start the Backend

```powershell
cd C:\Users\josep\OneDrive\Documents\Project\Backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Step 6: Start Celery Worker (New Terminal)

```powershell
cd C:\Users\Josep\OneDrive\Documents\Project\Backend
.\venv\Scripts\Activate.ps1
celery -A app.worker worker --loglevel=info --queues process_notes
```

Expected output:
```
[*] Connected to redis://localhost:6379/0
[*] mingle: searching for executable celery script in /path/to/venv
[*] celery@HOSTNAME ready.
```

---

## 🧪 Test Phase 2 Features

### Via Interactive API (Easiest)

1. Open http://localhost:8000/docs in browser
2. Click **"Try it out"** on the POST `/api/v1/notes/upload` endpoint
3. Fill in:
   - **file**: Select a PDF, DOCX, or TXT file
   - **title**: "Test Lesson"
   - **subject**: "Biology"
   - **grade_level**: "Grade 10"
4. Click **"Execute"**
5. Expected: 201 Created response with note ID

### Via cURL

```bash
# Upload a lesson note
curl -X POST http://localhost:8000/api/v1/notes/upload \
  -F "file=@path/to/your/file.pdf" \
  -F "title=Biology 101" \
  -F "subject=Biology" \
  -F "grade_level=Grade 10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response will include note_id (e.g., "550e8400-e29b-41d4...")
```

### Check Processing Status

The note will appear immediately with `status: PENDING_PROCESSING`. After 10-30 seconds (depending on file size), check if processing is complete:

```bash
# Get note details
curl http://localhost:8000/api/v1/notes/550e8400-e29b-41d4... \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Look for:
# "status": "READY"  ← Processing complete!
```

### View Generated Questions & Summary

Once status is `READY`:

```bash
# Get learning units
curl http://localhost:8000/api/v1/notes/550e8400-e29b-41d4.../units \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get questions (artefacts)
curl http://localhost:8000/api/v1/notes/550e8400-e29b-41d4.../units/UNIT_ID/artefacts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response includes MCQ, short-answer, fill-blank questions + summary
```

---

## 📋 What Phase 2 Does

### Teachers Upload Content
1. Click "Upload Lesson" 
2. Select PDF, DOCX, or TXT file
3. System automatically:
   - ✅ Validates file (size, format, content)
   - ✅ Extracts text content
   - ✅ Splits into learning units
   - ✅ Generates questions (MCQ, short-answer, fill-blank)
   - ✅ Creates summary & key points
   - ✅ Stores everything in database

### Students Access Content (Phase 3)
1. View learning units
2. Answer generated questions
3. Get immediate feedback
4. Track progress
5. Ask follow-up questions (Free Ask mode - Phase 3)

---

## 🔍 Monitoring

### Check Celery Tasks

**Terminal with Celery running:**
```
[2026-04-19 12:05:30,123: INFO/MainProcess] Received task: 
  process_note_task[550e8400-e29b-41d4-a5a0-b3d3d3d3d3d3]
[2026-04-19 12:05:35,456: INFO/MainProcess] Task 550e8400... succeeded in 5.33s
```

### Check Database

```powershell
# Connect to PostgreSQL
psql -U postgres -d visiolearn

# Verify learning units created
SELECT COUNT(*) FROM learning_units;

# Verify questions generated
SELECT COUNT(*) FROM ai_artefacts WHERE artefact_type = 'MCQ';

# Check note status
SELECT id, title, status FROM lesson_notes ORDER BY created_at DESC;
```

### Check File Storage

```powershell
# List uploaded files
Get-ChildItem -Path ".\uploads\notes\" -Recurse

# Example structure:
# uploads\notes\550e8400-e29b-41d4\original_filename.pdf
```

---

## ⚠️ Troubleshooting

### Issue: "Cannot find package 'express'" or similar import error
**Solution:** Ensure all dependencies are installed
```powershell
pip install -r requirements.txt
```

### Issue: "redis.exceptions.ConnectionError"
**Solution:** Redis server not running
```powershell
# Check if Redis is running
redis-cli ping  # Should output: PONG

# If not running, start it:
docker run --name visiolearn-redis -p 6379:6379 -d redis:7
```

### Issue: "No such file or directory: uploads/notes"
**Solution:** Create uploads directory (created automatically on first upload, but you can pre-create)
```powershell
mkdir uploads\notes
```

### Issue: spaCy model not found ("en_core_web_sm")
**Solution:** Download the model
```powershell
python -m spacy download en_core_web_sm
```

### Issue: "413 Request Entity Too Large"
**Solution:** File exceeds 25 MB limit. Check `.env`:
```bash
MAX_FILE_SIZE=26214400  # Bytes (25 MB default)
# Increase if needed, but be cautious about server resources
```

### Issue: Task stays in "PENDING_PROCESSING" forever
**Solution:** Celery worker not running
```powershell
# Check running processes
Get-Process celery  # Should show worker process

# If missing, start worker in new terminal:
celery -A app.worker worker --loglevel=info --queues process_notes
```

---

## 📊 Performance Expectations

**For a typical 5-10 page document:**

| Operation | Time |
|-----------|------|
| File Upload | <1s |
| Text Extraction | 1-2s |
| Content Chunking | <1s |
| Question Generation | 3-5s |
| Summarization | 2-3s |
| Database Storage | 1-2s |
| **Total (async)** | **7-13s** |

Notes will appear with status `READY` within 10-30 seconds of upload (async processing doesn't block the UI).

---

## 🔐 Security Notes

✅ **Phase 2 includes:**
- File format validation (magic byte checking)
- File size limits (25 MB default)
- Path traversal prevention (UUID-based storage)
- Content-bound AI (questions only from lesson text)
- Role-based access control (teachers see own, students see assigned)
- Soft delete audit trail

⚠️ **Production Checklist:**
- [ ] Enable HTTPS only
- [ ] Set strong SECRET_KEY (generate: `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Restrict ALLOWED_ORIGINS to your domain
- [ ] Move uploads directory outside web root
- [ ] Setup database backups
- [ ] Monitor Celery worker health
- [ ] Setup Redis persistence

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `app/routers/notes.py` | API endpoints for lesson notes |
| `app/storage/file_manager.py` | File upload & validation |
| `app/processing/text_extractor.py` | Extract text from files |
| `app/processing/content_chunker.py` | Split content into units |
| `app/processing/question_generator.py` | Generate questions |
| `app/processing/summarizer.py` | Create summaries |
| `app/worker.py` | Celery configuration |
| `app/tasks/process_note.py` | Async processing task |
| `.env` | Configuration (updated) |
| `PHASE2_IMPLEMENTATION.md` | Comprehensive documentation |

---

## 🎯 Next Steps

### Immediate (This Session)
- [ ] Download spaCy model
- [ ] Start Redis server
- [ ] Start backend & Celery worker
- [ ] Test file upload via Swagger UI
- [ ] Verify processing completes successfully

### Short Term (This Week)
- [ ] Write integration tests
- [ ] Performance test with larger files
- [ ] Setup monitoring/alerting
- [ ] Document API for frontend team

### Medium Term (Phase 3)
- [ ] Add voice interaction endpoints
- [ ] Implement delta sync
- [ ] Build student progress tracking
- [ ] Add embeddings/vector search

---

## 💬 Support

**Questions?**
1. Check PHASE2_IMPLEMENTATION.md for detailed documentation
2. Review code comments in each module
3. Check logs in terminal running Celery worker
4. Query database directly to debug issues

**Report bugs:**
- Check if Redis is running
- Check if Celery worker is running
- Check .env configuration
- Review application logs for exceptions

---

*Phase 2 is complete and ready for testing!*
