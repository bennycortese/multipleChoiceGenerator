chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tab.url.includes("youtube.com")) {
    chrome.action.enable(tabId);
  } else {
    chrome.action.disable(tabId);
  }
});

chrome.action.onClicked.addListener((tab) => {
  if (tab.url.includes("youtube.com")) {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"]
    });
  }
});
