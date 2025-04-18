"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-04-02 16:01:48.751419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artists',
    sa.Column('artist_id', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('reign', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('artist_id')
    )
    op.create_index(op.f('ix_artists_name'), 'artists', ['name'], unique=False)
    op.create_table('genres',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('info', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_genres_name'), 'genres', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=50), nullable=False),
    sa.Column('user_name', sa.String(length=50), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('gender', sa.String(length=50), nullable=False),
    sa.Column('constellation', sa.String(length=50), nullable=False),
    sa.Column('play_count', sa.Integer(), nullable=False),
    sa.Column('join_time', sa.Date(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('albums',
    sa.Column('album_id', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('artist_id', sa.String(length=20), nullable=False),
    sa.Column('album_lan', sa.String(length=10), nullable=False),
    sa.Column('release_date', sa.Date(), nullable=False),
    sa.Column('album_category', sa.String(length=20), nullable=False),
    sa.Column('record_label', sa.String(length=50), nullable=False),
    sa.Column('star', sa.Integer(), nullable=False),
    sa.Column('listen_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.artist_id'], ),
    sa.PrimaryKeyConstraint('album_id')
    )
    op.create_table('artist_comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.String(length=20), nullable=False),
    sa.Column('comment', sa.String(length=255), nullable=False),
    sa.Column('num_like', sa.Integer(), nullable=False),
    sa.Column('review_date', sa.Date(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.artist_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_genre_link',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('artist_id', sa.String(length=20), nullable=True),
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.artist_id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_meta',
    sa.Column('artist_id', sa.String(length=20), nullable=False),
    sa.Column('info', sa.Text(), nullable=False),
    sa.Column('pic_address', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.artist_id'], ),
    sa.PrimaryKeyConstraint('artist_id')
    )
    op.create_table('album_comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('album_id', sa.String(length=20), nullable=False),
    sa.Column('comment', sa.String(length=255), nullable=False),
    sa.Column('num_like', sa.Integer(), nullable=False),
    sa.Column('review_date', sa.Date(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['album_id'], ['albums.album_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('album_genre_link',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('album_id', sa.String(length=20), nullable=True),
    sa.Column('genre_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['album_id'], ['albums.album_id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('album_meta',
    sa.Column('album_id', sa.String(length=20), nullable=False),
    sa.Column('info', sa.Text(), nullable=False),
    sa.Column('pic_address', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['album_id'], ['albums.album_id'], ),
    sa.PrimaryKeyConstraint('album_id')
    )
    op.create_table('songs',
    sa.Column('song_id', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('star', sa.Integer(), nullable=False),
    sa.Column('album_id', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['album_id'], ['albums.album_id'], ),
    sa.PrimaryKeyConstraint('song_id')
    )
    op.create_table('song_artist_link',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('song_id', sa.String(length=20), nullable=True),
    sa.Column('artist_id', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.artist_id'], ),
    sa.ForeignKeyConstraint(['song_id'], ['songs.song_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('song_comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('song_id', sa.String(length=20), nullable=False),
    sa.Column('comment', sa.String(length=255), nullable=False),
    sa.Column('num_like', sa.Integer(), nullable=False),
    sa.Column('review_date', sa.Date(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('modified', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['song_id'], ['songs.song_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('song_meta',
    sa.Column('song_id', sa.String(length=20), nullable=False),
    sa.Column('lyrics', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['song_id'], ['songs.song_id'], ),
    sa.PrimaryKeyConstraint('song_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('song_meta')
    op.drop_table('song_comments')
    op.drop_table('song_artist_link')
    op.drop_table('songs')
    op.drop_table('album_meta')
    op.drop_table('album_genre_link')
    op.drop_table('album_comments')
    op.drop_table('artist_meta')
    op.drop_table('artist_genre_link')
    op.drop_table('artist_comments')
    op.drop_table('albums')
    op.drop_table('users')
    op.drop_index(op.f('ix_genres_name'), table_name='genres')
    op.drop_table('genres')
    op.drop_index(op.f('ix_artists_name'), table_name='artists')
    op.drop_table('artists')
    # ### end Alembic commands ###
