from pathlib import Path
from unittest.mock import patch, MagicMock


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


def test_synthesize_chunk_writes_file(tmp_path):
    from pipeline.modules.tts_dub import synthesize_chunk

    fake_audio_bytes = b"RIFF" + b"\x00" * 36

    mock_response = MagicMock()
    mock_response.audio_content = fake_audio_bytes

    mock_client = MagicMock()
    mock_client.synthesize_speech.return_value = mock_response

    mock_tts = MagicMock()
    mock_tts.TextToSpeechClient.return_value = mock_client
    mock_tts.AudioEncoding.LINEAR16 = "LINEAR16"

    mock_google_cloud = MagicMock()
    mock_google_cloud.texttospeech = mock_tts

    mock_google = MagicMock()
    mock_google.cloud = mock_google_cloud

    out = tmp_path / "chunk_0001.wav"
    with patch.dict("sys.modules", {
        "google": mock_google,
        "google.cloud": mock_google_cloud,
        "google.cloud.texttospeech": mock_tts,
    }):
        synthesize_chunk(
            text="안녕하세요",
            output_path=out,
            voice_name="ko-KR-Neural2-C",
            speaking_rate=0.95,
            pitch=-1.0,
        )

    assert out.exists()
    assert out.read_bytes() == fake_audio_bytes
