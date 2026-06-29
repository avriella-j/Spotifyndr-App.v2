# app/api/v1/swipes.py — Record swipe actions and taste summary
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.swipe import Swipe
from app.models.user_top_content import UserTopContent
from app.ml.discovery_engine import generate_discovery_batch, normalize_spotify_genres
from app.services.token_service import TokenService
from app.services.spotify_service import SpotifyService
import random

swipes_api_bp = Blueprint('swipes_api', __name__)

# High-fidelity artist-to-genre mapping (local dictionary — first tier)
ARTIST_TO_GENRE_MAP = {
    "mariah the scientist": "R&B",
    "ne-yo": "R&B",
    "kiana led\u00e9": "R&B",
    "giv\u0113on": "R&B",
    "coco lee": "Pop",
    "katseye": "Pop",
    "ariana grande": "Pop",
    "one direction": "Pop",
    "charlie puth": "Pop",
    "diddy": "Hip-Hop",
    "nelly": "Hip-Hop",
    "david guetta": "Electronic/Dance",
    "taylor swift": "Pop",
    "the weeknd": "R&B",
    "sza": "R&B",
    "drake": "Hip-Hop",
    "kendrick lamar": "Hip-Hop",
    "kanye west": "Hip-Hop",
    "j. cole": "Hip-Hop",
    "billie eilish": "Pop",
    "olivia rodrigo": "Pop",
    "dua lipa": "Pop",
    "doja cat": "Pop",
    "bad bunny": "Latin",
    "beyonc\u00e9": "R&B",
    "rihanna": "R&B",
    "bruno mars": "Pop",
    "ed sheeran": "Pop",
    "adele": "Pop",
    "coldplay": "Alternative Rock",
    "imagine dragons": "Alternative Rock",
    "the beatles": "Alternative Rock",
    "queen": "Alternative Rock",
}


def _find_artist_for_content(content_id, content_type, content):
    if content_type == 'artist':
        for artist in (content.top_artists or []):
            if artist.get('id') == content_id:
                return artist.get('id'), artist.get('name')
        return content_id, None

    all_tracks = (content.saved_tracks or []) + (content.top_tracks or [])
    for track in all_tracks:
        if track.get('id') == content_id:
            artist_ids = track.get('artist_ids') or []
            if artist_ids:
                primary_id = artist_ids[0]
                primary_name = (track.get('artist') or '').split(',')[0].strip()
                return primary_id, primary_name or None
    return None, None


@swipes_api_bp.route('', methods=['POST'])
@login_required
def record_swipe():
    """Record a single swipe (like/dislike) on a track or artist."""
    data = request.get_json(silent=True) or {}
    content_id = data.get('content_id')
    content_type = data.get('content_type')
    liked = data.get('liked')

    if not content_id or content_type not in ('track', 'artist', 'playlist'):
        return jsonify({'error': 'content_id and a valid content_type are required'}), 400
    if not isinstance(liked, bool):
        return jsonify({'error': 'liked must be a boolean'}), 400

    content = UserTopContent.query.filter_by(user_id=current_user.id).first()
    artist_id, artist_name = (None, None)
    if content:
        artist_id, artist_name = _find_artist_for_content(content_id, content_type, content)

    swipe = Swipe(
        user_id=current_user.id,
        content_id=content_id,
        content_type=content_type,
        liked=liked,
        artist_id=artist_id,
        artist_name=artist_name,
    )
    db.session.add(swipe)
    db.session.commit()

    return jsonify(swipe.to_dict()), 201


@swipes_api_bp.route('/deck', methods=['GET'])
@login_required
def get_swipe_deck():
    """Return the full pool of tracks for the user to swipe on."""
    content = UserTopContent.query.filter_by(user_id=current_user.id).first()
    if not content:
        return jsonify([])

    pool = (content.saved_tracks or []) + (content.top_tracks or [])
    if not pool:
        return jsonify([])

    seen_ids = set()
    deduped = []
    for track in pool:
        if track.get('id') not in seen_ids:
            seen_ids.add(track.get('id'))
            deduped.append(track)

    random.shuffle(deduped)
    return jsonify(deduped)


@swipes_api_bp.route('/discover', methods=['GET'])
@login_required
def get_discovery_batch():
    """Returns a fresh batch of NEW tracks via search, for when the
    user's own saved/top tracks pool runs low."""
    content = UserTopContent.query.filter_by(user_id=current_user.id).first()
    if not content:
        return jsonify([])

    exclude_param = request.args.get('exclude_ids', '')
    exclude_ids = [x for x in exclude_param.split(',') if x]
    offset = request.args.get('offset', 0, type=int)

    access_token = TokenService.get_valid_access_token(current_user)
    spotify = SpotifyService(access_token)

    batch = generate_discovery_batch(spotify, content, exclude_ids, offset=offset)
    return jsonify(batch)


@swipes_api_bp.route('/taste-summary', methods=['GET'])
@login_required
def get_taste_summary():
    """
    Aggregates user swipe actions for the current session. Maps individual
    artists to standardized genres using a two-tier pipeline:
      1. Local artistToGenreMap lookup (by lowercase artist name)
      2. Live GET /artists/{id} API call
      3. Keyword normalization via normalize_spotify_genres()
      4. Ultimate fallback to "Pop"
    """
    access_token = TokenService.get_valid_access_token(current_user)
    spotify = SpotifyService(access_token)

    swipes = Swipe.query.filter_by(user_id=current_user.id).all()

    genre_counts = {}
    total_liked = 0

    for swipe in swipes:
        if not swipe.liked or not swipe.artist_id:
            continue
        total_liked += 1

        parent_genre = None

        # --- Tier 1: Local dictionary check ---
        if swipe.artist_name:
            key = swipe.artist_name.lower().strip()
            mapped = ARTIST_TO_GENRE_MAP.get(key)
            if mapped:
                parent_genre = mapped

        # --- Tier 2: Live Spotify artist API ---
        if not parent_genre:
            try:
                artist_data = spotify.get_artist(swipe.artist_id)
                raw_genres = artist_data.get('genres', []) or []
                if raw_genres:
                    parent_genre = normalize_spotify_genres(raw_genres)
            except Exception:
                pass

        # --- Tier 3: Ultimate fallback ---
        if not parent_genre:
            parent_genre = "Pop"

        genre_counts[parent_genre] = genre_counts.get(parent_genre, 0) + 1

    genres_summary = []
    for genre, count in genre_counts.items():
        pct = round((count / total_liked) * 100) if total_liked > 0 else 0
        genres_summary.append({"name": genre, "percentage": pct})

    genres_summary.sort(key=lambda x: x['percentage'], reverse=True)

    top3 = ", ".join(g['name'] for g in genres_summary[:3])
    message = f"Your top genres are {top3}." if top3 else "Keep swiping to see your taste profile!"

    return jsonify({
        "message": message,
        "genres": genres_summary,
        "total_swipes": total_liked
    })
