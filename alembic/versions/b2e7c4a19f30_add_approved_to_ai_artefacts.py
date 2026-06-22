"""add approved flag to ai_artefacts

Revision ID: b2e7c4a19f30
Revises: f5c1d9a2e1b3
Create Date: 2026-06-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = 'b2e7c4a19f30'
down_revision: Union[str, Sequence[str], None] = 'f5c1d9a2e1b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    # If the table does not exist yet (e.g. a fresh SQLite dev DB), create_all
    # will build it with the column already present - nothing to do here.
    if 'ai_artefacts' not in insp.get_table_names():
        return
    cols = [c['name'] for c in insp.get_columns('ai_artefacts')]
    if 'approved' not in cols:
        op.add_column(
            'ai_artefacts',
            sa.Column('approved', sa.Boolean(), nullable=False,
                      server_default=sa.false()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if 'ai_artefacts' not in insp.get_table_names():
        return
    cols = [c['name'] for c in insp.get_columns('ai_artefacts')]
    if 'approved' in cols:
        op.drop_column('ai_artefacts', 'approved')
