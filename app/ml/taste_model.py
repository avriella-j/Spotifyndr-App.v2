# app/ml/taste_model.py — Logistic regression over a user's swipe history,
# using artist identity as the feature. Summarizes taste as genre
# percentages by mapping liked artists to their genres.

import numpy as np
from sklearn.linear_model import LogisticRegression


def build_training_data(swipes, known_artist_ids):
    X, y = [], []
    for swipe in swipes:
        if not swipe.artist_id or swipe.artist_id not in known_artist_ids:
            continue
        row = [1.0 if a == swipe.artist_id else 0.0 for a in known_artist_ids]
        X.append(row)
        y.append(1 if swipe.liked else 0)

    if len(X) < 10:
        return None, None
    if len(set(y)) < 2:
        return None, None

    return np.array(X), np.array(y)


def train_taste_model(X, y):
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    return model


def summarize_taste(model, known_artist_ids, artist_id_to_name, artist_id_to_genres, top_n=10):
    """Return genre percentages derived from the artists the model
    learned the user prefers. Maps each top artist's coefficient to
    their genres and aggregates into normalized percentages."""
    if model is None:
        return {'genres': [], 'message': 'Not enough swipe data yet — keep swiping!'}

    coefs = model.coef_[0]
    ranked = sorted(zip(known_artist_ids, coefs), key=lambda kv: kv[1], reverse=True)
    top_artists = [(aid, float(w)) for aid, w in ranked[:top_n] if w > 0]

    if not top_artists:
        return {'genres': [], 'message': "We need a bit more swipe data to find your taste pattern."}

    genre_scores = {}
    for aid, weight in top_artists:
        genres = artist_id_to_genres.get(aid, [])
        if not genres:
            genres = [artist_id_to_name.get(aid, 'Unknown').lower()]
        for g in genres:
            genre_scores[g] = genre_scores.get(g, 0) + weight

    total = sum(genre_scores.values())
    if total == 0:
        return {'genres': [], 'message': "We need a bit more swipe data to find your taste pattern."}

    sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
    genre_pcts = [
        {'genre': g, 'percentage': round((s / total) * 100, 1)}
        for g, s in sorted_genres
    ]

    top3 = [g['genre'] for g in genre_pcts[:3]]
    top3_pct = [f"{g['genre']} ({g['percentage']}%)" for g in genre_pcts[:3]]

    return {
        'genres': genre_pcts,
        'message': f"Your top genres are {', '.join(top3_pct)}."
    }
