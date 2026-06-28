# app/ml/taste_model.py — Logistic regression over a user's swipe history,
# to produce a simple "your taste leans toward X genres" summary.
import numpy as np
from sklearn.linear_model import LogisticRegression


def build_training_data(swipes, known_genres):
    """
    swipes: list of Swipe model instances for one user. Each Swipe now
        carries its own `genres` field, captured at swipe-creation time.
    known_genres: ordered list of all genre strings the system tracks

    Returns (X, y) suitable for sklearn, or (None, None) if there's not
    enough data to train on.
    """
    X, y = [], []
    for swipe in swipes:
        genres = swipe.genres or []
        if not genres:
            continue
        row = [1.0 if g in genres else 0.0 for g in known_genres]
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


def summarize_taste(model, known_genres, top_n=5):
    """Turn the trained model's coefficients into a human-readable summary."""
    if model is None:
        return {'genres': [], 'message': 'Not enough swipe data yet — keep swiping!'}

    coefs = model.coef_[0]
    ranked = sorted(zip(known_genres, coefs), key=lambda kv: kv[1], reverse=True)
    top_genres = [{'genre': g, 'weight': round(float(w), 3)} for g, w in ranked[:top_n] if w > 0]

    if not top_genres:
        return {'genres': [], 'message': "We need a bit more swipe data to find your taste pattern."}

    return {
        'genres': top_genres,
        'message': f"Your taste leans toward {', '.join(g['genre'] for g in top_genres[:3])}."
    }
