"""add recommendation tables

Revision ID: 005
Revises: 004
Create Date: 2026-05-26 21:00:00.000000

Adds three tables to persist AI recommendation pipeline output:
- taste_profiles: LLM-written English taste profiles (append-only audit log)
- recommendations: one row per generation run (links user + taste profile)
- recommendation_items: individual recommended albums with LLM judgment

Notes:
- album_id on recommendation_items is a plain String(20), NOT a FK to
  albums.album_id, because the catalog index has 53k albums but the albums
  table is currently a smaller subset. Denormalized artist_name / album_name
  are stored for fast display. FK can be added in a future migration when
  the full catalog is ingested.
- nearest_neighbors_json and styles_json are stored as Text (JSON-encoded)
  rather than normalized tables, to keep read path simple.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'taste_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('profile_text', sa.Text(), nullable=False),
        sa.Column('inputs_hash', sa.String(length=32), nullable=False),
        sa.Column('cache_key', sa.String(length=32), nullable=False),
        sa.Column('model', sa.String(length=64), nullable=False),
        sa.Column('prompt_version', sa.String(length=16), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False),
        sa.Column('output_tokens', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_taste_profiles_user_id'), 'taste_profiles', ['user_id'], unique=False)
    op.create_index(op.f('ix_taste_profiles_inputs_hash'), 'taste_profiles', ['inputs_hash'], unique=False)
    op.create_index(op.f('ix_taste_profiles_cache_key'), 'taste_profiles', ['cache_key'], unique=False)

    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('taste_profile_id', sa.Integer(), nullable=False),
        sa.Column('generation_method', sa.String(length=32), nullable=False),
        sa.Column('embedding_model', sa.String(length=64), nullable=False),
        sa.Column('judge_model', sa.String(length=64), nullable=False),
        sa.Column('top_n', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['taste_profile_id'], ['taste_profiles.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_recommendations_user_id'), 'recommendations', ['user_id'], unique=False)
    op.create_index(op.f('ix_recommendations_taste_profile_id'), 'recommendations', ['taste_profile_id'], unique=False)

    op.create_table(
        'recommendation_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=False),
        sa.Column('album_id', sa.String(length=20), nullable=False),
        sa.Column('artist_name', sa.String(length=255), nullable=False),
        sa.Column('album_name', sa.String(length=255), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('fit_score', sa.Float(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('risk', sa.Text(), nullable=True),
        sa.Column('nearest_neighbors_json', sa.Text(), nullable=True),
        sa.Column('styles_json', sa.Text(), nullable=True),
        sa.Column('judge_cache_key', sa.String(length=32), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_recommendation_items_recommendation_id'), 'recommendation_items', ['recommendation_id'], unique=False)
    op.create_index(op.f('ix_recommendation_items_album_id'), 'recommendation_items', ['album_id'], unique=False)
    op.create_index(op.f('ix_recommendation_items_judge_cache_key'), 'recommendation_items', ['judge_cache_key'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_recommendation_items_judge_cache_key'), table_name='recommendation_items')
    op.drop_index(op.f('ix_recommendation_items_album_id'), table_name='recommendation_items')
    op.drop_index(op.f('ix_recommendation_items_recommendation_id'), table_name='recommendation_items')
    op.drop_table('recommendation_items')

    op.drop_index(op.f('ix_recommendations_taste_profile_id'), table_name='recommendations')
    op.drop_index(op.f('ix_recommendations_user_id'), table_name='recommendations')
    op.drop_table('recommendations')

    op.drop_index(op.f('ix_taste_profiles_cache_key'), table_name='taste_profiles')
    op.drop_index(op.f('ix_taste_profiles_inputs_hash'), table_name='taste_profiles')
    op.drop_index(op.f('ix_taste_profiles_user_id'), table_name='taste_profiles')
    op.drop_table('taste_profiles')
