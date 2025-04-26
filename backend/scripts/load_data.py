# scripts/load_seed_data.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import insert

# Find the .env file - It should be in the backend directory
script_path = Path(__file__)
backend_dir = script_path.parent.parent  # Go up two levels: scripts/ -> backend/
env_path = backend_dir / '.env'

# Load the environment variables
load_dotenv(dotenv_path=env_path)

# Now import the database connection and other modules
from ..app.database import SessionLocal
from ..app.models import (  # adjust based on your actual model locations
    User, Genre, Artist, Album, Song,
    ArtistMeta, AlbumMeta, SongMeta,
    ArtistComment, AlbumComment, SongComment,
    artist_genre_link, album_genre_link, song_artist_link
)


def load_data():
    """Load data from seed_data.json into the database."""
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
            # Handle renamed field if data is from old format
            if 'reign' in artist and 'region' not in artist:
                artist['region'] = artist.pop('reign')
            obj = Artist(**artist)
            session.merge(obj)
        session.commit()

        # Step 3: Load Albums (depends on artists)
        print("Loading albums...")
        for album in data.get("albums", []):
            # Remove star field if it exists in data but not in model
            if 'star' in album:
                album.pop('star')
            obj = Album(**album)
            session.merge(obj)
        session.commit()

        # Step 4: Load Songs (depends on albums)
        print("Loading songs...")
        for song in data.get("songs", []):
            # Handle renamed field if data is from old format
            if 'star' in song and 'order' not in song:
                song['order'] = song.pop('star')
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

        # Step 7: Load Comments
        print("Loading comments...")
        for comment in data.get("song_comments", []):
            # Remove review_date field if it exists in data but not in model
            # and ensure star field exists
            if 'review_date' in comment:
                comment.pop('review_date')
            if 'star' not in comment:
                # Default value for star (1-5 range)
                comment['star'] = 3
            obj = SongComment(**comment)
            session.merge(obj)
        
        for comment in data.get("artist_comments", []):
            # Remove review_date field if it exists in data but not in model
            # and ensure star field exists
            if 'review_date' in comment:
                comment.pop('review_date')
            if 'star' not in comment:
                # Default middle value for artist star (1-100)
                comment['star'] = 50
            obj = ArtistComment(**comment)
            session.merge(obj)
        
        for comment in data.get("album_comments", []):
            # Remove review_date field if it exists in data but not in model
            # and ensure star field exists
            if 'review_date' in comment:
                comment.pop('review_date')
            if 'star' not in comment:
                # Default middle value for album star (1-100)
                comment['star'] = 50
            obj = AlbumComment(**comment)
            session.merge(obj)
        session.commit()

        # Step 8: Load Junction Tables
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
