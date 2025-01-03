# Research & Development Process

This document outlines how I reverse-engineered game.co.uk's stock checking system to create a reliable stock monitoring tool.
This writeup may be outdated; this was done in early 2024 and the site may have changed since then.

## Initial Investigation

I started by examining Game.co.uk's product pages and discovered two key approaches to stock checking:

1. Direct API Endpoint

```bash
"https://powerup.game.co.uk/StockCheckerUI/ExternalStockChecker/CheckForStock?caller=mcomm&&mintSku={SKU}"
```

This endpoint was found in the site's JavaScript.

2. JSON-LD Product Schema

```javascript
{
  "@type": "Product",
  "Offers": [{
    "availability": "http://schema.org/OutOfStock"
  }]
}
```

Found this was consistently present in the page's structured data.

3. Extracting the Javascript from the page

The file named `temp.js` contains the Javascript code that is extracted from the page. This is the code that I investigated to understand how the stock checking system works.

## Key Findings

### Product Data Structure

- Each product has a unique SKU (e.g., '836225' for PlayStation Portal)
- Stock status is available in two locations:
  - JSON-LD schema embedded in the page
  - Direct API endpoint responses

### Stock Status Detection

Found two reliable methods:

1. Parsing the JSON-LD schema from the product page
2. Checking the `availability` field in the product offers

## Implementation Evolution

### First Attempt: Simple HTTP Requests

Started with basic requests to the stock checker API:

```python
def check_stock_availability(product_sku):
    stock_check_url = f'https://powerup.game.co.uk/StockCheckerUI/ExternalStockChecker/CheckForStock?caller=mcomm&&mintSku={product_sku}'
```

However, this was not very successful as it pointed me to another endpoint, using postcodes to check availability. Building a checker for this specific endpoint yielded an error 500, which, even with all necessary information, persisted.

```python
def _make_request(self, endpoint: str, params: Dict[str, Any]) -> requests.Response:
        """Make HTTP request with error handling"""
        url = (f'{self.BASE_URL}/{endpoint}')
        try:
            response = self.session.get(url, params=params, timeout=10)
```

This only yielded:

```bash
ERROR:__main__:Request failed: 500 Server Error: Internal Server Error for url
```

### Second Attempt: JavaScript Injection

Attempted to replicate the site's stock checker widget:

```javascript
function checkStockAvailability(productSku) {
    var stockCheckUrl = `https://powerup.game.co.uk/StockCheckerUI/ExternalStockChecker/CheckForStock?caller=mcomm&&mintSku=${productSku}`;
}
```

Modelling this in a webpage, I yielded similar results to the first attempt, with the same error 500.

### Final Solution: Playwright Automation

Settled on using Playwright for reliable page loading and data extraction:

```python
async def check_stock_status(page):
    script_content = await page.evaluate("""() => {
        const typscript = document.getElementById('productJSONLD');
        return typscript ? typscript.textContent : null;
    }""")
```

This approach proved most reliable because it:

- Properly loads JavaScript content
- Handles rate limiting gracefully
- Successfully extracts structured data

Midway through this approach I also realised if I requested the product page, I could extract the JSON-LD schema from the page, which was a more reliable method, and probably faster.

So I implemented both methods, and the user can choose which one to use, in case one does not work.

## Challenges Overcome

1. Rate Limiting
   - Implemented automatic backoff
   - Added error handling for 429 responses

2. Data Reliability
   - Cross-referenced multiple data sources
   - Validated stock status through schema parsing

3. Performance
   - Added async support
   - Implemented efficient browser context management

## Final Implementation Notes

The final version combines the best elements discovered during research:

- Uses Playwright for reliable page loading
- Parses JSON-LD for stock status
- Includes comprehensive error handling
- Supports both HTTP and browser-based checking

This research led to a robust tool that reliably monitors Game.co.uk stock status while respecting the site's rate limits.

However, the headless browser method does not currently work, as it seems the site has implemented some form of bot detection that blocks the headless browser from accessing the site.

## Reference Material

Example successful stock data structure:

```json
{
  "@context": "http://schema.org",
  "@type": "Product",
  "name": "PlayStation Portal",
  "SKU": "836225",
  "Offers": [{
    "availability": "http://schema.org/InStock"
  }]
}
```
