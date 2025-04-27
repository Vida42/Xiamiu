from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
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
    region: str


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
    order: int


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


class SongCommentBase(CommentBase):
    star: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    
    @validator('star')
    def validate_star_range(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Song star rating must be between 1 and 5')
        return v


class SongCommentCreate(SongCommentBase):
    song_id: str
    user_id: int


class SongComment(SongCommentBase):
    id: int
    song_id: str
    user_id: int
    created: str
    modified: str

    model_config = {
        "from_attributes": True
    }


class ArtistCommentBase(CommentBase):
    # Remove validation for artist comments (they don't have ratings)
    star: Optional[int] = None
    
    # Commented out validation rules since we don't require star rating for artist comments
    # star: int = Field(default=1, ge=1, le=100, description="Rating from 1 to 100")
    # 
    # @validator('star')
    # def validate_star_range(cls, v):
    #     if v < 1 or v > 100:
    #         raise ValueError('Artist star rating must be between 1 and 100')
    #     return v


class ArtistCommentCreate(ArtistCommentBase):
    artist_id: str
    user_id: int


class ArtistComment(ArtistCommentBase):
    id: int
    artist_id: str
    user_id: int
    created: str
    modified: str

    model_config = {
        "from_attributes": True
    }


class AlbumCommentBase(CommentBase):
    star: int = Field(..., ge=1, le=100, description="Rating from 1 to 100")
    
    @validator('star')
    def validate_star_range(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Album star rating must be between 1 and 100')
        return v


class AlbumCommentCreate(AlbumCommentBase):
    album_id: str
    user_id: int


class AlbumComment(AlbumCommentBase):
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


# Rating schemas
class SongRating(BaseModel):
    song_id: str
    average_rating: int = Field(description="Average rating rounded to the nearest integer (1-5)")
    total_ratings: int = Field(description="Total number of ratings")

    model_config = {
        "from_attributes": True
    }


class AlbumRating(BaseModel):
    album_id: str
    average_rating: float = Field(description="Average rating normalized to 1-10 scale with one decimal place")
    total_ratings: int = Field(description="Total number of ratings")
    stars: float = Field(description="Star representation (1-5 with 0.5 increments)")

    model_config = {
        "from_attributes": True
    }
