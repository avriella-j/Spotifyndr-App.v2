.PHONY: help install test run migrate shell celery celery-beat clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make run          - Run Flask development server"
	@echo "  make migrate      - Run database migrations"
	@echo "  make shell        - Open Flask shell"
	@echo "  make celery       - Run Celery worker"
	@echo "  make celery-beat  - Run Celery beat scheduler"
	@echo "  make clean        - Clean up cache and build files"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest

run:
	flask run

migrate:
	flask db upgrade

shell:
	flask shell

celery:
	celery -A app.tasks.celery_app worker -l info

celery-beat:
	celery -A app.tasks.celery_app beat -l info

clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
