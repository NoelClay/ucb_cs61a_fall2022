#!/usr/bin/env python3
"""
Harvest cs61a.org Fall 2022 archived assets from the Wayback Machine.

During Fall 2022 the course site served from the root path (cs61a.org/),
not /fa22/. We query the Wayback CDX index for the 2022-08 ~ 2022-12
window, pick the latest snapshot per URL, download raw content via the
`id_` modifier, and drop files into folders that mirror the CS61A site
layout.

Output layout (writes into the private `materials/` submodule):
    materials/lecture-notes/slides/             <- assets/slides/*.pdf
    materials/exams/fa22-archive/               <- assets/pdfs/*, exam/**
    materials/supplementary-lectures/articles/  <- articles/**
    materials/assignments/pdf-specs/lab/        <- lab/labNN/**
    materials/assignments/pdf-specs/hw/         <- hw/hwNN/**
    materials/assignments/pdf-specs/proj/       <- proj/**
    materials/assignments/pdf-specs/disc/       <- disc/discNN/**

Run from the public repo root so the relative paths resolve into the
`materials/` submodule working tree. If the submodule isn't initialized
(`git submodule update --init`), the paths won't exist and the script
will create them — commit the results inside the submodule repo, not
the public repo.

The script is idempotent: already-downloaded files are skipped.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0"
CDX = "https://web.archive.org/cdx/search/cdx"
FROM_TS, TO_TS = "20220801", "20221231"

# Map URL path prefix -> local destination directory.
# All writes land inside the private `materials/` submodule.
MATERIALS = Path("materials")
ROUTING = [
    ("assets/slides/",        MATERIALS / "lecture-notes/slides"),
    ("assets/pdfs/",          MATERIALS / "exams/fa22-archive"),
    ("exam/",                 MATERIALS / "exams/fa22-archive"),
    ("articles/",             MATERIALS / "supplementary-lectures/articles"),
    ("lab/",                  MATERIALS / "assignments/pdf-specs/lab"),
    ("hw/",                   MATERIALS / "assignments/pdf-specs/hw"),
    ("proj/",                 MATERIALS / "assignments/pdf-specs/proj"),
    ("disc/",                 MATERIALS / "assignments/pdf-specs/disc"),
]

# Mimetypes worth saving.
KEEP_MIMES = {
    "application/pdf",
    "text/html",
    "text/plain",
    "application/zip",
}


def cdx_query(mime: str | None = None, page: int = 0, page_size: int = 10000) -> list[list]:
    """One page of CDX results. Returns list of [urlkey, timestamp, original, mimetype, status, digest, length]."""
    params = {
        "url": "cs61a.org",
        "matchType": "domain",
        "from": FROM_TS,
        "to": TO_TS,
        "output": "json",
        "filter": ["statuscode:200"],
        "limit": str(page_size),
        "offset": str(page * page_size),
    }
    if mime:
        params["filter"] = ["statuscode:200", f"mimetype:{mime}"]
    # urlencode handles list values by repeating key
    qs = urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(f"{CDX}?{qs}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data[1:] if len(data) > 1 else []  # skip header row


def latest_per_url(rows: list[list]) -> dict[str, tuple[str, int]]:
    """For each original URL, keep the (timestamp, byte_length) with the largest timestamp."""
    best: dict[str, tuple[str, int]] = {}
    for row in rows:
        ts = row[1]
        orig = row[2]
        try:
            length = int(row[6]) if row[6].isdigit() else 0
        except (IndexError, AttributeError):
            length = 0
        prev = best.get(orig)
        if prev is None or ts > prev[0]:
            best[orig] = (ts, length)
    return best


def pick_dest(path: str) -> Path | None:
    """Given a URL path (without leading /), return the local directory it should live in."""
    for prefix, dest in ROUTING:
        if path.startswith(prefix):
            return dest
    return None


def local_path(original_url: str) -> Path | None:
    """Translate an archived cs61a.org URL into a local filesystem Path, or None to skip."""
    # original_url like "https://cs61a.org/assets/slides/01-Computer_Science_1pp.pdf"
    p = urllib.parse.urlparse(original_url)
    rel = p.path.lstrip("/")
    if not rel:
        return None  # root index
    dest_dir = pick_dest(rel)
    if dest_dir is None:
        return None
    # Strip the prefix we routed on, and keep the rest as subpath
    for prefix, dd in ROUTING:
        if dd == dest_dir and rel.startswith(prefix):
            rel_sub = rel[len(prefix):]
            break
    else:
        rel_sub = rel
    if not rel_sub or rel_sub.endswith("/"):
        # directory index -> save as index.html
        rel_sub = (rel_sub + "index.html") if rel_sub.endswith("/") else "index.html"
    return dest_dir / rel_sub


def download_snapshot(original_url: str, timestamp: str, dest: Path,
                     max_retries: int = 3) -> bool:
    """Fetch raw archived content. Retries with exponential backoff on connection errors."""
    if dest.exists() and dest.stat().st_size > 0:
        return True
    wb_url = f"https://web.archive.org/web/{timestamp}id_/{original_url}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(wb_url, headers={"User-Agent": UA})

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            break
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            wait = 15 * (2 ** attempt)  # 15s, 30s, 60s
            msg = str(e)
            if attempt < max_retries - 1:
                print(f"    [retry {attempt+1}/{max_retries}] {msg[:60]} — sleep {wait}s")
                time.sleep(wait)
            else:
                print(f"    [FAIL after {max_retries} tries] {msg[:80]}")
                return False
    else:
        return False

    if len(data) < 200 and b"wayback" in data.lower():
        print(f"    [SKIP empty] {original_url}")
        return False
    dest.write_bytes(data)
    return True


def main() -> int:
    print(f"Querying CDX for cs61a.org from {FROM_TS} to {TO_TS} ...")
    all_rows: list[list] = []
    for mime in ["application/pdf", "text/html"]:
        page = 0
        while True:
            batch = cdx_query(mime=mime, page=page, page_size=10000)
            if not batch:
                break
            all_rows.extend(batch)
            print(f"  {mime} page {page}: +{len(batch)} rows (total {len(all_rows)})")
            if len(batch) < 10000:
                break
            page += 1
    print(f"Total CDX rows: {len(all_rows)}")

    best = latest_per_url(all_rows)
    print(f"Unique URLs: {len(best)}")

    # Filter by routing
    targets: list[tuple[str, str, Path]] = []
    for url, (ts, _length) in best.items():
        dest = local_path(url)
        if dest is None:
            continue
        targets.append((url, ts, dest))
    print(f"URLs routed to local paths: {len(targets)}")

    # Summary per dest dir
    from collections import Counter
    counts = Counter(str(d.parent) if d.suffix else str(d) for _, _, d in targets)
    for d, n in counts.most_common():
        print(f"  {n:>4}  {d}")

    # Download
    ok = fail = skip = 0
    for i, (url, ts, dest) in enumerate(targets, 1):
        if dest.exists() and dest.stat().st_size > 0:
            skip += 1
            continue
        print(f"[{i:>4}/{len(targets)}] {dest}")
        if download_snapshot(url, ts, dest):
            ok += 1
        else:
            fail += 1
        time.sleep(2.0)  # be a friendly Wayback client
    print(f"\nDONE: downloaded={ok} skipped={skip} failed={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
