import aiohttp
import asyncio
import json
import argparse
import sys
from typing import Optional
import extruct
from playwright.async_api import async_playwright, TimeoutError
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
import readchar

console = Console()

class BaseStockChecker:
    def __init__(self, url: str, check_interval: float = 1.0):
        self.url = url
        self.check_interval = check_interval
        self.running = True
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

class HTTPStockChecker(BaseStockChecker):
    async def check_stock_status(self, response_text: str) -> Optional[bool]:
        try:
            data = extruct.extract(
                response_text,
                base_url=self.url,
                syntaxes=['json-ld']
            )
            
            json_ld = data.get('json-ld', [])
            for item in json_ld:
                offers = item.get('offers', [])
                if not isinstance(offers, list):
                    offers = [offers]
                
                for offer in offers:
                    availability = offer.get('availability', '')
                    if availability:
                        return 'InStock' in availability
            
            return None

        except Exception as e:
            console.print(f"[red]Error parsing stock status: {str(e)}[/red]")
            return None

    async def run(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            with Progress() as progress:
                task = progress.add_task("[cyan]Checking stock...", total=None)

                while self.running:
                    try:
                        async with session.get(self.url) as response:
                            if response.status == 200:
                                response_text = await response.text()
                                stock_status = await self.check_stock_status(response_text)
                                
                                if stock_status is True:
                                    console.print("[green]Item is in stock![/green]")
                                elif stock_status is False:
                                    console.print("[red]Out of stock[/red]")
                                else:
                                    console.print("[yellow]Could not determine stock status[/yellow]")
                            
                            elif response.status == 429:
                                console.print("[red]Rate limited. Waiting before retry...[/red]")
                                await asyncio.sleep(60)
                            else:
                                console.print(f"[yellow]Unexpected status code: {response.status}[/yellow]")

                        progress.update(task, advance=1)
                        await asyncio.sleep(self.check_interval)

                    except aiohttp.ClientError as e:
                        console.print(f"[red]Network error: {str(e)}[/red]")
                        await asyncio.sleep(self.check_interval)
                    except KeyboardInterrupt:
                        self.running = False
                        break
                    except Exception as e:
                        console.print(f"[red]Error during check: {str(e)}[/red]")
                        await asyncio.sleep(self.check_interval)

class BrowserStockChecker(BaseStockChecker):
    def __init__(self, url: str, check_interval: float = 1.0, headless: bool = True):
        super().__init__(url, check_interval)
        self.headless = headless

    async def check_stock_status(self, page) -> Optional[bool]:
        try:
            await page.wait_for_load_state('domcontentloaded')
            
            script_content = await page.evaluate("""() => {
                const selectors = [
                    '#structuredDataLdJson',
                    '#productJSONLD',
                    'script[type="application/ld+json"]'
                ];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const element of elements) {
                        try {
                            const content = JSON.parse(element.textContent);
                            if (content.offers || (Array.isArray(content) && content[0]?.offers)) {
                                return element.textContent;
                            }
                        } catch (e) {
                            continue;
                        }
                    }
                }
                return null;
            }""")

            if script_content:
                product_data = json.loads(script_content)
                if isinstance(product_data, list):
                    product_data = product_data[0]

                availability = (
                    product_data.get('offers', {}).get('availability', '') 
                    if isinstance(product_data.get('offers'), dict) 
                    else product_data.get('offers', [{}])[0].get('availability', '')
                )

                return 'InStock' in availability
            
            return None

        except Exception as e:
            if isinstance(e, TimeoutError):
                console.print("[yellow]Page load timeout. Retrying...[/yellow]")
            elif "429" in str(e):
                console.print("[red]Rate limited. Waiting before retry...[/red]")
                await asyncio.sleep(60)
            else:
                console.print(f"[red]Error checking stock: {str(e)}[/red]")
            return None

    async def run(self):
        try:
            async with async_playwright() as p:
                browser_type = p.chromium
                browser = await browser_type.launch(
                    headless=self.headless,
                    args=['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
                )

                with Progress() as progress:
                    task = progress.add_task("[cyan]Checking stock...", total=None)

                    while self.running:
                        try:
                            context = await browser.new_context(
                                user_agent=self.headers['User-Agent']
                            )
                            page = await context.new_page()
                            
                            await page.goto(self.url, wait_until='domcontentloaded', timeout=30000)
                            
                            stock_status = await self.check_stock_status(page)
                            
                            if stock_status is True:
                                console.print("[green]Item is in stock![/green]")
                            elif stock_status is False:
                                console.print("[red]Out of stock[/red]")
                            else:
                                console.print("[yellow]Could not determine stock status[/yellow]")

                            await context.close()
                            progress.update(task, advance=1)
                            
                            await asyncio.sleep(self.check_interval)

                        except KeyboardInterrupt:
                            self.running = False
                            break
                        except Exception as e:
                            console.print(f"[red]Error during check: {str(e)}[/red]")
                            await asyncio.sleep(self.check_interval)

        except Exception as e:
            console.print(f"[red]Fatal error: {str(e)}[/red]")
        finally:
            console.print("[yellow]Shutting down...[/yellow]")

def menu_prompt(options, title="Select an option"):
    console.print(Panel.fit(f"[blue]{title}[/blue]", border_style="blue"))
    current_selection = 0

    while True:
        console.clear()
        console.print(Panel.fit(f"[bold]{title}[/bold]", border_style="cyan"))
        for i, option in enumerate(options):
            if i == current_selection:
                console.print(f"[cyan]> {option}[/cyan]")
            else:
                console.print(f"  {option}")
        
        key = readchar.readkey()
        if key == readchar.key.UP:
            current_selection = (current_selection - 1) % len(options)
        elif key == readchar.key.DOWN:
            current_selection = (current_selection + 1) % len(options)
        elif key == readchar.key.ENTER:
            return options[current_selection]

def main():
    parser = argparse.ArgumentParser(description='Stock Checker CLI - Combined Version')
    parser.add_argument('url', help='URL of the product to check')
    parser.add_argument('-i', '--interval', type=float, default=1.0,
                        help='Check interval in seconds (default: 1.0)')
    parser.add_argument('-m', '--method', choices=['http', 'browser'], 
                        help='Method to use for checking stock (http or browser)')
    
    args = parser.parse_args()
    
    if not args.method:
        args.method = menu_prompt(
            options=["http", "browser"],
            title="Choose a method for stock checking"
        )
        console.print(f"[green]You selected: {args.method}[/green]")

    console.print(Panel.fit(
        f"[bold blue]Stock Checker - {args.method.upper()} Method[/bold blue]\n[dim]Press Ctrl+C to exit[/dim]",
        title="Welcome",
        border_style="blue"
    ))

    if args.method == 'http':
        checker = HTTPStockChecker(
            url=args.url,
            check_interval=args.interval
        )
    else:
        checker = BrowserStockChecker(
            url=args.url,
            check_interval=args.interval,
            headless=False
        )
    
    try:
        asyncio.run(checker.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Gracefully shutting down...[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()