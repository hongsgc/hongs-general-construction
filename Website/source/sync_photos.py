#!/usr/bin/env python3
"""Copy Hong's job photos from the Desktop folder into the site, then rebuild the pages.

    python3 Website/source/sync_photos.py

Reads  ~/Desktop/Hongs Selected Photos/<Category>/*.jpg  (one subfolder per category in CATEGORIES)
Writes Website/assets/img/work/<slug>.jpg (max 1600px, for the full-size view)
       Website/assets/img/work/<slug>-sm.jpg (max 800px, for the grid; skipped when the photo is already small)
       Website/source/work_photos.json (what build_pages.py renders)
Removes photos from assets/img/work/ that are no longer in the Desktop folder.
Camera metadata (EXIF, including GPS) is stripped from every output.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

SRC = Path.home() / "Desktop" / "Hongs Selected Photos"
SITE = Path(__file__).resolve().parent.parent
OUT = SITE / "assets" / "img" / "work"
MANIFEST = Path(__file__).resolve().parent / "work_photos.json"

# Desktop subfolder -> category key (labels live in build_pages.py). Order here is the order on the page.
CATEGORIES = {"Nail Salons": "salons", "Homes": "homes", "Restaurants": "restaurants"}
# Shown first in their category (Anh's picks, 2026-10-09). Everything else sorts by file name.
FEATURED = ["DSC_2550.JPG", "DSC_2520.JPG"]
EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
FULL, SMALL = 1600, 800


def slugify(cat, name):
    return cat + "-" + re.sub(r"[^a-z0-9]+", "-", Path(name).stem.lower()).strip("-")


def trim_scan_border(im):
    """Crop a black border left by a scanned or rotated photo; leaves normal photos alone."""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    black = lambda xs: sum(1 for p in xs if p < 14) / max(len(xs), 1)
    row = lambda y, l, r: [px[x, y] for x in range(l, r)]
    col = lambda x, t, b: [px[x, y] for y in range(t, b)]
    if max(black(row(0, 0, w)), black(row(h - 1, 0, w)), black(col(0, 0, h)), black(col(w - 1, 0, h))) <= 0.6:
        return im
    t, b, l, r = 0, h, 0, w
    while True:  # trim whichever edge is blackest until all four are clean
        e = {"t": black(row(t, l, r)), "b": black(row(b - 1, l, r)), "l": black(col(l, t, b)), "r": black(col(r - 1, t, b))}
        k = max(e, key=e.get)
        if e[k] <= 0.01:
            break
        if k == "t": t += 1
        elif k == "b": b -= 1
        elif k == "l": l += 1
        else: r -= 1
    return im.crop((l, t, r, b))


def save(im, path, size):
    im = im.copy()
    im.thumbnail((size, size))
    im.save(path, "JPEG", quality=80, optimize=True, progressive=True)  # no exif= argument, so metadata is dropped
    return im.size


def main():
    if not SRC.is_dir():
        sys.exit(f"Photo folder not found: {SRC}")
    OUT.mkdir(parents=True, exist_ok=True)
    photos, written = [], set()
    for folder in sorted(p for p in SRC.iterdir() if p.is_dir()):
        if folder.name not in CATEGORIES:
            print(f"skipped folder (not a category): {folder.name}")
    for folder_name, cat in CATEGORIES.items():
        folder = SRC / folder_name
        if not folder.is_dir():
            continue
        files = sorted((f for f in folder.iterdir() if f.suffix.lower() in EXTS and not f.name.startswith(".")),
                       key=lambda f: (f.name not in FEATURED, f.name.lower()))
        for f in files:
            slug = slugify(cat, f.name)
            im = trim_scan_border(ImageOps.exif_transpose(Image.open(f)).convert("RGB"))
            full = f"{slug}.jpg"
            fw, fh = save(im, OUT / full, FULL)
            written.add(full)
            if max(im.size) > SMALL:
                sm = f"{slug}-sm.jpg"
                sw, sh = save(im, OUT / sm, SMALL)
                written.add(sm)
            else:
                sm, sw, sh = full, fw, fh
            photos.append({"cat": cat, "full": full, "w": fw, "h": fh, "sm": sm, "sw": sw, "sh": sh})
    for old in OUT.iterdir():
        if old.name not in written:
            old.unlink()
            print(f"removed {old.name}")
    MANIFEST.write_text(json.dumps(photos, indent=1) + "\n")
    counts = {c: sum(p["cat"] == c for p in photos) for c in CATEGORIES.values()}
    print(f"{len(photos)} photos: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "build_pages.py")], check=True)


if __name__ == "__main__":
    main()
