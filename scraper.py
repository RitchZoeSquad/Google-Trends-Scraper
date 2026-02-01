import asyncio
import json
import os
from playwright.async_api import async_playwright

async def get_trends():
    """
    Launches a headless browser, scrapes Google Trends, and returns a list of dictionaries.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            locale="en-US"
        )
        page = await context.new_page()

        url = "https://trends.google.com/trending?geo=US"
        print(f"Navigating to {url}...")
        await page.goto(url)

        # Handle cookie consent if it appears
        try:
            cookie_button = page.get_by_role("button", name="Reject all")
            if await cookie_button.is_visible():
                print("Handling cookie consent...")
                await cookie_button.click()
                await page.wait_for_timeout(2000)
        except Exception:
            pass 

        print("Waiting for trending data to load...")
        # Give it a bit more time for the JS to execute
        await page.wait_for_timeout(5000)
        
        # Capture rows
        rows = await page.locator("tr").all()
        
        trends = []
        print(f"Found {len(rows)} potential rows.")

        for row in rows:
            try:
                text_content = await row.inner_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                
                if len(lines) >= 2:
                    if lines[0].isdigit():
                        title = lines[1]
                        volume = lines[2] if len(lines) > 2 else "Unknown"
                    else:
                        title = lines[0]
                        volume = lines[1] if len(lines) > 1 else "Unknown"
                    
                    if title and len(title) > 1:
                        # Filter out known headers/junk
                        if title.lower() in ["search", "trending now", "rss feed"]:
                            continue
                        trends.append({
                            "title": title,
                            "search_volume": volume
                        })
            except Exception:
                continue

        # Fallback selector logic
        if not trends:
            print("Trying alternative selectors...")
            items = await page.locator("div[role='row']").all()
            for item in items:
                text = await item.inner_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if len(lines) >= 2:
                    trends.append({
                        "title": lines[1] if lines[0].isdigit() else lines[0],
                        "search_volume": lines[2] if lines[0].isdigit() and len(lines) > 2 else (lines[1] if len(lines) > 1 else "Unknown")
                    })

        # Filter duplicates
        seen = set()
        unique_trends = []
        for t in trends:
            if t['title'].lower() not in seen:
                unique_trends.append(t)
                seen.add(t['title'].lower())
        
        await browser.close()
        return unique_trends

async def main():
    trends = await get_trends()
    print(json.dumps(trends, indent=2))

    with open('trends.json', 'w') as f:
        json.dump(trends, f, indent=2)
        print(f"\nSuccess! Found {len(trends)} trends. Data saved to trends.json")

    if os.path.exists("debug_screenshot.png"):
        os.remove("debug_screenshot.png")

if __name__ == '__main__':
    asyncio.run(main())
