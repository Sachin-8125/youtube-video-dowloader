#!/usr/bin/env python3
"""Register the native messaging host. Usage: python3 install.py <extension-id>"""
import json, os, platform, stat, sys
from pathlib import Path

NAME = "com.local.ytdlp_host"
if len(sys.argv) != 2:
    sys.exit("Usage: python3 install.py <extension-id>")
ext_id = sys.argv[1]
here = Path(__file__).resolve().parent
host = here / "host.py"
system = platform.system()

if system == "Windows":
    launcher = here / "host.bat"
    launcher.write_text(f'@echo off\r\n"{sys.executable}" "{host}"\r\n')
    target = launcher
else:
    host.chmod(host.stat().st_mode | stat.S_IXUSR)
    target = host

manifest = {
    "name": NAME,
    "description": "yt-dlp native host",
    "path": str(target),
    "type": "stdio",
    "allowed_origins": [f"chrome-extension://{ext_id}/"],
}

if system == "Windows":
    import winreg
    mpath = here / f"{NAME}.json"
    mpath.write_text(json.dumps(manifest, indent=2))
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Google\Chrome\NativeMessagingHosts\{NAME}")
    winreg.SetValue(key, "", winreg.REG_SZ, str(mpath))
    print("Registered in HKCU registry:", mpath)
else:
    home = Path.home()
    if system == "Darwin":
        dirs = [home / "Library/Application Support/Google/Chrome/NativeMessagingHosts",
                home / "Library/Application Support/Chromium/NativeMessagingHosts"]
    else:
        dirs = [home / ".config/google-chrome/NativeMessagingHosts",
                home / ".config/chromium/NativeMessagingHosts"]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{NAME}.json").write_text(json.dumps(manifest, indent=2))
        print("Wrote", d / f"{NAME}.json")
print("Done. Restart Chrome if the extension was already open.")
