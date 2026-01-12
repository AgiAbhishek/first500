#!/bin/bash
set -e

echo "Starting AI RAG Agent deployment..."

# Navigate to the app directory
cd /home/site/wwwroot

# Install dependencies
echo "Installing dependencies from requirements.txt..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Dependencies installed successfully!"

# Start the application with Gunicorn
echo "Starting application with Gunicorn..."
python -m gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind=0.0.0.0:${PORT:-8000} --timeout 600
