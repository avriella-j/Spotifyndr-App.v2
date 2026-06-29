# app/ml/discovery_engine.py — Generates fresh, non-repeating swipe deck
# content using Spotify's /search endpoint seeded by the user's own top
# artists/genres.

import random


def _get_seed_genres(top_content, limit=5):
    genres = set()
    for artist in (top_content.top_artists or []):
        for g in artist.get('genres', []) or []:
            genres.add(g)
    return list(genres)[:limit]


def _get_seed_artist_names(top_content, limit=8):
    names = []
    for artist in (top_content.top_artists or []):
        if artist.get('name'):
            names.append(artist['name'])
    return names[:limit]


def _get_known_track_ids(top_content):
    ids = set()
    for track in (top_content.saved_tracks or []) + (top_content.top_tracks or []):
        if track.get('id'):
            ids.add(track['id'])
    return ids


def generate_discovery_batch(spotify_service, top_content, exclude_ids, batch_size=20, offset_seed=0):
    seed_genres = _get_seed_genres(top_content)
    seed_artists = _get_seed_artist_names(top_content)
    known_ids = _get_known_track_ids(top_content) | set(exclude_ids)

    queries = []
    for genre in seed_genres:
        queries.append(f'genre:"{genre}"')
    for artist in seed_artists:
        queries.append(artist)

    if not queries:
        queries = ['pop', 'hip hop', 'rock', 'r&b', 'edm']

    random.shuffle(queries)

    results = {}
    for query in queries:
        if len(results) >= batch_size:
            break
        try:
            resp = spotify_service.search(query, type='track', limit=10, offset=offset_seed)
        except TypeError:
            try:
                resp = spotify_service.search(query, type='track', limit=10)
            except Exception:
                continue
        except Exception:
            continue

        for track in resp.get('tracks', {}).get('items', []):
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
