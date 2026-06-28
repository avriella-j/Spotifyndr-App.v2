# app/ml/known_genres.py — Union of all genres the system tracks

from app.seed.genre_clusters import GENRE_CLUSTERS
from app.models.user_top_content import UserTopContent


def get_known_genres():
    """Union of all genres from seed clusters + genres seen on real users."""
    genres = set()
    for cluster in GENRE_CLUSTERS.values():
        genres.update(cluster['genres'])

    # also pick up genres from real synced users that aren't in the seed clusters
    for content in UserTopContent.query.all():
        for artist in (content.top_artists or []):
            genres.update(artist.get('genres', []))

    return sorted(genres)
