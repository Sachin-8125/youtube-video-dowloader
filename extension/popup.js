const $ = (id) => document.getElementById(id);
let tabUrl = "";

function isYouTube(u) {
    try {
        const h = new URL(u).hostname;
        return ["youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"].includes(h);
    } catch { return false; }
}

function render(s) {
    if (!s) return;
    const running = s.status === "starting" || s.status === "downloading" || s.status === "processing";
    $("go").disabled = running || !isYouTube(tabUrl);
    $("bar").hidden = !running;
    if (s.percent != null) $("bar").value = s.percent;
    const text = {
        starting: "Starting…",
        downloading: `Downloading ${s.percent ?? 0}%  ${s.speed || ""}  ETA ${s.eta || "?"}`,
        processing: "Merging / converting…",
        done: `Done. Saved to ${s.dir || "Downloads/yt-dlp"}`,
        error: `Error: ${s.message || "unknown"}`
    }[s.status];
    $("status").textContent = text || "";
}

(async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    tabUrl = tab?.url || "";
    $("title").textContent = isYouTube(tabUrl) ? tab.title : "Open a YouTube video first";
    $("go").disabled = !isYouTube(tabUrl);

    const { state } = await chrome.storage.session.get("state");
    render(state);
    chrome.storage.onChanged.addListener((c, area) => {
        if (area === "session" && c.state) render(c.state.newValue);
    });
})();

$("go").addEventListener("click", async () => {
    $("go").disabled = true;
    const res = await chrome.runtime.sendMessage({ type: "download", url: tabUrl, format: $("format").value });
    if (!res?.ok) $("status").textContent = res?.error || "Failed to start";
});
