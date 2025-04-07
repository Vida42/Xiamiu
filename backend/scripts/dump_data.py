import os
from pathlib import Path
from dotenv import load_dotenv
import json

# Find the .env file - It should be in the backend directory
script_path = Path(__file__)
backend_dir = script_path.parent.parent  # Go up two levels: scripts/ -> backend/
env_path = backend_dir / '.env'

# Load the environment variables
load_dotenv(dotenv_path=env_path)

# Now import the database connection and other modules
from ..app.database import SessionLocal
from ..app.models import (
    User, Genre, Artist, Album, Song,
    ArtistMeta, AlbumMeta, SongMeta,
    artist_genre_link, album_genre_link, song_artist_link
)
from sqlalchemy import select


def dump_data():
    """Dump all data from the database into seed_data.json"""
    print("Starting database dump process...")
    
    session = SessionLocal()
    try:
        data = {}
        
        # Dump Genres
        print("Dumping genres...")
        genres = session.query(Genre).all()
        data['genres'] = [
            {
                'id': genre.id,
                'name': genre.name,
                'info': genre.info
            } for genre in genres
        ]

        # Dump Artists
        print("Dumping artists...")
        artists = session.query(Artist).all()
        data['artists'] = [
            {
                'artist_id': artist.artist_id,
                'name': artist.name,
                'reign': artist.reign
            } for artist in artists
        ]

        # Dump Albums
        print("Dumping albums...")
        albums = session.query(Album).all()
        data['albums'] = [
            {
                'album_id': album.album_id,
                'name': album.name,
                'album_lan': album.album_lan,
                'release_date': str(album.release_date),
                'album_category': album.album_category,
                'record_label': album.record_label,
                'star': album.star,
                'listen_date': str(album.listen_date),
                'artist_id': album.artist_id
            } for album in albums
        ]

        # Dump Songs
        print("Dumping songs...")
        songs = session.query(Song).all()
        data['songs'] = [
            {
                'song_id': song.song_id,
                'name': song.name,
                'star': song.star,
                'album_id': song.album_id
            } for song in songs
        ]

        # Dump Users
        print("Dumping users...")
        users = session.query(User).all()
        data['users'] = [
            {
                'id': user.id,
                'user_name': user.user_name,
                'location': user.location,
                'age': user.age,
                'gender': user.gender,
                'constellation': user.constellation,
                'play_count': user.play_count,
                'join_time': str(user.join_time)
            } for user in users
        ]

        # Dump Metadata
        print("Dumping metadata...")
        artist_metas = session.query(ArtistMeta).all()
        data['artist_meta'] = [
            {
                'artist_id': meta.artist_id,
                'info': meta.info,
                'pic_address': meta.pic_address
            } for meta in artist_metas
        ]

        album_metas = session.query(AlbumMeta).all()
        data['album_meta'] = [
            {
                'album_id': meta.album_id,
                'info': meta.info,
                'pic_address': meta.pic_address
            } for meta in album_metas
        ]

        song_metas = session.query(SongMeta).all()
        data['song_meta'] = [
            {
                'song_id': meta.song_id,
                'lyrics': meta.lyrics
            } for meta in song_metas
        ]

        # Dump Junction Tables
        print("Dumping relationships...")
        artist_genres = session.execute(select(artist_genre_link)).all()
        data['artist_genre_link'] = [
            {
                'artist_id': link.artist_id,
                'genre_id': link.genre_id
            } for link in artist_genres
        ]

        album_genres = session.execute(select(album_genre_link)).all()
        data['album_genre_link'] = [
            {
                'album_id': link.album_id,
                'genre_id': link.genre_id
            } for link in album_genres
        ]

        song_artists = session.execute(select(song_artist_link)).all()
        data['song_artist_link'] = [
            {
                'song_id': link.song_id,
                'artist_id': link.artist_id
            } for link in song_artists
        ]

        # Write to file
        backup_dir = backend_dir / 'backup'
        backup_dir.mkdir(exist_ok=True)
        
        json_path = backup_dir / 'seed_data.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Database successfully dumped to {json_path}")
        return True

    except Exception as e:
        print(f"❌ Error dumping data: {e}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    dump_data()
