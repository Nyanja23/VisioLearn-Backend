"""Core Celery task for processing lesson notes"""

import logging
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..worker import app
from ..database import SessionLocal
from .. import models
from ..processing import (
    extract_from_file,
    sanitize_text,
    chunk_text,
    generate_questions,
    generate_summary,
    generate_key_points
)
from ..storage import FileManager

logger = logging.getLogger(__name__)


@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    time_limit=1800,  # 30 minutes
    name='app.tasks.process_note.process_note_task'
)
def process_note_task(self, note_id: str):
    """
    Process lesson note: extract text, generate questions, summaries, chunks
    
    This is an async Celery task that:
    1. Retrieves the lesson note and file
    2. Extracts text from the file
    3. Chunks content into learning units
    4. Generates MCQ and short-answer questions
    5. Generates summary and key points
    6. Stores results in database
    7. Updates note status to READY
    
    Args:
        note_id: UUID of the LessonNote to process
    """
    db: Session = None
    try:
        db = SessionLocal()
        
        # Get the lesson note
        note = db.query(models.LessonNote).filter(
            models.LessonNote.id == note_id
        ).first()
        
        if not note:
            logger.error(f"Lesson note not found: {note_id}")
            raise ValueError(f"Lesson note not found: {note_id}")
        
        logger.info(f"Processing lesson note: {note.title} (ID: {note_id})")
        
        # Step 1: Extract text from file
        logger.info("Step 1: Extracting text from file...")
        file_path = FileManager.get_file_full_path(note.file_url)
        raw_text = extract_from_file(str(file_path))
        clean_text = sanitize_text(raw_text)
        
        logger.info(f"Extracted {len(clean_text)} characters")
        
        # Step 2: Chunk content into learning units
        logger.info("Step 2: Creating learning units from content...")
        chunks = chunk_text(clean_text, strategy="sentences", min_words_per_chunk=100)
        
        units = []
        for chunk in chunks:
            unit = models.LearningUnit(
                note_id=UUID(note_id),
                sequence_number=chunk.sequence_number,
                content_text=chunk.text
            )
            db.add(unit)
            units.append(unit)
        
        db.flush()  # Get unit IDs without committing
        logger.info(f"Created {len(units)} learning units")
        
        # Step 3: Generate questions and summaries for each unit
        logger.info("Step 3: Generating questions and summaries...")
        for unit in units:
            try:
                # Generate all question types
                questions_dict = generate_questions(
                    unit.content_text,
                    question_type="all",
                    num_mcq=3,
                    num_short_answer=2
                )
                
                # Store MCQ questions
                for mcq in questions_dict.get("mcq", []):
                    artefact = models.AiArtefact(
                        unit_id=unit.id,
                        artefact_type="MCQ",
                        content=mcq
                    )
                    db.add(artefact)
                
                # Store short answer questions
                for short_ans in questions_dict.get("short_answer", []):
                    artefact = models.AiArtefact(
                        unit_id=unit.id,
                        artefact_type="SHORT_ANSWER",
                        content=short_ans
                    )
                    db.add(artefact)
                
                # Generate and store summary
                summary_text = generate_summary(unit.content_text, summary_ratio=0.4)
                key_points = generate_key_points(unit.content_text, num_points=4)
                
                summary_content = {
                    "summary": summary_text,
                    "key_points": key_points
                }
                
                summary_artefact = models.AiArtefact(
                    unit_id=unit.id,
                    artefact_type="SUMMARY",
                    content=summary_content
                )
                db.add(summary_artefact)
                
                logger.info(f"Generated content for unit {unit.sequence_number}")
            
            except Exception as e:
                logger.error(f"Error processing unit {unit.sequence_number}: {str(e)}")
                # Continue with next unit
                continue
        
        # Step 4: Update note status to READY
        logger.info("Step 4: Finalizing...")
        note.status = "READY"
        note.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        logger.info(f"Successfully processed lesson note: {note.title}")
        
        return {
            "status": "success",
            "note_id": note_id,
            "units_created": len(units),
            "message": f"Processed {note.title} with {len(units)} learning units"
        }
    
    except Exception as exc:
        if db:
            db.rollback()
        
        logger.error(f"Error processing note {note_id}: {str(exc)}")
        
        # Update note status to ERROR
        try:
            db_note = db.query(models.LessonNote).filter(
                models.LessonNote.id == note_id
            ).first()
            if db_note:
                db_note.status = "ERROR"
                db_note.updated_at = datetime.now(timezone.utc)
                db.commit()
        except:
            pass
        
        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for note {note_id}")
            return {
                "status": "failed",
                "note_id": note_id,
                "error": str(exc),
                "retries_exceeded": True
            }
    
    finally:
        if db:
            db.close()


@app.task(name='app.tasks.process_note.check_stale_tasks')
def check_stale_tasks():
    """
    Check for notes stuck in PROCESSING status for too long
    
    This periodic task runs daily to find and potentially restart
    processing for notes that timed out.
    """
    db = SessionLocal()
    try:
        from datetime import timedelta
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=2)
        
        stale_notes = db.query(models.LessonNote).filter(
            models.LessonNote.status == "PROCESSING",
            models.LessonNote.updated_at < cutoff_time
        ).all()
        
        logger.info(f"Found {len(stale_notes)} stale processing tasks")
        
        for note in stale_notes:
            # Reset to PENDING so it can be reprocessed
            note.status = "PENDING_PROCESSING"
            db.add(note)
        
        if stale_notes:
            db.commit()
            logger.info(f"Reset {len(stale_notes)} stale tasks to PENDING_PROCESSING")
        
        return {"stale_tasks_found": len(stale_notes)}
    
    except Exception as e:
        logger.error(f"Error checking stale tasks: {str(e)}")
        return {"error": str(e)}
    
    finally:
        db.close()
