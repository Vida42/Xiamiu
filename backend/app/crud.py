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
    db_genre = models.Genre(
        id=genre.id,
        name=genre.name,
        info=genre.info,
        info_zh=genre.info_zh,
        info_en=genre.info_en,
        category_id=genre.category_id,
    )
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
    pattern = f"%{name_query}%"
    prefix = f"{name_query}%"
    return (
        db.query(models.Artist)
        .filter(models.Artist.name.ilike(pattern))
        .order_by(
            models.Artist.name.ilike(prefix).desc(),
            models.Artist.name,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_artists(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Artist).offset(skip).limit(limit).all()


def create_artist(db: Session, artist: schemas.ArtistCreate):
    db_artist = models.Artist(
        artist_id=artist.artist_id,
        name=artist.name,
        region=artist.region,
        gender=artist.gender,
        play_count=artist.play_count,
        count_likes=artist.count_likes,
        recommends=artist.recommends,
        comment_count=artist.comment_count,
        alias=artist.alias,
        category_id=artist.category_id,
        pinyin=artist.pinyin,
    )
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist


ARTIST_REGION_ALIASES = {
    "China": ["China", "China 中国大陆", "中国大陆 China", "中国大陆"],
    "中国": ["中国", "China", "China 中国大陆", "中国大陆 China", "中国大陆"],
    "United States of America": ["United States of America", "United States of America 美国", "美国"],
    "United States": ["United States", "United States of America", "United States of America 美国", "美国"],
    "美国": ["美国", "United States of America", "United States of America 美国"],
    "United Kingdom": ["United Kingdom", "United Kingdom 英国", "英国"],
    "英国": ["英国", "United Kingdom", "United Kingdom 英国"],
    "Japan": ["Japan", "Japan 日本", "日本"],
    "日本": ["日本", "Japan", "Japan 日本"],
    "Korea": ["Korea", "Korea 韩国", "韩国"],
    "韩国": ["韩国", "Korea", "Korea 韩国"],
}


def get_artists_by_region(db: Session, region: str, skip: int = 0, limit: int = 100):
    region_values = ARTIST_REGION_ALIASES.get(region, [region])
    return (
        db.query(models.Artist)
        .filter(models.Artist.region.in_(region_values))
        .offset(skip)
        .limit(limit)
        .all()
    )


# Album operations
def get_album(db: Session, album_id: str):
    return db.query(models.Album).filter(models.Album.album_id == album_id).first()


def get_album_by_name(db: Session, name: str):
    return db.query(models.Album).filter(models.Album.name == name).first()


def search_albums_by_name(db: Session, name_query: str, skip: int = 0, limit: int = 100):
    pattern = f"%{name_query}%"
    prefix = f"{name_query}%"
    return (
        db.query(models.Album)
        .filter(models.Album.name.ilike(pattern))
        .order_by(
            models.Album.name.ilike(prefix).desc(),
            models.Album.release_date.desc().nullslast(),
            models.Album.name,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


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
        album_type=album.album_type,
        category_id=album.category_id,
        song_count=album.song_count,
        cd_count=album.cd_count,
        play_count=album.play_count,
        collects=album.collects,
        comment_count=album.comment_count,
        recommends=album.recommends,
        grade=album.grade,
        grade_count=album.grade_count,
        sub_name=album.sub_name,
        pinyin=album.pinyin,
        company_id=album.company_id,
    )
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return db_album


ALBUM_LANGUAGE_ALIASES = {
    "Mandarin": ["Mandarin", "国语", "华语"],
    "Chinese": ["Chinese", "国语", "华语"],
    "English": ["English", "英语", "欧美"],
    "Western": ["Western", "English", "英语", "欧美"],
    "Japanese": ["Japanese", "日语"],
    "Korean": ["Korean", "韩语"],
    "国语": ["国语", "Mandarin", "Chinese"],
    "华语": ["华语", "国语", "Mandarin", "Chinese"],
    "英语": ["英语", "English", "Western"],
    "欧美": ["欧美", "English", "Western"],
    "日语": ["日语", "Japanese"],
    "韩语": ["韩语", "Korean"],
}


def get_albums_by_language(db: Session, album_lan: str, skip: int = 0, limit: int = 100):
    language_values = ALBUM_LANGUAGE_ALIASES.get(album_lan, [album_lan])
    return (
        db.query(models.Album)
        .filter(models.Album.album_lan.in_(language_values))
        .offset(skip)
        .limit(limit)
        .all()
    )


# Song operations
def get_song(db: Session, song_id: str):
    return db.query(models.Song).filter(models.Song.song_id == song_id).first()


def get_song_by_name(db: Session, name: str):
    return db.query(models.Song).filter(models.Song.name == name).first()


def search_songs_by_name(db: Session, name_query: str, skip: int = 0, limit: int = 100):
    pattern = f"%{name_query}%"
    prefix = f"{name_query}%"
    return (
        db.query(models.Song)
        .filter(models.Song.name.ilike(pattern))
        .order_by(
            models.Song.name.ilike(prefix).desc(),
            models.Song.name,
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_songs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Song).offset(skip).limit(limit).all()


def get_songs_by_album(db: Session, album_id: str, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Song)
        .filter(models.Song.album_id == album_id)
        .order_by(models.Song.cd_serial, models.Song.order)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_song(db: Session, song: schemas.SongCreate):
    db_song = models.Song(
        song_id=song.song_id,
        name=song.name,
        order=song.order,
        album_id=song.album_id,
        cd_serial=song.cd_serial,
        length=song.length,
        pace=song.pace,
        play_count=song.play_count,
        fav_count=song.fav_count,
        share_count=song.share_count,
        composer=song.composer,
        songwriters=song.songwriters,
        arrangement=song.arrangement,
        music_type=song.music_type,
        sub_name=song.sub_name,
        hot_part_start=song.hot_part_start,
        hot_part_end=song.hot_part_end,
        comment_count=song.comment_count,
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
    normalized_query = query.strip()
    if not normalized_query:
        return {"artists": [], "albums": [], "songs": []}

    artists = search_artists_by_name(db, normalized_query)
    albums = search_albums_by_name(db, normalized_query)
    songs = search_songs_by_name(db, normalized_query)

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


# ===== Recommendation operations =====

from typing import Optional as _Optional


def _build_recommendation_payload(db: Session, rec: "models.Recommendation", user_id: int, top_n: int = 20):
    """Build the enriched response payload for a single recommendation set.

    Engagement counts (play_count/collects/recommends) live denormalized on
    recommendation_items (migration 007). The serving path no longer reads
    private_data/.
    """
    items = (
        db.query(models.RecommendationItem)
        .filter(models.RecommendationItem.recommendation_id == rec.id)
        .order_by(models.RecommendationItem.rank)
        .limit(top_n)
        .all()
    )

    taste = (
        db.query(models.TasteProfile)
        .filter(models.TasteProfile.id == rec.taste_profile_id)
        .first()
    )

    item_ids = [it.id for it in items]
    quick_by_item = {}
    feedback_by_item = {}
    if item_ids:
        quick_rows = (
            db.query(models.RecommendationQuickReaction)
            .filter(
                models.RecommendationQuickReaction.user_id == user_id,
                models.RecommendationQuickReaction.recommendation_item_id.in_(item_ids),
            )
            .all()
        )
        for q in quick_rows:
            quick_by_item[q.recommendation_item_id] = q

        feedback_rows = (
            db.query(models.RecommendationFeedback)
            .filter(
                models.RecommendationFeedback.user_id == user_id,
                models.RecommendationFeedback.recommendation_item_id.in_(item_ids),
            )
            .all()
        )
        for f in feedback_rows:
            feedback_by_item[f.recommendation_item_id] = f

    enriched_items = []
    for it in items:
        enriched_items.append({
            "id": it.id,
            "rank": it.rank,
            "album_id": it.album_id,
            "artist_name": it.artist_name,
            "album_name": it.album_name,
            "styles": it.styles_json,
            "similarity_score": it.similarity_score,
            "fit_score": it.fit_score,
            "reason": it.reason,
            "risk": it.risk,
            "nearest_neighbors": it.nearest_neighbors_json,
            "play_count": it.play_count,
            "collects": it.collects,
            "recommends": it.recommends,
            "quick_reaction": quick_by_item.get(it.id),
            "feedback": feedback_by_item.get(it.id),
        })

    return {
        "id": rec.id,
        "user_id": rec.user_id,
        "generated_at": rec.created,
        "generation_method": rec.generation_method,
        "embedding_model": rec.embedding_model,
        "judge_model": rec.judge_model,
        "top_n": rec.top_n,
        "taste_profile_id": rec.taste_profile_id,
        "taste_profile_text": taste.profile_text if taste else "",
        "items": enriched_items,
    }


def get_daily_recommendation(db: Session, user_id: int, top_n: int = 20):
    """Latest recommendation set for user_id, with top_n items by rank ASC."""
    rec = (
        db.query(models.Recommendation)
        .filter(models.Recommendation.user_id == user_id)
        .order_by(models.Recommendation.created.desc())
        .first()
    )
    if rec is None:
        return None
    return _build_recommendation_payload(db, rec, user_id=user_id, top_n=top_n)


def get_recommendation_by_id(db: Session, user_id: int, rec_id: int, top_n: int = 20):
    """A specific recommendation set by id, scoped to user_id."""
    rec = (
        db.query(models.Recommendation)
        .filter(
            models.Recommendation.id == rec_id,
            models.Recommendation.user_id == user_id,
        )
        .first()
    )
    if rec is None:
        return None
    return _build_recommendation_payload(db, rec, user_id=user_id, top_n=top_n)


def list_recommendations(db: Session, user_id: int):
    """All recommendation sets for user_id, newest first, metadata only."""
    rows = (
        db.query(models.Recommendation)
        .filter(models.Recommendation.user_id == user_id)
        .order_by(models.Recommendation.created.desc())
        .all()
    )
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.id,
                "generated_at": r.created,
                "top_n": r.top_n,
                "generation_method": r.generation_method,
                "embedding_model": r.embedding_model,
                "judge_model": r.judge_model,
                "notes": r.notes,
            }
            for r in rows
        ],
    }


def upsert_quick_reaction(db: Session, user_id: int, item_id: int, reaction: str):
    """Upsert this user's quick reaction (interested/skip/save) on a recommendation item."""
    existing = (
        db.query(models.RecommendationQuickReaction)
        .filter(
            models.RecommendationQuickReaction.user_id == user_id,
            models.RecommendationQuickReaction.recommendation_item_id == item_id,
        )
        .first()
    )
    if existing:
        existing.reaction = reaction
        db.commit()
        db.refresh(existing)
        return existing

    row = models.RecommendationQuickReaction(
        user_id=user_id,
        recommendation_item_id=item_id,
        reaction=reaction,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def upsert_feedback(
    db: Session,
    user_id: int,
    item_id: int,
    star: int,
    song_impression: _Optional[str],
    recommendation_advice: _Optional[str],
):
    """Upsert this user's deep feedback (star + impressions + advice) on a recommendation item."""
    existing = (
        db.query(models.RecommendationFeedback)
        .filter(
            models.RecommendationFeedback.user_id == user_id,
            models.RecommendationFeedback.recommendation_item_id == item_id,
        )
        .first()
    )
    if existing:
        existing.star = star
        existing.song_impression = song_impression
        existing.recommendation_advice = recommendation_advice
        db.commit()
        db.refresh(existing)
        return existing

    row = models.RecommendationFeedback(
        user_id=user_id,
        recommendation_item_id=item_id,
        star=star,
        song_impression=song_impression,
        recommendation_advice=recommendation_advice,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_recommendation_item(db: Session, item_id: int):
    return (
        db.query(models.RecommendationItem)
        .filter(models.RecommendationItem.id == item_id)
        .first()
    )
