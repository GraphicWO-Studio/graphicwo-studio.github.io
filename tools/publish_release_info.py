"""Called by the build workflows AFTER a new download is published.
Writes organizer.json / android.json so every installed copy is told automatically."""
import json, re, sys, time
kind, ver = sys.argv[1], sys.argv[2]
notes = json.load(open("release-notes.json", encoding="utf-8")).get(kind, {})
urls = {"organizer": "https://github.com/GraphicWO-Studio/graphicwo-studio.github.io/releases/download/organizer-latest/GraphicWO_Organizer.exe",
        "android": "https://github.com/GraphicWO-Studio/graphicwo-studio.github.io/releases/download/android-latest/GraphicWO_Studio.apk"}
info = {"version": ver, "url": urls[kind], "published": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        **{f"notes_{k}": v for k, v in notes.items()}}
open(f"{kind}.json", "w", encoding="utf-8").write(json.dumps(info, ensure_ascii=False, indent=1))
print(json.dumps(info))
if kind == "organizer":  # النسخ القديمة (1.1 و1.2) بتقرا version.json
    try:
        v = json.load(open("version.json", encoding="utf-8"))
        v["organizer"] = info
        open("version.json", "w", encoding="utf-8").write(json.dumps(v, ensure_ascii=False, indent=1))
    except Exception as e:
        print("version.json:", e)
