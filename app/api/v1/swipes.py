# app/api/v1/swipes.py — Record swipe actions and taste summary
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.swipe import Swipe
from app.models.user_top_content import UserTopContent
from app.ml.taste_model import build_training_data, train_taste_model, summarize_taste
from app.ml.discovery_engine import generate_discovery_batch
from app.services.token_service import TokenService
from app.services.spotify_service import SpotifyService
import random

swipes_api_bp = Blueprint('swipes_api', __name__)


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
    offset = int(request.args.get('offset', 0))

    access_token = TokenService.get_valid_access_token(current_user)
    spotify = SpotifyService(access_token)

    batch = generate_discovery_batch(spotify, content, exclude_ids, batch_size=20, offset_seed=offset)
    return jsonify(batch)


def _build_known_artists(user_id):
    content = UserTopContent.query.filter_by(user_id=user_id).first()
    artist_id_to_name = {}
    if content:
        for artist in (content.top_artists or []):
            if artist.get('id'):
                artist_id_to_name[artist['id']] = artist.get('name', 'Unknown artist')

    swipes = Swipe.query.filter_by(user_id=user_id).all()
    for swipe in swipes:
        if swipe.artist_id and swipe.artist_id not in artist_id_to_name:
            artist_id_to_name[swipe.artist_id] = swipe.artist_name or 'Unknown artist'

    return list(artist_id_to_name.keys()), artist_id_to_name, swipes


@swipes_api_bp.route('/taste-summary', methods=['GET'])
@login_required
def taste_summary():
    """Return a logistic-regression-derived summary of the user's taste,
    based on which artists they tend to like vs dislike when swiping."""
    known_artist_ids, artist_id_to_name, swipes = _build_known_artists(current_user.id)

    X, y = build_training_data(swipes, known_artist_ids)
    model = train_taste_model(X, y) if X is not None else None
    summary = summarize_taste(model, known_artist_ids, artist_id_to_name)

    return jsonify(summary)
