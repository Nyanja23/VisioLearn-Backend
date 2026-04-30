# Phase 1: Database Setup & Data Modeling

## Overview
Based on the PRD specification and Amendment A (Voice Interaction), we have set up the foundational database architecture for the VisioLearn backend. The application relies on `PostgreSQL 15+` for storage and uses `SQLAlchemy` as the primary Object Relational Mapper (ORM), alongside `Alembic` for schema migrations.

## What Was Completed
1.  **Environment Setup**: 
    - Initialized the Python virtual environment (`venv`).
    - Created `requirements.txt` with all dependencies including FastAPI, SQLAlchemy, Alembic, psycopg2-binary, and AI tooling (`spaCy`, `sentence-transformers`).
2.  **Database Connection Management**:
    - Created `app/database.py` with SQLAlchemy `create_engine` and `sessionmaker` bound to `DATABASE_URL`.
    - Setup `get_db` generator dependency for FastAPI injection.
3.  **Data Models Created** (in `app/models.py`):
    - **Core Schema (PRD v1.0)**:
        - `School`: Tracks schools utilizing the system.
        - `User`: Standardized user tracking for ADMIN, TEACHER, and STUDENT roles.
        - `RefreshToken`: For secure mobile API sessions.
        - `LessonNote`: Stores metadata for teacher-uploaded files (`.txt`, `.pdf`, `.docx`).
        - `LearningUnit`: Note chunks for offline transfer.
        - `AiArtefact`: Stores generated questions/summaries (`MCQ`, `SHORT_ANSWER`, `SUMMARY`).
        - `StudentProgress`: Tracks offline interactions.
        - `NoteAssignment`: Links notes to target grade groups or students.
        - `AnalyticsEvent`: For tracking research outcomes.
    - **Voice Interaction Schema (Amendment A)**:
        - `VoiceSession`: Tracks an active audio interaction loop linking a student to a lesson note.
        - `VoiceInteraction`: Logs all raw voice inputs and NLU intent mapping.
        - `FreeAskExchange`: Stores explicit RAG question-and-answer tracking for research review.
4.  **Alembic Migration System**:
    - Standard `alembic init alembic` run.
    - Patched `alembic/env.py` to auto-import our SQLAlchemy `Base` metadata and load environment variables for the database string automatically.

## Required Next Steps for Developer (You)
Before continuing to Phase 2, ensure you have a running PostgreSQL database.

1.  **Start PostgreSQL**: Either locally or using Docker:
    ```bash
    docker run --name visiolearn-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=visiolearn -p 5432:5432 -d postgres:15
    ```
2.  **Generate Migration**: 
    ```bash
    .\venv\Scripts\alembic revision --autogenerate -m "Initial schema"
    ```
3.  **Apply Migration**:
    ```bash
    .\venv\Scripts\alembic upgrade head
    ```

Once your database is fully set up, we can proceed to **Phase 2: Authentication & Role-Based Access Control (RBAC)**.