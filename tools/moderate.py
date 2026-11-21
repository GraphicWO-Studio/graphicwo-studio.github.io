"""Automatic moderation for the GraphicWO dataset.

pending/  ->  checks  ->  approved/   (or deleted)
Checks: real image, size >= 256 px, not blank, not a near-duplicate, NSFW classifier.
Only counts are printed (logs of this public repo are visible to everyone).
"""
import json, os, shutil, sys
from pathlib import Path

from PIL import Image, ImageStat
import imagehash
from transformers import pipeline

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "ds")
PENDING, APPROVED = ROOT / "pending", ROOT / "approved"
INDEX = APPROVED / "index.json"
APPROVED.mkdir(parents=True, exist_ok=True)
index = json.loads(INDEX.read_text()) if INDEX.exists() else {"hashes": [], "count": 0}
known = [imagehash.hex_to_hash(h) for h in index["hashes"]]

nsfw = pipeline("image-classification", model="Falconsai/nsfw_image_detection")
stats = {"approved": 0, "nsfw": 0, "duplicate": 0, "low_quality": 0, "broken": 0}

images = sorted(p for p in PENDING.rglob("*") if p.suffix.lower() in (".jpg", ".png", ".webp")) if PENDING.exists() else []
for img_path in images:
    meta_path = img_path.with_suffix(".json")
    verdict = None
    try:
        with Image.open(img_path) as im:
            im = im.convert("RGB")
            if min(im.size) < 256:
                verdict = "low_quality"
            elif max(ImageStat.Stat(im.convert("L")).stddev) < 8:
                verdict = "low_quality"
            else:
                h = imagehash.phash(im)
                if any(h - k <= 4 for k in known):
                    verdict = "duplicate"
                else:
                    scores = {r["label"].lower(): r["score"] for r in nsfw(im)}
                    if scores.get("nsfw", 0) >= 0.5:
                        verdict = "nsfw"
                    else:
                        verdict = "approved"
                        known.append(h)
                        index["hashes"].append(str(h))
    except Exception:
        verdict = "broken"

    stats[verdict] += 1
    if verdict == "approved":
        index["count"] += 1
        n = index["count"]
        dest = APPROVED / f"{n:06d}{img_path.suffix.lower()}"
        shutil.move(str(img_path), dest)
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        (APPROVED / f"{n:06d}.txt").write_text("graphicwo style, " + " ".join(str(meta.get("prompt", "")).split()), encoding="utf-8")
        (APPROVED / f"{n:06d}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        meta_path.unlink(missing_ok=True)
    else:
        img_path.unlink(missing_ok=True)
        meta_path.unlink(missing_ok=True)

INDEX.write_text(json.dumps(index))
for d in sorted((p for p in PENDING.rglob("*") if p.is_dir()), reverse=True) if PENDING.exists() else []:
    if not any(d.iterdir()):
        d.rmdir()
print("Moderation:", json.dumps(stats), "| total approved:", index["count"])
