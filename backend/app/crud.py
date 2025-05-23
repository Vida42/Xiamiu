from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from . import schemas
from .utils import get_password_hash, verify_password
import math


# Genre operations
def get_genre(db: Session, genre_id: int):
    return db.query(models.Genre).filter(models.Genre.id == genre_id).first()


def get_genre_by_name(db: Session, name: str):
    return db.query(models.Genre).filter(models.Genre.name == name).first()


def get_genres(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Genre).offset(skip).limit(limit).all()


def create_genre(db: Session, genre: schemas.GenreCreate):
    db_genre = models.Genre(name=genre.name, info=genre.info)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre


def get_artists_by_genre(db: Session, genre_id: int, skip: int = 0, limit: int = 100):
    # Get the genre
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not genre:
        return []

    # Return artists associated with this genre through the many-to-many relationship
    return genre.artists[skip:skip + limit]


def get_albums_by_genre(db: Session, genre_id: int, skip: int = 0, limit: int = 100):
    # Get the genre
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not genre:
        return []

    # Return albums associated with this genre through the many-to-many relationship
    return genre.albums[skip:skip + limit]


# Artist operations
def get_artist(db: Session, artist_id: str):
    return db.query(models.Artist).filter(models.Artist.artist_id == artist_id).first()


def get_artist_by_name(db: Session, name: str):
    return db.query(models.Artist).filter(models.Artist.name == name).first()


def search_artists_by_name(db: Session, name_query: str, skip: int = 0, limit: int = 100):
    return db.query(models.Artist).filter(models.Artist.name.contains(name_query)).offset(skip).limit(limit).all()


def get_artists(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Artist).offset(skip).limit(limit).all()


def create_artist(db: Session, artist: schemas.ArtistCreate):
    db_artist = models.Artist(artist_id=artist.artist_id, name=artist.name, region=artist.region)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist


def get_artists_by_region(db: Session, region: str, skip: int = 0, limit: int = 100):
    return db.query(models.Artist).filter(models.Artist.region == region).offset(skip).limit(limit).all()


# Album operations
def get_album(db: Session, album_id: str):
    return db.query(models.Album).filter(models.Album.album_id == album_id).first()


def get_album_by_name(db: Session, name: str):
    return db.query(models.Album).filter(models.Album.name == name).first()


def search_albums_by_name(db: Session, name_query: str, skip: int = 0, limit: int = 100):
    return db.query(models.Album).filter(models.Album.name.contains(name_query)).offset(skip).limit(limit).all()


def get_albums(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Album).offset(skip).limit(limit).all()


def get_albums_by_artist(db: Session, artist_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Album).filter(models.Album.artist_id == artist_id).offset(skip).limit(limit).all()


def create_album(db: Session, album: schemas.AlbumCreate):
    db_album = models.Album(
        album_id=album.album_id,
        name=album.name,
        artist_id=album.artist_id,
        album_lan=album.album_lan,
        release_date=album.release_date,
        album_category=album.album_category,
        record_label=album.record_label,
        listen_date=album.listen_date
    )
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album


def get_albums_by_language(db: Session, album_lan: str, skip: int = 0, limit: int = 100):
    return db.query(models.Album).filter(models.Album.album_lan == album_lan).offset(skip).limit(limit).all()


# Song operations
def get_song(db: Session, song_id: str):
    return db.query(models.Song).filter(models.Song.song_id == song_id).first()


def get_song_by_name(db: Session, name: str):
    return db.query(models.Song).filter(models.Song.name == name).first()


def search_songs_by_name(db: Session, name_query: str, skip: int = 0, limit: int = 100):
    return db.query(models.Song).filter(models.Song.name.contains(name_query)).offset(skip).limit(limit).all()


def get_songs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Song).offset(skip).limit(limit).all()


def get_songs_by_album(db: Session, album_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Song).filter(models.Song.album_id == album_id).order_by(models.Song.order).offset(skip).limit(limit).all()


def create_song(db: Session, song: schemas.SongCreate):
    db_song = models.Song(
        song_id=song.song_id,
        name=song.name,
        order=song.order,
        album_id=song.album_id
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


# Meta operations
def get_song_meta(db: Session, song_id: str):
    return db.query(models.SongMeta).filter(models.SongMeta.song_id == song_id).first()


def create_song_meta(db: Session, meta: schemas.SongMetaCreate):
    db_meta = models.SongMeta(song_id=meta.song_id, lyrics=meta.lyrics)
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    return db_meta


def get_artist_meta(db: Session, artist_id: str):
    return db.query(models.ArtistMeta).filter(models.ArtistMeta.artist_id == artist_id).first()


def create_artist_meta(db: Session, meta: schemas.ArtistMetaCreate):
    db_meta = models.ArtistMeta(
        artist_id=meta.artist_id,
        info=meta.info,
        pic_address=meta.pic_address
    )
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    return db_meta


def get_album_meta(db: Session, album_id: str):
    return db.query(models.AlbumMeta).filter(models.AlbumMeta.album_id == album_id).first()


def create_album_meta(db: Session, meta: schemas.AlbumMetaCreate):
    db_meta = models.AlbumMeta(
        album_id=meta.album_id,
        info=meta.info,
        pic_address=meta.pic_address
    )
    db.add(db_meta)
    db.commit()
    db.refresh(db_meta)
    return db_meta


# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.user_name == user_name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        user_name=user.user_name,
        password=hashed_password,
        location=user.location,
        age=user.age,
        gender=user.gender,
        constellation=user.constellation,
        play_count=user.play_count,
        join_time=user.join_time
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_name(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_user_song_comments(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.SongComment).filter(models.SongComment.user_id == user_id).offset(skip).limit(limit).all()


def get_user_artist_comments(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.ArtistComment).filter(models.ArtistComment.user_id == user_id).offset(skip).limit(
        limit).all()


def get_user_album_comments(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.AlbumComment).filter(models.AlbumComment.user_id == user_id).offset(skip).limit(limit).all()


# Comment operations
def create_song_comment(db: Session, comment: schemas.SongCommentCreate):
    db_comment = models.SongComment(
        song_id=comment.song_id,
        comment=comment.comment,
        num_like=comment.num_like,
        user_id=comment.user_id,
        star=comment.star
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_song_comments(db: Session, song_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.SongComment).filter(models.SongComment.song_id == song_id).offset(skip).limit(limit).all()


def create_artist_comment(db: Session, comment: schemas.ArtistCommentCreate):
    db_comment = models.ArtistComment(
        artist_id=comment.artist_id,
        comment=comment.comment,
        num_like=comment.num_like,
        user_id=comment.user_id,
        star=comment.star
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_artist_comments(db: Session, artist_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.ArtistComment).filter(models.ArtistComment.artist_id == artist_id).offset(skip).limit(
        limit).all()


def create_album_comment(db: Session, comment: schemas.AlbumCommentCreate):
    db_comment = models.AlbumComment(
        album_id=comment.album_id,
        comment=comment.comment,
        num_like=comment.num_like,
        user_id=comment.user_id,
        star=comment.star
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_album_comments(db: Session, album_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AlbumComment).filter(models.AlbumComment.album_id == album_id).offset(skip).limit(
        limit).all()


# Search operations
def search_all(db: Session, query: str):
    artists = search_artists_by_name(db, query)
    albums = search_albums_by_name(db, query)
    songs = search_songs_by_name(db, query)

    return {
        "artists": artists,
        "albums": albums,
        "songs": songs
    }


# Rating operations
def get_song_rating(db: Session, song_id: str) -> schemas.SongRating:
    """Get the average rating and total number of ratings for a song."""
    result = db.query(
        func.avg(models.SongComment.star).label('average'),
        func.count(models.SongComment.star).label('count')
    ).filter(models.SongComment.song_id == song_id).first()

    if result and result.count > 0:
        average = round(result.average)  # Round to nearest integer
        count = result.count
    else:
        average = 0
        count = 0

    return schemas.SongRating(
        song_id=song_id,
        average_rating=average,
        total_ratings=count
    )


def get_album_rating(db: Session, album_id: str):
    """Calculate the average rating for an album."""
    result = db.query(
        func.avg(models.AlbumComment.star).label("average"),
        func.count(models.AlbumComment.id).label("count")
    ).filter(models.AlbumComment.album_id == album_id).first()
    
    average = 0.0
    count = 0
    stars = 0.0
    
    if result and result.count > 0:
        # Normalize average from 1-100 to 1-10 scale with one decimal place
        raw_avg = result.average
        normalized = round((raw_avg / 10), 1)
        average = normalized
        count = result.count
        
        # Calculate star representation (1-5 stars with half star precision)
        # 1 point = 0.5 stars, 10 points = 5 stars
        stars = round((normalized / 2), 1)
        
        # Ensure stars is a multiple of 0.5
        stars = round(stars * 2) / 2
    
    return {
        "album_id": album_id,
        "average_rating": average,
        "total_ratings": count,
        "stars": stars
    }


def get_album_songs_avg_rating(db: Session, album_id: str):
    """Calculate the average of song ratings for an album."""
    # Get all songs for this album
    songs = get_songs_by_album(db, album_id=album_id)
    song_ids = [song.song_id for song in songs]
    
    if not song_ids:
        return {
            "album_id": album_id,
            "average_rating": 0.0,
            "total_ratings": 0,
            "stars": 0.0
        }
    
    # Aggregate song ratings
    total_rating = 0
    total_count = 0
    
    for song_id in song_ids:
        song_rating = get_song_rating(db, song_id)
        if song_rating["total_ratings"] > 0:
            total_rating += song_rating["average_rating"]
            total_count += 1
    
    average = 0.0
    stars = 0.0
    
    if total_count > 0:
        # Calculate average (1-5 scale)
        average = total_rating / total_count
        # Convert to 1-10 scale
        average = round(average * 2, 1)
        # Calculate stars (1-5 scale with half star precision)
        stars = round(average / 2, 1)
        # Ensure stars is a multiple of 0.5
        stars = round(stars * 2) / 2
    
    return {
        "album_id": album_id,
        "average_rating": average,
        "total_ratings": total_count,
        "stars": stars
    }
