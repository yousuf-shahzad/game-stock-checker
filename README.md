# Game.co.uk Stock Checker

A simple CLI tool to monitor product stock availability on Game.co.uk using either HTTP requests or browser automation.
Disclaimer: This is NOT being updated or developed further and may be outdated.

## Features

- Two checking methods: HTTP requests (fast) or browser automation (more reliable)
- Real-time stock status updates
- Rate limit handling and error recovery
- Interactive CLI interface
- Configurable check intervals

## Installation

```bash
# Install dependencies
pip install aiohttp playwright asyncio extruct rich readchar

# Install browser automation support
playwright install chromium
```

## Usage

Basic usage:
```bash
python stock_checker.py <game.co.uk_product_url>
```

With options:
```bash
python stock_checker.py <game.co.uk_product_url> -i <interval> -m <method>

Options:
  -i, --interval  Check interval in seconds (default: 1.0)
  -m, --method    Checking method: 'http' or 'browser'
```

Example:
```bash
# Check PS5 stock every 5 seconds using browser method (url might be outdated)
python stock_checker.py https://www.game.co.uk/playstation-playstation-5-slim-disc-console-848410 -i 5 -m browser
```

## Notes

- Use reasonable check intervals to avoid rate limiting
- Browser method is more reliable but slower than HTTP
- Tool is for personal use only


Additionally, there is a proof of concept in this repository that implements an automated checkout system for Game.co.uk. This script is not intended for actual use and is provided for educational purposes only.

## Proof of concept Checkout System

This project includes a proof of concept for automating the checkout process on Game.co.uk using playwright. Below is a brief overview of the script functionality:

### Workflow

1. **Navigation**: Accesses the product page.
2. **Add to Cart**: Clicks the "Buy New" button to add the item to the cart.
3. **Checkout as Guest**: Proceeds through the checkout process, filling out a form with randomly generated user details.
4. **Payment Simulation**: Simulates entering payment details and submitting the form.
5. **Data Logging**: Saves a log of transaction details (e.g., timestamps and user information) in order_data.json.

### Notes relating

- This script was developed purely as a proof of concept to demonstrate feasibility.
- No further development is planned, and this tool should not be used for real-world transactions.
- The script generates random data and does not process real payments.
- The script is provided for educational purposes only.

## License

MIT License
