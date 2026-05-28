"""widen catalog varchar columns

Revision ID: 011
Revises: 010
Create Date: 2026-05-28 00:00:00.000000

Real catalog data exceeds the original varchar(50) limits:
- albums.record_label up to 81 chars ("... under exclusive license to ...")
- artists.name up to 100 chars (slash-joined collaboration credits)
Widen both to 255.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '011'
down_revision: Union[str, None] = '010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('albums', 'record_label',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=255),
                    existing_nullable=False)
    op.alter_column('artists', 'name',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=255),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('artists', 'name',
                    existing_type=sa.String(length=255),
                    type_=sa.String(length=50),
                    existing_nullable=False)
    op.alter_column('albums', 'record_label',
                    existing_type=sa.String(length=255),
                    type_=sa.String(length=50),
                    existing_nullable=False)