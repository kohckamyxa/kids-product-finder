// Listen for a message from the popup script.
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "GET_PRODUCT_INFO") {
      findProductInfo(sendResponse);
    }
    // Return true to indicate that the response will be sent asynchronously.
    return true;
  });
  
  function findProductInfo(sendResponse) {
    const pageLanguage = document.documentElement.lang || 'en';
  
    const titleSelectors = [
      '#productTitle',                // Amazon
      'h1.product-title',               // House of Disaster
      'h1.h2',                          // The new selector you found
      'h1',                           // Generic fallback
      '.product-title',                 // Generic fallback
      '.product_title',                 // Generic fallback
      '.product-name',                  // Generic fallback
    ];
    
    const eanSelectors = ['.ean', '.upc', '.barcode', '[itemprop="gtin13"]'];
  
    let retries = 0;
    const maxRetries = 20; // Try for up to 2 seconds (20 * 100ms)
  
    const intervalId = setInterval(() => {
      let productName = null;
      let productEan = null;
  
      // --- Find Title ---
      for (const selector of titleSelectors) {
        const element = document.querySelector(selector);
        if (element && element.innerText.trim()) {
          productName = element.innerText.trim();
          break; // Exit the loop once a name is found
        }
      }
      
      // --- Find EAN ---
      for (const selector of eanSelectors) {
        const element = document.querySelector(selector);
        if (element && element.innerText.trim()) {
          const eanCandidate = element.innerText.replace(/\D/g, '');
          if (eanCandidate.length >= 12) {
              productEan = eanCandidate;
              break;
          }
        }
      }
  
      // If we found a name OR we've run out of retries, send the response.
      if (productName || retries >= maxRetries) {
        clearInterval(intervalId); // Stop the interval
        sendResponse({ 
            productName: productName, 
            productEan: productEan,
            sourceLang: pageLanguage.split('-')[0]
        });
      }
  
      retries++;
    }, 100); // Check every 100 milliseconds
  }