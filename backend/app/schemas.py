from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


# Genre schemas
class GenreBase(BaseModel):
    name: str
    info: str


class GenreCreate(GenreBase):
    pass


class Genre(GenreBase):
    id: int

    model_config = {
        "from_attributes": True
    }


# Artist schemas
class ArtistBase(BaseModel):
    name: str
    reign: str


class ArtistCreate(ArtistBase):
    artist_id: str


class Artist(ArtistBase):
    artist_id: str

    model_config = {
        "from_attributes": True
    }


# Album schemas
class AlbumBase(BaseModel):
    name: str
    album_lan: str
    release_date: date
    album_category: str
    record_label: str
    star: int
    listen_date: Optional[date] = None


class AlbumCreate(AlbumBase):
    album_id: str
    artist_id: str


class Album(AlbumBase):
    album_id: str
    artist_id: str

    model_config = {
        "from_attributes": True
    }


# Song schemas
class SongBase(BaseModel):
    name: str
    star: int


class SongCreate(SongBase):
    song_id: str
    album_id: str


class Song(SongBase):
    song_id: str
    album_id: str

    model_config = {
        "from_attributes": True
    }


# Meta schemas
class SongMetaBase(BaseModel):
    lyrics: str


class SongMetaCreate(SongMetaBase):
    song_id: str


class SongMeta(SongMetaBase):
    song_id: str

    model_config = {
        "from_attributes": True
    }


class ArtistMetaBase(BaseModel):
    info: str
    pic_address: str


class ArtistMetaCreate(ArtistMetaBase):
    artist_id: str


class ArtistMeta(ArtistMetaBase):
    artist_id: str

    model_config = {
        "from_attributes": True
    }


class AlbumMetaBase(BaseModel):
    info: str
    pic_address: str


class AlbumMetaCreate(AlbumMetaBase):
    album_id: str


class AlbumMeta(AlbumMetaBase):
    album_id: str

    model_config = {
        "from_attributes": True
    }


# User schema
class UserBase(BaseModel):
    user_name: str
    location: str
    age: int
    gender: str
    constellation: str
    play_count: int
    join_time: Optional[date] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    model_config = {
        "from_attributes": True
    }


# Comment schemas
class CommentBase(BaseModel):
    comment: str
    num_like: int = 0
    review_date: date = Field(default_factory=date.today)


class SongCommentCreate(CommentBase):
    song_id: str
    user_id: int


class SongComment(CommentBase):
    id: int
    song_id: str
    user_id: int
    created: str
    modified: str

    model_config = {
        "from_attributes": True
    }


class ArtistCommentCreate(CommentBase):
    artist_id: str
    user_id: int


class ArtistComment(CommentBase):
    id: int
    artist_id: str
    user_id: int
    created: str
    modified: str

    model_config = {
        "from_attributes": True
    }


class AlbumCommentCreate(CommentBase):
    album_id: str
    user_id: int


class AlbumComment(CommentBase):
    id: int
    album_id: str
    user_id: int
    created: str
    modified: str

    model_config = {
        "from_attributes": True
    }


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


# Search response schema
class SearchResponse(BaseModel):
    artists: List[Artist] = []
    albums: List[Album] = []
    songs: List[Song] = []
