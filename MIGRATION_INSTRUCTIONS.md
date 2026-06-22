# Flask-Migrate / Alembic deployment notes (PythonAnywhere)

## 1) Ensure environment variables are set
Required for this app:
- `SECRET_KEY`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_REDIRECT_URI` (must match your PythonAnywhere URL + `/auth/callback`)
- `DATABASE_URL` (optional; defaults to local sqlite)

## 2) Run migrations (fresh deploy)
On your dev machine (recommended):

```bash
# from project root
python -c "from app import create_app; app=create_app(); print(app.import_name)"

# create migration if models changed
flask db migrate -m "your message"

# apply to database
flask db upgrade
```

On PythonAnywhere, after setting `DATABASE_URL` (if using Postgres/MySQL), run:

```bash
flask db upgrade
```

## 3) Make sure models are imported
This repo already imports models in `migrations/env.py`, so Alembic autogenerate and upgrades should detect schemas.

## 4) If `flask db` is not available
`flask db` requires Flask-Migrate integration (done in this repo) and a Flask app factory that can be discovered.

If needed, set `FLASK_APP=run.py` or configure accordingly for PythonAnywhere.

