import csv
from pathlib import Path
from pipeline.utils.logger import get_logger

logger = get_logger("download")


def build_output_path(video_id: str, raw_dir: str) -> Path:
    return Path(raw_dir) / f"{video_id}.mp4"


def download_video(url: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    if output_path.exists():
        logger.info(f"[SKIP] Already downloaded: {output_path.name}")
        return output_path

    from yt_dlp import YoutubeDL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": str(output_path),
        "quiet": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    logger.info(f"[DONE] Downloaded: {output_path.name}")
    return output_path


def download_all(video_list_csv: str, raw_dir: str):
    with open(video_list_csv, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("video_id", "").startswith("#"):
                continue
            output = build_output_path(row["video_id"], raw_dir)
            try:
                download_video(row["bilibili_url"], output)
            except Exception as e:
                logger.error(f"[FAIL] {row['video_id']}: {e}")
