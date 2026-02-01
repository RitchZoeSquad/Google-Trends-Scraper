from fastapi import FastAPI, HTTPException, Query
import asyncio
from typing import List

from scraper import get_trends
from google_trends import (
    interest_over_time,
    interest_by_region,
    related_topics,
    related_queries,
    trending_searches,
)

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


# New endpoints using pytrends-backed functions (run sync functions in thread)
@app.get("/google/trends/interest_over_time")
async def api_interest_over_time(
    keywords: str = Query(..., description="Comma-separated keywords, e.g. 'bitcoin,ethereum'"),
    timeframe: str = Query("today 12-m", description='Timeframe string, e.g. "today 12-m"'),
    geo: str = Query("US", description="Country code or region (US, GB, etc.)"),
):
    try:
        data = await asyncio.to_thread(interest_over_time, keywords, timeframe, geo)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/google/trends/interest_by_region")
async def api_interest_by_region(
    keywords: str = Query(..., description="Single keyword or comma-separated list"),
    timeframe: str = Query("today 12-m"),
    geo: str = Query("", description="Parent geo (optional, e.g., 'US' or '')"),
    resolution: str = Query("COUNTRY", description="COUNTRY / REGION / CITY"),
):
    try:
        data = await asyncio.to_thread(interest_by_region, keywords, timeframe, geo, resolution)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/google/trends/related_topics")
async def api_related_topics(
    keyword: str = Query(..., description="Keyword to fetch related topics for"),
    timeframe: str = Query("today 12-m"),
    geo: str = Query("", description="Geo code (optional)"),
    top_or_rising: str = Query("top", description="'top' or 'rising'"),
):
    try:
        data = await asyncio.to_thread(related_topics, keyword, timeframe, geo, top_or_rising)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/google/trends/related_queries")
async def api_related_queries(
    keyword: str = Query(..., description="Keyword to fetch related queries for"),
    timeframe: str = Query("today 12-m"),
    geo: str = Query("", description="Geo code (optional)"),
    top_or_rising: str = Query("top", description="'top' or 'rising'"),
):
    try:
        data = await asyncio.to_thread(related_queries, keyword, timeframe, geo, top_or_rising)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/google/trends/trending_searches")
async def api_trending_searches(
    geo: str = Query("US", description="Country code (US, or 'global')"),
):
    try:
        data = await asyncio.to_thread(trending_searches, geo)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
