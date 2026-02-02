import httpx
import asyncio

# Default key from user request
DEFAULT_API_KEY = "ZDdjMzJlYWIyZWI5NDM1ZGJjMDJiZWM3MzY5NGM3MWJ8NjhlMTY2YjM0MA"
SEARCH_API_URL = "https://api.outscraper.cloud/google-search"
CONTENT_SCRAPER_URL = "http://185.249.196.192:6000/scrape"

# Control how many concurrent requests hit the scraper at once
CONCURRENCY_LIMIT = 20
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

async def search_google(client: httpx.AsyncClient, query: str, api_key: str = DEFAULT_API_KEY):
    """
    Searches Google for a specific query using the Outscraper API.
    """
    headers = {"X-API-KEY": api_key}
    params = {"query": query, "async": "false"}
    
    try:
        response = await client.get(SEARCH_API_URL, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return None

async def scrape_page_content(client: httpx.AsyncClient, url: str):
    """
    Calls the external scraping service with concurrency control (semaphore).
    """
    if not url:
        return None
        
    async with semaphore:
        try:
            # Reusing the shared client for performance
            response = await client.get(CONTENT_SCRAPER_URL, params={"url": url}, timeout=45.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "code": response.status_code, "detail": f"Server returned {response.status_code}"}
        except httpx.ConnectTimeout:
             return {"status": "error", "detail": "Connection Timeout (Server Unreachable)"}
        except httpx.ReadTimeout:
             return {"status": "error", "detail": "Read Timeout (Server took too long)"}
        except httpx.ConnectError:
             return {"status": "error", "detail": "Connection Refused"}
        except Exception as e:
            return {"status": "error", "detail": f"{type(e).__name__}: {str(e)}"}

async def enrich_trends_with_search(trends: list, limit: int = 5):
    """
    Highly concurrent enrichment using a shared HTTP client.
    """
    trends_to_process = trends[:limit]
    
    # Use a single client session for ALL requests (Search + Scrape)
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=100)) as client:
        
        # 1. Concurrent Google Searches
        print(f"Searching Google for top {len(trends_to_process)} trends...")
        search_tasks = [search_google(client, t['title']) for t in trends_to_process]
        search_results = await asyncio.gather(*search_tasks)
        
        # 2. Build tasks for EVERY organic result found
        all_scrape_tasks = []
        result_map = [] # To map flat results back to trends
        
        for i, s_res in enumerate(search_results):
            if s_res and 'data' in s_res and s_res['data']:
                organic = s_res['data'][0].get('organic_results', [])
                for item in organic:
                    link = item.get('link')
                    if link:
                        all_scrape_tasks.append(scrape_page_content(client, link))
                        result_map.append(i) # Belongs to trend i

        print(f"Concurrently scraping {len(all_scrape_tasks)} results via 185.249.196.192...")
        scraped_data_list = await asyncio.gather(*all_scrape_tasks)
        
        # 3. Assemble final data
        enriched_trends = []
        for i, trend in enumerate(trends_to_process):
            trend_copy = trend.copy()
            
            # Extract original organic results
            s_res = search_results[i]
            organic_results = []
            if s_res and 'data' in s_res and s_res['data']:
                organic_results = s_res['data'][0].get('organic_results', [])
            
            # Map the flat scraped data back to these organic results
            enhanced_organic = []
            # This logic finds all scraped items that belong to trend 'i'
            # (Note: This assumes organic_results length matches what we put in result_map)
            scrape_idx = 0
            for item in organic_results:
                # Re-verify logic: find results in scraped_data_list where result_map == i
                # Simpler: just keep track of the index globally
                # Since we processed trends in order, we can just consume the flat list
                pass
            
            # Let's use a simpler mapping reconstruction
            enriched_trends.append(trend_copy)

        # Re-mapping (more robust way)
        # Create a dictionary of results for each trend
        trend_results = {idx: [] for idx in range(len(trends_to_process))}
        
        # We know scraped_data_list[j] belongs to trend result_map[j]
        # But we need to know WHICH result in that trend.
        # Let's adjust the merge logic.
        
        # Cleaned up reconstruction:
        flat_idx = 0
        final_list = []
        for i, trend in enumerate(trends_to_process):
            t_copy = trend.copy()
            s_res = search_results[i]
            organic = []
            if s_res and 'data' in s_res and s_res['data']:
                organic = s_res['data'][0].get('organic_results', [])
            
            enhanced_organic = []
            for org_item in organic:
                if org_item.get('link'):
                    org_item['scraped_page_data'] = scraped_data_list[flat_idx]
                    flat_idx += 1
                else:
                    org_item['scraped_page_data'] = None
                enhanced_organic.append(org_item)
            
            t_copy['google_search_results'] = enhanced_organic
            final_list.append(t_copy)
            
        return final_list