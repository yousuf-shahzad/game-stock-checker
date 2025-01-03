function checkStockAvailability(productSku) {
    // Construct the URL for checking stock availability
    var stockCheckUrl = `https://powerup.game.co.uk/StockCheckerUI/ExternalStockChecker/CheckForStock?caller=mcomm&&mintSku=${productSku}`;
  
    // Make the HTTP request to check stock
    fetch(stockCheckUrl)
      .then(response => response.json())
      .then(data => {
        // Process the response to determine stock availability
        console.log(data)
        //processStockResponse(data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }
  
  function processStockResponse(data) {
    if (data && data.stockStatus === 'InStock') {
      console.log('Product is in stock!');
    } else if (data && data.stockStatus === 'OutOfStock') {
      console.log('Product is out of stock.');
    } else {
      console.log('Unable to determine stock status.');
    }
  }
  
  // Example: Replace 'YOUR_PRODUCT_SKU' with the actual SKU of the product you want to check
  var productSkuToCheck = '836225';
  checkStockAvailability(productSkuToCheck);
  