# Google Trends Scraper

A Python-based tool to scrape "Trending Now" data from Google Trends (US region) using Playwright. It offers both a Command Line Interface (CLI) and a REST API.

## Prerequisites

- Python 3.8+
- Linux/macOS/Windows (Scripts provided are for bash)

## Installation & Usage

### 1. CLI Scraper

Run the scraper directly to fetch trends and save them to a JSON file.

```bash
./start.sh
```

This will:
1.  Set up a virtual environment.
2.  Install dependencies.
3.  Scrape data from Google Trends.
4.  Save the output to `trends.json` and print it to the console.

### 2. API Server

Start the FastAPI server to access trends via HTTP.

```bash
./start_api.sh
```

Once the server is running (default: http://127.0.0.1:8000), you can access the following:

### Endpoints
- **Health Check**: `GET http://127.0.0.1:8000/`
- **Get Trends**: `GET http://127.0.0.1:8000/trends`
- **Interactive Docs**: `GET http://127.0.0.1:8000/docs` (Swagger UI)

### Usage Examples

#### 1. Browser
Open [http://127.0.0.1:8000/trends](http://127.0.0.1:8000/trends) in your web browser to see the JSON output.

#### 2. Command Line (curl)
```bash
curl http://127.0.0.1:8000/trends
```

#### 3. Python Code
```python
import requests

response = requests.get("http://127.0.0.1:8000/trends")
trends = response.json()["data"]
for item in trends:
    print(f"{item['title']}: {item['search_volume']}")
```

## Files

-   `scraper.py`: Core logic for scraping Google Trends.
-   `api.py`: FastAPI application serving the scraper.
-   `requirements.txt`: Python dependencies.
-   `start.sh`: Helper script for the CLI.
-   `start_api.sh`: Helper script for the API.
