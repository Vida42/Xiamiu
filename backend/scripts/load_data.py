# scripts/load_seed_data.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Find the .env file - It should be in the backend directory
script_path = Path(__file__)
backend_dir = script_path.parent.parent  # Go up two levels: scripts/ -> backend/
env_path = backend_dir / '.env'

# Load the environment variables
load_dotenv(dotenv_path=env_path)

# Now import the database connection and other modules
import json
from ..app.database import SessionLocal
from ..app.models import (  # adjust based on your actual model locations
    User, Genre, Artist, Album, Song,
    ArtistMeta, AlbumMeta, SongMeta,
    ArtistComment, AlbumComment, SongComment,
)

from ..app.models import artist_genre_link, album_genre_link, song_artist_link
from sqlalchemy import insert


def load_data():
    # Initialize database session
    session = SessionLocal()
    
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level and then to backup/seed_data.json
        json_path = os.path.join(script_dir, '..', 'backup', 'seed_data.json')

        # Load JSON data
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Step 1: Load Genres (they have no dependencies)
        print("Loading genres...")
        for genre in data.get("genres", []):
            obj = Genre(**genre)
            session.merge(obj)
        session.commit()

        # Step 2: Load Artists (they have no dependencies)
        print("Loading artists...")
        for artist in data.get("artists", []):
            obj = Artist(**artist)
            session.merge(obj)
        session.commit()

        # Step 3: Load Albums (depends on artists)
        print("Loading albums...")
        for album in data.get("albums", []):
            obj = Album(**album)
            session.merge(obj)
        session.commit()

        # Step 4: Load Songs (depends on albums)
        print("Loading songs...")
        for song in data.get("songs", []):
            obj = Song(**song)
            session.merge(obj)
        session.commit()

        # Step 5: Load Users
        print("Loading users...")
        for user in data.get("users", []):
            obj = User(**user)
            session.merge(obj)
        session.commit()

        # Step 6: Load Metadata (after their respective main tables)
        print("Loading metadata...")
        for artist_meta in data.get("artist_meta", []):
            obj = ArtistMeta(**artist_meta)
            session.merge(obj)
        
        for album_meta in data.get("album_meta", []):
            obj = AlbumMeta(**album_meta)
            session.merge(obj)
        
        for song_meta in data.get("song_meta", []):
            obj = SongMeta(**song_meta)
            session.merge(obj)
        session.commit()

        # Step 7: Load Junction Tables
        print("Loading artist-genre links...")
        for link in data.get("artist_genre_link", []):
            # Convert genre_id to integer if it's not already
            link["genre_id"] = int(link["genre_id"])
            session.execute(insert(artist_genre_link).values(link))
        session.commit()

        print("Loading album-genre links...")
        for link in data.get("album_genre_link", []):
            # Convert genre_id to integer if it's not already
            link["genre_id"] = int(link["genre_id"])
            session.execute(insert(album_genre_link).values(link))
        session.commit()

        print("Loading song-artist links...")
        for link in data.get("song_artist_link", []):
            session.execute(insert(song_artist_link).values(link))
        session.commit()

        print("✅ All data loaded successfully.")

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    load_data()
