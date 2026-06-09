"""Add class_id column to lesson_notes table

Revision ID: f5c1d9a2e1b3
Revises: 18610ce9ee70
Create Date: 2026-05-19 06:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f5c1d9a2e1b3'
down_revision: Union[str, Sequence[str], None] = '18610ce9ee70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add subject_id and class_id columns to lesson_notes table.

    subject_id was added to the model but never got a migration.
    class_id is new. Both are kept nullable because pre-class-system
    notes (uploaded before the class hierarchy existed) have no class context.
    """

    # Add subject_id column — was in the model but missing from all prior migrations
    op.add_column('lesson_notes', sa.Column('subject_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_lesson_notes_subject_id', 'lesson_notes', 'class_subjects', ['subject_id'], ['id'])
    op.create_index(op.f('ix_lesson_notes_subject_id'), 'lesson_notes', ['subject_id'], unique=False)

    # Add class_id column
    op.add_column('lesson_notes', sa.Column('class_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_lesson_notes_class_id', 'lesson_notes', 'classes', ['class_id'], ['id'])
    op.create_index(op.f('ix_lesson_notes_class_id'), 'lesson_notes', ['class_id'], unique=False)

    # NOTE: No data backfill — existing notes predated the class/subject system.
    # All new notes set both fields explicitly via the upload endpoint.


def downgrade() -> None:
    """Remove class_id and subject_id columns from lesson_notes table."""
    op.drop_index(op.f('ix_lesson_notes_class_id'), table_name='lesson_notes')
    op.drop_constraint('fk_lesson_notes_class_id', 'lesson_notes', type_='foreignkey')
    op.drop_column('lesson_notes', 'class_id')

    op.drop_index(op.f('ix_lesson_notes_subject_id'), table_name='lesson_notes')
    op.drop_constraint('fk_lesson_notes_subject_id', 'lesson_notes', type_='foreignkey')
    op.drop_column('lesson_notes', 'subject_id')
