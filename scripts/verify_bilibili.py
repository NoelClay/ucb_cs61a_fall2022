#!/usr/bin/env python3
"""
Verify each Bilibili download against the playurl API's expected size.
Prints a table and re-downloads any mismatched file via curl -C - (resume).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

BVID = "BV1GK411Q7qp"
RAW_DIR = Path("data/01_raw")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0"

FAILED = [
    "lecture_04", "disc_04", "lecture_19", "lecture_23",
    "lecture_27", "lecture_28", "lecture_31", "lecture_34", "lecture_37",
]

PROJECT_NAMES = {1: "hog", 2: "cats", 3: "ants", 4: "scheme"}


def http_json(url: str, referer: str | None = None) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if referer:
        req.add_header("Referer", referer)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def classify(part: str, page: int) -> str:
    import re
    m = re.search(r"[Ll]ecture\s+(\d+)", part)
    if m:
        return f"lecture_{int(m.group(1)):02d}"
    m = re.search(r"[Dd]isc(?:ussion)?\s*(\d+)", part)
    if m:
        return f"disc_{int(m.group(1)):02d}"
    m = re.match(r"p(\d+)[-\s]", part)
    if m:
        n = int(m.group(1))
        return f"project_{n:02d}_{PROJECT_NAMES.get(n, f'proj{n:02d}')}"
    return f"p{page:02d}"


def expected_for(pages: list[dict]) -> dict[str, tuple[int, int, str]]:
    """Returns {video_id: (cid, expected_size, mp4_url)}"""
    out: dict[str, tuple[int, int, str]] = {}
    for p in pages:
        vid = classify(p["part"], p["page"])
        # Preserve legacy downloader filenames for project pages too, so we can verify them
        ref = f"https://www.bilibili.com/video/{BVID}?p={p['page']}"
        url = (
            f"https://api.bilibili.com/x/player/playurl"
            f"?bvid={BVID}&cid={p['cid']}&qn=64&platform=html5&high_quality=1"
        )
        try:
            data = http_json(url, referer=ref)
            durl = data["data"]["durl"][0]
            out[vid] = (p["cid"], durl["size"], durl["url"])
        except Exception as e:
            print(f"  [probe FAIL] {vid}: {e}")
        time.sleep(0.5)
    return out


def main() -> int:
    pages = http_json(f"https://api.bilibili.com/x/player/pagelist?bvid={BVID}")["data"]
    print(f"Checking {len(pages)} parts...")
    expected = expected_for(pages)
    print(f"Probed {len(expected)} playurl entries")
    print()

    bad: list[tuple[str, str, int, int]] = []  # (vid, url, actual, expected)

    # Current filenames on disk may still use legacy naming for projects (p06/p18/p30/p41);
    # we check both new and legacy names.
    legacy = {1: "p06", 2: "p18", 3: "p30", 4: "p41"}
    legacy_rev = {v: f"project_{k:02d}_{PROJECT_NAMES[k]}" for k, v in legacy.items()}

    for vid, (cid, exp_size, url) in expected.items():
        disk_name = vid
        f = RAW_DIR / f"{disk_name}.mp4"
        if not f.exists():
            # Maybe it was saved under legacy project name
            for old, new in legacy_rev.items():
                if new == vid:
                    f = RAW_DIR / f"{old}.mp4"
                    break
        actual = f.stat().st_size if f.exists() else 0
        ok = actual == exp_size
        mark = "OK" if ok else "BAD"
        print(f"  [{mark}] {f.name:<36} actual={actual:>11}  expected={exp_size:>11}  diff={actual-exp_size:+}")
        if not ok:
            bad.append((vid, url, actual, exp_size))

    print(f"\nValid: {len(expected) - len(bad)}/{len(expected)}   Bad: {len(bad)}")
    if not bad:
        print("All files intact.")
        return 0

    print("\nRe-downloading bad files (curl -C - for resume)...")
    for vid, url, actual, exp in bad:
        dest = RAW_DIR / f"{vid}.mp4"
        if not dest.exists():
            # It may still be under legacy name
            for old, new in legacy_rev.items():
                if new == vid:
                    dest = RAW_DIR / f"{old}.mp4"
                    break
        print(f"  -> {dest.name} ({actual}/{exp})")
        rc = subprocess.call([
            "curl", "-L", "-C", "-",
            "--retry", "5", "--retry-delay", "5", "--retry-max-time", "300",
            "--connect-timeout", "15",
            "-A", UA,
            "-e", f"https://www.bilibili.com/video/{BVID}",
            "-o", str(dest),
            url,
        ])
        if rc != 0:
            print(f"    curl rc={rc}")
        else:
            new_size = dest.stat().st_size
            print(f"    now {new_size} (expected {exp}) {'OK' if new_size == exp else 'STILL BAD'}")
        time.sleep(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
