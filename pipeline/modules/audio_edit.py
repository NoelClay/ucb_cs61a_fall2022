import os
from pathlib import Path
from typing import Tuple
import ffmpeg
from pipeline.utils.logger import get_logger

logger = get_logger("audio_edit")


def get_spleeter_output_paths(video_id: str, audio_dir) -> Tuple[Path, Path]:
    audio_dir = Path(audio_dir)
    return (
        audio_dir / f"{video_id}_vocals.wav",
        audio_dir / f"{video_id}_bgm.wav",
    )


def extract_audio(video_path: Path, output_path: Path, sr: int = 44100):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    (
        ffmpeg
        .input(str(video_path))
        .output(str(output_path), ar=sr, ac=2, acodec="pcm_s16le")
        .run(overwrite_output=True, quiet=True)
    )
    logger.info(f"[AUDIO] Extracted: {output_path.name}")


def normalize_lufs(input_path: Path, output_path: Path, target_lufs: float = -18.0):
    (
        ffmpeg
        .input(str(input_path))
        .filter("loudnorm", I=target_lufs, LRA=11, TP=-1.5)
        .output(str(output_path))
        .run(overwrite_output=True, quiet=True)
    )
    logger.info(f"[NORM] {output_path.name} → {target_lufs} LUFS")


def separate_audio(
    audio_path: Path,
    video_id: str,
    audio_dir: Path,
    model_dir: str,
) -> Tuple[Path, Path]:
    vocals_path, bgm_path = get_spleeter_output_paths(video_id, audio_dir)

    if vocals_path.exists() and bgm_path.exists():
        logger.info(f"[SKIP] Spleeter output exists for {video_id}")
        return vocals_path, bgm_path

    from spleeter.separator import Separator
    import soundfile as sf

    os.environ.setdefault("MODEL_PATH", model_dir)
    sep = Separator("spleeter:2stems")
    prediction = sep.separate(str(audio_path))

    audio_dir = Path(audio_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)

    sf.write(str(vocals_path), prediction["vocals"], 44100)
    sf.write(str(bgm_path), prediction["accompaniment"], 44100)

    normalize_lufs(vocals_path, vocals_path, target_lufs=-18.0)
    normalize_lufs(bgm_path, bgm_path, target_lufs=-25.0)

    logger.info(f"[DONE] Spleeter: {video_id}")
    return vocals_path, bgm_path
