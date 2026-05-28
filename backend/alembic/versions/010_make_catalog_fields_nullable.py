"""make catalog fields nullable

Revision ID: 010
Revises: 009
Create Date: 2026-05-28 00:00:00.000000

The full catalog dump legitimately contains nulls for these fields:
genres.info (245/714), albums.release_date (77/53081), song_meta.lyrics
(25657/114629). Relax the NOT NULL constraints to match real data.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('genres', 'info', existing_type=sa.Text(), nullable=True)
    op.alter_column('albums', 'release_date', existing_type=sa.Date(), nullable=True)
    op.alter_column('song_meta', 'lyrics', existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    op.alter_column('song_meta', 'lyrics', existing_type=sa.Text(), nullable=False)
    op.alter_column('albums', 'release_date', existing_type=sa.Date(), nullable=False)
    op.alter_column('genres', 'info', existing_type=sa.Text(), nullable=False)
