chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tab.url.includes("youtube.com/watch")) {
    chrome.action.enable(tabId);
  } else {
    chrome.action.disable(tabId);
  }
});

chrome.action.onClicked.addListener((tab) => {
  if (tab.url.includes("youtube.com/watch")) {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"]
    });
  }
});

function fetchData() {
    // Return the fetch promise
    return fetch('https://jsonplaceholder.typicode.com/todos/1')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Data fetched', data);
        return data; // Resolve the promise with the data
      })
      .catch(error => {
        console.error('Error fetching data', error);
        throw error; // Re-throw the error to be handled in the caller function
      });
  }

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (tab.url.includes("www.youtube.com/watch") && changeInfo.status === "complete") {
      fetchData(); // Fetch the data
    }
  });
  
  // Listen for a message request from the content script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === "fetchData") {
      fetchData().then(data => {
        sendResponse({ data: data }); // Send the data back to the content script
      }).catch(error => {
        sendResponse({ error: error.toString() }); // Send error information back if needed
      });
      return true; // Keep the messaging channel open for sendResponse
    }
  });