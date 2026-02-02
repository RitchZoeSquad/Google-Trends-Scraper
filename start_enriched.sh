#!/bin/bash
set -e
echo "=== Running ENRICHED CLI Scraper (Trends + Search) ==="
source venv/bin/activate
pip install -r requirements.txt > /dev/null
python3 scraper_enriched.py
