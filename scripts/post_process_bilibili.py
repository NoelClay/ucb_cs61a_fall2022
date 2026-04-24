#!/usr/bin/env python3
"""
Post-process the Bilibili bulk download:

  1) Re-classify misclassified "other" parts into project/lecture/disc.
     In particular, the anthology has 4 project intros with titles like
     "p1-Hog", "p2-Cats", "p3-Ants", "p4-Scheme" which the initial
     downloader saved as p06.mp4, p18.mp4, p30.mp4, p41.mp4.
  2) Rename those files to descriptive names.
  3) Regenerate pipeline/video_list.csv with the corrected mapping.

Safe to re-run: mappings are idempotent.
"""
from __future__ import annotations

import csv
import json
import re
import urllib.request
from pathlib import Path

BVID = "BV1GK411Q7qp"
RAW_DIR = Path("data/01_raw")
CSV_PATH = Path("pipeline/video_list.csv")
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

PROJECT_NAMES = {1: "hog", 2: "cats", 3: "ants", 4: "scheme"}


def fetch_pagelist(bvid: str) -> list[dict]:
    req = urllib.request.Request(
        f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}",
        headers={"User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read().decode("utf-8"))
    return d["data"]


def classify(part: str, page: int) -> tuple[str, str]:
    t = part.strip()
    m = re.search(r"[Ll]ecture\s+(\d+)", t)
    if m:
        return (f"lecture_{int(m.group(1)):02d}", "lecture")
    m = re.search(r"[Dd]isc(?:ussion)?\s*(\d+)", t)
    if m:
        return (f"disc_{int(m.group(1)):02d}", "discussion")
    m = re.match(r"p(\d+)[-\s]", t)
    if m:
        n = int(m.group(1))
        name = PROJECT_NAMES.get(n, f"proj{n:02d}")
        return (f"project_{n:02d}_{name}", "project")
    return (f"p{page:02d}", "other")


def main() -> int:
    pages = fetch_pagelist(BVID)
    renames: list[tuple[Path, Path]] = []
    rows: list[dict] = []

    for p in pages:
        page = p["page"]
        vid, vtype = classify(p["part"], page)
        rows.append({
            "video_id": vid,
            "title": re.sub(r'[\\/:*?"<>|]', "_", p["part"]).strip()[:120],
            "type": vtype,
            "bilibili_url": f"https://www.bilibili.com/video/{BVID}?p={page}",
        })

        # File that the original downloader produced (using its own classify)
        # The only divergence is for project intros, which originally became p06/p18/p30/p41.
        if vtype == "project":
            old = RAW_DIR / f"p{page:02d}.mp4"
            new = RAW_DIR / f"{vid}.mp4"
            if old.exists() and not new.exists():
                renames.append((old, new))

    print(f"pagelist: {len(pages)} parts")
    print(f"renames needed: {len(renames)}")
    for old, new in renames:
        print(f"  {old.name}  ->  {new.name}")
        old.rename(new)

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["video_id", "title", "type", "bilibili_url"])
        w.writeheader()
        w.writerows(rows)
    print(f"CSV rewritten: {CSV_PATH} ({len(rows)} rows)")

    present = {p.stem for p in RAW_DIR.glob("*.mp4")}
    expected = {r["video_id"] for r in rows}
    missing = expected - present
    extra = present - expected
    print(f"\nfiles present: {len(present)}/{len(expected)}")
    if missing:
        print(f"still missing: {sorted(missing)}")
    if extra:
        print(f"unexpected extras: {sorted(extra)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
