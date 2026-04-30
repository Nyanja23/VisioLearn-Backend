# Next Steps: Phase 3 - File Upload & Task Queuing

## Objective
The next phase will focus on implementing PRD Section 6.4 (Lesson Note Endpoints) and laying the foundation for PRD Section 7 (AI Processing Pipeline). When we resume, we will build the endpoints allowing teachers to upload `.pdf`, `.docx`, and `.txt` files, store those files securely, and drop a "process note" background job into a Celery task queue via Redis.

## Modules to Implement Next
1.  **File Storage Infrastructure**:
    - Update `app/main.py` and `app/routers/` to include a local file saving strategy (which acts as a stand-in for S3 blobs during the Pilot Phase).
2.  **Notes Routing (`app/routers/notes.py`)**:
    - Build `POST /api/v1/notes`: Accepts `UploadFile`, validates extensions, saves the file to disk, creates the `LessonNote` database record with `status: PENDING_PROCESSING`.
    - Secure this router so that only authenticated users with the `teacher` or `admin` role can upload.
3.  **Celery Worker Basics (`app/worker.py`)**:
    - Implement the asynchronous `Celery` application instance linking strictly to a local Redis broker (`redis://localhost:6379/0`).
    - Write the skeleton for the `process_note_task(note_id)` function that will eventually house the content-bound AI operations.

## Prerequisites for Next Session
Before we start Phase 3, you'll need the message broker running to utilize Celery efficiently:
- **Redis Server**: Make sure Redis is installed (either natively on Windows/WSL or via Docker: `docker run --name visiolearn-redis -p 6379:6379 -d redis:7`). 
- We will integrate it directly into `.env` upon continuation.
