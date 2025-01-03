const { chromium } = require('playwright');

// js implementation of the game.co.uk stock checker
// just comparing speeds between the two
// ignore

async function checkStockStatus(page) {
    try {
        const scriptContent = await page.evaluate(() => {
            const typscript = document.getElementById('productJSONLD');
            return typscript ? typscript.textContent : null;
        });

        if (scriptContent) {
            const productData = JSON.parse(scriptContent);

            if (productData && Array.isArray(productData)) {
                for (const product of productData) {
                    if (product['@type'] === 'Product') {
                        const availability = (product.Offers && product.Offers[0].availability) || '';
                        
                        if (availability.includes('OutOfStock')) {
                            console.log('Out of stock. Rechecking...');
                            return false;
                        } else if (availability.includes('InStock')) {
                            console.log('In stock.');
                        } else {
                            console.log('Stock status not determined.');
                        }
                    }
                }
            }
            return true;
        }

    } catch (e) {
        console.error(`Error checking stock status: ${e}`);
        if (e.toString().includes("429")) {
            const retryAfterHeader = page.headers().['Retry-After'];
            const retryAfterSeconds = retryAfterHeader ? parseInt(retryAfterHeader) : 60;

            console.log(`Rate limited. Waiting for ${retryAfterSeconds} seconds before retrying.`);
            await new Promise(resolve => setTimeout(resolve, retryAfterSeconds * 1000));
        }
    }
}

async function run() {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    });

    while (true) {
        const start = Date.now();
        const page = await context.newPage();
        await page.goto('https://www.game.co.uk/en/playstation-portal-2924759');
        await checkStockStatus(page);
        const end = Date.now();
        console.log(`Elapsed time: ${end - start}.`);
        await page.close();
        await new Promise(resolve => setTimeout(resolve, 500));
    }
}

console.log('Written by Yousuf Shahzad\nAll credit goes to Yousuf Shahzad');
run();
