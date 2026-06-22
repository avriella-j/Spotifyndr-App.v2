# Spotifyndr

A social music discovery platform built with Flask, featuring Spotify integration, ML-based recommendations, and real-time messaging.

## Features

- Spotify OAuth authentication with PKCE flow
- ML-powered music recommendations (Logistic Regression + KNN)
- Real-time messaging with Socket.IO
- Social features (follow, explore, find mutuals)
- Swipe-based discovery interface
- Asynchronous task processing with Celery

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Spotify Developer Account (for OAuth)

### Installation

```bash
# Copy environment template
cp .env.example .env

# Install dependencies
make install

# Run database migrations
make migrate

# Start development server
make run
```

### Docker Setup

```bash
# Start all services
docker-compose up

# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## Project Structure

See `project_specifications.md` for detailed architecture documentation.

## License

MIT
