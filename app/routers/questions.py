"""
Teacher question-review router.

Auto-generated MCQs are created unapproved. A teacher (the note owner) reviews
them here - editing wording/options, approving the good ones, deleting the bad
ones - and only approved MCQs are then served to students. This is the single
biggest quality lever: a sighted human check before questions reach a blind
student.

Endpoints:
- GET    /api/v1/notes/{note_id}/questions   list all MCQs in a note for review
- POST   /api/v1/notes/{note_id}/questions   push generated MCQs for review
- PATCH  /api/v1/questions/{artefact_id}      edit question text/options/explanation
- POST   /api/v1/questions/{artefact_id}/approve   approve (or un-approve)
- DELETE /api/v1/questions/{artefact_id}      delete a bad question

Question generation itself happens on the teacher's phone (the offline
generator is the engine); the app pushes the results here right after a note
upload so the teacher can review them from any device and the approval gate
has something to guard.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

from .. import models
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/v1", tags=["questions"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class OptionModel(BaseModel):
    text: str
    is_correct: bool


class QuestionReviewItem(BaseModel):
    id: UUID
    unit_id: UUID
    question_text: str
    options: List[OptionModel]
    explanation: str = ""
    approved: bool


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[OptionModel]] = None
    explanation: Optional[str] = None


class ApproveRequest(BaseModel):
    approved: bool = True


class QuestionCreateItem(BaseModel):
    question_text: str
    options: List[OptionModel]
    explanation: str = ""


class QuestionBulkCreate(BaseModel):
    questions: List[QuestionCreateItem]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ensure_note_owner(note: models.LessonNote, user: models.User) -> None:
    """Only the note's teacher (or an admin) may review its questions."""
    if user.role == "admin":
        return
    if note.teacher_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not manage this lesson note.",
        )


def _artefact_with_note(artefact_id: UUID, db: Session):
    artefact = db.query(models.AiArtefact).filter(
        models.AiArtefact.id == artefact_id
    ).first()
    if not artefact:
        raise HTTPException(status_code=404, detail="Question not found")
    unit = db.query(models.LearningUnit).filter(
        models.LearningUnit.id == artefact.unit_id
    ).first()
    note = (
        db.query(models.LessonNote).filter(
            models.LessonNote.id == unit.note_id
        ).first()
        if unit else None
    )
    if not note:
        raise HTTPException(status_code=404, detail="Parent lesson note not found")
    return artefact, note


def _to_item(a: models.AiArtefact) -> QuestionReviewItem:
    c = a.content or {}
    return QuestionReviewItem(
        id=a.id,
        unit_id=a.unit_id,
        question_text=c.get("question_text", ""),
        options=[
            OptionModel(text=o.get("text", ""), is_correct=bool(o.get("is_correct")))
            for o in c.get("options", [])
        ],
        explanation=c.get("explanation", ""),
        approved=bool(a.approved),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/notes/{note_id}/questions", response_model=List[QuestionReviewItem])
def list_questions_for_review(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """All MCQs across a note's units, with their approval state, for review."""
    note = db.query(models.LessonNote).filter(
        models.LessonNote.id == note_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Lesson note not found")
    _ensure_note_owner(note, current_user)

    unit_ids = [
        u.id for u in db.query(models.LearningUnit).filter(
            models.LearningUnit.note_id == note_id
        ).all()
    ]
    if not unit_ids:
        return []

    artefacts = db.query(models.AiArtefact).filter(
        models.AiArtefact.unit_id.in_(unit_ids),
        models.AiArtefact.artefact_type == "MCQ",
    ).all()
    return [_to_item(a) for a in artefacts]


@router.post(
    "/notes/{note_id}/questions",
    response_model=List[QuestionReviewItem],
    status_code=status.HTTP_201_CREATED,
)
def push_questions_for_review(
    note_id: UUID,
    body: QuestionBulkCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Store app-generated MCQs as unapproved artefacts on a note.

    Idempotent-ish: a question whose text already exists on the note is
    skipped, so re-pushing after a flaky connection can't duplicate the
    review list. Notes created before units existed get their unit here.
    """
    note = db.query(models.LessonNote).filter(
        models.LessonNote.id == note_id,
        models.LessonNote.is_deleted == False,
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Lesson note not found")
    _ensure_note_owner(note, current_user)

    unit = (
        db.query(models.LearningUnit)
        .filter(models.LearningUnit.note_id == note_id)
        .order_by(models.LearningUnit.sequence_number)
        .first()
    )
    if unit is None:
        content = (note.description or note.title or "").strip()
        unit = models.LearningUnit(
            note_id=note_id,
            sequence_number=1,
            content_text=content or note.title,
        )
        db.add(unit)
        db.flush()

    existing_texts = {
        (a.content or {}).get("question_text", "").strip().lower()
        for a in db.query(models.AiArtefact).filter(
            models.AiArtefact.unit_id == unit.id,
            models.AiArtefact.artefact_type == "MCQ",
        ).all()
    }

    created: List[models.AiArtefact] = []
    for q in body.questions:
        text = q.question_text.strip()
        if not text or text.lower() in existing_texts:
            continue
        if len(q.options) < 2:
            continue
        artefact = models.AiArtefact(
            unit_id=unit.id,
            artefact_type="MCQ",
            content={
                "question_text": text,
                "options": [
                    {"text": o.text, "is_correct": o.is_correct}
                    for o in q.options
                ],
                "explanation": q.explanation,
            },
            approved=False,  # the teacher approves in the review screen
        )
        db.add(artefact)
        created.append(artefact)
        existing_texts.add(text.lower())

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save questions: {e}")
    for a in created:
        db.refresh(a)
    return [_to_item(a) for a in created]


@router.patch("/questions/{artefact_id}", response_model=QuestionReviewItem)
def update_question(
    artefact_id: UUID,
    body: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Edit a question's wording, options, or explanation."""
    artefact, note = _artefact_with_note(artefact_id, db)
    _ensure_note_owner(note, current_user)

    content = dict(artefact.content or {})
    if body.question_text is not None:
        content["question_text"] = body.question_text
    if body.explanation is not None:
        content["explanation"] = body.explanation
    if body.options is not None:
        content["options"] = [
            {"text": o.text, "is_correct": o.is_correct} for o in body.options
        ]
    artefact.content = content  # reassign so SQLAlchemy marks the JSON dirty

    try:
        db.commit()
        db.refresh(artefact)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update: {e}")
    return _to_item(artefact)


@router.post("/questions/{artefact_id}/approve", response_model=QuestionReviewItem)
def approve_question(
    artefact_id: UUID,
    body: ApproveRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Approve (default) or un-approve a question for student delivery."""
    artefact, note = _artefact_with_note(artefact_id, db)
    _ensure_note_owner(note, current_user)

    artefact.approved = bool(body.approved)
    try:
        db.commit()
        db.refresh(artefact)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to approve: {e}")
    return _to_item(artefact)


@router.delete("/questions/{artefact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    artefact_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a bad question entirely."""
    artefact, note = _artefact_with_note(artefact_id, db)
    _ensure_note_owner(note, current_user)
    db.delete(artefact)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")
    return None
