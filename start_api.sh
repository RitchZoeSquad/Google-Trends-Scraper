#!/bin/bash
set -e

echo "=== Google Trends API Setup ==="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers (if not already done)
echo "Ensuring Playwright browsers are installed..."
playwright install chromium

# Run the API
echo "Starting API server at http://127.0.0.1:8000 ..."
uvicorn api:app --reload --host 127.0.0.1 --port 8000
