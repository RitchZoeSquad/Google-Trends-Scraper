import asyncio
import json
import os
from scraper import get_trends
from search import enrich_trends_with_search

async def main():
    print("--- Starting Enriched Scraper ---")
    
    # 1. Scrape Trends
    trends = await get_trends()
    if not trends:
        print("Failed to find any trends.")
        return

    # 2. Enrich with Search (Default limit to top 5)
    print(f"Scraping complete. Now searching top 5 trends via Outscraper...")
    enriched_data = await enrich_trends_with_search(trends, limit=5)

    # 3. Save to file
    output_file = 'trends_enriched.json'
    with open(output_file, 'w') as f:
        json.dump(enriched_data, f, indent=2)
        print(f"\nSuccess! Found {len(trends)} trends and searched top {len(enriched_data)}.")
        print(f"Data saved to {output_file}")

    if os.path.exists("debug_screenshot.png"):
        os.remove("debug_screenshot.png")

if __name__ == '__main__':
    asyncio.run(main())
