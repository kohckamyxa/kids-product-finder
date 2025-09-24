// Function to update the popup's display
function setContent(html) {
    document.getElementById('content').innerHTML = `<h3>Nordic Product Finder</h3>${html}`;
  }
  
  function triggerSearch() {
    setContent("<p>Finding deals...</p>");
  
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0];
      if (!activeTab || !activeTab.id || activeTab.url.startsWith('chrome://')) {
        setContent("<p>This extension cannot run on this page.</p>");
        return;
      }
  
      // Get product info from the content script
      chrome.tabs.sendMessage(activeTab.id, { type: "GET_PRODUCT_INFO" }, (response) => {
        // This checks if the content script failed to inject or connect
        if (chrome.runtime.lastError) {
          setContent("<p>Could not connect to the page. Please reload the page and try again.</p>");
          console.error(chrome.runtime.lastError.message);
          return;
        }
        
        // This checks if the content script ran but didn't find a product name
        if (response && response.productName) {
          chrome.runtime.sendMessage({
            type: "START_SEARCH",
            data: {
              productName: response.productName,
              productEan: response.productEan,
              sourceLang: response.sourceLang
            }
          });
        } else {
          setContent("<p>Could not find a product name on this page.</p>");
        }
      });
    });
  }
  
  // Listen for the final results from the background script
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "SEARCH_COMPLETE") {
      displayResults(message.data);
    }
  });
  
  function displayResults(results) {
    if (!results || results.length === 0) {
      setContent("<p>No matching products found in local stores.</p>");
      return;
    }
    
    let resultsHTML = "";
    results.forEach(item => {
      if (item.url) {
        resultsHTML += `
          <div class="result">
            <strong>${item.store_name}:</strong> ${item.price} <br/>
            <a href="${item.url}" target="_blank">View Product</a>
          </div>
        `;
      }
    });
    setContent(resultsHTML);
  }
  
  // Run the search when the popup is opened
  triggerSearch();