#!/bin/bash
# Build frontend and run combined app
set -e
cd "$(dirname "$0")"

echo "Building frontend..."
cd frontend && npm run build && cd ..

echo "Starting server..."
source venv/bin/activate 2>/dev/null || true
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
