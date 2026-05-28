"""add engagement columns to recommendation_items

Revision ID: 007
Revises: 006
Create Date: 2026-05-27 16:00:00.000000

Removes the last private_data/ runtime dependency from the serving code
(crud._load_catalog_index reading private_data/10_intermediate/catalog_indexes/album_by_id.json).

Adds three nullable int columns to recommendation_items:
- play_count
- collects
- recommends

After the columns exist, attempts to backfill from
private_data/10_intermediate/catalog_indexes/album_by_id.json IF that file is available at the
machine running the migration. On a fresh demo clone there are no rows to
backfill, so this is a no-op there.

"""
import json
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('recommendation_items', sa.Column('play_count', sa.Integer(), nullable=True))
    op.add_column('recommendation_items', sa.Column('collects', sa.Integer(), nullable=True))
    op.add_column('recommendation_items', sa.Column('recommends', sa.Integer(), nullable=True))

    # Best-effort backfill from the local catalog index if present.
    catalog_path = (
        Path(__file__).resolve().parents[3]
        / "private_data" / "10_intermediate" / "catalog_indexes" / "album_by_id.json"
    )
    if not catalog_path.exists():
        return  # fresh demo clone — no private_data, no rows to backfill

    with catalog_path.open("r", encoding="utf-8") as f:
        catalog = json.load(f)

    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, album_id FROM recommendation_items")).fetchall()
    for row_id, album_id in rows:
        entry = catalog.get(str(album_id))
        if not entry:
            continue
        bind.execute(
            sa.text(
                "UPDATE recommendation_items "
                "SET play_count = :pc, collects = :co, recommends = :re "
                "WHERE id = :id"
            ),
            {
                "pc": entry.get("playCount"),
                "co": entry.get("collects"),
                "re": entry.get("recommends"),
                "id": row_id,
            },
        )


def downgrade() -> None:
    op.drop_column('recommendation_items', 'recommends')
    op.drop_column('recommendation_items', 'collects')
    op.drop_column('recommendation_items', 'play_count')
