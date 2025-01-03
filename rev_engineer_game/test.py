from playwright.async_api import async_playwright
import asyncio
import time
import json
from concurrent.futures import ThreadPoolExecutor

async def check_stock_status(page):
    try:
        script_content = await page.evaluate("""() => {
            const typscript = document.getElementById('productJSONLD');
            return typscript ? typscript.textContent : null;
        }""")

        if script_content:
            product_data = json.loads(script_content)

            if product_data and isinstance(product_data, list):
                for product in product_data:
                    if '@type' in product and product['@type'] == 'Product':
                        availability = product.get('Offers', [{}])[0].get('availability', '')
                        if 'OutOfStock' in availability:
                            print("Out of stock.")
                            return False
                        elif 'InStock':
                            print("In stock.")
                        else:
                            print("Stock status not determined.")
        return True

    except Exception as e:
        print(f"Error checking stock status: {e}")
        return False

async def process_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(extra_http_headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'})
        await page.goto(url)
        await check_stock_status(page)
        await page.close()

async def run():
    urls = ['https://www.game.co.uk/en/playstation-portal-2924759'] * 10
    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, lambda: asyncio.run(process_page(url))) for url in urls]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run())
