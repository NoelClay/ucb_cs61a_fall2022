import json
from pathlib import Path
from pipeline.utils.logger import get_logger

logger = get_logger("transcribe")


def normalize_transcript(raw: dict) -> dict:
    """WhisperX 출력을 표준 포맷으로 정규화."""
    segments = raw.get("segments", [])
    normalized = []
    for seg in segments:
        normalized.append({
            "start": seg.get("start", 0.0),
            "end": seg.get("end", 0.0),
            "text": seg.get("text", "").strip(),
            "speaker": seg.get("speaker", "SPEAKER_UNKNOWN"),
            "words": seg.get("words", []),
        })
    return {"segments": normalized}


def save_transcript(transcript: dict, output_path: Path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"[SAVED] {output_path.name}")


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def transcribe_video(
    video_path: Path,
    output_path: Path,
    model_dir: str,
    hf_token: str,
    model: str = "large-v2",
) -> dict:
    """WhisperX로 영상 전사 + 화자 분리. WhisperX 미설치 시 ImportError."""
    import whisperx

    video_path = Path(video_path)
    output_path = Path(output_path)

    if output_path.exists():
        logger.info(f"[SKIP] Transcript exists: {output_path.name}")
        return json.loads(output_path.read_text())

    logger.info(f"[START] Transcribing {video_path.name}")
    device = "cuda" if _cuda_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    model_obj = whisperx.load_model(
        model, device, compute_type=compute_type, download_root=model_dir
    )
    audio = whisperx.load_audio(str(video_path))
    result = model_obj.transcribe(audio, language="en")

    align_model, metadata = whisperx.load_align_model(language_code="en", device=device)
    result = whisperx.align(result["segments"], align_model, metadata, audio, device)

    diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_token, device=device)
    diarize_segments = diarize_model(audio, min_speakers=1, max_speakers=5)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    normalized = normalize_transcript(result)
    save_transcript(normalized, output_path)
    logger.info(f"[DONE] {len(normalized['segments'])} segments transcribed")
    return normalized
