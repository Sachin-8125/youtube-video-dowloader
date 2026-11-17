#!/usr/bin/env python3
"""Native messaging host: receives {url, format} from the extension and runs yt-dlp."""
import json, os, re, shutil, struct, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse

OUT_DIR = Path.home() / "Downloads" / "yt-dlp"
ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}

# Chrome launches hosts with a minimal PATH; add the usual install locations.
extra = ["/usr/local/bin", "/opt/homebrew/bin", str(Path.home() / ".local" / "bin")]
os.environ["PATH"] = os.pathsep.join([os.environ.get("PATH", "")] + extra)

# winget's ffmpeg package has no PATH shim; locate its bin dir directly.
if os.name == "nt" and not shutil.which("ffmpeg"):
    winget_pkgs = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    for d in winget_pkgs.glob("Gyan.FFmpeg*/ffmpeg-*-full_build/bin"):
        os.environ["PATH"] = os.pathsep.join([str(d), os.environ["PATH"]])
        break

FORMATS = {
    "best":  ["-f", "bv*+ba/b", "--merge-output-format", "mp4"],
    "1080":  ["-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4"],
    "720":   ["-f", "bv*[height<=720]+ba/b[height<=720]", "--merge-output-format", "mp4"],
    "audio": ["-x", "--audio-format", "mp3"],
}

def read_msg():
    raw = sys.stdin.buffer.read(4)
    if len(raw) < 4:
        return None
    n = struct.unpack("<I", raw)[0]
    return json.loads(sys.stdin.buffer.read(n).decode("utf-8"))

def send(obj):
    data = json.dumps(obj).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("<I", len(data)) + data)
    sys.stdout.buffer.flush()

def valid_url(u):
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and p.hostname in ALLOWED_HOSTS
    except Exception:
        return False

def handle(msg):
    url, fmt = msg.get("url", ""), msg.get("format", "best")
    if not valid_url(url) or fmt not in FORMATS:
        return send({"status": "error", "message": "Invalid URL or format"})

    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        return send({"status": "error", "message": "yt-dlp not found in PATH"})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        ytdlp, "--no-playlist", "--newline", "--no-colors",
        "--progress-template", "download:DL|%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s",
        "-P", str(OUT_DIR), "-o", "%(title).150B [%(id)s].%(ext)s",
        *FORMATS[fmt], "--", url,
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, text=True, bufsize=1)
    last_error = None
    last_pct = -1
    for line in proc.stdout:
        line = line.strip()
        if line.startswith("DL|"):
            _, pct, speed, eta = (line.split("|") + ["", "", ""])[:4]
            try:
                p = int(float(pct.strip().rstrip("%")))
            except ValueError:
                continue
            if p != last_pct:
                last_pct = p
                send({"status": "downloading", "percent": p, "speed": speed.strip(), "eta": eta.strip()})
        elif re.match(r"\[(Merger|ExtractAudio|VideoConvertor)\]", line):
            send({"status": "processing"})
        elif line.startswith("ERROR"):
            last_error = line
    code = proc.wait()
    if code == 0:
        send({"status": "done", "dir": str(OUT_DIR)})
    else:
        send({"status": "error", "message": last_error or f"yt-dlp exited with code {code}"})

def main():
    # Keep the process alive until Chrome closes stdin, so the port does not
    # disconnect (and surface "Native host has exited") after each download.
    while True:
        msg = read_msg()
        if not msg:
            return
        try:
            handle(msg)
        except Exception as e:
            try:
                send({"status": "error", "message": str(e)})
            except Exception:
                return

if __name__ == "__main__":
    main()
