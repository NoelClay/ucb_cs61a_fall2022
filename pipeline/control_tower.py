import csv
import json
import os
import shutil
from pathlib import Path
from typing import List, Dict

import yaml

from pipeline.utils.logger import get_logger
from pipeline.utils.state_manager import StateManager

logger = get_logger("control_tower")


class ControlTower:
    def __init__(self, config_path: str, data_dir: Path = None):
        with open(config_path, encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.data_dir = Path(data_dir) if data_dir else Path(
            os.environ.get("USB_ROOT", ".") + "/data"
        )
        self.state_manager = StateManager(self.data_dir / "progress.json")
        self.failed_videos: List[str] = []

    # ── Stage runners ────────────────────────────────────────────────────────

    def run_download(self, video_id: str, url: str):
        from pipeline.modules.download import download_video, build_output_path
        output = build_output_path(video_id, self.data_dir / "00_raw")
        download_video(url, output)

    def run_transcribe(self, video_id: str):
        from pipeline.modules.transcribe import transcribe_video
        transcribe_video(
            video_path=self.data_dir / "00_raw" / f"{video_id}.mp4",
            output_path=self.data_dir / "01_transcripts" / f"{video_id}.json",
            model_dir=os.environ.get("WHISPER_MODEL_DIR", "models/whisperx"),
            hf_token=os.environ.get("HF_TOKEN", ""),
            model=self.config["whisperx"]["model"],
        )

    def run_subtitle(self, video_id: str) -> List[Dict]:
        from pipeline.modules.subtitle import (
            merge_segments, segments_to_srt,
            translate_subtitles_with_claude, save_srt,
        )
        transcript = json.loads(
            (self.data_dir / "01_transcripts" / f"{video_id}.json").read_text()
        )
        merged = merge_segments(
            transcript["segments"],
            min_duration=self.config["subtitle"]["min_duration_sec"],
            max_duration=self.config["subtitle"]["max_duration_sec"],
            max_chars=self.config["subtitle"]["max_chars_per_line"],
        )
        en_srt = segments_to_srt(merged, include_speaker=True)
        save_srt(en_srt, self.data_dir / "02_subtitles" / f"{video_id}_en.srt")

        ko_segments = translate_subtitles_with_claude(
            merged,
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            cs_terms_path="pipeline/utils/cs_terms.yaml",
            batch_size=self.config["subtitle"]["batch_size"],
        )
        ko_srt = segments_to_srt(ko_segments, include_speaker=True)
        save_srt(ko_srt, self.data_dir / "02_subtitles" / f"{video_id}_ko.srt")
        return ko_segments

    def run_audio_edit(self, video_id: str):
        from pipeline.modules.audio_edit import extract_audio, separate_audio
        video_path = self.data_dir / "00_raw" / f"{video_id}.mp4"
        wav_path = self.data_dir / "03_audio" / f"{video_id}.wav"
        extract_audio(video_path, wav_path)
        separate_audio(
            wav_path, video_id,
            self.data_dir / "03_audio",
            os.environ.get("SPLEETER_MODEL_DIR", "models/spleeter"),
        )

    def run_tts_dub(self, video_id: str, ko_segments: List[Dict]) -> List[Dict]:
        from pipeline.modules.tts_dub import dub_segments
        speaker_cfg_path = Path("pipeline/utils/speaker_config.yaml")
        with open(speaker_cfg_path, encoding="utf-8") as f:
            speaker_cfg = yaml.safe_load(f)
        return dub_segments(
            ko_segments,
            output_dir=self.data_dir / "04_dubbed_chunks" / video_id,
            speaker_config=speaker_cfg,
            tolerance=self.config["tts"]["timing_tolerance"],
        )

    def run_synthesize(self, video_id: str, dubbed_chunks: List[Dict]):
        from pipeline.modules.synthesize import synthesize_final_video
        synthesize_final_video(
            original_video=self.data_dir / "00_raw" / f"{video_id}.mp4",
            bgm_path=self.data_dir / "03_audio" / f"{video_id}_bgm.wav",
            dubbed_chunks=dubbed_chunks,
            output_path=self.data_dir / "05_output" / f"{video_id}_ko.mp4",
        )
        # 청크 삭제 (USB 용량 절약)
        chunks_dir = self.data_dir / "04_dubbed_chunks" / video_id
        if chunks_dir.exists():
            shutil.rmtree(chunks_dir)
            logger.info(f"[CLEANUP] Removed chunks: {chunks_dir.name}")

    # ── Orchestration ────────────────────────────────────────────────────────

    def process_video(self, video_id: str, url: str):
        sm = self.state_manager
        logger.info(f"[START] {video_id}")

        if sm.is_before(video_id, "DOWNLOADED"):
            self.run_download(video_id, url)
            sm.set_state(video_id, "DOWNLOADED")

        if sm.is_before(video_id, "TRANSCRIBED"):
            self.run_transcribe(video_id)
            sm.set_state(video_id, "TRANSCRIBED")

        ko_segments = None
        if sm.is_before(video_id, "SUBTITLED"):
            ko_segments = self.run_subtitle(video_id)
            sm.set_state(video_id, "SUBTITLED")

        if sm.is_before(video_id, "AUDIO_EDITED"):
            self.run_audio_edit(video_id)
            sm.set_state(video_id, "AUDIO_EDITED")

        dubbed_chunks = None
        if sm.is_before(video_id, "DUBBED"):
            if ko_segments is None:
                ko_segments = self._load_ko_segments(video_id)
            dubbed_chunks = self.run_tts_dub(video_id, ko_segments)
            sm.set_state(video_id, "DUBBED")

        if sm.is_before(video_id, "SYNTHESIZED"):
            if dubbed_chunks is None:
                dubbed_chunks = self._load_dubbed_chunks(video_id)
            self.run_synthesize(video_id, dubbed_chunks)
            sm.set_state(video_id, "DONE")

        logger.info(f"[DONE] {video_id}")

    def process_all(self, video_list: List[Dict]):
        for item in video_list:
            if item.get("video_id", "").startswith("#"):
                continue
            try:
                self.process_video(item["video_id"], item["bilibili_url"])
            except Exception as e:
                logger.error(f"[FAIL] {item['video_id']}: {e}")
                self.failed_videos.append(item["video_id"])

    def process_csv(self, csv_path: str):
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.process_all(rows)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _load_ko_segments(self, video_id: str) -> List[Dict]:
        from pipeline.modules.subtitle import _parse_numbered_translations
        srt_path = self.data_dir / "02_subtitles" / f"{video_id}_ko.srt"
        if not srt_path.exists():
            return []
        lines = srt_path.read_text(encoding="utf-8").strip().split("\n\n")
        segments = []
        for block in lines:
            parts = block.strip().split("\n")
            if len(parts) >= 3:
                times = parts[1].split(" --> ")
                segments.append({
                    "start": _srt_time_to_sec(times[0]),
                    "end": _srt_time_to_sec(times[1]),
                    "text": " ".join(parts[2:]),
                    "speaker": "SPEAKER_UNKNOWN",
                })
        return segments

    def _load_dubbed_chunks(self, video_id: str) -> List[Dict]:
        chunks_dir = self.data_dir / "04_dubbed_chunks" / video_id
        if not chunks_dir.exists():
            return []
        return sorted(
            [{"path": p, "start": 0.0, "end": 0.0} for p in chunks_dir.glob("*.wav")],
            key=lambda x: x["path"].name,
        )


def _srt_time_to_sec(t: str) -> float:
    t = t.strip().replace(",", ".")
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)
