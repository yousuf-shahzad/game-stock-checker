import requests

def check_stock_availability(product_sku):
    # Construct the URL for checking stock availability
    stock_check_url = f'https://powerup.game.co.uk/StockCheckerUI/ExternalStockChecker/CheckForStock?caller=mcomm&&mintSku={product_sku}'
    
    try:
        # Make the HTTP request to check stock
        response = requests.get(stock_check_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Process the response to determine stock availability
        #data = response.json()
        print(response.text)
        # process_stock_response(data)
    except requests.exceptions.RequestException as e:
        print('Error:', e)

# Example: Replace 'YOUR_PRODUCT_SKU' with the actual SKU of the product you want to check
product_sku_to_check = '836225'
check_stock_availability(product_sku_to_check)
