from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Text, Table, DateTime
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


class Genre(Base):
    __tablename__ = 'genres'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    info: Mapped[str] = mapped_column(Text)
    
    # Relationships
    artists = relationship("Artist", secondary=artist_genre_link, back_populates="genres")
    albums = relationship("Album", secondary=album_genre_link, back_populates="genres")


class Artist(Base):
    __tablename__ = 'artists'
    artist_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    reign: Mapped[str] = mapped_column(String(50))
    
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
    star: Mapped[int] = mapped_column(Integer)
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
    star: Mapped[int] = mapped_column(Integer)
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
    location: Mapped[str] = mapped_column(String(50))
    user_name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(50))
    constellation: Mapped[str] = mapped_column(String(50))
    play_count: Mapped[int] = mapped_column(Integer)
    join_time: Mapped[date] = mapped_column(Date, default=date.today)
    
    # Relationships
    song_comments = relationship("SongComment", back_populates="user")
    artist_comments = relationship("ArtistComment", back_populates="user")
    album_comments = relationship("AlbumComment", back_populates="user")


class SongComment(Base, BaseModel):
    __tablename__ = 'song_comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    song_id: Mapped[str] = mapped_column(String(20), ForeignKey('songs.song_id'))
    comment: Mapped[str] = mapped_column(String(255))
    num_like: Mapped[int] = mapped_column(Integer, default=0)
    review_date: Mapped[date] = mapped_column(Date, default=date.today)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    
    # Relationships
    song = relationship("Song", back_populates="comments")
    user = relationship("User", back_populates="song_comments")


class ArtistComment(Base, BaseModel):
    __tablename__ = 'artist_comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artist_id: Mapped[str] = mapped_column(String(20), ForeignKey('artists.artist_id'))
    comment: Mapped[str] = mapped_column(String(255))
    num_like: Mapped[int] = mapped_column(Integer, default=0)
    review_date: Mapped[date] = mapped_column(Date, default=date.today)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    
    # Relationships
    artist = relationship("Artist", back_populates="comments")
    user = relationship("User", back_populates="artist_comments")


class AlbumComment(Base, BaseModel):
    __tablename__ = 'album_comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    album_id: Mapped[str] = mapped_column(String(20), ForeignKey('albums.album_id'))
    comment: Mapped[str] = mapped_column(String(255))
    num_like: Mapped[int] = mapped_column(Integer, default=0)
    review_date: Mapped[date] = mapped_column(Date, default=date.today)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    
    # Relationships
    album = relationship("Album", back_populates="comments")
    user = relationship("User", back_populates="album_comments")
