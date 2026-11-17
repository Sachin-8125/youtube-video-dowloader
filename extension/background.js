const HOST = "com.local.ytdlp_host";
let port = null;

const setState = (s) => chrome.storage.session.set({ state: s });

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === "download") {
    if (port) return sendResponse({ ok: false, error: "A download is already running" });
    start(msg.url, msg.format);
    sendResponse({ ok: true });
  }
});

function start(url, format) {
  setState({ status: "starting", percent: 0 });
  port = chrome.runtime.connectNative(HOST);
  port.onMessage.addListener((m) => setState(m));
  port.onDisconnect.addListener(() => {
    const err = chrome.runtime.lastError;
    if (err) setState({ status: "error", message: err.message });
    port = null;
  });
  port.postMessage({ url, format });
}