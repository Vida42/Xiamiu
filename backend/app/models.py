from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Text, Table, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import date, datetime

Base = declarative_base()

# Association Tables for Many-to-Many relationships
artist_genre_link = Table(
    'artist_genre_link',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('artist_id', ForeignKey('artists.artist_id')),
    Column('genre_id', ForeignKey('genres.id'))
)

album_genre_link = Table(
    'album_genre_link',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('album_id', ForeignKey('albums.album_id')),
    Column('genre_id', ForeignKey('genres.id'))
)

song_artist_link = Table(
    'song_artist_link',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('song_id', ForeignKey('songs.song_id')),
    Column('artist_id', ForeignKey('artists.artist_id'))
)


class BaseModel:
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modified: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GenreCategory(Base):
    __tablename__ = 'genre_categories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    info_zh: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    info_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    genres = relationship("Genre", back_populates="category")


class Genre(Base):
    __tablename__ = 'genres'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    info: Mapped[str] = mapped_column(Text)
    info_zh: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    info_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('genre_categories.id'), nullable=False, index=True)
    
    # Relationships
    category = relationship("GenreCategory", back_populates="genres")
    artists = relationship("Artist", secondary=artist_genre_link, back_populates="genres")
    albums = relationship("Album", secondary=album_genre_link, back_populates="genres")


class Artist(Base):
    __tablename__ = 'artists'
    artist_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    region: Mapped[str] = mapped_column(String(50))
    
    # Relationships
    genres = relationship("Genre", secondary=artist_genre_link, back_populates="artists")
    albums = relationship("Album", back_populates="artist")
    songs = relationship("Song", secondary=song_artist_link, back_populates="artists")
    meta = relationship("ArtistMeta", uselist=False, back_populates="artist")
    comments = relationship("ArtistComment", back_populates="artist")


class Album(Base):
    __tablename__ = 'albums'
    album_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    artist_id: Mapped[str] = mapped_column(String(20), ForeignKey('artists.artist_id'))
    album_lan: Mapped[str] = mapped_column(String(10))
    release_date: Mapped[date] = mapped_column(Date)
    album_category: Mapped[str] = mapped_column(String(20))
    record_label: Mapped[str] = mapped_column(String(50))
    listen_date: Mapped[date] = mapped_column(Date, nullable=True)
    
    # Relationships
    artist = relationship("Artist", back_populates="albums")
    genres = relationship("Genre", secondary=album_genre_link, back_populates="albums")
    songs = relationship("Song", back_populates="album")
    meta = relationship("AlbumMeta", uselist=False, back_populates="album")
    comments = relationship("AlbumComment", back_populates="album")


class Song(Base):
    __tablename__ = 'songs'
    song_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    order: Mapped[int] = mapped_column(Integer)
    album_id: Mapped[str] = mapped_column(String(20), ForeignKey('albums.album_id'))
    
    # Relationships
    album = relationship("Album", back_populates="songs")
    artists = relationship("Artist", secondary=song_artist_link, back_populates="songs")
    meta = relationship("SongMeta", uselist=False, back_populates="song")
    comments = relationship("SongComment", back_populates="song")


class SongMeta(Base):
    __tablename__ = 'song_meta'
    song_id: Mapped[str] = mapped_column(String(20), ForeignKey('songs.song_id'), primary_key=True)
    lyrics: Mapped[str] = mapped_column(Text)
    
    # Relationships
    song = relationship("Song", back_populates="meta")


class ArtistMeta(Base):
    __tablename__ = 'artist_meta'
    artist_id: Mapped[str] = mapped_column(String(20), ForeignKey('artists.artist_id'), primary_key=True)
    info: Mapped[str] = mapped_column(Text)
    pic_address: Mapped[str] = mapped_column(String(255))
    
    # Relationships
    artist = relationship("Artist", back_populates="meta")


class AlbumMeta(Base):
    __tablename__ = 'album_meta'
    album_id: Mapped[str] = mapped_column(String(20), ForeignKey('albums.album_id'), primary_key=True)
    info: Mapped[str] = mapped_column(Text)
    pic_address: Mapped[str] = mapped_column(String(255))
    
    # Relationships
    album = relationship("Album", back_populates="meta")


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(50))
    constellation: Mapped[str] = mapped_column(String(50))
    play_count: Mapped[int] = mapped_column(Integer)
    join_time: Mapped[date] = mapped_column(Date, default=date.today)
    
    # Relationships
    song_comments = relationship("SongComment", back_populates="user")
    artist_comments = relationship("ArtistComment", back_populates="user")
    album_comments = relationship("AlbumComment", back_populates="user")
    taste_profiles = relationship("TasteProfile", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")


class SongComment(Base, BaseModel):
    __tablename__ = 'song_comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    song_id: Mapped[str] = mapped_column(String(20), ForeignKey('songs.song_id'))
    comment: Mapped[str] = mapped_column(String(255))
    num_like: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    star: Mapped[int] = mapped_column(Integer)
    
    # Relationships
    song = relationship("Song", back_populates="comments")
    user = relationship("User", back_populates="song_comments")


class ArtistComment(Base, BaseModel):
    __tablename__ = 'artist_comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artist_id: Mapped[str] = mapped_column(String(20), ForeignKey('artists.artist_id'))
    comment: Mapped[str] = mapped_column(String(255))
    num_like: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    star: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    
    # Relationships
    artist = relationship("Artist", back_populates="comments")
    user = relationship("User", back_populates="artist_comments")


class AlbumComment(Base, BaseModel):
    __tablename__ = 'album_comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    album_id: Mapped[str] = mapped_column(String(20), ForeignKey('albums.album_id'))
    comment: Mapped[str] = mapped_column(String(255))
    num_like: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    star: Mapped[int] = mapped_column(Integer)

    # Relationships
    album = relationship("Album", back_populates="comments")
    user = relationship("User", back_populates="album_comments")


class TasteProfile(Base, BaseModel):
    __tablename__ = 'taste_profiles'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    profile_text: Mapped[str] = mapped_column(Text)
    inputs_hash: Mapped[str] = mapped_column(String(32), index=True)
    cache_key: Mapped[str] = mapped_column(String(32), index=True)
    model: Mapped[str] = mapped_column(String(64))
    prompt_version: Mapped[str] = mapped_column(String(16))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="taste_profiles")
    recommendations = relationship("Recommendation", back_populates="taste_profile")


class Recommendation(Base, BaseModel):
    __tablename__ = 'recommendations'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    taste_profile_id: Mapped[int] = mapped_column(Integer, ForeignKey('taste_profiles.id'), index=True)
    generation_method: Mapped[str] = mapped_column(String(32))
    embedding_model: Mapped[str] = mapped_column(String(64))
    judge_model: Mapped[str] = mapped_column(String(64))
    top_n: Mapped[int] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="recommendations")
    taste_profile = relationship("TasteProfile", back_populates="recommendations")
    items = relationship("RecommendationItem", back_populates="recommendation", cascade="all, delete-orphan")


class RecommendationItem(Base, BaseModel):
    __tablename__ = 'recommendation_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recommendation_id: Mapped[int] = mapped_column(Integer, ForeignKey('recommendations.id'), index=True)
    album_id: Mapped[str] = mapped_column(String(20), index=True)
    artist_name: Mapped[str] = mapped_column(String(255))
    album_name: Mapped[str] = mapped_column(String(255))
    rank: Mapped[int] = mapped_column(Integer)
    similarity_score: Mapped[float] = mapped_column(Float)
    fit_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nearest_neighbors_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    styles_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    judge_cache_key: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    play_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    collects: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    recommends: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    recommendation = relationship("Recommendation", back_populates="items")
    quick_reactions = relationship("RecommendationQuickReaction", back_populates="item", cascade="all, delete-orphan")
    feedback_entries = relationship("RecommendationFeedback", back_populates="item", cascade="all, delete-orphan")


class RecommendationQuickReaction(Base, BaseModel):
    __tablename__ = 'recommendation_quick_reactions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    recommendation_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('recommendation_items.id'), index=True)
    reaction: Mapped[str] = mapped_column(String(16))

    __table_args__ = (
        UniqueConstraint('user_id', 'recommendation_item_id', name='uq_quick_reaction_user_item'),
    )

    item = relationship("RecommendationItem", back_populates="quick_reactions")


class RecommendationFeedback(Base, BaseModel):
    __tablename__ = 'recommendation_feedback'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True)
    recommendation_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('recommendation_items.id'), index=True)
    star: Mapped[int] = mapped_column(Integer)
    song_impression: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendation_advice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'recommendation_item_id', name='uq_feedback_user_item'),
    )

    item = relationship("RecommendationItem", back_populates="feedback_entries")
