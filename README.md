# Google Trends Scraper (Simple & Enriched)

This project provides two versions of a Google Trends scraper:
1.  **Simple**: Scrapes only the trending titles and volumes.
2.  **Enriched**: Scrapes trends AND performs a Google Search for each using the Outscraper API.

## 🚀 Simple Version (Trends Only)

### CLI
```bash
./start.sh
```
- Saves to: `trends.json`

### API
```bash
./start_api.sh
```
- Endpoint: `GET http://127.0.0.1:8000/trends`

---

## 💎 Enriched Version (Trends + Search)
*Uses Outscraper API Key: `ZDdjMzJl...`*

### CLI (Automatic Search)
```bash
./start_enriched.sh
```
- Automatically scrapes and then searches the top 5 trends.
- Saves to: `trends_enriched.json`

### API (On-demand Search)
```bash
./start_api_enriched.sh
```
- Endpoint: `GET http://127.0.0.1:8001/trends/enriched?limit=5`
- Port: **8001** (to avoid conflict with simple API)

---

## Prerequisites
- Python 3.8+
- Playwright (installed automatically by scripts)

## Files
- `scraper.py`: Core trend scraping logic.
- `search.py`: Outscraper API search logic.
- `scraper_enriched.py`: CLI script for automatic search.
- `api.py`: Simple API.
- `api_enriched.py`: Enriched API.