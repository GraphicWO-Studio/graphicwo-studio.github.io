"""Build a Kaggle dataset folder (images + metadata.jsonl) from ds/approved."""
import json, shutil, sys
from pathlib import Path
src, dst = Path(sys.argv[1]) / "approved", Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
rows = []
for img in sorted(src.glob("*.jpg")):
    cap = img.with_suffix(".txt")
    prompt = cap.read_text(encoding="utf-8").strip() if cap.exists() else "graphicwo style"
    shutil.copy(img, dst / img.name)
    rows.append({"file_name": img.name, "prompt": prompt})
(dst / "metadata.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(len(rows))
