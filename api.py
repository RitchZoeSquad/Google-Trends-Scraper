from fastapi import FastAPI, HTTPException
from scraper import get_trends

app = FastAPI(title="Google Trends Scraper API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Google Trends Scraper API. Go to /trends to get the latest trends."}

@app.get("/trends")
async def read_trends():
    try:
        trends = await get_trends()
        if not trends:
            return {"message": "No trends found or scraping failed", "data": []}
        return {"count": len(trends), "data": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))