#!/usr/bin/env bash
set -e

# Run DB migrations on boot (Railway Postgres)
alembic upgrade head

# IMPORTANT: Railway provides $PORT. Don't hardcode 8000.
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}