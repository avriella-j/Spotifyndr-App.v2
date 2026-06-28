# app/ml/feature_builder.py — Builds a numeric genre-vector feature for each
# user from their Spotify data (top tracks, top artists, saved tracks),
# for use by KNN (mutuals matching, For You suggestions).

from collections import Counter


def _collect_genres_and_artists(top_content):
    genre_counts = Counter()
    artist_names = set()

    def _consume_artist(artist_dict):
        name = artist_dict.get('name')
        if name:
            artist_names.add(name)
        for g in artist_dict.get('genres', []) or []:
            genre_counts[g] += 1

    def _consume_track(track_dict):
        name = track_dict.get('artist')
        if name:
            artist_names.add(name)

    if not top_content:
        return genre_counts, artist_names

    for artist in (top_content.top_artists or []):
        _consume_artist(artist)
    for track in (top_content.top_tracks or []):
        _consume_track(track)
    for track in (top_content.saved_tracks or []):
        _consume_track(track)

    return genre_counts, artist_names


def build_feature_vector(top_content, known_genres):
    """Build a {genre: weight} dict for one user, normalized to the
    provided known_genres list so every user's vector has the same shape
    (required for KNN to compare them)."""
    genre_counts, _artist_names = _collect_genres_and_artists(top_content)

    total = sum(genre_counts.values())
    vector = {}
    for g in known_genres:
        if total == 0:
            vector[g] = 0.0
        else:
            vector[g] = round(genre_counts.get(g, 0) / total, 4)
    return vector


def vector_to_array(vector, known_genres):
    """Convert a {genre: weight} dict into an ordered list matching
    known_genres, for feeding into sklearn."""
    return [vector.get(g, 0.0) for g in known_genres]
