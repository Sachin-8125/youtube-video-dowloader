# youtube-video-downloader Chrome Extension

Chrome extensions can't run programs, so this uses **Native Messaging**: the extension talks to a small Python host (`host/host.py`) that runs yt-dlp.

## Requirements
- Python 3, `yt-dlp` and `ffmpeg` on your PATH
  - `winget install yt-dlp.yt-dlp`
  - `winget install Gyan.FFmpeg`

## Quick install (from YouTubeDownloader.zip)

1. Download `YouTubeDownloader.zip` from the [Releases](../../releases) page and extract it anywhere.
2. Run `setup.bat` — it finds Python, registers the native messaging host (the extension ID is fixed, so no manual step needed), and warns if `yt-dlp`/`ffmpeg` are missing.
3. Open `chrome://extensions` → enable **Developer mode** → **Load unpacked** → select the `extension/` folder inside the extracted zip.
4. Open any YouTube video, click the extension icon, pick a format, **Download**.

Files land in `%USERPROFILE%\Downloads\yt-dlp\`.

## Manual setup (from source)

1. `chrome://extensions` → enable Developer mode → **Load unpacked** → select the `extension/` folder.
2. The extension ID is pinned (`onbalapjafnioafghlolojeejobjaiag`), but if you changed the key, copy the ID shown on that page.
3. `python3 host/install.py onbalapjafnioafghlolojeejobjaiag` (or your ID)
4. Open a YouTube video, click the extension icon, pick a format, Download.

Files land in `~/Downloads/yt-dlp/`.

## Notes
- Only youtube.com / youtu.be URLs are accepted; the URL is passed to yt-dlp after `--` with no shell.
- Downloading may violate YouTube's Terms of Service unless it's your own or permitted content. For personal/local use only (Chrome Web Store won't accept this).
