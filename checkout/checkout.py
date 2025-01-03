from playwright.async_api import async_playwright, Playwright, Page
import asyncio
import pywintypes
import win32api
import time
import json
import random

async def run(playwright: Playwright, order_data_file):
    start = time.time()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page(extra_http_headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'})
    await page.goto('https://www.game.co.uk/en/playstation-5-console-2826338')
    print("On website.")
    await page.get_by_text('BUY NEW').click();
    print("BUY.")
    time.sleep(0.5)
    await page.get_by_text('SECURE').click();
    print("CHECKOUT.")
    await page.get_by_text('SECURE CHECKOUT').click();
    print("CHECKOUT.")
    await page.get_by_text('Checkout as Guest').click();
    print("GUEST.")
    order_number = await fill_form(page, order_data_file)
    await payment_details(page, order_data_file, order_number)
    end = time.time()
    print(f"Elapsed time: {end-start}")
    time.sleep(100)
    await page.close()

async def fill_form(page: Page, order_data_file):
    order_number = str(int(time.time()))
    await page.click('mat-select[formcontrolname="title"]')
    await page.click('span:has-text("Mr")')
    first_name = generate_random_string(5)
    last_name = generate_random_string(8)
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    mobile_number = generate_random_mobile_number()
    await page.fill('input[formcontrolname="firstName"]', first_name)
    await page.fill('input[formcontrolname="lastName"]', last_name)
    await page.fill('input[formcontrolname="email"]', email)
    await page.fill('input[formcontrolname="mobile"]', mobile_number)
    await page.screenshot(path=f"screenshots/{order_number}_personal_details.png", full_page=True)
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("load")
    await page.fill('input[formcontrolname="postcode"]', '{postcode}')
    await page.click('mat-option span:has-text("{address}")')
    print("ADDRESS INFO FINISHED.")
    await page.screenshot(path=f"screenshots/{order_number}_addr_info.png", full_page=True)
    await page.click('button[data-test="continue-button"]')
    print("CONTINUE BUTTON.")
    await page.screenshot(path=f"screenshots/{order_number}_delivery_info.png", full_page=True)
    await page.click('button[data-test="continue-to-payment"]')
    print("PAYMENT OPTIONS.")
    return order_number

async def payment_details(page: Page, order_data_file, order_number):
    await page.locator("game-card-payment").click()
    await page.frame_locator('iframe[title="secure payment field"]').get_by_label('Card number').fill("{cardnum}")
    cardholder_name = generate_random_string(10)
    await page.fill('input[formcontrolname="name"]', cardholder_name)
    await page.fill('input[formcontrolname="expiryDate"]', '{expir}')
    await page.fill('input[formcontrolname="cvv"]', '{cvv}')
    await page.screenshot(path=f"screenshots/{order_number}_card_info.png", full_page=True)
    await page.click('button[data-test="confirm-card"]')
    order_data = get_order_data(order_number, cardholder_name)
    append_order_data(order_data_file, order_data)

def get_order_data(order_number, cardholder_name):
    return {
        "order_number": order_number,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "cardholder_name": cardholder_name,
        # Add more dynamically generated information about the transaction
    }

def append_order_data(order_data_file, order_data):
    with open(order_data_file, 'a') as file:
        file.write(json.dumps(order_data) + '\n')

def generate_random_string(length):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choice(letters) for _ in range(length))

def generate_random_mobile_number():
    return '07' + ''.join(random.choice('0123456789') for _ in range(9))

async def main():
    order_data_file = 'order_data.json'
    print("Written by Yousuf Shahzad\nAll credit goes to Yousuf Shahzad")
    async with async_playwright() as playwright:
        await run(playwright, order_data_file)
asyncio.run(main())
