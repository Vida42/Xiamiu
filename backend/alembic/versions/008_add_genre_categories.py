"""add genre categories

Revision ID: 008
Revises: 007
Create Date: 2026-05-28 00:00:00.000000

Xiami style URLs encode two distinct ID spaces:
- style/<id> is the child genre ID
- ?<id> is the parent category ID

Those IDs can collide numerically, so parent categories need their own table
instead of a self-referencing genres.parent_id column.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'genre_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('info', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_genre_categories_name'), 'genre_categories', ['name'], unique=False)

    op.alter_column(
        'genres',
        'name',
        existing_type=sa.String(length=50),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
    op.add_column('genres', sa.Column('category_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_genres_category_id'), 'genres', ['category_id'], unique=False)
    op.create_foreign_key(
        'fk_genres_category_id_genre_categories',
        'genres',
        'genre_categories',
        ['category_id'],
        ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_genres_category_id_genre_categories', 'genres', type_='foreignkey')
    op.drop_index(op.f('ix_genres_category_id'), table_name='genres')
    op.drop_column('genres', 'category_id')
    op.alter_column(
        'genres',
        'name',
        existing_type=sa.String(length=100),
        type_=sa.String(length=50),
        existing_nullable=False,
    )

    op.drop_index(op.f('ix_genre_categories_name'), table_name='genre_categories')
    op.drop_table('genre_categories')
