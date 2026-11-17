# youtube-video-downloader Chrome Extension

Chrome extensions can't run programs, so this uses **Native Messaging**: the extension talks to a small Python host (`host/host.py`) that runs yt-dlp.

## Requirements
- Python 3, `yt-dlp` and `ffmpeg` on your PATH

## Setup
1. `chrome://extensions` → enable Developer mode → **Load unpacked** → select the `extension/` folder.
2. Copy the extension's ID shown on that page.
3. `python3 host/install.py <extension-id>`
4. Open a YouTube video, click the extension icon, pick a format, Download.

Files land in `~/Downloads/yt-dlp/`.

## Notes
- Only youtube.com / youtu.be URLs are accepted; the URL is passed to yt-dlp after `--` with no shell.
- Downloading may violate YouTube's Terms of Service unless it's your own or permitted content. For personal/local use only (Chrome Web Store won't accept this).
