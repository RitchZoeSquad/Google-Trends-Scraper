from fastapi import FastAPI, HTTPException, Query
from scraper import get_trends
from search import enrich_trends_with_search

app = FastAPI(title="Google Trends Enriched API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Enriched Google Trends API."}

@app.get("/trends")
async def read_trends():
    """
    Get basic trends (no search).
    """
    try:
        trends = await get_trends()
        if not trends:
            return {"message": "No trends found or scraping failed", "data": []}
        return {"count": len(trends), "data": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends/enriched")
async def read_trends_enriched(limit: int = Query(5, description="Number of trends to search (default 5)")):
    """
    Get trends and automatically perform a Google Search for the top results.
    """
    try:
        # 1. Get the trends
        trends = await get_trends()
        if not trends:
            return {"message": "No trends found", "data": []}
        
        # 2. Enrich them with search results
        enriched_data = await enrich_trends_with_search(trends, limit=limit)
        
        return {"count": len(enriched_data), "data": enriched_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
