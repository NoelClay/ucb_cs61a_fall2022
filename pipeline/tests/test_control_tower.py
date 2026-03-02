import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def _make_ko_srt(data_dir: Path, video_id: str):
    """Korean SRT 파일을 미리 생성 (번역 완료 시뮬레이션)."""
    srt_dir = data_dir / "02_subtitles"
    srt_dir.mkdir(parents=True, exist_ok=True)
    (srt_dir / f"{video_id}_ko.srt").write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n[SPEAKER_00]\n안녕하세요\n",
        encoding="utf-8",
    )


def test_process_video_calls_all_stages(tmp_path):
    from pipeline.control_tower import ControlTower

    _make_ko_srt(tmp_path, "lecture_01")
    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)

    mocks = {
        "run_download": MagicMock(return_value=None),
        "run_transcribe": MagicMock(return_value=None),
        "run_subtitle": MagicMock(return_value=None),
        "run_audio_edit": MagicMock(return_value=None),
        "run_tts_dub": MagicMock(return_value=[]),
        "run_synthesize": MagicMock(return_value=None),
    }
    with patch.multiple(ct, **mocks):
        ct.process_video("lecture_01", "https://fake-url")
        mocks["run_download"].assert_called_once()
        mocks["run_transcribe"].assert_called_once()
        mocks["run_subtitle"].assert_called_once()
        mocks["run_audio_edit"].assert_called_once()
        mocks["run_tts_dub"].assert_called_once()
        mocks["run_synthesize"].assert_called_once()


def test_process_video_resumes_from_state(tmp_path):
    from pipeline.control_tower import ControlTower
    from pipeline.utils.state_manager import StateManager

    _make_ko_srt(tmp_path, "lecture_01")
    sm = StateManager(tmp_path / "progress.json")
    sm.set_state("lecture_01", "TRANSCRIBED")

    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    ct.state_manager = sm

    mocks = {
        "run_download": MagicMock(return_value=None),
        "run_transcribe": MagicMock(return_value=None),
        "run_subtitle": MagicMock(return_value=None),
        "run_audio_edit": MagicMock(return_value=None),
        "run_tts_dub": MagicMock(return_value=[]),
        "run_synthesize": MagicMock(return_value=None),
    }
    with patch.multiple(ct, **mocks):
        ct.process_video("lecture_01", "https://fake-url")
        mocks["run_download"].assert_not_called()
        mocks["run_transcribe"].assert_not_called()
        mocks["run_subtitle"].assert_called_once()
        mocks["run_audio_edit"].assert_called_once()


def test_process_video_translation_pending(tmp_path):
    from pipeline.control_tower import ControlTower, TranslationPendingError
    from pipeline.utils.state_manager import StateManager

    # 한국어 SRT 없음 → TRANSLATION PENDING 상태
    sm = StateManager(tmp_path / "progress.json")
    sm.set_state("lecture_01", "SUBTITLED")

    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    ct.state_manager = sm

    with pytest.raises(TranslationPendingError):
        ct.process_video("lecture_01", "https://fake-url")


def test_process_all_records_failures(tmp_path):
    from pipeline.control_tower import ControlTower

    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    with patch.object(ct, "process_video", side_effect=Exception("boom")):
        ct.process_all([
            {"video_id": "lecture_01", "bilibili_url": "https://x"},
            {"video_id": "lecture_02", "bilibili_url": "https://y"},
        ])

    assert "lecture_01" in ct.failed_videos
    assert "lecture_02" in ct.failed_videos


def test_process_all_skips_comment_rows(tmp_path):
    from pipeline.control_tower import ControlTower

    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    called = []
    with patch.object(ct, "process_video", side_effect=lambda vid, url: called.append(vid)):
        ct.process_all([
            {"video_id": "#comment", "bilibili_url": "https://x"},
            {"video_id": "lecture_01", "bilibili_url": "https://y"},
        ])

    assert called == ["lecture_01"]


def test_process_all_does_not_fail_on_translation_pending(tmp_path):
    from pipeline.control_tower import ControlTower, TranslationPendingError

    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    with patch.object(ct, "process_video", side_effect=TranslationPendingError("대기중")):
        ct.process_all([
            {"video_id": "lecture_01", "bilibili_url": "https://x"},
        ])

    # TranslationPendingError는 failed_videos에 추가되지 않는다
    assert "lecture_01" not in ct.failed_videos
