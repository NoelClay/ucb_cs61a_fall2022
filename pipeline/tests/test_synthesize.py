import numpy as np
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def _make_wav(path, duration=1.0, sr=44100, value=0.1):
    try:
        import soundfile as sf
        data = np.full(int(sr * duration), value, dtype=np.float32)
        sf.write(str(path), data, sr)
    except ImportError:
        path.write_bytes(b"\x00" * int(sr * duration * 2))
    return path


def test_place_chunks_empty():
    from pipeline.modules.synthesize import place_chunks_on_timeline
    timeline = place_chunks_on_timeline([], total_duration=2.0, sr=100)
    assert len(timeline) == 200
    assert np.all(timeline == 0.0)


def test_place_chunks_correct_length(tmp_path):
    from pipeline.modules.synthesize import place_chunks_on_timeline

    wav = tmp_path / "chunk.wav"
    try:
        import soundfile as sf
        data = np.zeros(100, dtype=np.float32)
        sf.write(str(wav), data, 100)
        chunks = [{"path": wav, "start": 0.0, "end": 1.0}]
        timeline = place_chunks_on_timeline(chunks, total_duration=2.0, sr=100)
        assert len(timeline) == 200
    except ImportError:
        pytest.skip("soundfile not installed")


def test_mix_audio_with_voice():
    from pipeline.modules.synthesize import mix_audio
    sr = 100
    voice = np.full(sr, 0.5, dtype=np.float32)
    bgm = np.full(sr, 1.0, dtype=np.float32)
    has_voice = [True] * sr
    mixed = mix_audio(voice, bgm, has_voice)
    # voice 구간: bgm이 -20dB(약 0.1배)로 줄어들어야 함
    assert mixed[0] > 0
    assert mixed.shape == voice.shape


def test_mix_audio_without_voice():
    from pipeline.modules.synthesize import mix_audio
    sr = 100
    voice = np.zeros(sr, dtype=np.float32)
    bgm = np.full(sr, 0.8, dtype=np.float32)
    has_voice = [False] * sr
    mixed = mix_audio(voice, bgm, has_voice)
    # 음성 없는 구간: bgm 그대로
    assert abs(mixed[0] - 0.8) < 0.01


def test_synthesize_final_video_skips_if_exists(tmp_path):
    from pipeline.modules.synthesize import synthesize_final_video
    output = tmp_path / "output.mp4"
    output.write_bytes(b"fake mp4")
    result = synthesize_final_video(
        original_video=tmp_path / "video.mp4",
        bgm_path=tmp_path / "bgm.wav",
        dubbed_chunks=[],
        output_path=output,
    )
    assert result == output
