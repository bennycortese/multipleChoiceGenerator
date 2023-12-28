chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes("youtube.com/watch")) {
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


function fetchData(videoUrl) {
    
    const url = 'https://bennycortese--activelearnendpoints-flask-app-dev.modal.run/echo';


    let match = videoUrl.match(/(?<=v=)[^&#]+/);

    if (match && match[0]) {
        console.log(match[0]);  // Output: YNYMQv6GQX8
    } else {
        console.error("No video ID found in URL");
        return; // or handle this case appropriately
    }
    videoId = match[0]; 

    console.log(videoId);
    
    return fetch(url, { // Pass the URL
        method: 'POST', // Set the method to POST
        body: videoId, // Convert the JavaScript object to a JSON string
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
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
      fetchData(tab.url);
    }
  });
  
  // Listen for messages from the content script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === "fetchData") {
      fetchData(sender.tab.url)
        .then(data => sendResponse({ data: data }))
        .catch(error => sendResponse({ error: error.toString() }));
      return true;  // indicates you wish to send a response asynchronously
    }
  });