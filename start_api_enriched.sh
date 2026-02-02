#!/bin/bash
set -e
echo "=== Starting ENRICHED API Server (Trends + Search) ==="
source venv/bin/activate
pip install -r requirements.txt > /dev/null
echo "Starting API at http://127.0.0.1:8001 ..."
uvicorn api_enriched:app --reload --host 127.0.0.1 --port 8001
