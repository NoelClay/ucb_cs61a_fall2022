from pathlib import Path
from typing import List, Dict
from pipeline.utils.logger import get_logger

logger = get_logger("tts_dub")


def chunk_filename(seq: int, speaker: str) -> str:
    return f"chunk_{seq:04d}_{speaker}.wav"


def needs_speed_adjustment(
    original: float, generated: float, tolerance: float = 0.25
) -> bool:
    if original <= 0:
        return False
    ratio = generated / original
    return abs(ratio - 1.0) > tolerance


def calculate_speed_ratio(original: float, generated: float) -> float:
    return generated / original


def _rate_to_str(speaking_rate: float) -> str:
    """float 속도(1.0 기준)를 edge-tts rate 문자열로 변환."""
    pct = int(round((speaking_rate - 1.0) * 100))
    return f"{'+' if pct >= 0 else ''}{pct}%"


def _mp3_to_wav(mp3_path: Path, wav_path: Path):
    """ffmpeg으로 MP3 → WAV 24kHz mono 변환."""
    import ffmpeg
    ffmpeg.input(str(mp3_path)).output(
        str(wav_path), ar=24000, ac=1
    ).run(overwrite_output=True, quiet=True)


def synthesize_chunk(
    text: str,
    output_path: Path,
    voice_name: str,
    speaking_rate: float = 1.0,
    pitch: float = 0.0,  # 인터페이스 호환용 (edge-tts에서는 사용 안 함)
):
    import asyncio
    import edge_tts

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rate_str = _rate_to_str(speaking_rate)
    mp3_path = output_path.with_suffix(".mp3")

    async def _run():
        communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
        await communicate.save(str(mp3_path))

    asyncio.run(_run())
    _mp3_to_wav(mp3_path, output_path)
    mp3_path.unlink(missing_ok=True)
    logger.info(f"[TTS] {output_path.name}")


def adjust_speed(input_path: Path, output_path: Path, ratio: float):
    """pyrubberband으로 피치 보존 속도 조정."""
    import soundfile as sf
    import pyrubberband as rb

    data, sr = sf.read(str(input_path))
    stretched = rb.time_stretch(data, sr, 1.0 / ratio)
    sf.write(str(output_path), stretched, sr)
    logger.info(f"[SPEED] {output_path.name} ratio={ratio:.2f}")


def _get_wav_duration(path: Path) -> float:
    import soundfile as sf
    info = sf.info(str(path))
    return info.duration


def dub_segments(
    ko_segments: List[Dict],
    output_dir: Path,
    speaker_config: dict,
    tolerance: float = 0.25,
) -> List[Dict]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for i, seg in enumerate(ko_segments):
        speaker = seg["speaker"]
        cfg = speaker_config.get(speaker, speaker_config.get("SPEAKER_UNKNOWN", {}))
        fname = chunk_filename(i + 1, speaker)
        chunk_path = output_dir / fname

        if chunk_path.exists():
            logger.info(f"[SKIP] {fname}")
        else:
            synthesize_chunk(
                text=seg["text"],
                output_path=chunk_path,
                voice_name=cfg.get("voice", "ko-KR-SunHiNeural"),
                speaking_rate=cfg.get("speaking_rate", 1.0),
                pitch=cfg.get("pitch", 0.0),
            )
            original_dur = seg["end"] - seg["start"]
            generated_dur = _get_wav_duration(chunk_path)
            if needs_speed_adjustment(original_dur, generated_dur, tolerance):
                ratio = calculate_speed_ratio(original_dur, generated_dur)
                logger.info(f"[ADJUST] {fname} ratio={ratio:.2f}")
                adjust_speed(chunk_path, chunk_path, ratio)

        results.append({
            "path": chunk_path,
            "start": seg["start"],
            "end": seg["end"],
            "speaker": speaker,
        })

    return results
