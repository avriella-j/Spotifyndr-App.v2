# app/ml/discovery_engine.py — Generates fresh, non-repeating swipe deck
# content using Spotify's /search endpoint seeded by the user's own top
# artists/genres.

import random


def normalize_spotify_genres(spotify_genres_list):
    """
    Takes a raw list of strings from Spotify's artist genres array
    and sanitizes/maps them to parent UI buckets.
    """
    if not spotify_genres_list:
        return "Pop"

    combined_raw = " ".join(spotify_genres_list).lower()

    if any(keyword in combined_raw for keyword in ["rock", "punk", "grunge", "alternative", "emo"]):
        return "Alternative Rock"
    if any(keyword in combined_raw for keyword in ["r&b", "soul", "motown", "neo-soul"]):
        return "R&B"
    if any(keyword in combined_raw for keyword in ["hip hop", "rap", "trap", "drill"]):
        return "Hip-Hop"
    if any(keyword in combined_raw for keyword in ["house", "techno", "edm", "dance", "electronic"]):
        return "Electronic/Dance"

    return "Pop"


def _get_seed_genres(top_content, limit=10):
    genres = []
    seen = set()
    for artist in (top_content.top_artists or []):
        for g in artist.get('genres', []) or []:
            if g not in seen:
                seen.add(g)
                genres.append(g)
    return genres[:limit]


def _get_seed_artist_names(top_content, limit=10):
    names = []
    for artist in (top_content.top_artists or []):
        if artist.get('name') and artist['name'] not in names:
            names.append(artist['name'])
    return names[:limit]


def _get_known_track_ids(top_content):
    ids = set()
    for track in (top_content.saved_tracks or []) + (top_content.top_tracks or []):
        if track.get('id'):
            ids.add(track['id'])
    return ids


# Track offsets per query across calls
_query_offsets = {}


def generate_discovery_batch(spotify_service, top_content, exclude_ids, batch_size=50):
    seed_genres = _get_seed_genres(top_content)
    seed_artists = _get_seed_artist_names(top_content)
    known_ids = _get_known_track_ids(top_content) | set(exclude_ids)

    queries = []

    for genre in seed_genres:
        queries.append(f'genre:"{genre}"')
        queries.append(f'{genre}')

    for artist in seed_artists:
        queries.append(artist)
        queries.append(f'{artist} playlist')

    if not queries:
        queries = ['pop', 'hip hop', 'rock', 'r&b', 'edm',
                   'electronic', 'latin', 'indie', 'jazz', 'country']

    random.shuffle(queries)

    results = {}
    for query in queries:
        if len(results) >= batch_size:
            break

        offset = _query_offsets.get(query, 0)

        try:
            resp = spotify_service.search(query, type='track', limit=50, offset=offset)
        except Exception:
            _query_offsets[query] = offset + 50
            continue

        items = resp.get('tracks', {}).get('items', [])
        if not items:
            _query_offsets[query] = 0
            continue

        _query_offsets[query] = offset + 50

        for track in items:
            if track['id'] in known_ids or track['id'] in results:
                continue
            results[track['id']] = {
                'id': track['id'],
                'name': track['name'],
                'artist': ', '.join(a['name'] for a in track['artists']),
                'album': track['album']['name'],
                'image_url': track['album']['images'][0]['url'] if track['album'].get('images') else None,
                'preview_url': track.get('preview_url'),
                'uri': track['uri'],
                'popularity': track.get('popularity'),
            }

    batch = list(results.values())
    random.shuffle(batch)
    return batch[:batch_size]
