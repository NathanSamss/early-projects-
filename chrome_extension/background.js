// background.js
// Service worker: relays status, shows CAPTCHA notifications, logs applications,
// and optionally reports results back to the Flask API.

const API_BASE = "http://localhost:8000";
const tabStatus = {};

async function reportToApi(payload) {
  // Best-effort report to the backend. Silently ignored if API is down.
  try {
    await fetch(`${API_BASE}/applications/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    // API not running — standalone mode, that's fine
  }
}

chrome.runtime.onMessage.addListener((msg, sender) => {
  const tabId = sender.tab?.id;
  if (msg.type === "STATUS") {
    if (tabId) tabStatus[tabId] = msg;

    if (msg.status === "captcha") {
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icons/icon48.png",
        title: "Action needed — CAPTCHA",
        message: msg.message,
        priority: 2,
      });
    }

    if (msg.status === "submitted" && sender.tab?.url) {
      reportToApi({ url: sender.tab.url, status: "applied", platform: msg.platform || "" });
    }
  }

  if (msg.type === "GET_STATUS" && msg.tabId) {
    return Promise.resolve(tabStatus[msg.tabId] || null);
  }
});

chrome.tabs.onRemoved.addListener(id => delete tabStatus[id]);
