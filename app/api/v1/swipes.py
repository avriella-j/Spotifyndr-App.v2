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


@swipes_api_bp.route('', methods=['POST'])
@login_required
def record_swipe():
    """Record a single swipe (like/dislike) on a track or artist.

    Expected JSON body:
    {
        "content_id": "<spotify id>",
        "content_type": "track" | "artist",
        "liked": true | false
    }
    """
    data = request.get_json(silent=True) or {}
    content_id = data.get('content_id')
    content_type = data.get('content_type')
    liked = data.get('liked')

    if not content_id or content_type not in ('track', 'artist', 'playlist'):
        return jsonify({'error': 'content_id and a valid content_type are required'}), 400
    if not isinstance(liked, bool):
        return jsonify({'error': 'liked must be a boolean'}), 400

    swipe = Swipe(
        user_id=current_user.id,
        content_id=content_id,
        content_type=content_type,
        liked=liked,
    )
    db.session.add(swipe)
    db.session.commit()

    return jsonify(swipe.to_dict()), 201


@swipes_api_bp.route('/deck', methods=['GET'])
@login_required
def get_swipe_deck():
    """Return a batch of tracks for the user to swipe on, pulled from
    their own saved + top tracks (already-synced data, no live Spotify
    call needed here)."""
    content = UserTopContent.query.filter_by(user_id=current_user.id).first()
    if not content:
        return jsonify([])

    pool = (content.saved_tracks or []) + (content.top_tracks or [])
    if not pool:
        return jsonify([])

    random.shuffle(pool)
    return jsonify(pool[:20])


@swipes_api_bp.route('/taste-summary', methods=['GET'])
@login_required
def taste_summary():
    """Return a logistic-regression-derived summary of the user's taste
    based on their swipe history."""
    swipes = Swipe.query.filter_by(user_id=current_user.id).all()
    known_genres = get_known_genres()

    # Build content_id -> genres lookup from the user's own cached top
    # content (covers swipes on content that also appears there) plus
    # fall back to empty for anything else.
    content = UserTopContent.query.filter_by(user_id=current_user.id).first()
    content_genre_lookup = {}
    if content:
        for artist in (content.top_artists or []):
            content_genre_lookup[artist['id']] = artist.get('genres', [])

    X, y = build_training_data(swipes, content_genre_lookup, known_genres)
    model = train_taste_model(X, y) if X is not None else None
    summary = summarize_taste(model, known_genres)

    return jsonify(summary)
