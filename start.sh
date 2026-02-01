#!/bin/bash
set -e

echo "=== Google Trends Scraper Setup ==="

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

# Install Playwright browsers (required for the scraper to run)
echo "Installing Playwright browsers..."
playwright install chromium

# Run the scraper
echo "Running scraper..."
python3 scraper.py
