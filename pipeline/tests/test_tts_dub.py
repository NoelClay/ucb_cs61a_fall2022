from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock


def test_chunk_filename_format():
    from pipeline.modules.tts_dub import chunk_filename
    assert chunk_filename(1, "SPEAKER_00") == "chunk_0001_SPEAKER_00.wav"
    assert chunk_filename(42, "SPEAKER_01") == "chunk_0042_SPEAKER_01.wav"


def test_needs_speed_adjustment_within_tolerance():
    from pipeline.modules.tts_dub import needs_speed_adjustment
    assert not needs_speed_adjustment(original=4.0, generated=4.5, tolerance=0.25)
    assert not needs_speed_adjustment(original=4.0, generated=3.5, tolerance=0.25)


def test_needs_speed_adjustment_outside_tolerance():
    from pipeline.modules.tts_dub import needs_speed_adjustment
    assert needs_speed_adjustment(original=4.0, generated=5.5, tolerance=0.25)
    assert needs_speed_adjustment(original=4.0, generated=2.5, tolerance=0.25)


def test_needs_speed_adjustment_zero_original():
    from pipeline.modules.tts_dub import needs_speed_adjustment
    assert not needs_speed_adjustment(original=0.0, generated=1.0, tolerance=0.25)


def test_calculate_speed_ratio():
    from pipeline.modules.tts_dub import calculate_speed_ratio
    ratio = calculate_speed_ratio(original=4.0, generated=5.0)
    assert abs(ratio - 1.25) < 0.001


def test_rate_to_str():
    from pipeline.modules.tts_dub import _rate_to_str
    assert _rate_to_str(1.0) == "+0%"
    assert _rate_to_str(0.95) == "-5%"
    assert _rate_to_str(1.1) == "+10%"


def test_synthesize_chunk_writes_file(tmp_path):
    from pipeline.modules.tts_dub import synthesize_chunk

    fake_mp3 = b"\xff\xe3" + b"\x00" * 100
    fake_wav = b"RIFF" + b"\x00" * 36

    async def fake_save(path):
        Path(path).write_bytes(fake_mp3)

    mock_communicate = MagicMock()
    mock_communicate.save = fake_save

    mock_edge_tts = MagicMock()
    mock_edge_tts.Communicate.return_value = mock_communicate

    def fake_mp3_to_wav(mp3_path, wav_path):
        wav_path.write_bytes(fake_wav)

    out = tmp_path / "chunk_0001.wav"
    with patch.dict("sys.modules", {"edge_tts": mock_edge_tts}), \
         patch("pipeline.modules.tts_dub._mp3_to_wav", side_effect=fake_mp3_to_wav):
        synthesize_chunk(
            text="안녕하세요",
            output_path=out,
            voice_name="ko-KR-SunHiNeural",
            speaking_rate=0.95,
        )
        mock_edge_tts.Communicate.assert_called_once_with(
            "안녕하세요", "ko-KR-SunHiNeural", rate="-5%"
        )

    assert out.exists()
    assert out.read_bytes() == fake_wav
