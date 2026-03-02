SAMPLE_SEGMENTS = [
    {"start": 0.0, "end": 3.2, "text": "Welcome to CS61A.", "speaker": "SPEAKER_00"},
    {"start": 3.5, "end": 6.0, "text": "Today we talk about functions.", "speaker": "SPEAKER_00"},
    {"start": 6.5, "end": 9.0, "text": "What is a function?", "speaker": "SPEAKER_01"},
]


def test_format_timestamp_zero():
    from pipeline.modules.subtitle import format_timestamp
    assert format_timestamp(0.0) == "00:00:00,000"


def test_format_timestamp_nonzero():
    from pipeline.modules.subtitle import format_timestamp
    assert format_timestamp(3661.5) == "01:01:01,500"


def test_segments_to_srt_numbering():
    from pipeline.modules.subtitle import segments_to_srt
    srt = segments_to_srt(SAMPLE_SEGMENTS)
    assert "1\n" in srt
    assert "2\n" in srt


def test_segments_to_srt_timestamp_format():
    from pipeline.modules.subtitle import segments_to_srt
    srt = segments_to_srt(SAMPLE_SEGMENTS)
    assert "00:00:00,000 --> 00:00:03,200" in srt


def test_segments_to_srt_text_content():
    from pipeline.modules.subtitle import segments_to_srt
    srt = segments_to_srt(SAMPLE_SEGMENTS)
    assert "Welcome to CS61A." in srt


def test_segments_to_srt_with_speaker_tag():
    from pipeline.modules.subtitle import segments_to_srt
    srt = segments_to_srt(SAMPLE_SEGMENTS, include_speaker=True)
    assert "[SPEAKER_00]" in srt
    assert "[SPEAKER_01]" in srt


def test_merge_short_segments_same_speaker():
    from pipeline.modules.subtitle import merge_segments
    short = [
        {"start": 0.0, "end": 0.3, "text": "Hello", "speaker": "SPEAKER_00"},
        {"start": 0.4, "end": 0.8, "text": "world.", "speaker": "SPEAKER_00"},
    ]
    merged = merge_segments(short, min_duration=1.0)
    assert len(merged) == 1
    assert "Hello world." in merged[0]["text"]


def test_merge_splits_on_speaker_change():
    from pipeline.modules.subtitle import merge_segments
    segs = [
        {"start": 0.0, "end": 0.3, "text": "Hello", "speaker": "SPEAKER_00"},
        {"start": 0.4, "end": 0.8, "text": "world.", "speaker": "SPEAKER_01"},
    ]
    merged = merge_segments(segs, min_duration=1.0)
    assert len(merged) == 2


def test_merge_splits_on_max_chars():
    from pipeline.modules.subtitle import merge_segments
    long_text = "A" * 40
    segs = [
        {"start": 0.0, "end": 1.0, "text": long_text, "speaker": "SPEAKER_00"},
        {"start": 1.1, "end": 2.0, "text": "more text", "speaker": "SPEAKER_00"},
    ]
    merged = merge_segments(segs, min_duration=0.5, max_chars=42)
    assert len(merged) == 2


def test_save_srt_creates_file(tmp_path):
    from pipeline.modules.subtitle import save_srt
    out = tmp_path / "test.srt"
    save_srt("1\n00:00:00,000 --> 00:00:01,000\nHello\n", out)
    assert out.exists()
    assert "Hello" in out.read_text()
