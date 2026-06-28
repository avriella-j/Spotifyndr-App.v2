# app/ml/taste_model.py — Logistic regression over a user's swipe history,
# using artist identity as the feature (genres are no longer reliably
# returned by Spotify's API).
import numpy as np
from sklearn.linear_model import LogisticRegression


def build_training_data(swipes, known_artist_ids):
    """
    swipes: list of Swipe model instances for one user.
    known_artist_ids: ordered list of all artist IDs the system has seen
        for this user (their own top/saved artists + anything swiped).

    Returns (X, y) suitable for sklearn, or (None, None) if there's not
    enough data to train on.
    """
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


def summarize_taste(model, known_artist_ids, artist_id_to_name, top_n=5):
    """Turn the trained model's coefficients into a human-readable summary,
    naming the artists the model learned the user prefers."""
    if model is None:
        return {'artists': [], 'message': 'Not enough swipe data yet — keep swiping!'}

    coefs = model.coef_[0]
    ranked = sorted(zip(known_artist_ids, coefs), key=lambda kv: kv[1], reverse=True)
    top_artists = [
        {'artist_id': aid, 'name': artist_id_to_name.get(aid, 'Unknown artist'), 'weight': round(float(w), 3)}
        for aid, w in ranked[:top_n] if w > 0
    ]

    if not top_artists:
        return {'artists': [], 'message': "We need a bit more swipe data to find your taste pattern."}

    names = ', '.join(a['name'] for a in top_artists[:3])
    return {
        'artists': top_artists,
        'message': f"Your taste leans toward {names}."
    }
