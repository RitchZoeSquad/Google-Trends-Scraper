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
        
        # Scroll down to ensure lazy-loaded elements appear
        await page.mouse.wheel(0, 1000)
        await page.wait_for_timeout(2000)
        
        trends = []
        
        # Strategy 1: Look for the classic table structure
        rows = await page.locator("tr").all()
        print(f"Strategy 1 (Table): Found {len(rows)} rows.")
        
        for row in rows:
            try:
                text_content = await row.inner_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                if len(lines) >= 2:
                    # Check for rank (digit) to confirm it's a trend row
                    if lines[0].isdigit():
                        trends.append({"title": lines[1], "search_volume": lines[2] if len(lines) > 2 else "Unknown"})
                    elif len(lines) > 1:
                         # Sometimes rank isn't first text
                        trends.append({"title": lines[0], "search_volume": lines[1]})
            except:
                continue

        # Strategy 2: Look for Material Design List Items (common in new UI)
        if not trends:
            print("Strategy 1 failed. Trying Strategy 2 (List Items)...")
            # This selector targets the specific grid/list items in the daily trends view
            # "md-list-item" or generic divs with specific class patterns
            
            # This selector looks for the 'feed-item' or specific trend rows
            # We try a few common patterns found in the DOM
            candidates = await page.locator("div[class*='feed-item'], div[class*='row'], div[jsname]").all()
            
            for item in candidates:
                text = await item.inner_text()
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                
                # A valid trend block usually has: Rank, Title, Traffic
                # Example: "1\nReal Madrid\n50K+"
                if len(lines) >= 3 and lines[0].isdigit() and ("K+" in lines[-1] or "M+" in lines[-1]):
                     trends.append({
                        "title": lines[1],
                        "search_volume": lines[-1] # Volume is often last
                    })
        
        # Strategy 3: Target "title" class specifically
        if not trends:
            print("Strategy 2 failed. Trying Strategy 3 (Specific Classes)...")
            titles = await page.locator("div[class*='title']").all()
            for t_el in titles:
                t_text = await t_el.inner_text()
                if t_text and len(t_text) > 2 and t_text.lower() != "search":
                    # Try to find volume nearby (parent's sibling or similar)
                    # For now, just getting titles is better than nothing
                    trends.append({"title": t_text.strip(), "search_volume": "N/A"})

        # Filter duplicates and junk
        seen = set()
        unique_trends = []
        for t in trends:
            clean_title = t['title'].lower().strip()
            if clean_title not in seen and clean_title not in ["search", "daily search trends", "realtime search trends"]:
                unique_trends.append(t)
                seen.add(clean_title)
        
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
