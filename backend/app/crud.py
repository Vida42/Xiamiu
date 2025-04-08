from sqlalchemy.orm import Session
from . import models
from . import schemas


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
    return genre.artists[skip:skip+limit]

def get_albums_by_genre(db: Session, genre_id: int, skip: int = 0, limit: int = 100):
    # Get the genre
    genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
    if not genre:
        return []
    
    # Return albums associated with this genre through the many-to-many relationship
    return genre.albums[skip:skip+limit]


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
    db_artist = models.Artist(artist_id=artist.artist_id, name=artist.name, reign=artist.reign)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

def get_artists_by_reign(db: Session, reign: str, skip: int = 0, limit: int = 100):
    return db.query(models.Artist).filter(models.Artist.reign == reign).offset(skip).limit(limit).all()


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
        star=album.star,
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
    return db.query(models.Song).filter(models.Song.album_id == album_id).offset(skip).limit(limit).all()

def create_song(db: Session, song: schemas.SongCreate):
    db_song = models.Song(
        song_id=song.song_id,
        name=song.name,
        star=song.star,
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
    db_user = models.User(
        user_name=user.user_name,
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


# Comment operations
def create_song_comment(db: Session, comment: schemas.SongCommentCreate):
    db_comment = models.SongComment(
        song_id=comment.song_id,
        comment=comment.comment,
        num_like=comment.num_like,
        review_date=comment.review_date,
        user_id=comment.user_id
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
        review_date=comment.review_date,
        user_id=comment.user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_artist_comments(db: Session, artist_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.ArtistComment).filter(
        models.ArtistComment.artist_id == artist_id).offset(skip).limit(limit).all()

def create_album_comment(db: Session, comment: schemas.AlbumCommentCreate):
    db_comment = models.AlbumComment(
        album_id=comment.album_id,
        comment=comment.comment,
        num_like=comment.num_like,
        review_date=comment.review_date,
        user_id=comment.user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_album_comments(db: Session, album_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.AlbumComment).filter(
        models.AlbumComment.album_id == album_id).offset(skip).limit(limit).all()


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