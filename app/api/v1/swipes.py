# app/api/v1/swipes.py — Record swipe actions and taste summary
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.swipe import Swipe
from app.models.user_top_content import UserTopContent
from app.ml.taste_model import build_training_data, train_taste_model, summarize_taste
from app.ml.known_genres import get_known_genres
import random

swipes_api_bp = Blueprint('swipes_api', __name__)


def _build_artist_genre_lookup(content):
    lookup = {}
    for artist in (content.top_artists or []):
        if artist.get('id'):
            lookup[artist['id']] = artist.get('genres', [])
    return lookup


def _genres_for_content(content_id, content_type, content, artist_genre_lookup):
    if content_type == 'artist':
        return artist_genre_lookup.get(content_id, [])

    all_tracks = (content.saved_tracks or []) + (content.top_tracks or [])
    for track in all_tracks:
        if track.get('id') == content_id:
            for artist_id in track.get('artist_ids', []):
                genres = artist_genre_lookup.get(artist_id)
                if genres:
                    return genres
    return []


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
    genres = []
    if content:
        artist_genre_lookup = _build_artist_genre_lookup(content)
        genres = _genres_for_content(content_id, content_type, content, artist_genre_lookup)

    swipe = Swipe(
        user_id=current_user.id,
        content_id=content_id,
        content_type=content_type,
        liked=liked,
        genres=genres,
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


@swipes_api_bp.route('/taste-summary', methods=['GET'])
@login_required
def taste_summary():
    """Return a logistic-regression-derived summary of the user's taste,
    reading genres directly from each Swipe row (captured at swipe-time)."""
    swipes = Swipe.query.filter_by(user_id=current_user.id).all()
    known_genres = get_known_genres()

    X, y = build_training_data(swipes, known_genres)
    model = train_taste_model(X, y) if X is not None else None
    summary = summarize_taste(model, known_genres)

    return jsonify(summary)
