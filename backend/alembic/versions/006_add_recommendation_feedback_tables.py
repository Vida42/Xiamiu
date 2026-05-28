"""add recommendation feedback tables

Revision ID: 006
Revises: 005
Create Date: 2026-05-27 12:00:00.000000

Adds two tables for the Day 9 feedback loop:
- recommendation_quick_reactions: low-friction interested/skip/save per item
- recommendation_feedback: 1-5 star + song impression + recommendation advice

Both have UNIQUE(user_id, recommendation_item_id) so resubmits upsert in code.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'recommendation_quick_reactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_item_id', sa.Integer(), nullable=False),
        sa.Column('reaction', sa.String(length=16), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['recommendation_item_id'], ['recommendation_items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'recommendation_item_id', name='uq_quick_reaction_user_item'),
    )
    op.create_index(
        op.f('ix_recommendation_quick_reactions_user_id'),
        'recommendation_quick_reactions',
        ['user_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_recommendation_quick_reactions_recommendation_item_id'),
        'recommendation_quick_reactions',
        ['recommendation_item_id'],
        unique=False,
    )

    op.create_table(
        'recommendation_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_item_id', sa.Integer(), nullable=False),
        sa.Column('star', sa.Integer(), nullable=False),
        sa.Column('song_impression', sa.Text(), nullable=True),
        sa.Column('recommendation_advice', sa.Text(), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['recommendation_item_id'], ['recommendation_items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'recommendation_item_id', name='uq_feedback_user_item'),
    )
    op.create_index(
        op.f('ix_recommendation_feedback_user_id'),
        'recommendation_feedback',
        ['user_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_recommendation_feedback_recommendation_item_id'),
        'recommendation_feedback',
        ['recommendation_item_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_recommendation_feedback_recommendation_item_id'), table_name='recommendation_feedback')
    op.drop_index(op.f('ix_recommendation_feedback_user_id'), table_name='recommendation_feedback')
    op.drop_table('recommendation_feedback')

    op.drop_index(op.f('ix_recommendation_quick_reactions_recommendation_item_id'), table_name='recommendation_quick_reactions')
    op.drop_index(op.f('ix_recommendation_quick_reactions_user_id'), table_name='recommendation_quick_reactions')
    op.drop_table('recommendation_quick_reactions')
