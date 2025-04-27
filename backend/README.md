# Xiamiu FastAPI Backend

This is the FastAPI implementation of the Xiamiu music database API

## Getting Started

### Prerequisites

- Python 3.8+
- Virtual environment (optional but recommended)

### Installation

1. Clone the repository
2. Create and activate a virtual environment using python venv module:
   ```zsh
      python -m venv .venv
      source .venv/bin/activate
      # On Windows, use: venv\Scripts\activate
      deactivate
      rm -rf .venv
   ```
3. Install dependencies:
   ```zsh
   pip3 install -r requirements.txt
   ```

### Database Setup

#### Related command

under root folder

```zsh
# reset database and relaod data:
python3 -m backend.scripts.reset_db --reload
# Dump current state, reset, and reload:
python3 -m backend.scripts.reset_db --dump --reload
# Just dump the current database state:
python3 -m backend.scripts.dump_data
# For simpler cases where you just want to reset the database:
python3 -m backend.scripts.reset_db
# just reload data
python3 -m backend.scripts.load_data
```

in the backend directory:

```zsh
python3 reset_database.py --reload
```

in the scripts directory:

```zsh
python3 reset_db.py --reload
```

in the backend directory, create a user

```zsh
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "x",
    "password": "y",
    "location": "New York",
    "age": 10,
    "gender": "Male",
    "constellation": "Gemini",
    "play_count": 0
  }'

```

#### Migration management using alembic

under backend folder

```zsh
alembic revision --autogenerate -m "migration name" --rev-id=001
alembic upgrade head
```

`-m`, It runs a Python module as a script, so should give it a dotted import path

test upgrade:
```zsh
alembic upgrade 003
# or
alembic upgrade head  # Move to latest version
```

test downgrade:
```zsh
alembic downgrade 002
# or
alembic downgrade -1  # Move down one version
```

### Running the Application

Start the FastAPI server:

```zsh
uvicorn backend.main:app --reload
```

or

```zsh
python3 run.py
```

The API will be available at http://127.0.0.1:8000

### API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Features

- Search functionality for artists, albums, and songs
- CRUD operations for all entities (artists, albums, songs, genres)
- Support for metadata, user comments, and ratings
- RESTful API design with proper validation

## Project Structure

- `main.py`: API routes and endpoint definitions
- `models.py`: SQLAlchemy ORM models
- `schemas.py`: Pydantic models for request/response validation
- `database.py`: Database connection and session management
- `crud.py`: Database operations

## API Endpoints

### Search
- `GET /search/?query=<search_term>` - Search for artists, albums, and songs

### Artists
- `GET /artists/` - List all artists
- `GET /artists/{artist_id}` - Get a specific artist
- `POST /artists/` - Create a new artist
- `GET /artists/{artist_id}/albums` - Get all albums by an artist
- `GET /artists/{artist_id}/meta` - Get artist metadata
- `POST /artists/{artist_id}/meta` - Create artist metadata
- `GET /artists/{artist_id}/comments` - Get comments for an artist
- `POST /artists/{artist_id}/comments` - Add a comment to an artist

### Albums
- `GET /albums/` - List all albums
- `GET /albums/{album_id}` - Get a specific album
- `POST /albums/` - Create a new album
- `GET /albums/{album_id}/songs` - Get all songs in an album
- `GET /albums/{album_id}/meta` - Get album metadata
- `POST /albums/{album_id}/meta` - Create album metadata
- `GET /albums/{album_id}/comments` - Get comments for an album
- `POST /albums/{album_id}/comments` - Add a comment to an album

### Songs
- `GET /songs/` - List all songs
- `GET /songs/{song_id}` - Get a specific song
- `POST /songs/` - Create a new song
- `GET /songs/{song_id}/meta` - Get song metadata
- `POST /songs/{song_id}/meta` - Create song metadata
- `GET /songs/{song_id}/comments` - Get comments for a song
- `POST /songs/{song_id}/comments` - Add a comment to a song

### Genres
- `GET /genres/` - List all genres
- `GET /genres/{genre_id}` - Get a specific genre
- `POST /genres/` - Create a new genre

### Users
- `GET /users/` - List all users
- `GET /users/{user_id}` - Get a specific user
- `POST /users/` - Create a new user 
