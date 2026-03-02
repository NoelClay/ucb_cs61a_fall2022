import os
import tempfile
from pathlib import Path
from typing import List, Dict
import numpy as np
import ffmpeg
from pipeline.utils.logger import get_logger

logger = get_logger("synthesize")


def place_chunks_on_timeline(
    chunks: List[Dict], total_duration: float, sr: int = 44100
) -> np.ndarray:
    timeline = np.zeros(int(total_duration * sr), dtype=np.float32)
    for chunk in chunks:
        try:
            import soundfile as sf
            data, chunk_sr = sf.read(str(chunk["path"]))
        except Exception as e:
            logger.warning(f"[WARN] Cannot read {chunk['path']}: {e}")
            continue
        if data.ndim > 1:
            data = data.mean(axis=1)
        if chunk_sr != sr:
            import librosa
            data = librosa.resample(data, orig_sr=chunk_sr, target_sr=sr)
        start_idx = int(chunk["start"] * sr)
        end_idx = min(start_idx + len(data), len(timeline))
        copy_len = end_idx - start_idx
        if copy_len > 0:
            timeline[start_idx:end_idx] += data[:copy_len]
    return timeline


def mix_audio(
    voice: np.ndarray, bgm: np.ndarray, has_voice: List[bool]
) -> np.ndarray:
    bgm_in_voice = 10 ** (-20 / 20)  # -20dB
    mixed = np.zeros_like(voice)
    for i in range(len(mixed)):
        v = voice[i] if i < len(voice) else 0.0
        b = bgm[i] if i < len(bgm) else 0.0
        if i < len(has_voice) and has_voice[i]:
            mixed[i] = v + b * bgm_in_voice
        else:
            mixed[i] = b
    return mixed


def get_video_duration(video_path: Path) -> float:
    probe = ffmpeg.probe(str(video_path))
    return float(probe["format"]["duration"])


def synthesize_final_video(
    original_video: Path,
    bgm_path: Path,
    dubbed_chunks: List[Dict],
    output_path: Path,
    sr: int = 44100,
) -> Path:
    original_video = Path(original_video)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        logger.info(f"[SKIP] Output exists: {output_path.name}")
        return output_path

    import soundfile as sf

    total_dur = get_video_duration(original_video)
    logger.info(f"[SYNTH] Building {total_dur:.1f}s timeline")

    voice_timeline = place_chunks_on_timeline(dubbed_chunks, total_dur, sr)

    bgm_data, bgm_sr = sf.read(str(bgm_path))
    if bgm_data.ndim > 1:
        bgm_data = bgm_data.mean(axis=1)
    if bgm_sr != sr:
        import librosa
        bgm_data = librosa.resample(bgm_data, orig_sr=bgm_sr, target_sr=sr)

    n = len(voice_timeline)
    if len(bgm_data) < n:
        bgm_data = np.pad(bgm_data, (0, n - len(bgm_data)))
    else:
        bgm_data = bgm_data[:n]

    has_voice = (np.abs(voice_timeline) > 1e-6).tolist()
    mixed = mix_audio(voice_timeline, bgm_data, has_voice)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, mixed, sr)
        tmp_audio = tmp.name

    try:
        # ffmpeg-python: video와 audio 스트림을 명시적으로 분리하여 map 충돌 방지
        video_in = ffmpeg.input(str(original_video))
        audio_in = ffmpeg.input(tmp_audio)
        (
            ffmpeg
            .output(
                video_in.video,
                audio_in.audio,
                str(output_path),
                vcodec="copy",
                acodec="aac",
                audio_bitrate="192k",
            )
            .run(overwrite_output=True, quiet=True)
        )
    finally:
        os.unlink(tmp_audio)

    logger.info(f"[DONE] {output_path.name}")
    return output_path
