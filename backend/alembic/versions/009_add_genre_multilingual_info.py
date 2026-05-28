"""add multilingual genre info fields

Revision ID: 009
Revises: 008
Create Date: 2026-05-28 00:30:00.000000

Keep the original mixed/source description in info, and add optional parsed
Chinese/English descriptions for UI display and future recommendation context.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('genre_categories', sa.Column('info_zh', sa.Text(), nullable=True))
    op.add_column('genre_categories', sa.Column('info_en', sa.Text(), nullable=True))
    op.add_column('genres', sa.Column('info_zh', sa.Text(), nullable=True))
    op.add_column('genres', sa.Column('info_en', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('genres', 'info_en')
    op.drop_column('genres', 'info_zh')
    op.drop_column('genre_categories', 'info_en')
    op.drop_column('genre_categories', 'info_zh')
