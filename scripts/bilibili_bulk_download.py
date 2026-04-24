#!/usr/bin/env python3
"""
Anonymous Bilibili anthology bulk downloader.

Uses the legacy playurl API (api.bilibili.com/x/player/playurl) with
platform=html5 to fetch MP4 URLs without login. Only qualities exposed
anonymously are 720P (qn=64) and 360P (qn=16); 480P is not offered for
CS61A Fall 2022.

Usage:
    python3 bilibili_bulk_download.py BV1GK411Q7qp --qn 64 --out data/01_raw

Writes:
    <out>/<video_id>.mp4 for each anthology part
    pipeline/video_list.csv regenerated with all entries
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
PAGELIST_API = "https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
PLAYURL_API = (
    "https://api.bilibili.com/x/player/playurl"
    "?bvid={bvid}&cid={cid}&qn={qn}&platform=html5&high_quality=1"
)


def http_json(url: str, referer: str | None = None) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    if referer:
        req.add_header("Referer", referer)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_pagelist(bvid: str) -> list[dict]:
    data = http_json(PAGELIST_API.format(bvid=bvid))
    if data.get("code") != 0:
        raise RuntimeError(f"pagelist failed: {data}")
    return data["data"]


def fetch_playurl(bvid: str, cid: int, qn: int) -> dict:
    url = PLAYURL_API.format(bvid=bvid, cid=cid, qn=qn)
    ref = f"https://www.bilibili.com/video/{bvid}"
    data = http_json(url, referer=ref)
    if data.get("code") != 0:
        raise RuntimeError(f"playurl failed cid={cid}: {data}")
    return data["data"]


def classify(part_title: str, page: int) -> tuple[str, str]:
    """
    Return (video_id, type) from Bilibili part title.

    Examples:
        "61A Fall 2022 Lecture 1-Computer Science"  -> ("lecture_01", "lecture")
        "CS 61A Fall 2022 Lecture 37"               -> ("lecture_37", "lecture")
        "Disc1-Control, Environment Diagrams"       -> ("disc_01",    "discussion")
        (unrecognized)                              -> ("p05",        "other")
    """
    t = part_title.strip()
    m = re.search(r"[Ll]ecture\s+(\d+)", t)
    if m:
        n = int(m.group(1))
        return (f"lecture_{n:02d}", "lecture")
    m = re.search(r"[Dd]isc(?:ussion)?\s*(\d+)", t)
    if m:
        n = int(m.group(1))
        return (f"disc_{n:02d}", "discussion")
    return (f"p{page:02d}", "other")


def sanitize(s: str) -> str:
    s = re.sub(r"[\\/:*?\"<>|]", "_", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:120]


def download(url: str, dest: Path, ref_url: str, expected_size: int | None) -> bool:
    """Resumable curl download. Returns True on success."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and expected_size and dest.stat().st_size == expected_size:
        print(f"    [SKIP] already have {dest.name} ({expected_size/1024/1024:.1f}MB)")
        return True
    cmd = [
        "curl", "-L", "-C", "-",
        "--retry", "5", "--retry-delay", "3",
        "--connect-timeout", "15",
        "-A", UA,
        "-e", ref_url,
        "-o", str(dest),
        url,
    ]
    rc = subprocess.call(cmd)
    if rc != 0:
        print(f"    [FAIL] curl rc={rc}")
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bvid", help="e.g. BV1GK411Q7qp")
    ap.add_argument("--qn", type=int, default=64, help="64=720P, 16=360P")
    ap.add_argument("--out", default="data/01_raw", help="video output dir")
    ap.add_argument("--csv", default="pipeline/video_list.csv",
                    help="video_list.csv path to regenerate")
    ap.add_argument("--limit", type=int, default=0, help="stop after N parts (0=all)")
    ap.add_argument("--sleep", type=float, default=1.5,
                    help="seconds between downloads to avoid throttling")
    args = ap.parse_args()

    out_dir = Path(args.out).resolve()
    csv_path = Path(args.csv).resolve()
    print(f"BV: {args.bvid}  qn: {args.qn}  out: {out_dir}")

    pages = fetch_pagelist(args.bvid)
    print(f"pagelist: {len(pages)} parts")

    rows: list[dict] = []
    failures: list[str] = []
    total = len(pages) if args.limit == 0 else min(args.limit, len(pages))

    for i, p in enumerate(pages[:total], start=1):
        page = p["page"]
        cid = p["cid"]
        part = p["part"]
        vid, vtype = classify(part, page)
        disp = f"[{i:>2}/{total}] p{page:02d} {vid:<12} {part[:60]}"
        print(disp)

        try:
            info = fetch_playurl(args.bvid, cid, args.qn)
        except Exception as e:
            print(f"    [FAIL] playurl: {e}")
            failures.append(vid)
            time.sleep(args.sleep)
            continue

        durl = info.get("durl", [{}])[0]
        mp4_url = durl.get("url")
        size = durl.get("size")
        actual_q = info.get("quality")
        if not mp4_url:
            print(f"    [FAIL] no durl")
            failures.append(vid)
            time.sleep(args.sleep)
            continue

        if actual_q != args.qn:
            print(f"    [WARN] requested qn={args.qn} but got quality={actual_q}")

        dest = out_dir / f"{vid}.mp4"
        ok = download(
            mp4_url, dest,
            ref_url=f"https://www.bilibili.com/video/{args.bvid}?p={page}",
            expected_size=size,
        )
        if not ok:
            failures.append(vid)

        rows.append({
            "video_id": vid,
            "title": sanitize(part),
            "type": vtype,
            "bilibili_url": f"https://www.bilibili.com/video/{args.bvid}?p={page}",
        })
        time.sleep(args.sleep)

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["video_id", "title", "type", "bilibili_url"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nCSV updated: {csv_path} ({len(rows)} rows)")

    if failures:
        print(f"\n{len(failures)} FAILURES: {failures}")
        return 1
    print(f"\nAll {len(rows)} parts OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
