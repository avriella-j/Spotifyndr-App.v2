# app/services/spotify_sync_service.py — Pulls Spotify data into our DB
from datetime import datetime
from app.extensions import db
from app.models.user_top_content import UserTopContent
from app.services.spotify_service import SpotifyService
from app.services.token_service import TokenService


class SpotifySyncService:
    """Fetches data from Spotify and writes it into our own tables."""

    @staticmethod
    def sync_top_content(user, time_range='medium_term', limit=10):
        """Fetch top tracks + top artists from Spotify and upsert into
        UserTopContent. Call this right after login, and periodically
        afterward (e.g. daily, via a scheduled task)."""

        access_token = TokenService.get_valid_access_token(user)
        spotify = SpotifyService(access_token)

        tracks_resp = spotify.get_top_tracks(limit=limit, time_range=time_range)
        artists_resp = spotify.get_top_artists(limit=limit, time_range=time_range)

        top_tracks = [
            {
                'id': t['id'],
                'name': t['name'],
                'artist': ', '.join(a['name'] for a in t['artists']),
                'artist_ids': [a['id'] for a in t['artists']],
                'album': t['album']['name'],
                'image_url': t['album']['images'][0]['url'] if t['album']['images'] else None,
                'preview_url': t.get('preview_url'),
                'uri': t['uri'],
                'popularity': t.get('popularity'),
            }
            for t in tracks_resp.get('items', [])
        ]

        top_artists = [
            {
                'id': a['id'],
                'name': a['name'],
                'genres': a.get('genres', []),
                'image_url': a['images'][0]['url'] if a.get('images') else None,
                'followers': a.get('followers', {}).get('total', 0),
                'popularity': a.get('popularity'),
                'uri': a['uri'],
            }
            for a in artists_resp.get('items', [])
        ]

        content = UserTopContent.query.filter_by(user_id=user.id).first()
        if not content:
            content = UserTopContent(user_id=user.id)
            db.session.add(content)

        content.top_tracks = top_tracks
        content.top_artists = top_artists
        content.updated_at = datetime.utcnow()
        db.session.commit()

        return content

    @staticmethod
    def needs_sync(user, max_age_hours=24):
        """Should we refresh this user's top content from Spotify?"""
        content = UserTopContent.query.filter_by(user_id=user.id).first()
        if not content or not content.updated_at:
            return True
        age = datetime.utcnow() - content.updated_at
        return age.total_seconds() > max_age_hours * 3600

    @staticmethod
    def sync_if_stale(user, max_age_hours=24):
        """Convenience: sync only if data is missing or old."""
        if SpotifySyncService.needs_sync(user, max_age_hours):
            return SpotifySyncService.sync_top_content(user)
        return UserTopContent.query.filter_by(user_id=user.id).first()
