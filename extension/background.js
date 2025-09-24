// Listen for a message from the popup to start the search
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "START_SEARCH") {
      const searchData = message.data;
  
      // Make the long-running fetch call to the backend
      fetch('http://127.0.0.1:5000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchData),
      })
      .then(response => response.json())
      .then(data => {
        // When the search is done, send the results back to the popup
        chrome.runtime.sendMessage({
          type: "SEARCH_COMPLETE",
          data: data.results
        });
      })
      .catch(error => {
        console.error('Error in background fetch:', error);
        // Send an empty result back in case of an error
        chrome.runtime.sendMessage({
          type: "SEARCH_COMPLETE",
          data: []
        });
      });
      
      // Return true to indicate you will be sending a response asynchronously
      return true; 
    }
  });