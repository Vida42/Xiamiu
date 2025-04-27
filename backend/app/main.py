import os
from dotenv import load_dotenv
from enum import Enum
from fastapi import FastAPI, Depends, HTTPException, Query, status, Security
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import crud
from . import schemas
from . import models
from .database import get_db
from .utils import convert_datetime_to_iso8601, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import JWTError, jwt
from .utils import SECRET_KEY, ALGORITHM

# Load environment variables
load_dotenv()


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI(title="Xiamiu API", description="Music database API for Xiamiu project")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from the Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Set up OAuth2 with Password Flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_name(db, user_name=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Xiamiu API"}


# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


@app.get("/users/{user_id}/comments/songs", response_model=List[schemas.SongComment])
def read_user_song_comments(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = crud.get_user_song_comments(db, user_id=user_id, skip=skip, limit=limit)
    return comments


@app.get("/users/{user_id}/comments/artists", response_model=List[schemas.ArtistComment])
def read_user_artist_comments(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = crud.get_user_artist_comments(db, user_id=user_id, skip=skip, limit=limit)
    return comments


@app.get("/users/{user_id}/comments/albums", response_model=List[schemas.AlbumComment])
def read_user_album_comments(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = crud.get_user_album_comments(db, user_id=user_id, skip=skip, limit=limit)
    return comments


# Search endpoint (similar to Django's SearchView)
@app.get("/search/", response_model=schemas.SearchResponse)
def search(query: str = Query(..., description="Search query"), db: Session = Depends(get_db)):
    result = crud.search_all(db, query)
    return result


# Genre endpoints
@app.post("/genres/", response_model=schemas.Genre)
def create_genre(genre: schemas.GenreCreate, db: Session = Depends(get_db)):
    db_genre = crud.get_genre_by_name(db, name=genre.name)
    if db_genre:
        raise HTTPException(status_code=400, detail="Genre already registered")
    return crud.create_genre(db=db, genre=genre)


@app.get("/genres/", response_model=List[schemas.Genre])
def read_genres(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    genres = crud.get_genres(db, skip=skip, limit=limit)
    return genres


@app.get("/genres/{genre_id}", response_model=schemas.Genre)
def read_genre(genre_id: int, db: Session = Depends(get_db)):
    db_genre = crud.get_genre(db, genre_id=genre_id)
    if db_genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    return db_genre


@app.get("/genres/{genre_id}/artists", response_model=List[schemas.Artist])
def read_artists_by_genre(genre_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_genre = crud.get_genre(db, genre_id=genre_id)
    if db_genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    artists = crud.get_artists_by_genre(db, genre_id=genre_id, skip=skip, limit=limit)
    return artists


@app.get("/genres/{genre_id}/albums", response_model=List[schemas.Album])
def read_albums_by_genre(genre_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_genre = crud.get_genre(db, genre_id=genre_id)
    if db_genre is None:
        raise HTTPException(status_code=404, detail="Genre not found")
    albums = crud.get_albums_by_genre(db, genre_id=genre_id, skip=skip, limit=limit)
    return albums


# Artist endpoints
@app.post("/artists/", response_model=schemas.Artist)
def create_artist(artist: schemas.ArtistCreate, db: Session = Depends(get_db)):
    db_artist = crud.get_artist(db, artist_id=artist.artist_id)
    if db_artist:
        raise HTTPException(status_code=400, detail="Artist ID already registered")
    return crud.create_artist(db=db, artist=artist)


@app.get("/artists/", response_model=List[schemas.Artist])
def read_artists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    artists = crud.get_artists(db, skip=skip, limit=limit)
    return artists


@app.get("/artists/region/{region}", response_model=List[schemas.Artist])
def read_artists_by_region(region: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    artists = crud.get_artists_by_region(db, region=region, skip=skip, limit=limit)
    return artists


@app.get("/artists/{artist_id}", response_model=schemas.Artist)
def read_artist(artist_id: str, db: Session = Depends(get_db)):
    db_artist = crud.get_artist(db, artist_id=artist_id)
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    return db_artist


@app.get("/artists/{artist_id}/albums", response_model=List[schemas.Album])
def read_artist_albums(artist_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_artist = crud.get_artist(db, artist_id=artist_id)
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    albums = crud.get_albums_by_artist(db, artist_id=artist_id, skip=skip, limit=limit)
    return albums


# Album endpoints
@app.post("/albums/", response_model=schemas.Album)
def create_album(album: schemas.AlbumCreate, db: Session = Depends(get_db)):
    db_album = crud.get_album(db, album_id=album.album_id)
    if db_album:
        raise HTTPException(status_code=400, detail="Album ID already registered")
    return crud.create_album(db=db, album=album)


@app.get("/albums/", response_model=List[schemas.Album])
def read_albums(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    albums = crud.get_albums(db, skip=skip, limit=limit)
    return albums


@app.get("/albums/language/{language}", response_model=List[schemas.Album])
def read_albums_by_language(language: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    albums = crud.get_albums_by_language(db, album_lan=language, skip=skip, limit=limit)
    return albums


@app.get("/albums/{album_id}", response_model=schemas.Album)
def read_album(album_id: str, db: Session = Depends(get_db)):
    db_album = crud.get_album(db, album_id=album_id)
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    return db_album


@app.get("/albums/{album_id}/songs", response_model=List[schemas.Song])
def read_album_songs(album_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_album = crud.get_album(db, album_id=album_id)
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    songs = crud.get_songs_by_album(db, album_id=album_id, skip=skip, limit=limit)
    return songs


# Song endpoints
@app.post("/songs/", response_model=schemas.Song)
def create_song(song: schemas.SongCreate, db: Session = Depends(get_db)):
    db_song = crud.get_song(db, song_id=song.song_id)
    if db_song:
        raise HTTPException(status_code=400, detail="Song ID already registered")
    return crud.create_song(db=db, song=song)


@app.get("/songs/", response_model=List[schemas.Song])
def read_songs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    songs = crud.get_songs(db, skip=skip, limit=limit)
    return songs


@app.get("/songs/{song_id}", response_model=schemas.Song)
def read_song(song_id: str, db: Session = Depends(get_db)):
    db_song = crud.get_song(db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    return db_song


# Meta endpoints
@app.post("/songs/{song_id}/meta", response_model=schemas.SongMeta)
def create_song_meta_info(song_id: str, meta: schemas.SongMetaCreate, db: Session = Depends(get_db)):
    db_song = crud.get_song(db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    db_meta = crud.get_song_meta(db, song_id=song_id)
    if db_meta:
        raise HTTPException(status_code=400, detail="Song meta already exists")
    meta.song_id = song_id
    return crud.create_song_meta(db=db, meta=meta)


@app.get("/songs/{song_id}/meta", response_model=schemas.SongMeta)
def read_song_meta(song_id: str, db: Session = Depends(get_db)):
    db_meta = crud.get_song_meta(db, song_id=song_id)
    if db_meta is None:
        raise HTTPException(status_code=404, detail="Song meta not found")
    return db_meta


@app.post("/artists/{artist_id}/meta", response_model=schemas.ArtistMeta)
def create_artist_meta_info(artist_id: str, meta: schemas.ArtistMetaCreate, db: Session = Depends(get_db)):
    db_artist = crud.get_artist(db, artist_id=artist_id)
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    db_meta = crud.get_artist_meta(db, artist_id=artist_id)
    if db_meta:
        raise HTTPException(status_code=400, detail="Artist meta already exists")
    meta.artist_id = artist_id
    return crud.create_artist_meta(db=db, meta=meta)


@app.get("/artists/{artist_id}/meta", response_model=schemas.ArtistMeta)
def read_artist_meta(artist_id: str, db: Session = Depends(get_db)):
    db_meta = crud.get_artist_meta(db, artist_id=artist_id)
    if db_meta is None:
        raise HTTPException(status_code=404, detail="Artist meta not found")
    return db_meta


@app.post("/albums/{album_id}/meta", response_model=schemas.AlbumMeta)
def create_album_meta_info(album_id: str, meta: schemas.AlbumMetaCreate, db: Session = Depends(get_db)):
    db_album = crud.get_album(db, album_id=album_id)
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    db_meta = crud.get_album_meta(db, album_id=album_id)
    if db_meta:
        raise HTTPException(status_code=400, detail="Album meta already exists")
    meta.album_id = album_id
    return crud.create_album_meta(db=db, meta=meta)


@app.get("/albums/{album_id}/meta", response_model=schemas.AlbumMeta)
def read_album_meta(album_id: str, db: Session = Depends(get_db)):
    db_meta = crud.get_album_meta(db, album_id=album_id)
    if db_meta is None:
        raise HTTPException(status_code=404, detail="Album meta not found")
    return db_meta


# User endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, user_name=user.user_name)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Comment endpoints
@app.post("/songs/{song_id}/comments", response_model=schemas.SongComment)
def create_comment_for_song(song_id: str, comment: schemas.SongCommentCreate, db: Session = Depends(get_db)):
    db_song = crud.get_song(db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    comment.song_id = song_id
    created_comment = crud.create_song_comment(db=db, comment=comment)
    
    # Convert datetime fields to strings
    created_comment.created = convert_datetime_to_iso8601(created_comment.created)
    created_comment.modified = convert_datetime_to_iso8601(created_comment.modified)
    
    return created_comment


@app.get("/songs/{song_id}/comments", response_model=List[schemas.SongComment])
def read_comments_for_song(song_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_song = crud.get_song(db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    comments = crud.get_song_comments(db, song_id=song_id, skip=skip, limit=limit)
    
    # Convert datetime fields to strings
    for comment in comments:
        comment.created = convert_datetime_to_iso8601(comment.created)
        comment.modified = convert_datetime_to_iso8601(comment.modified)
    
    return comments


@app.post("/artists/{artist_id}/comments", response_model=schemas.ArtistComment)
def create_comment_for_artist(artist_id: str, comment: schemas.ArtistCommentCreate, db: Session = Depends(get_db)):
    db_artist = crud.get_artist(db, artist_id=artist_id)
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    comment.artist_id = artist_id
    created_comment = crud.create_artist_comment(db=db, comment=comment)
    
    # Convert datetime fields to strings
    created_comment.created = convert_datetime_to_iso8601(created_comment.created)
    created_comment.modified = convert_datetime_to_iso8601(created_comment.modified)
    
    return created_comment


@app.get("/artists/{artist_id}/comments", response_model=List[schemas.ArtistComment])
def read_comments_for_artist(artist_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_artist = crud.get_artist(db, artist_id=artist_id)
    if db_artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    comments = crud.get_artist_comments(db, artist_id=artist_id, skip=skip, limit=limit)
    
    # Convert datetime fields to strings
    for comment in comments:
        comment.created = convert_datetime_to_iso8601(comment.created)
        comment.modified = convert_datetime_to_iso8601(comment.modified)
    
    return comments


@app.delete("/artists/comments/{comment_id}")
def delete_artist_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = db.query(models.ArtistComment).filter(models.ArtistComment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Delete the comment
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


@app.post("/albums/{album_id}/comments", response_model=schemas.AlbumComment)
def create_comment_for_album(album_id: str, comment: schemas.AlbumCommentCreate, db: Session = Depends(get_db)):
    db_album = crud.get_album(db, album_id=album_id)
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    comment.album_id = album_id
    created_comment = crud.create_album_comment(db=db, comment=comment)
    
    # Convert datetime fields to strings
    created_comment.created = convert_datetime_to_iso8601(created_comment.created)
    created_comment.modified = convert_datetime_to_iso8601(created_comment.modified)
    
    return created_comment


@app.get("/albums/{album_id}/comments", response_model=List[schemas.AlbumComment])
def read_comments_for_album(album_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_album = crud.get_album(db, album_id=album_id)
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    comments = crud.get_album_comments(db, album_id=album_id, skip=skip, limit=limit)
    
    # Convert datetime fields to strings
    for comment in comments:
        comment.created = convert_datetime_to_iso8601(comment.created)
        comment.modified = convert_datetime_to_iso8601(comment.modified)
    
    return comments


# Rating endpoints
@app.get("/songs/{song_id}/rating", response_model=schemas.SongRating)
def get_song_rating(song_id: str, db: Session = Depends(get_db)):
    """Get the average rating for a song."""
    db_song = crud.get_song(db, song_id=song_id)
    if db_song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    
    return crud.get_song_rating(db, song_id=song_id)


@app.get("/albums/{album_id}/rating", response_model=schemas.AlbumRating)
def get_album_rating(album_id: str, db: Session = Depends(get_db)):
    """Get the average rating for an album based on album comments."""
    db_album = crud.get_album(db, album_id=album_id)
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    
    return crud.get_album_rating(db, album_id=album_id)


@app.get("/albums/{album_id}/songs-rating", response_model=schemas.AlbumRating)
def get_album_songs_rating(album_id: str, db: Session = Depends(get_db)):
    """Get the average rating for an album based on its songs' ratings."""
    db_album = crud.get_album(db, album_id=album_id)
    if db_album is None:
        raise HTTPException(status_code=404, detail="Album not found")
    
    return crud.get_album_songs_avg_rating(db, album_id=album_id)


@app.delete("/songs/comments/{comment_id}")
def delete_song_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = db.query(models.SongComment).filter(models.SongComment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Delete the comment
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


@app.delete("/albums/comments/{comment_id}")
def delete_album_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = db.query(models.AlbumComment).filter(models.AlbumComment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Delete the comment
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}


# Add this at the end of the file for running the app directly
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)