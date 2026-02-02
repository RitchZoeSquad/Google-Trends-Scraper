import httpx
import asyncio

SCRAPER_URL = "http://185.249.196.192:6000/scrape"
TEST_TARGET = "https://example.com"

async def test_connection():
    print(f"Testing connection to {SCRAPER_URL}...")
    print(f"Target URL to scrape: {TEST_TARGET}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                SCRAPER_URL, 
                params={"url": TEST_TARGET}, 
                timeout=10.0
            )
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Body: {response.text}")
        except httpx.ConnectError:
            print("\nError: Connection Refused. The server might be down or blocking connections.")
        except httpx.ReadTimeout:
            print("\nError: Read Timeout. The server accepted the connection but didn't respond in time.")
        except Exception as e:
            print(f"\nError: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())

