# PROJECT_SPECIFICATION.md
# Spotifyndr — Master Blueprint

**Version:** 1.0.0
**Status:** Pre-Development Planning Document
**Last Updated:** 2026-06-13
**Classification:** Internal — Architecture & Engineering

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Goals](#2-project-goals)
3. [Application Description](#3-application-description)
4. [User Features](#4-user-features)
   - 4.1 [Login System](#41-login-system)
   - 4.2 [For You Page (FYP)](#42-for-you-page-fyp)
   - 4.3 [Explore Page](#43-explore-page)
   - 4.4 [Find Mutuals Page](#44-find-mutuals-page)
   - 4.5 [Messaging System](#45-messaging-system)
   - 4.6 [User Profiles](#46-user-profiles)
   - 4.7 [Settings](#47-settings)
5. [Machine Learning Specification](#5-machine-learning-specification)
   - 5.1 [Logistic Regression](#51-logistic-regression)
   - 5.2 [K-Nearest Neighbours (KNN)](#52-k-nearest-neighbours-knn)
6. [Database Design](#6-database-design)
7. [API Design](#7-api-design)
8. [Spotify API Integration](#8-spotify-api-integration)
9. [Security Architecture](#9-security-architecture)
10. [Frontend Architecture](#10-frontend-architecture)
11. [UI/UX Design](#11-uiux-design)
12. [Folder Structure](#12-folder-structure)
13. [Testing Strategy](#13-testing-strategy)
14. [Deployment Strategy](#14-deployment-strategy)
15. [Scalability Considerations](#15-scalability-considerations)
16. [Future Features](#16-future-features)

---

## 1. Executive Summary

Spotifyndr is a production-grade social networking platform built around Spotify listening data. It enables users to authenticate via Spotify OAuth 2.0, have their listening habits automatically ingested, and then engage with a community of users who share similar musical taste. The platform combines real-time social features — direct messaging, follow/follower graphs, public profiles — with an intelligent recommendation engine powered by machine learning (Logistic Regression and K-Nearest Neighbours) trained on continuously updated Spotify behavioural data.

The application is architected as a Flask-based backend served over Gunicorn/Nginx, backed by a PostgreSQL relational database, Redis for caching and pub/sub, and Celery for asynchronous task processing. The frontend is rendered via Jinja2 templates enhanced with vanilla JavaScript, with SocketIO powering real-time messaging. Machine learning models are trained using Scikit-Learn and retrained on a rolling schedule via Celery Beat.

Spotifyndr is designed to be deployed in Docker containers, horizontally scalable to 10,000+ concurrent users, and maintainable by a small engineering team. The product is not affiliated with or endorsed by Spotify AB. It integrates with the Spotify Web API as a third-party application compliant with Spotify's Developer Terms of Service and Branding Guidelines.

---

## 2. Project Goals

### 2.1 Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Users must be able to authenticate exclusively via Spotify OAuth 2.0 |
| FR-02 | On first login, the system must create a local user account and import top tracks, top artists, saved tracks, and playlists from Spotify |
| FR-03 | The For You Page must surface personalised song, artist, podcast, radio, playlist, and mix recommendations |
| FR-04 | The Explore Page must present swipeable music cards with audio previews; swipe actions must feed the recommendation engine |
| FR-05 | The Find Mutuals Page must display other users with a computed match percentage based on music taste similarity |
| FR-06 | Users must be able to send and receive real-time direct messages |
| FR-07 | User profiles must be publicly viewable (subject to privacy settings) and display Spotify-sourced music data |
| FR-08 | Users must be able to follow and unfollow other users |
| FR-09 | The recommendation engine must retrain continuously based on user interaction events |
| FR-10 | Settings must allow fine-grained privacy, visibility, and notification controls |

### 2.2 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | API Response Time (p95) | < 300 ms |
| NFR-02 | Page Load Time (LCP) | < 2.5 s |
| NFR-03 | Concurrent WebSocket Connections | 5,000+ |
| NFR-04 | Uptime SLA | 99.5% |
| NFR-05 | ML Recommendation Latency | < 100 ms (cached) |
| NFR-06 | Message Delivery Latency | < 500 ms |
| NFR-07 | Spotify API Token Refresh | Transparent to user |
| NFR-08 | Data Encryption | AES-256 at rest, TLS 1.3 in transit |
| NFR-09 | Compliance | GDPR-ready data handling |
| NFR-10 | Scalability | Horizontal scale to 10,000+ users without re-architecture |

### 2.3 Constraints

- The application must not violate Spotify's Developer Terms of Service or Branding Guidelines.
- No Spotify trademarks, logos, or proprietary audio content may be stored permanently; audio previews are streamed via Spotify's CDN URLs with short-lived links.
- All third-party data attribution must comply with Spotify's display requirements.
- Machine learning models must not expose personally identifiable information from one user to another.

---

## 3. Application Description

### 3.1 Platform Overview

Spotifyndr is a music-first social platform. Unlike general social networks, every piece of social signal — who you follow, who you match with, what you are recommended — is derived from verifiable Spotify listening data rather than self-reported interests.

### 3.2 Core User Journey

```
[Landing Page]
      │
      ▼
[Spotify OAuth Login]
      │
      ▼
[Account Created / Returned User Detected]
      │
      ▼
[Spotify Data Import via Celery Background Task]
      │
      ├──▶ [For You Page] — ML-generated personalised recommendations
      │
      ├──▶ [Explore Page] — Swipe-based music discovery
      │
      ├──▶ [Find Mutuals] — KNN-powered user similarity matching
      │
      ├──▶ [Messaging]    — Real-time DMs via SocketIO
      │
      └──▶ [Profile]      — Public music identity page
```

### 3.3 Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Web Framework | Flask 3.x |
| WSGI Server | Gunicorn |
| Reverse Proxy | Nginx |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x + Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Caching / Pub-Sub | Redis 7.x |
| Async Task Queue | Celery 5.x + Celery Beat |
| Real-Time | Flask-SocketIO (gevent or eventlet) |
| ML | Scikit-Learn 1.x (Logistic Regression, KNN) |
| Frontend | HTML5, CSS3, Vanilla JS (ES2022) |
| Containerisation | Docker + Docker Compose |
| Auth | Spotify OAuth 2.0 (PKCE flow) |

---

## 4. User Features

### 4.1 Login System

#### 4.1.1 Overview

Authentication is handled exclusively via Spotify OAuth 2.0 using the Authorization Code with PKCE (Proof Key for Code Exchange) flow. There are no usernames or passwords managed by Spotifyndr. The platform is a Spotify-dependent service — a valid Spotify account is required.

#### 4.1.2 OAuth Flow Detail

```
[Browser]
    │  1. User clicks "Continue with Spotify"
    ▼
[Flask /auth/login]
    │  2. Generate code_verifier + code_challenge (SHA-256)
    │  3. Store code_verifier in server-side session
    │  4. Redirect to Spotify Accounts Service with:
    │     - client_id
    │     - response_type=code
    │     - redirect_uri
    │     - scope (see §8.1)
    │     - code_challenge
    │     - code_challenge_method=S256
    │     - state (CSRF token)
    ▼
[Spotify Accounts Service]
    │  5. User grants permissions
    │  6. Redirect to /auth/callback?code=...&state=...
    ▼
[Flask /auth/callback]
    │  7. Validate state matches session CSRF token
    │  8. Exchange code + code_verifier for access_token + refresh_token
    │  9. Fetch user profile from Spotify /me endpoint
    │ 10. Upsert User record in PostgreSQL
    │ 11. Store encrypted tokens in DB
    │ 12. Create Flask server-side session (Redis-backed)
    │ 13. Enqueue Celery task: full_spotify_import(user_id)
    ▼
[For You Page]
```

#### 4.1.3 Session Management

- Sessions are server-side, stored in Redis with a 24-hour TTL.
- Session IDs are cryptographically random (128-bit) stored in an HttpOnly, Secure, SameSite=Strict cookie.
- Session data stored in Redis: `user_id`, `spotify_user_id`, `session_created_at`, `last_active`.
- Flask-Session configured with `SESSION_TYPE=redis`.
- Sliding expiry: each authenticated request resets TTL to 24 hours.
- Concurrent sessions per user: maximum 5 (oldest invalidated on sixth login).

#### 4.1.4 Token Management

- `access_token` (1-hour TTL) and `refresh_token` are AES-256-encrypted before storage in PostgreSQL.
- A Celery Beat periodic task (`refresh_expiring_tokens`) runs every 45 minutes, identifying tokens expiring within 15 minutes and refreshing them proactively.
- The Flask request context middleware (`@app.before_request`) checks token validity on every authenticated route and refreshes inline if within 5 minutes of expiry, using a Redis distributed lock to prevent race conditions.

#### 4.1.5 Logout

- Server-side session deleted from Redis.
- Session cookie cleared (`Set-Cookie: session=; Max-Age=0`).
- Spotify access/refresh tokens are NOT revoked (Spotify does not support application-initiated revocation in all flows; users can revoke via Spotify Account settings).

#### 4.1.6 Security Requirements

- PKCE mandatory; implicit flow not used.
- `state` parameter validated on every callback to prevent CSRF.
- All OAuth redirect URIs whitelisted in Spotify Developer Dashboard.
- Tokens never logged or exposed in error messages.
- HTTPS enforced (HTTP → HTTPS redirect in Nginx).

---

### 4.2 For You Page (FYP)

#### 4.2.1 Overview

The For You Page is the primary landing surface after login. It presents an algorithmically curated feed of content personalised to each user based on their Spotify history and in-app behaviour. Content types are rendered in distinct, visually separated sections, similar in spirit to Spotify's Home page but layered with social signals from mutual connections.

#### 4.2.2 Content Types

| Section | Content Type | Data Source |
|---------|-------------|-------------|
| Recommended Songs | Tracks | Spotify Recommendations API + LR model |
| Recommended Artists | Artists | Spotify Related Artists + LR model |
| Podcasts You Might Like | Podcasts | Spotify Search (podcasts) + LR model |
| Radio Stations | Spotify Radio | Spotify Recommendations (seed_genres) |
| Curated Playlists | Playlists | Spotify Featured Playlists + user similarity |
| Your Mixes | Daily Mixes | Generated from user top genres/artists |

#### 4.2.3 Recommendation Generation Pipeline

```
[User Event] (swipe, play, skip, follow, like)
      │
      ▼
[Event logged to recommendation_events table]
      │
      ▼
[Celery task: update_user_feature_vector(user_id)]
      │
      ▼
[Feature vector recomputed and cached in Redis]
      │
      ▼
[LR model scores candidate items]
      │
      ▼
[Scored items cached in Redis with 1-hour TTL]
      │
      ▼
[FYP endpoint reads from Redis cache]
      │
      ▼ (cache miss)
[Synchronous LR inference on request]
```

#### 4.2.4 Search Functionality

The FYP includes a unified search bar supporting:

- **Content type filters:** Songs, Artists, Podcasts, Radio, Playlists, Mixes (multi-select chips)
- **Query:** Free-text search forwarded to Spotify Search API
- **Results display:** Unified card grid, identical visual treatment to recommendations
- **Debounce:** 300 ms debounce on input; results replace FYP feed inline

#### 4.2.5 Rendering

- Initial FYP content rendered server-side via Jinja2 for fast LCP.
- Subsequent interactions (search, filter) handled via `fetch()` to `/api/fyp` returning JSON, re-rendered client-side.
- Infinite scroll: next page fetched 200px before viewport bottom using Intersection Observer.

---

### 4.3 Explore Page

#### 4.3.1 Overview

The Explore Page is a Tinder-style swipeable music discovery interface. Each card represents a single track and includes enough information for the user to make an informed swipe decision. Swipe events are the primary training signal for the recommendation model.

#### 4.3.2 Card Specification

Each card renders:

| Field | Source | Display |
|-------|--------|---------|
| Album Artwork | Spotify `album.images[0].url` | Full-bleed card background with gradient overlay |
| Song Title | `track.name` | Bold, 24px, white, bottom-left |
| Artist Name | `track.artists[0].name` | 16px, white/70%, below title |
| Genre(s) | Derived from artist genres | Tag chips, bottom-right |
| Popularity | `track.popularity` (0–100) | Subtle progress bar or percentage label |
| Audio Preview | `track.preview_url` (30s MP3) | Auto-plays on card focus, mutes on swipe |

#### 4.3.3 Swipe Interaction

- **Swipe Right (Like):** Card animates off-screen right with green tint. Event logged as `swipe_right`.
- **Swipe Left (Dislike):** Card animates off-screen left with red tint. Event logged as `swipe_left`.
- **Keyboard:** Arrow keys trigger equivalent swipe events (accessibility).
- **Buttons:** On-screen Like/Dislike buttons for non-touch devices.
- **Touch events:** `touchstart`, `touchmove`, `touchend` with velocity-based snap decision.
- **Threshold:** Card snaps back if released within 30% of screen width; commits swipe beyond 30%.

#### 4.3.4 Card Queue Management

- Client maintains a queue of 10 pre-fetched cards in memory.
- When queue drops to 3, `GET /api/explore/next-batch` fetches the next 10.
- The batch endpoint calls the LR model to score candidates from the Spotify catalogue, filtered to exclude previously seen tracks (checked against `swipe_history` table).
- Candidates sourced from: Spotify Recommendations (seed_tracks from user top tracks), Spotify New Releases, and genre-expanded pools.
- Cards are presented in score-descending order, with randomised reshuffling within score bands to avoid repetition.

#### 4.3.5 Model Training from Swipes

- Every swipe event triggers a lightweight online update:
  - `swipe_right` → positive label (1) appended to user's training set
  - `swipe_left` → negative label (0) appended to user's training set
- A Celery task `retrain_user_model(user_id)` is enqueued after every 20 swipes.
- Full global model retraining (`retrain_global_model`) runs nightly at 02:00 via Celery Beat.

#### 4.3.6 Infinite Recommendations

- Candidate pool is refreshed by:
  - Rotating seed tracks (top tracks, recently swiped-right tracks)
  - Expanding to second-degree artists (related artists of already-liked artists)
  - Pulling from genre pools of currently liked tracks
- Pool exhaustion is practically impossible given Spotify's catalogue size (~100M+ tracks).

---

### 4.4 Find Mutuals Page

#### 4.4.1 Overview

The Find Mutuals Page helps users discover other Spotifyndr members who share their musical taste. Each displayed user shows a computed match percentage derived from KNN similarity analysis of music feature vectors.

#### 4.4.2 User Card Specification

Each user card displays:

| Field | Source |
|-------|--------|
| Profile Picture | Spotify profile image or initials avatar |
| Username | Derived from Spotify `display_name` |
| Followers Count | Spotifyndr follow graph |
| Following Count | Spotifyndr follow graph |
| Match Percentage | KNN similarity score (see §5.2) |
| Follow Button | Toggles follow/unfollow via `POST /api/follow` |

#### 4.4.3 Sorting & Filtering

| Option | Mechanism |
|--------|-----------|
| Sort by Match % (default) | `ORDER BY similarity_score DESC` |
| Sort Alphabetically | `ORDER BY username ASC` |
| Sort by Followers | `ORDER BY follower_count DESC` |
| Search by Username | `ILIKE %query%` with tsvector for performance |

- Results paginated: 20 users per page, infinite scroll.
- Mutual followers (users who already follow the current user) marked with a "Follows you" badge.

#### 4.4.4 Match Percentage Computation

See §5.2 for full KNN specification. Match percentages are pre-computed nightly and cached in the `user_similarities` table. Real-time recomputation is triggered when a user's feature vector changes significantly (cosine distance delta > 0.05).

---

### 4.5 Messaging System

#### 4.5.1 Overview

Spotifyndr includes a real-time direct messaging system powered by Flask-SocketIO. Messages are persisted to PostgreSQL, with delivery state tracked per message per recipient.

#### 4.5.2 Feature Set

| Feature | Implementation |
|---------|---------------|
| Real-time message delivery | SocketIO `emit` to private room `user_{id}` |
| Read receipts | `message_reads` table; receipt emitted on `READ` event |
| Typing indicators | Ephemeral SocketIO event `typing`; 3-second auto-timeout |
| Online status | Redis key `user_online:{user_id}` with 30s TTL, refreshed by heartbeat |
| Conversation history | Paginated `GET /api/messages/{conversation_id}` — 50 messages per page |
| Conversation list | Sidebar listing all conversations, sorted by last message time |
| Message search | Full-text search within a conversation (PostgreSQL `tsvector`) |
| Attachments | Not in v1 (roadmap item) |

#### 4.5.3 SocketIO Architecture

```
[Client Browser]
      │  socket.io client connects to /socket.io
      ▼
[Flask-SocketIO (gevent)]
      │  authenticate via session cookie on connect
      │  join room: user_{user_id}
      ▼
[Redis Pub/Sub Channel: messages]
      │  SocketIO server subscribes; fans out to connected clients
      ▼
[PostgreSQL]  ←──── persisted by message handler before emit
```

#### 4.5.4 Message Model

```
{
  "id": "uuid",
  "conversation_id": "uuid",
  "sender_id": "integer",
  "content": "string (max 2000 chars)",
  "sent_at": "ISO8601 timestamp",
  "read_at": "ISO8601 timestamp | null",
  "is_deleted": "boolean"
}
```

#### 4.5.5 Conversation Initiation

- Users can open a DM from any profile page via "Message" button.
- If no conversation exists between the two users, one is created automatically.
- Users can only message users they follow OR users who follow them (configurable in settings).

---

### 4.6 User Profiles

#### 4.6.1 Overview

Each user has a public profile page — the user's musical identity card on Spotifyndr. Profiles are powered by Spotify data synced at login and refreshed periodically.

#### 4.6.2 Profile Header

| Element | Source |
|---------|--------|
| Profile Picture | Spotify profile image (cached locally); fallback to generated initials avatar |
| Username | Spotify `display_name` (editable in settings with a local override) |
| Bio | User-entered in settings (max 200 chars) |
| Selected Song | User-pinned track; renders artwork + 30s preview player |
| Followers | Spotifyndr follow graph count |
| Following | Spotifyndr follow graph count |
| Follow / Following Button | Visible to non-owners |
| Edit Profile Button | Visible to profile owner only |

#### 4.6.3 Profile Tabs

| Tab | Content | Privacy Option |
|-----|---------|---------------|
| Spotify Playlists | User's public Spotify playlists (paginated) | Public / Followers-only / Private |
| Reposted Songs | Songs the user has liked/reposted on Spotifyndr | Public / Followers-only / Private |
| Top 5 Songs | User's Spotify top tracks (long term) | Hideable |
| Top 5 Artists | User's Spotify top artists (long term) | Hideable |

#### 4.6.4 Edit Profile

- Accessible to profile owner only (enforced server-side).
- Editable fields: display name override, bio, pinned song (Spotify search widget), top songs visibility, top artists visibility, profile visibility.
- All edits persisted to `users` table; Spotify-sourced data is read-only through the profile UI.

#### 4.6.5 Profile URL

- Canonical URL: `/profile/{spotifyndr_username}`
- Username derived from Spotify `display_name` with collision resolution (append `_N`).

---

### 4.7 Settings

#### 4.7.1 Privacy Settings

| Setting | Options |
|---------|---------|
| Profile Visibility | Public / Followers Only / Private |
| Top Songs Visibility | Show / Hide |
| Top Artists Visibility | Show / Hide |
| Playlists Visibility | Public / Followers Only / Private |
| Allow DMs From | Anyone / Followers Only / Nobody |
| Show Online Status | Everyone / Followers Only / Nobody |
| Match % Visibility | Show / Hide (on Find Mutuals) |

#### 4.7.2 Notification Settings

| Setting | Options |
|---------|---------|
| New Follower | Email / In-App / Both / Off |
| New Message | In-App / Off |
| New Recommendation | In-App / Off |
| Weekly Insights | Email / Off |

#### 4.7.3 Account Settings

| Setting | Action |
|---------|--------|
| Reconnect Spotify | Re-initiates OAuth flow |
| Delete Account | Soft delete (30-day grace period), then hard delete via scheduled Celery task |
| Export My Data | GDPR data export (JSON archive, async generation) |

---

## 5. Machine Learning Specification

### 5.1 Logistic Regression

#### 5.1.1 Purpose

Logistic Regression (LR) serves as the primary ranking model for both the For You Page and the Explore Page. Its role is to predict the probability that a given user will positively engage (play, like, swipe right) with a given content item, given the joint features of the user and the item.

LR is preferred for this use case because:
- Inference is O(d) where d is feature dimensionality — extremely fast, suitable for real-time scoring.
- Outputs calibrated probabilities, which map directly to ranking scores.
- Coefficients are interpretable — facilitating debugging and bias auditing.
- It regularises well with L2 penalty (Ridge), preventing overfitting on sparse user histories.

#### 5.1.2 Feature Engineering

**User Feature Vector (u ∈ ℝ^n)**

| Feature | Description | Dimensionality |
|---------|-------------|---------------|
| `top_genre_vector` | TF-IDF weighted genre distribution from top artists | 100 |
| `avg_track_valence` | Mean valence of top 50 tracks (Spotify Audio Features) | 1 |
| `avg_track_energy` | Mean energy of top 50 tracks | 1 |
| `avg_track_danceability` | Mean danceability | 1 |
| `avg_track_tempo` | Mean BPM, normalised 60–200 | 1 |
| `avg_track_acousticness` | Mean acousticness | 1 |
| `avg_track_instrumentalness` | Mean instrumentalness | 1 |
| `avg_track_loudness` | Mean loudness (dB), normalised | 1 |
| `swipe_right_rate` | Rolling 30-day right-swipe rate | 1 |
| `activity_level` | Log-normalised total events last 30 days | 1 |
| `follower_genre_centroid` | Genre centroid of users this user follows | 100 |

**Item Feature Vector (i ∈ ℝ^m)** (for tracks)

| Feature | Description | Dimensionality |
|---------|-------------|---------------|
| `genre_vector` | Artist genre one-hot (top 100 genres) | 100 |
| `valence` | Spotify audio feature | 1 |
| `energy` | Spotify audio feature | 1 |
| `danceability` | Spotify audio feature | 1 |
| `tempo_norm` | Normalised BPM | 1 |
| `acousticness` | Spotify audio feature | 1 |
| `instrumentalness` | Spotify audio feature | 1 |
| `loudness_norm` | Normalised loudness | 1 |
| `popularity_norm` | Spotify popularity / 100 | 1 |
| `release_recency` | Days since release, log-normalised | 1 |

**Interaction Features (u ⊗ i, element-wise product of genre vectors)**

| Feature | Description | Dimensionality |
|---------|-------------|---------------|
| `genre_overlap` | Element-wise product of user and item genre vectors | 100 |
| `valence_delta` | `|user_avg_valence - item_valence|` | 1 |
| `energy_delta` | `|user_avg_energy - item_energy|` | 1 |

**Total feature dimensionality:** ~413 features per (user, item) pair.

#### 5.1.3 Labels

| Event | Label |
|-------|-------|
| Swipe Right | 1 (positive) |
| Play to >80% completion | 1 (positive) |
| Swipe Left | 0 (negative) |
| Play skip within 10s | 0 (negative) |
| No interaction (sampled) | 0 (negative, down-sampled 5:1) |

Negative sampling is critical: for every positive event, 5 negatives are randomly sampled from the candidate pool to prevent class imbalance.

#### 5.1.4 Model Architecture

```python
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

model = Pipeline([
    ('scaler', StandardScaler()),
    ('lr', LogisticRegression(
        penalty='l2',
        C=1.0,           # Regularisation strength (tuned via CV)
        solver='lbfgs',
        max_iter=1000,
        class_weight='balanced',
        random_state=42
    ))
])
```

One model is maintained per user (personalised) once sufficient data exists (>50 events). Users with insufficient data fall back to the global model.

#### 5.1.5 Training Process

**Global Model Training (nightly, 02:00 UTC via Celery Beat):**

1. Pull all `recommendation_events` from last 90 days from PostgreSQL.
2. Build (user, item, label) triplets.
3. Compute feature vectors for all users and items.
4. Train global LR model on full dataset.
5. Evaluate against held-out validation set (80/20 split).
6. If AUC-ROC > 0.70, serialise model with `joblib` to `/app/models/global_lr_model.joblib`.
7. Publish model version update to Redis channel `model_updates`.
8. All workers reload model on next request.

**Per-User Model Retraining (triggered after every 20 swipe events):**

1. Fetch user's personal event history (all time).
2. Build feature matrix for that user.
3. Fine-tune: initialise from global model weights, then fit on user data.
4. Serialise to `/app/models/user/{user_id}_lr_model.joblib`.
5. Invalidate user's FYP and Explore cache keys in Redis.

#### 5.1.6 Retraining Process (Online Update)

For immediate responsiveness (before full retraining):
- Maintain a running feature accumulator per user in Redis.
- On swipe, update accumulator and adjust cached ranking scores for similar items.
- This provides a "soft" real-time update without full retraining overhead.

#### 5.1.7 Data Pipeline

```
[Spotify Web API]
      │ Audio features, track metadata
      ▼
[spotify_content_cache table]  ←── refreshed by Celery on access + nightly
      │
      ▼
[feature_pipeline.py]
      │ Builds (user_vector, item_vector, interaction_features)
      ▼
[training_dataset.pkl] (ephemeral, generated at train time)
      │
      ▼
[Scikit-Learn Pipeline]
      │
      ▼
[model.joblib] → Redis cache → Flask inference endpoint
```

#### 5.1.8 Performance Metrics

| Metric | Target | Monitoring |
|--------|--------|-----------|
| AUC-ROC | > 0.72 | Logged per training run |
| Precision@10 | > 0.40 | Logged per training run |
| Recall@10 | > 0.35 | Logged per training run |
| Inference latency (p95) | < 20 ms | Prometheus gauge |
| Model staleness | < 24 hours | Celery Beat monitor |
| Positive label rate in events | 30–70% | Alerts if outside range |

---

### 5.2 K-Nearest Neighbours (KNN)

#### 5.2.1 Purpose

KNN is used to compute pairwise user similarity, powering the match percentage on the Find Mutuals page, the friend suggestion algorithm, and as a secondary signal in the LR recommendation model (via `follower_genre_centroid` feature).

#### 5.2.2 User Feature Vector for KNN

Each user is represented as a fixed-length feature vector:

| Feature | Description | Dimensionality | Weight |
|---------|-------------|---------------|--------|
| `top_genre_distribution` | Normalised genre frequency across top 50 tracks | 100 | 3.0× |
| `top_artist_ids_minhash` | MinHash of top 50 artist IDs (locality-sensitive) | 128 | 2.0× |
| `audio_centroid` | [valence, energy, danceability, tempo, acousticness, instrumentalness] mean | 6 | 1.5× |
| `listening_era` | Weighted mean release decade of top tracks (normalised) | 1 | 1.0× |
| `explicit_preference` | Ratio of explicit tracks in top 50 | 1 | 0.5× |

**Total dimensionality:** 236 features per user.

Features are weighted by domain importance and then L2-normalised before distance computation, ensuring cosine similarity between any two users is well-defined and bounded [−1, 1].

#### 5.2.3 Similarity Scoring

**Distance metric:** Cosine similarity (preferred over Euclidean for high-dimensional sparse genre vectors).

```
similarity(u1, u2) = (u1 · u2) / (‖u1‖ · ‖u2‖)
```

Cosine similarity ranges [−1, 1]. For music taste vectors, values practically range [0, 1] (no negative components after normalisation).

#### 5.2.4 KNN Algorithm Configuration

```python
from sklearn.neighbors import NearestNeighbors

knn = NearestNeighbors(
    n_neighbors=50,        # Top 50 similar users per user
    metric='cosine',
    algorithm='brute',     # Exact; switch to 'ball_tree' at 50k+ users
    n_jobs=-1              # Parallelise over all cores
)
knn.fit(user_feature_matrix)  # shape: (n_users, 236)
```

For each user, `knn.kneighbors()` returns the 50 nearest neighbours and their cosine distances.

#### 5.2.5 Percentage Conversion

Raw cosine similarity is converted to a display percentage:

```
match_pct = round(cosine_similarity * 100, 1)
```

Floor applied at 0% (no negative percentages displayed). Users with similarity < 0.10 (< 10%) are excluded from Find Mutuals results.

#### 5.2.6 Neighbour Selection & Filtering

From the 50 raw KNN neighbours, the displayed set is filtered by:

1. **Privacy filter:** Exclude users with `profile_visibility = 'private'`.
2. **Block filter:** Exclude blocked users (bidirectional).
3. **Self-exclusion:** User never appears as their own match.
4. **Already-following filter:** Users the current user already follows are shown with a "Following" state on the Follow button (not hidden).
5. **Minimum similarity floor:** Only users with match% ≥ 10% are shown.

The final result is sorted by `match_pct DESC` by default.

#### 5.2.7 Precomputation Schedule

- Full KNN fit runs nightly at 03:00 UTC via Celery Beat (after LR model update completes).
- Results written to `user_similarities` table: `(user_id, similar_user_id, similarity_score, computed_at)`.
- Partial recomputation triggered when a user's feature vector changes (new Spotify data imported, 50+ swipe events since last computation).
- `computed_at` timestamp surfaced in UI: "Based on data from X hours ago".

#### 5.2.8 Friend Suggestion Ranking

Beyond pure similarity, the friend suggestion order incorporates:

```
final_score = (0.7 × match_pct) + (0.2 × mutual_follower_bonus) + (0.1 × activity_recency_bonus)
```

- `mutual_follower_bonus`: +10 if a user the current user follows also follows the suggested user.
- `activity_recency_bonus`: +10 if suggested user was active on Spotifyndr in last 7 days; +5 if last 30 days.

---

## 6. Database Design

### 6.1 Schema Overview

All tables use PostgreSQL with UUID primary keys where noted, snake_case naming, and timezone-aware timestamps (`TIMESTAMP WITH TIME ZONE`).

### 6.2 Table Definitions

#### 6.2.1 `users`

The central user table. One row per Spotifyndr account (1:1 with a Spotify account).

```sql
CREATE TABLE users (
    id                      SERIAL PRIMARY KEY,
    spotify_user_id         VARCHAR(255) UNIQUE NOT NULL,
    display_name            VARCHAR(255),
    display_name_override   VARCHAR(255),          -- User-set override
    bio                     VARCHAR(200),
    email                   VARCHAR(255),          -- From Spotify, encrypted
    profile_image_url       VARCHAR(1024),         -- Cached Spotify image URL
    profile_image_cached_at TIMESTAMPTZ,
    pinned_track_id         VARCHAR(255),          -- Spotify track ID
    encrypted_access_token  TEXT NOT NULL,
    encrypted_refresh_token TEXT NOT NULL,
    token_expires_at        TIMESTAMPTZ NOT NULL,
    spotify_product         VARCHAR(50),           -- 'premium' | 'free'
    country                 VARCHAR(5),
    follower_count          INTEGER DEFAULT 0,
    following_count         INTEGER DEFAULT 0,
    is_active               BOOLEAN DEFAULT TRUE,
    deleted_at              TIMESTAMPTZ,           -- Soft delete
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW(),

    -- Privacy settings (denormalised for query performance)
    privacy_profile_visibility  VARCHAR(20) DEFAULT 'public',   -- 'public'|'followers'|'private'
    privacy_top_songs           BOOLEAN DEFAULT TRUE,
    privacy_top_artists         BOOLEAN DEFAULT TRUE,
    privacy_playlists           VARCHAR(20) DEFAULT 'public',
    privacy_allow_dms           VARCHAR(20) DEFAULT 'anyone',   -- 'anyone'|'followers'|'nobody'
    privacy_show_online         VARCHAR(20) DEFAULT 'everyone', -- 'everyone'|'followers'|'nobody'
    privacy_show_match_pct      BOOLEAN DEFAULT TRUE,

    -- Notification preferences
    notif_new_follower          VARCHAR(20) DEFAULT 'in_app',
    notif_new_message           VARCHAR(20) DEFAULT 'in_app',
    notif_recommendations       BOOLEAN DEFAULT TRUE,
    notif_weekly_insights       BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_users_spotify_id ON users(spotify_user_id);
CREATE INDEX idx_users_display_name ON users USING gin(to_tsvector('english', COALESCE(display_name_override, display_name, '')));
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
```

#### 6.2.2 `follows`

Directional follow graph.

```sql
CREATE TABLE follows (
    id              BIGSERIAL PRIMARY KEY,
    follower_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_follow UNIQUE (follower_id, following_id),
    CONSTRAINT no_self_follow CHECK (follower_id != following_id)
);

CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);
```

#### 6.2.3 `conversations`

Each DM thread between exactly two users.

```sql
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_a   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    participant_b   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ,
    CONSTRAINT uq_conversation UNIQUE (LEAST(participant_a, participant_b), GREATEST(participant_a, participant_b))
);

CREATE INDEX idx_conv_participant_a ON conversations(participant_a);
CREATE INDEX idx_conv_participant_b ON conversations(participant_b);
CREATE INDEX idx_conv_last_message ON conversations(last_message_at DESC);
```

#### 6.2.4 `messages`

```sql
CREATE TABLE messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    content             TEXT NOT NULL CHECK (char_length(content) <= 2000),
    sent_at             TIMESTAMPTZ DEFAULT NOW(),
    read_at             TIMESTAMPTZ,
    is_deleted          BOOLEAN DEFAULT FALSE,
    search_vector       TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, sent_at DESC);
CREATE INDEX idx_messages_search ON messages USING gin(search_vector);
```

#### 6.2.5 `swipe_history`

Records every Explore Page swipe for model training and deduplication.

```sql
CREATE TABLE swipe_history (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    track_id        VARCHAR(255) NOT NULL,  -- Spotify track ID
    direction       VARCHAR(10) NOT NULL CHECK (direction IN ('left', 'right')),
    swiped_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_swipe_unique ON swipe_history(user_id, track_id);
CREATE INDEX idx_swipe_user_time ON swipe_history(user_id, swiped_at DESC);
```

#### 6.2.6 `recommendation_events`

General-purpose event log powering ML training.

```sql
CREATE TABLE recommendation_events (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_type    VARCHAR(20) NOT NULL,   -- 'track'|'artist'|'podcast'|'playlist'
    content_id      VARCHAR(255) NOT NULL,  -- Spotify content ID
    event_type      VARCHAR(30) NOT NULL,   -- 'swipe_right'|'swipe_left'|'play'|'skip'|'save'|'impression'
    label           SMALLINT,              -- 1 = positive, 0 = negative (derived)
    source          VARCHAR(30),           -- 'explore'|'fyp'|'search'
    session_id      VARCHAR(128),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_user ON recommendation_events(user_id, created_at DESC);
CREATE INDEX idx_events_training ON recommendation_events(user_id, label, created_at);
```

#### 6.2.7 `user_feature_vectors`

Persisted feature vectors for ML. Also maintained in Redis for real-time access.

```sql
CREATE TABLE user_feature_vectors (
    user_id         INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    feature_vector  FLOAT8[] NOT NULL,     -- 236-element array
    computed_at     TIMESTAMPTZ DEFAULT NOW(),
    event_count     INTEGER DEFAULT 0      -- events incorporated into this vector
);
```

#### 6.2.8 `user_similarities`

Pre-computed KNN similarity scores.

```sql
CREATE TABLE user_similarities (
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    similar_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    similarity_score FLOAT4 NOT NULL CHECK (similarity_score BETWEEN 0 AND 1),
    computed_at     TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, similar_user_id)
);

CREATE INDEX idx_similarity_user ON user_similarities(user_id, similarity_score DESC);
```

#### 6.2.9 `spotify_content_cache`

Cached Spotify content metadata to reduce API calls and avoid rate limits.

```sql
CREATE TABLE spotify_content_cache (
    spotify_id      VARCHAR(255) PRIMARY KEY,
    content_type    VARCHAR(20) NOT NULL,   -- 'track'|'artist'|'album'|'playlist'|'podcast'
    data            JSONB NOT NULL,         -- Full Spotify API response object
    cached_at       TIMESTAMPTZ DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_cache_type ON spotify_content_cache(content_type);
CREATE INDEX idx_cache_expiry ON spotify_content_cache(expires_at);
```

#### 6.2.10 `user_top_content`

User's Spotify top tracks and artists at various time ranges.

```sql
CREATE TABLE user_top_content (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_type    VARCHAR(20) NOT NULL,   -- 'track'|'artist'
    time_range      VARCHAR(20) NOT NULL,   -- 'short_term'|'medium_term'|'long_term'
    spotify_id      VARCHAR(255) NOT NULL,
    rank_position   SMALLINT NOT NULL,
    synced_at       TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_user_content UNIQUE (user_id, content_type, time_range, spotify_id)
);

CREATE INDEX idx_top_content_user ON user_top_content(user_id, content_type, time_range);
```

#### 6.2.11 `user_playlists`

Cached playlist metadata for profile display.

```sql
CREATE TABLE user_playlists (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    spotify_playlist_id VARCHAR(255) NOT NULL,
    name            VARCHAR(255),
    description     TEXT,
    image_url       VARCHAR(1024),
    track_count     INTEGER,
    is_public       BOOLEAN DEFAULT TRUE,
    synced_at       TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_user_playlist UNIQUE (user_id, spotify_playlist_id)
);
```

#### 6.2.12 `blocks`

User block relationships.

```sql
CREATE TABLE blocks (
    id              BIGSERIAL PRIMARY KEY,
    blocker_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    blocked_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_block UNIQUE (blocker_id, blocked_id)
);
```

#### 6.2.13 `notifications`

In-app notification queue.

```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            VARCHAR(50) NOT NULL,   -- 'new_follower'|'new_message'|'recommendation'
    actor_id        INTEGER REFERENCES users(id) ON DELETE SET NULL,
    payload         JSONB,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notif_user ON notifications(user_id, is_read, created_at DESC);
```

---

## 7. API Design

### 7.1 Base URL and Versioning

All REST endpoints are prefixed with `/api/v1`. Responses use `application/json`. All timestamps are ISO 8601 UTC. HTTP status codes follow RFC 7231 conventions.

### 7.2 Authentication

All `/api/v1/*` endpoints require a valid server-side session. Unauthenticated requests receive `401 Unauthorized`. The session cookie is sent automatically by the browser.

### 7.3 Endpoint Catalogue

#### 7.3.1 Auth Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/auth/login` | Initiates Spotify OAuth flow (redirect) |
| GET | `/auth/callback` | OAuth callback handler |
| POST | `/auth/logout` | Invalidates session |

#### 7.3.2 User Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/v1/users/me` | Current user profile | ✓ |
| PATCH | `/api/v1/users/me` | Update profile (bio, display_name_override, pinned_track_id) | ✓ |
| GET | `/api/v1/users/{username}` | Public profile by username | ✓ |
| GET | `/api/v1/users/{username}/playlists` | User's public playlists | ✓ |
| GET | `/api/v1/users/{username}/top-tracks` | Top 5 tracks | ✓ |
| GET | `/api/v1/users/{username}/top-artists` | Top 5 artists | ✓ |
| GET | `/api/v1/users/search?q=&page=&limit=` | Search users | ✓ |
| DELETE | `/api/v1/users/me` | Delete account (initiates soft delete) | ✓ |

**PATCH /api/v1/users/me Request:**
```json
{
  "bio": "string (max 200)",
  "display_name_override": "string (max 255)",
  "pinned_track_id": "spotify_track_id"
}
```

#### 7.3.3 Follow Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/follow/{user_id}` | Follow a user |
| DELETE | `/api/v1/follow/{user_id}` | Unfollow a user |
| GET | `/api/v1/users/{user_id}/followers?page=&limit=` | Follower list |
| GET | `/api/v1/users/{user_id}/following?page=&limit=` | Following list |

**POST /api/v1/follow/{user_id} Response:**
```json
{
  "following": true,
  "follower_count": 142
}
```

#### 7.3.4 FYP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/fyp?page=&content_type=` | Personalised recommendations |
| GET | `/api/v1/fyp/search?q=&type=&page=` | Search with FYP content-type filter |

**GET /api/v1/fyp Response:**
```json
{
  "sections": [
    {
      "type": "tracks",
      "title": "Recommended Songs",
      "items": [
        {
          "spotify_id": "...",
          "name": "Track Name",
          "artist": "Artist Name",
          "album_art": "https://...",
          "preview_url": "https://...",
          "score": 0.87
        }
      ]
    }
  ],
  "page": 1,
  "has_next": true
}
```

#### 7.3.5 Explore Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/explore/next-batch` | Fetch next 10 swipeable cards |
| POST | `/api/v1/explore/swipe` | Record swipe event |

**POST /api/v1/explore/swipe Request:**
```json
{
  "track_id": "spotify_track_id",
  "direction": "right"
}
```

**POST /api/v1/explore/swipe Response:**
```json
{
  "recorded": true,
  "swipe_count": 47
}
```

#### 7.3.6 Mutuals Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/mutuals?sort=match&page=&limit=` | Find mutuals with sorting |
| GET | `/api/v1/mutuals/{user_id}/score` | Match score for a specific user |

**GET /api/v1/mutuals Response:**
```json
{
  "users": [
    {
      "id": 42,
      "username": "musiclover99",
      "display_name": "Music Lover",
      "profile_image": "https://...",
      "follower_count": 112,
      "following_count": 89,
      "match_percentage": 87.4,
      "is_following": false,
      "follows_you": true
    }
  ],
  "page": 1,
  "has_next": true
}
```

#### 7.3.7 Messaging Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/conversations` | List all conversations |
| POST | `/api/v1/conversations` | Create or retrieve conversation with user |
| GET | `/api/v1/conversations/{id}/messages?before=&limit=` | Paginated message history |
| POST | `/api/v1/conversations/{id}/messages` | Send message (REST fallback; primary via SocketIO) |
| POST | `/api/v1/conversations/{id}/read` | Mark messages as read |

#### 7.3.8 Settings Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/settings` | Retrieve current settings |
| PATCH | `/api/v1/settings/privacy` | Update privacy settings |
| PATCH | `/api/v1/settings/notifications` | Update notification preferences |
| POST | `/api/v1/settings/export-data` | Request GDPR data export |

#### 7.3.9 Notification Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/notifications?unread=true` | Fetch notifications |
| PATCH | `/api/v1/notifications/{id}/read` | Mark notification read |
| PATCH | `/api/v1/notifications/read-all` | Mark all notifications read |

### 7.4 Error Response Format

All errors return a consistent JSON structure:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested user does not exist.",
    "status": 404
  }
}
```

### 7.5 Rate Limiting

| Endpoint Group | Limit |
|----------------|-------|
| Auth endpoints | 10 requests / minute / IP |
| General API | 120 requests / minute / user |
| Swipe endpoint | 200 requests / minute / user |
| Spotify-proxied content | 60 requests / minute / user |

Rate limit state stored in Redis with sliding window counters. `429 Too Many Requests` with `Retry-After` header returned on breach.

---

## 8. Spotify API Integration

### 8.1 Required OAuth Scopes

| Scope | Purpose |
|-------|---------|
| `user-read-private` | User's subscription level, country |
| `user-read-email` | User email (for notifications) |
| `user-top-read` | Top artists and tracks |
| `user-library-read` | Saved tracks and albums |
| `playlist-read-private` | Private playlists for profile |
| `playlist-read-collaborative` | Collaborative playlists |
| `user-follow-read` | Spotify follows (optional — cross-reference) |

### 8.2 Data Synchronisation Strategy

| Data Type | Sync Frequency | Trigger |
|-----------|---------------|---------|
| Top Tracks (all 3 ranges) | On login + weekly | Celery Beat `sync_user_spotify` |
| Top Artists (all 3 ranges) | On login + weekly | Celery Beat `sync_user_spotify` |
| Saved Tracks | On login + weekly | Celery Beat |
| Playlists | On login + weekly | Celery Beat |
| Profile Image | On login + monthly | Celery Beat |
| Audio Features (for cached tracks) | On demand + nightly | Cache miss → API call |

### 8.3 Rate Limit Handling

Spotify enforces rate limits per application (not per user) at approximately 100 requests per 10-second window.

**Mitigation strategy:**

1. **Content caching:** All Spotify content responses cached in `spotify_content_cache` with TTL (tracks: 7 days, artists: 7 days, playlists: 1 day, search results: 1 hour).
2. **Request queuing:** Spotify API calls are dispatched via a Celery task queue with a dedicated `spotify_api` queue and a concurrency cap of 10 workers. Requests throttled with exponential backoff on 429 responses.
3. **Batch requests:** Audio features fetched in batches of 100 tracks (Spotify supports up to 100 per request).
4. **Staggered sync:** Nightly syncs distributed over a 4-hour window using Celery ETA to spread API load.

### 8.4 Token Refresh Process

```
[request arrives for user]
      │
      ▼
[middleware checks token_expires_at]
      │
      ├── expires_in > 300s ──▶ [proceed with current token]
      │
      └── expires_in ≤ 300s ──▶ [acquire Redis lock refresh:user:{id}]
                                        │
                                        ├── lock acquired ──▶ POST /token (Spotify)
                                        │                          │
                                        │                     [store new tokens + expires_at]
                                        │                          │
                                        │                     [release lock]
                                        │
                                        └── lock not acquired ──▶ [wait 100ms, retry]
```

### 8.5 Content Retrieval Architecture

```
[Client Request for Content]
      │
      ▼
[Check Redis L1 cache (TTL: 1hr)]
      │
      ├── HIT ──▶ [return cached response]
      │
      └── MISS ──▶ [Check PostgreSQL spotify_content_cache]
                          │
                          ├── HIT + not expired ──▶ [populate Redis, return]
                          │
                          └── MISS or expired ──▶ [Spotify Web API call]
                                                          │
                                                    [store in PostgreSQL + Redis]
                                                          │
                                                    [return response]
```

### 8.6 Attribution Requirements (Spotify Guidelines Compliance)

- All Spotify content displayed with "Powered by Spotify" attribution.
- Album artwork displayed as-is (no modification).
- Track names, artist names, album names displayed exactly as returned by Spotify.
- Audio previews played via Spotify's preview URL (streamed, not downloaded).
- Spotify logo displayed according to Spotify's branding guidelines in the footer and on any Spotify-sourced content cards.
- The platform name "Spotifyndr" does not incorporate the word "Spotify" in a way that implies official affiliation.

---

## 9. Security Architecture

### 9.1 Authentication Security

- Spotify OAuth 2.0 with PKCE. No password storage.
- Session IDs: 128-bit CSPRNG, stored HttpOnly + Secure + SameSite=Strict.
- Session fixation prevention: session ID regenerated on every login.
- Concurrent session limit: 5 per user.
- Brute force protection: 10 login attempts per IP per minute (Redis-backed counter).

### 9.2 Authorization

- All endpoints enforce authentication via `@login_required` decorator.
- Resource ownership enforced at the service layer (not just route level).
- Follow-relationship-gated messaging: DM initiation checks follow relationship before creating conversation.
- Profile edit: server-side check `current_user.id == profile.user_id` before any write.

### 9.3 Role-Based Access Control (RBAC)

| Role | Capabilities |
|------|-------------|
| `user` (default) | Full access to all user-facing features within own scope |
| `moderator` | Read-only access to reported content; can soft-delete messages |
| `admin` | Full read/write; can hard-delete users; access to `/admin/*` dashboard |

Roles stored in `users.role` column (enum type). Admin routes prefixed `/admin` protected by `@admin_required` decorator.

### 9.4 CSRF Protection

- Flask-WTF `CSRFProtect` enabled globally.
- CSRF tokens injected into all HTML forms and exposed via `GET /api/v1/csrf-token` for SPA-style fetch calls.
- `X-CSRFToken` header required on all state-mutating API requests.
- SocketIO connections authenticated via session (no separate CSRF needed; SameSite cookie provides equivalent protection).

### 9.5 XSS Protection

- Jinja2 autoescaping enabled globally (`autoescape=True`).
- Content Security Policy (CSP) header enforced via Nginx:
  ```
  Content-Security-Policy: default-src 'self'; img-src 'self' i.scdn.co *.scdn.co data:; media-src *.spotify.com; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self' wss:
  ```
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- Referrer-Policy: `strict-origin-when-cross-origin`

### 9.6 SQL Injection Prevention

- All database interactions via SQLAlchemy ORM using parameterised queries.
- Raw SQL fragments (for `tsvector` searches etc.) use `text()` with bound parameters only.
- No string-interpolated SQL queries anywhere in codebase (enforced by linting rule `S608`).

### 9.7 Rate Limiting

Implemented via `flask-limiter` backed by Redis.

```python
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://redis:6379",
    default_limits=["200 per day", "50 per hour"]
)
```

Per-endpoint overrides as documented in §7.5.

### 9.8 Secrets Management

- All secrets (database URL, Redis URL, Spotify client secret, session secret, encryption key) loaded from environment variables.
- Never committed to version control. `.env.example` provided with placeholder values.
- In production: injected via Docker secrets or a secrets manager (HashiCorp Vault or AWS Secrets Manager).
- Spotify tokens encrypted in the database with AES-256-GCM using a key stored in the environment (`TOKEN_ENCRYPTION_KEY`).
- Encryption handled by the `cryptography` library (`Fernet` symmetric encryption).

### 9.9 Input Validation

- Pydantic v2 models used for all incoming request body validation.
- URL parameters validated with type coercion and range checks at the route level.
- File upload endpoints (not in v1) will enforce MIME type and size limits.

### 9.10 Secure Deployment Checklist

- [ ] TLS 1.3 enforced; TLS 1.0/1.1 disabled in Nginx.
- [ ] HSTS header: `Strict-Transport-Security: max-age=31536000; includeSubDomains`.
- [ ] PostgreSQL not exposed externally; accessible only on Docker internal network.
- [ ] Redis not exposed externally; no auth bypass possible on internal network.
- [ ] Gunicorn workers run as non-root user (`www-data`).
- [ ] Debug mode disabled (`FLASK_DEBUG=0`) in production.
- [ ] Dependency vulnerability scanning via `pip-audit` in CI pipeline.
- [ ] Docker images scanned with Trivy in CI.

---

## 10. Frontend Architecture

### 10.1 Rendering Strategy

- **Server-Side Rendering (SSR):** All page shells rendered by Jinja2. Initial data injected as `data-*` attributes or inline JSON for fast LCP and SEO-friendly markup.
- **Client-Side Enhancement:** JavaScript progressively enhances SSR pages. Swipe interactions, infinite scroll, real-time messaging, and search are client-side, communicating with REST APIs and SocketIO.
- No frontend framework (React/Vue) in v1. Vanilla JS with a lightweight custom component pattern.

### 10.2 Page Architecture

| Page | URL | Rendering | Key JS Modules |
|------|-----|-----------|----------------|
| Landing | `/` | SSR | — |
| For You Page | `/fyp` | SSR + CSR (search, infinite scroll) | `fyp.js`, `search.js` |
| Explore | `/explore` | SSR + CSR (swipe engine) | `swipe.js`, `audio-player.js` |
| Find Mutuals | `/mutuals` | SSR + CSR (sort, search, follow) | `mutuals.js`, `follow.js` |
| Messages | `/messages` | SSR + CSR (SocketIO) | `messaging.js`, `socket.js` |
| Profile | `/profile/{username}` | SSR + CSR (tabs) | `profile.js`, `tabs.js` |
| Settings | `/settings` | SSR + CSR (form AJAX) | `settings.js` |

### 10.3 JavaScript Module Structure

```
static/js/
├── core/
│   ├── api.js          # Fetch wrapper with CSRF token injection
│   ├── socket.js       # SocketIO client initialisation
│   ├── toast.js        # Toast notification system
│   └── utils.js        # Debounce, throttle, formatters
├── pages/
│   ├── fyp.js
│   ├── explore/
│   │   ├── swipe.js    # Touch + mouse swipe engine
│   │   └── card.js     # Card DOM construction
│   ├── mutuals.js
│   ├── messaging.js
│   ├── profile.js
│   └── settings.js
└── components/
    ├── audio-player.js # 30s preview player (Web Audio API)
    ├── follow-button.js
    ├── infinite-scroll.js
    └── search-bar.js
```

### 10.4 State Management

No centralised state store in v1. State is managed locally per component using module-scoped variables and DOM data attributes as source of truth for simple page state. SocketIO events trigger direct DOM updates in messaging module.

### 10.5 Performance

- CSS and JS assets minified and hashed (via Flask-Assets + webassets).
- Images lazy-loaded with `loading="lazy"` and Intersection Observer for JS-loaded images.
- Spotify album artwork served directly from Spotify's CDN (no re-hosting).
- Audio preview loaded on-demand (not preloaded) to avoid unnecessary bandwidth.
- Service Worker (v2 roadmap): offline support for cached profile and FYP data.

### 10.6 Responsive Design (Mobile-First)

Breakpoints:

| Breakpoint | Width | Layout |
|------------|-------|--------|
| `sm` | 0–599px | Single column; navigation as bottom tab bar |
| `md` | 600–959px | Two columns; sidebar collapsed |
| `lg` | 960px+ | Three columns where applicable |

The Explore swipe page is fullscreen on mobile (no sidebar). On desktop, the swipe card is centred with a fixed max-width of 480px.

---

## 11. UI/UX Design

### 11.1 Design Philosophy

Spotifyndr's visual identity is heavily inspired by Spotify's design language: dark backgrounds, vibrant green accents, bold typography, and high-contrast content cards. The UI is clean, immersive, and music-first. However, the application is an independent product and does not use Spotify's proprietary UI components, fonts, or trademarked visual marks.

### 11.2 Design Tokens

```css
:root {
    /* Backgrounds */
    --color-bg-base:        #121212;
    --color-bg-elevated:    #1e1e1e;
    --color-bg-card:        #282828;
    --color-bg-highlight:   #3e3e3e;

    /* Brand accent */
    --color-accent:         #1ed760;
    --color-accent-hover:   #1fdf64;
    --color-accent-muted:   #1db954;

    /* Text */
    --color-text-primary:   #ffffff;
    --color-text-secondary: #b3b3b3;
    --color-text-muted:     #6a6a6a;

    /* Semantic */
    --color-error:          #e5534b;
    --color-warning:        #e3a800;
    --color-success:        #1ed760;

    /* Typography */
    --font-family:          'Circular', 'Inter', -apple-system, sans-serif;
    --font-size-xs:         11px;
    --font-size-sm:         13px;
    --font-size-md:         14px;
    --font-size-lg:         16px;
    --font-size-xl:         24px;
    --font-size-2xl:        32px;

    /* Spacing */
    --space-xs:             4px;
    --space-sm:             8px;
    --space-md:             16px;
    --space-lg:             24px;
    --space-xl:             32px;
    --space-2xl:            48px;

    /* Radii */
    --radius-sm:            4px;
    --radius-md:            8px;
    --radius-lg:            16px;
    --radius-pill:          50px;
    --radius-circle:        50%;

    /* Shadows */
    --shadow-card:          0 4px 24px rgba(0,0,0,0.5);
    --shadow-elevated:      0 8px 40px rgba(0,0,0,0.7);
}
```

### 11.3 Navigation

**Desktop:** Fixed left sidebar (240px) containing:
- Spotifyndr logo (top)
- Primary navigation: FYP, Explore, Find Mutuals, Messages
- User avatar + username (bottom)
- Settings link (bottom)

**Mobile:** Bottom tab bar with icons for the four primary pages. Navigation labels hidden; icons only (with `aria-label`).

### 11.4 Explore Page UX

- Card stack: 3 cards rendered in DOM; only the top card is interactive.
- Background blurs to a desaturated version of the card artwork using CSS `filter: blur(40px)`.
- Green glow on right-swipe start; red glow on left-swipe start.
- Action buttons (❤ / ✕) fixed at the bottom, pulse briefly after a swipe is recorded.
- Audio preview auto-plays with a waveform visualisation (canvas-based).

### 11.5 Accessibility

- WCAG 2.1 AA compliance target.
- All interactive elements keyboard-navigable.
- Focus rings visible (`outline: 2px solid var(--color-accent)`).
- All images have `alt` attributes.
- `aria-live` regions for dynamic content updates (toast notifications, message count).
- Swipe page: keyboard arrow keys trigger swipe actions; `aria-label` on all icon buttons.
- Colour contrast: minimum 4.5:1 for body text, 3:1 for large text.

### 11.6 Spotify Branding Compliance

- The "Powered by Spotify" attribution is displayed in the footer and on all Spotify-sourced content cards (light green on dark background).
- No Spotify icons or logo marks are used in navigation or branding areas of Spotifyndr.
- Audio preview players include a link to the full track on Spotify (`spotify.com` deep link).
- No Spotify trademarks appear in Spotifyndr's own name, tagline, or marketing copy.

---

## 12. Folder Structure

```
spotifyndr/
├── .env.example                    # Environment variable template
├── .gitignore
├── docker-compose.yml              # Full-stack compose (dev)
├── docker-compose.prod.yml         # Production overrides
├── Dockerfile                      # Flask app image
├── Dockerfile.celery               # Celery worker image
├── Makefile                        # Developer shortcuts
├── README.md
├── requirements.txt                # Python dependencies (pinned)
├── requirements-dev.txt            # Dev dependencies (pytest, etc.)
│
├── nginx/
│   ├── nginx.conf                  # Main Nginx config
│   └── spotifyndr.conf             # App-specific server block
│
├── app/
│   ├── __init__.py                 # Flask application factory
│   ├── config.py                   # Configuration classes (Dev/Prod/Test)
│   ├── extensions.py               # SQLAlchemy, Redis, SocketIO, Celery init
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py               # /auth/login, /auth/callback, /auth/logout
│   │   ├── spotify_oauth.py        # PKCE flow implementation
│   │   └── decorators.py           # @login_required, @admin_required
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── users.py            # User endpoints
│   │   │   ├── follows.py          # Follow/unfollow endpoints
│   │   │   ├── fyp.py              # For You Page endpoints
│   │   │   ├── explore.py          # Explore/swipe endpoints
│   │   │   ├── mutuals.py          # Find Mutuals endpoints
│   │   │   ├── messaging.py        # REST messaging endpoints
│   │   │   ├── settings.py         # Settings endpoints
│   │   │   └── notifications.py    # Notification endpoints
│   │   └── errors.py               # Error handlers (404, 429, 500)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── follow.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── swipe.py
│   │   ├── recommendation_event.py
│   │   ├── user_feature_vector.py
│   │   ├── user_similarity.py
│   │   ├── spotify_cache.py
│   │   ├── user_top_content.py
│   │   ├── notification.py
│   │   └── block.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── spotify_service.py      # Spotify Web API client (rate-limit-aware)
│   │   ├── user_service.py         # User CRUD, profile logic
│   │   ├── follow_service.py
│   │   ├── recommendation_service.py
│   │   ├── messaging_service.py
│   │   ├── notification_service.py
│   │   ├── similarity_service.py   # KNN computation
│   │   └── token_service.py        # Encrypt/decrypt tokens, refresh logic
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── feature_pipeline.py     # Feature vector construction
│   │   ├── logistic_regression.py  # LR model training + inference
│   │   ├── knn_similarity.py       # KNN fitting + similarity scoring
│   │   ├── model_store.py          # joblib serialisation + Redis model cache
│   │   └── metrics.py              # AUC-ROC, Precision@K logging
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py           # Celery application factory
│   │   ├── spotify_sync.py         # full_spotify_import, sync_user_spotify
│   │   ├── ml_tasks.py             # retrain_user_model, retrain_global_model, knn_fit
│   │   ├── token_refresh.py        # refresh_expiring_tokens
│   │   └── maintenance.py          # cleanup_expired_cache, process_deletions
│   │
│   ├── sockets/
│   │   ├── __init__.py
│   │   ├── events.py               # SocketIO event handlers
│   │   └── namespace.py            # /messaging namespace
│   │
│   ├── views/
│   │   ├── __init__.py
│   │   ├── main.py                 # Landing page
│   │   ├── fyp.py                  # FYP page
│   │   ├── explore.py              # Explore page
│   │   ├── mutuals.py              # Find Mutuals page
│   │   ├── messaging.py            # Messaging page
│   │   ├── profile.py              # Profile page
│   │   └── settings.py             # Settings page
│   │
│   └── templates/
│       ├── base.html               # Base layout with nav, SocketIO init
│       ├── landing.html
│       ├── fyp.html
│       ├── explore.html
│       ├── mutuals.html
│       ├── messaging.html
│       ├── profile.html
│       ├── settings.html
│       └── partials/
│           ├── _nav_sidebar.html
│           ├── _nav_mobile.html
│           ├── _track_card.html
│           ├── _user_card.html
│           ├── _playlist_card.html
│           ├── _artist_card.html
│           └── _toast.html
│
├── static/
│   ├── css/
│   │   ├── main.css                # Design tokens + global styles
│   │   ├── components/
│   │   │   ├── cards.css
│   │   │   ├── navigation.css
│   │   │   ├── buttons.css
│   │   │   ├── modals.css
│   │   │   ├── audio-player.css
│   │   │   └── swipe.css
│   │   └── pages/
│   │       ├── fyp.css
│   │       ├── explore.css
│   │       ├── mutuals.css
│   │       ├── messaging.css
│   │       ├── profile.css
│   │       └── settings.css
│   ├── js/
│   │   ├── core/
│   │   │   ├── api.js
│   │   │   ├── socket.js
│   │   │   ├── toast.js
│   │   │   └── utils.js
│   │   ├── pages/
│   │   │   ├── fyp.js
│   │   │   ├── explore/
│   │   │   │   ├── swipe.js
│   │   │   │   └── card.js
│   │   │   ├── mutuals.js
│   │   │   ├── messaging.js
│   │   │   ├── profile.js
│   │   │   └── settings.js
│   │   └── components/
│   │       ├── audio-player.js
│   │       ├── follow-button.js
│   │       ├── infinite-scroll.js
│   │       └── search-bar.js
│   └── img/
│       ├── logo.svg
│       ├── spotify-attribution.svg
│       └── default-avatar.svg
│
├── migrations/                     # Flask-Migrate / Alembic migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── models_store/                   # Persisted ML model files (gitignored)
│   ├── global_lr_model.joblib
│   └── users/                      # Per-user models (user_{id}_lr_model.joblib)
│
└── tests/
    ├── conftest.py                 # Fixtures (test app, test DB, mock Spotify)
    ├── unit/
    │   ├── test_feature_pipeline.py
    │   ├── test_lr_model.py
    │   ├── test_knn_similarity.py
    │   ├── test_token_service.py
    │   └── test_user_service.py
    ├── integration/
    │   ├── test_auth_flow.py
    │   ├── test_follow_api.py
    │   ├── test_messaging_api.py
    │   ├── test_swipe_api.py
    │   └── test_mutuals_api.py
    ├── security/
    │   ├── test_csrf.py
    │   ├── test_auth_bypass.py
    │   └── test_rate_limiting.py
    └── ml/
        ├── test_lr_training.py
        ├── test_knn_output.py
        └── test_recommendation_pipeline.py
```

---

## 13. Testing Strategy

### 13.1 Unit Testing

**Framework:** `pytest` with `pytest-flask`

**Coverage target:** 80% line coverage across `app/` (excluding templates)

**Key test areas:**

| Module | Test Focus |
|--------|-----------|
| `token_service.py` | Encrypt/decrypt round-trip, expired token detection |
| `feature_pipeline.py` | Feature vector shape, dtype, normalisation invariants |
| `logistic_regression.py` | Training on synthetic data, score range [0,1], no NaN outputs |
| `knn_similarity.py` | Cosine similarity bounds, self-similarity = 1.0, percentage conversion |
| `user_service.py` | Profile update validation, display name collision resolution |
| `spotify_service.py` | Cache hit/miss logic, rate limit backoff (mocked Spotify responses) |

### 13.2 Integration Testing

**Fixtures:** In-memory SQLite (for speed) or PostgreSQL (for `tsvector` tests); Redis replaced with `fakeredis`.

**Spotify API:** Mocked with `responses` library using real response fixtures.

**Key integration test scenarios:**

- Full OAuth callback flow: code exchange → user creation → Celery task enqueue
- POST /swipe → swipe_history row created → Celery retraining task enqueued
- POST /follow → follows row created → follower_count denormalised counter updated
- GET /mutuals → returns pre-computed similarity scores in correct order
- SocketIO message send → message persisted → emitted to recipient room
- Rate limit: 11th login attempt within 60s returns 429

### 13.3 Security Testing

- **CSRF bypass attempt:** Omitting `X-CSRFToken` header on POST endpoints → expect 400.
- **Session fixation:** Re-using pre-auth session ID after login → expect new session ID.
- **IDOR:** Requesting another user's private data via direct ID manipulation → expect 403.
- **SQL injection probe:** Malformed query strings in search parameters → expect 400, no DB error.
- **Rate limiting:** Automated requests above limit → expect 429 with correct `Retry-After`.
- **Static analysis:** `bandit` run in CI; `S608` (SQL injection) treated as error.

### 13.4 Machine Learning Testing

- **Feature pipeline determinism:** Same input → same output vector across runs.
- **Model serialisation:** `joblib` dump + load preserves predictions within 1e-6 tolerance.
- **KNN output bounds:** All similarity scores ∈ [0, 1]; self-similarity = 1.0.
- **LR training convergence:** Model trained on synthetic data converges (no `ConvergenceWarning`).
- **Negative sampling:** Training dataset label distribution 16%–50% positive after sampling.
- **Regression test:** Pre-trained model scores on a fixed test set must not degrade by > 5% AUC-ROC across code changes.

### 13.5 Performance Testing

**Tool:** `locust`

**Scenarios:**

| Scenario | Users | Ramp | Duration | Pass Criterion |
|----------|-------|------|----------|---------------|
| FYP page load | 200 | 20/s | 5 min | p95 < 300ms, 0% errors |
| Explore swipe burst | 100 | 50/s | 2 min | p95 < 200ms |
| Concurrent messaging | 500 | 10/s | 10 min | SocketIO delivery < 500ms |
| Mutuals page | 100 | 10/s | 5 min | p95 < 400ms |

CI pipeline runs a 60-second smoke performance test on every PR merge to `main`.

---

## 14. Deployment Strategy

### 14.1 Docker Compose (Development)

```yaml
# docker-compose.yml (abbreviated)
services:
  flask:
    build: .
    ports: ["5000:5000"]
    environment:
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://user:pass@postgres:5432/spotifyndr
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
    depends_on: [postgres, redis]

  celery_worker:
    build:
      context: .
      dockerfile: Dockerfile.celery
    command: celery -A app.tasks.celery_app worker -l info -Q default,spotify_api,ml
    environment: *flask_env
    depends_on: [postgres, redis]

  celery_beat:
    build:
      context: .
      dockerfile: Dockerfile.celery
    command: celery -A app.tasks.celery_app beat -l info --scheduler redbeat.RedBeatScheduler
    environment: *flask_env
    depends_on: [redis]

  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: spotifyndr
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on: [flask]
```

### 14.2 Production Architecture

```
[Internet]
    │
    ▼
[Nginx] (TLS termination, static asset serving, rate limiting)
    │
    ├──▶ [/static/*]  →  Served directly by Nginx (no Flask hit)
    │
    └──▶ [/*]  →  Upstream: Gunicorn cluster (4 workers × 2 threads)
                       │
                       ├──▶ [Flask app]
                       │         │
                       │         ├──▶ [PostgreSQL 16]
                       │         ├──▶ [Redis 7]
                       │         └──▶ [Celery (via Redis broker)]
                       │
                       └──▶ [Flask-SocketIO (gevent)]
                                 │
                                 └──▶ [Redis pub/sub]
```

### 14.3 Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4                    # 2× CPU cores
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
threads = 2
timeout = 60
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
loglevel = "info"
access_logfile = "-"
error_logfile = "-"
```

### 14.4 Environment Variables

```bash
# Flask
SECRET_KEY=<128-bit random>
FLASK_ENV=production
FLASK_DEBUG=0

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/spotifyndr
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://redis:6379/0
SESSION_REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/2

# Spotify
SPOTIFY_CLIENT_ID=<from Spotify Developer Dashboard>
SPOTIFY_CLIENT_SECRET=<from Spotify Developer Dashboard>
SPOTIFY_REDIRECT_URI=https://spotifyndr.example.com/auth/callback

# Security
TOKEN_ENCRYPTION_KEY=<32-byte Fernet key, base64-encoded>
CSRF_SECRET=<128-bit random>

# ML
MODEL_STORE_PATH=/app/models_store
ML_RETRAIN_THRESHOLD_EVENTS=20
```

### 14.5 CI/CD Pipeline

```
[GitHub Push to main]
      │
      ▼
[GitHub Actions]
      │
      ├── [Lint] flake8 + bandit + black --check
      │
      ├── [Test] pytest --cov=app --cov-fail-under=80
      │
      ├── [Build] docker build → tag with git SHA
      │
      ├── [Scan] trivy image (fail on HIGH/CRITICAL CVEs)
      │
      └── [Deploy] docker-compose pull + up -d (rolling restart)
```

### 14.6 Database Migrations

- Migrations managed by Flask-Migrate (Alembic).
- Migration files committed to version control.
- Deployment runs `flask db upgrade` before new app containers start.
- Rollback: `flask db downgrade -1` on failed deployment.

### 14.7 Backup Strategy

- PostgreSQL: daily `pg_dump` to encrypted S3 bucket (30-day retention).
- Redis: RDB snapshots every 15 minutes to Docker volume; AOF persistence enabled.
- ML models: `models_store/` directory synced to S3 on every successful training run.

---

## 15. Scalability Considerations

### 15.1 Horizontal Scaling Plan (10,000+ Users)

| Component | Current (v1) | At 10k Users |
|-----------|-------------|-------------|
| Flask (Gunicorn) | 1 instance, 4 workers | 3–5 instances behind load balancer |
| PostgreSQL | Single primary | Primary + 1 read replica (PgBouncer pool) |
| Redis | Single instance | Redis Sentinel (1 primary + 2 replicas) |
| Celery | 1 worker, 3 queues | 3 workers (dedicated ML, Spotify, general) |
| SocketIO | Single server | Sticky sessions + Redis adapter for multi-server |

### 15.2 Database Optimisation

- All foreign keys indexed.
- Partial indexes on `users.is_active = TRUE` and similar common filters.
- PgBouncer connection pooling in transaction mode for read replicas.
- `user_similarities` table partitioned by `user_id % 10` at 10k+ users.
- Archived events (> 90 days) moved to `recommendation_events_archive` via pg_partman.

### 15.3 Caching Strategy

| Data | Cache | TTL |
|------|-------|-----|
| User session | Redis | 24 hours (sliding) |
| FYP recommendations | Redis (per-user key) | 1 hour |
| Explore card batch | Redis (per-user key) | 15 minutes |
| Mutuals list | Redis (per-user key) | 6 hours |
| Spotify content | Redis L1 + PostgreSQL L2 | 1 hour / 7 days |
| KNN similarity scores | PostgreSQL (authoritative) + Redis | 6 hours |
| User feature vector | Redis | 30 minutes |

### 15.4 SocketIO at Scale

- Flask-SocketIO configured with Redis message queue (`message_queue=REDIS_URL`).
- Sticky sessions configured in Nginx (`ip_hash` upstream directive) so a user's WebSocket connection always routes to the same Flask instance.
- At 5k+ concurrent WebSocket connections, evaluate migration to dedicated SocketIO cluster (Node.js `socket.io` + Redis adapter) keeping Flask as REST backend only.

### 15.5 ML Model Scalability

- Global model training parallelised with `n_jobs=-1` in Scikit-Learn.
- Per-user models only created after 50+ events (avoids storing thousands of near-identical models).
- Model storage: at 10k users with 50+ events each, estimated 10k × 500KB = 5GB model store (acceptable; backed by S3 at scale).
- At 100k+ users: transition to approximate KNN (Faiss `IndexFlatIP`) and a model serving microservice (Flask-based, separate container).

---

## 16. Future Features

### 16.1 Version 1.1 — Polish & Retention

| Feature | Description |
|---------|-------------|
| Push Notifications | Web Push API for mobile browser notifications (new follower, message) |
| Emoji Reactions | React to messages with emoji (SocketIO event) |
| Message Attachments | Image sharing in DMs (S3 storage) |
| Profile Themes | User-selectable colour themes derived from their top artist's palette |
| Repost Feed | Dedicated feed of tracks reposted by followed users |

### 16.2 Version 1.2 — Discovery Expansion

| Feature | Description |
|---------|-------------|
| Group Listening | Shared listening rooms (multi-user synchronised preview playback) |
| Concert Discovery | Surface upcoming concerts for top artists (via Ticketmaster API integration) |
| Music Quiz | Daily genre/artist trivia generated from user's top tracks |
| Collaborative Playlist Builder | Two matched users co-curate a playlist, exported to Spotify |
| Podcast Rooms | Shared "listening clubs" for podcast episodes |

### 16.3 Version 2.0 — Platform Expansion

| Feature | Description |
|---------|-------------|
| Native Mobile Apps | React Native iOS/Android wrapping the REST/SocketIO backend |
| Music Graph | Interactive visualisation of a user's genre map and artist connections |
| Deep Link to Spotify | "Open in Spotify" CTA on every track/artist using `spotify:` URI scheme |
| Advanced ML | Collaborative filtering (matrix factorisation) replacing/augmenting LR |
| Artist Verification | Verified badge for artist accounts with Spotify-confirmed artist profiles |
| Multi-Platform Support | Apple Music OAuth integration as alternative to Spotify |

### 16.4 Technical Debt & Infrastructure Roadmap

| Item | Target Version |
|------|---------------|
| Service Worker + offline FYP | v1.1 |
| TypeScript migration for static JS | v1.2 |
| OpenTelemetry distributed tracing | v1.1 |
| Prometheus + Grafana observability dashboard | v1.1 |
| Transition from Scikit-Learn to PyTorch for recommendation model | v2.0 |
| GDPR right-to-erasure automated pipeline | v1.1 |
| Multi-region deployment (US + EU) | v2.0 |

---

*End of PROJECT_SPECIFICATION.md*

---

**Document History**

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 1.0.0 | 2026-06-13 | Architecture Team | Initial master blueprint |