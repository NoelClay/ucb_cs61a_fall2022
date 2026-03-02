# Korean CS61A Localization Pipeline — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 49개 Fall 2022 CS61A 영상을 WhisperX + Claude API + Spleeter + Google Cloud TTS로 처리하여 한국어 자막/더빙 완성 MP4를 자동 생성하는 파이프라인을 구축한다.

**Architecture:** USB 루트 기반 자급자족 환경 (`pipeline/venv/`, `models/`)에서 6개 독립 모듈이 순서대로 실행되며, Control Tower(`control_tower.py`)가 상태 머신으로 진행 상황을 추적하고 재개 가능하게 관리한다.

**Tech Stack:** Python 3.11, WhisperX, Spleeter, Google Cloud TTS, Anthropic Claude API, ffmpeg, rubberband, yt-dlp

---

## 환경 변수 & 경로 규칙

```bash
# 모든 스크립트는 이 변수를 기준으로 경로를 구성한다
USB_ROOT=/media/namykim/391B-C6F7/workspace/c61a
PIPELINE_DIR=$USB_ROOT/pipeline
DATA_DIR=$USB_ROOT/data
MODELS_DIR=$USB_ROOT/models
GOOGLE_APPLICATION_CREDENTIALS=$PIPELINE_DIR/gcp_key.json
ANTHROPIC_API_KEY=<your-key>
HF_TOKEN=<your-huggingface-token>  # pyannote diarization 접근용
WHISPER_MODEL_DIR=$MODELS_DIR/whisperx
SPLEETER_MODEL_DIR=$MODELS_DIR/spleeter
```

---

## Task 1: 프로젝트 디렉토리 구조 생성

**Files:**
- Create: `pipeline/config.yaml`
- Create: `pipeline/requirements.txt`
- Create: `pipeline/utils/__init__.py`
- Create: `pipeline/modules/__init__.py`
- Create: `.env.example`

**Step 1: 디렉토리 구조 생성**

```bash
cd $USB_ROOT
mkdir -p pipeline/{modules,utils,tests}
mkdir -p models/{whisperx,spleeter}
mkdir -p data/{00_raw,01_transcripts,02_subtitles,03_audio,04_dubbed_chunks,05_output}
mkdir -p logs
touch pipeline/modules/__init__.py
touch pipeline/utils/__init__.py
touch pipeline/tests/__init__.py
```

Expected: 에러 없이 완료

**Step 2: requirements.txt 작성**

```
# pipeline/requirements.txt
whisperx==3.1.1
spleeter==2.4.0
google-cloud-texttospeech==2.16.3
anthropic==0.28.0
yt-dlp==2024.4.9
ffmpeg-python==0.2.0
pyrubberband==0.3.0
soundfile==0.12.1
librosa==0.10.2
python-dotenv==1.0.1
tqdm==4.66.4
pydantic==2.7.1
pytest==8.2.0
pytest-mock==3.14.0
```

**Step 3: config.yaml 작성**

```yaml
# pipeline/config.yaml
paths:
  usb_root: "${USB_ROOT}"
  data: "${USB_ROOT}/data"
  models: "${USB_ROOT}/models"
  logs: "${USB_ROOT}/logs"

whisperx:
  model: "large-v2"
  language: "en"
  min_speakers: 1
  max_speakers: 5
  diarize: true

subtitle:
  max_chars_per_line: 42
  min_duration_sec: 1.0
  max_duration_sec: 5.0
  batch_size: 30  # Claude API 배치 크기

tts:
  timing_tolerance: 0.25   # ±25% 타임스탬프 허용 범위
  default_voice: "ko-KR-Neural2-C"
  speakers:
    SPEAKER_00:
      voice: "ko-KR-Neural2-C"
      speaking_rate: 0.95
      pitch: -1.0
    SPEAKER_01:
      voice: "ko-KR-Neural2-B"
      speaking_rate: 1.0
      pitch: 0.0
    SPEAKER_UNKNOWN:
      voice: "ko-KR-Neural2-A"
      speaking_rate: 1.05
      pitch: 1.0

audio:
  vocals_lufs: -18
  bgm_lufs: -25
  mix_ratio:
    dubbed_segment: {bgm: -20, voice: 0}   # dB
    silent_segment: {bgm: 0}

cost:
  tts_per_million_chars: 16.0   # USD, Neural2
  claude_per_million_tokens: 3.0
```

**Step 4: .env.example 작성**

```bash
# .env.example (복사해서 .env로 사용, git에 .env는 커밋하지 말 것)
USB_ROOT=/media/namykim/391B-C6F7/workspace/c61a
GOOGLE_APPLICATION_CREDENTIALS=${USB_ROOT}/pipeline/gcp_key.json
ANTHROPIC_API_KEY=sk-ant-...
HF_TOKEN=hf_...
WHISPER_MODEL_DIR=${USB_ROOT}/models/whisperx
SPLEETER_MODEL_DIR=${USB_ROOT}/models/spleeter
```

**Step 5: .gitignore에 .env 추가**

```bash
echo ".env" >> $USB_ROOT/.gitignore
echo "pipeline/gcp_key.json" >> $USB_ROOT/.gitignore
echo "data/" >> $USB_ROOT/.gitignore
echo "models/" >> $USB_ROOT/.gitignore
echo "logs/" >> $USB_ROOT/.gitignore
```

**Step 6: Commit**

```bash
git add pipeline/ .env.example .gitignore
git commit -m "feat: initialize pipeline project structure and config"
```

---

## Task 2: Python 가상환경 설치 (USB 내)

**Step 1: USB 내에 venv 생성**

```bash
cd $USB_ROOT/pipeline
python3.11 -m venv venv
source venv/bin/activate
which python  # $USB_ROOT/pipeline/venv/bin/python 이어야 함
```

**Step 2: pip 업그레이드 + 의존성 설치**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected: 모든 패키지 성공 설치. 에러가 있다면 버전 충돌 확인.

**Step 3: ffmpeg 설치 확인**

```bash
ffmpeg -version
# ffmpeg version 6.x 이상이면 OK
# 없으면: sudo apt install ffmpeg (또는 conda install ffmpeg)
```

**Step 4: 설치 검증 스크립트 실행**

```python
# pipeline/tests/test_environment.py
import pytest

def test_whisperx_importable():
    import whisperx
    assert whisperx.__version__

def test_spleeter_importable():
    from spleeter.separator import Separator
    assert Separator

def test_google_tts_importable():
    from google.cloud import texttospeech
    assert texttospeech

def test_anthropic_importable():
    import anthropic
    assert anthropic.__version__

def test_ffmpeg_python_importable():
    import ffmpeg
    assert ffmpeg

def test_yt_dlp_importable():
    import yt_dlp
    assert yt_dlp
```

```bash
pytest pipeline/tests/test_environment.py -v
```

Expected: 6 passed

**Step 5: Commit**

```bash
git add pipeline/tests/test_environment.py
git commit -m "test: add environment sanity checks"
```

---

## Task 3: 유틸리티 — logger.py

**Files:**
- Create: `pipeline/utils/logger.py`
- Test: `pipeline/tests/test_logger.py`

**Step 1: 실패하는 테스트 작성**

```python
# pipeline/tests/test_logger.py
import pytest
import os
from pathlib import Path

def test_logger_creates_log_file(tmp_path):
    from pipeline.utils.logger import get_logger
    logger = get_logger("test", log_dir=tmp_path)
    logger.info("test message")
    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) == 1

def test_logger_writes_to_stdout_and_file(tmp_path, capsys):
    from pipeline.utils.logger import get_logger
    logger = get_logger("test2", log_dir=tmp_path)
    logger.info("hello world")
    captured = capsys.readouterr()
    assert "hello world" in captured.out
```

```bash
pytest pipeline/tests/test_logger.py -v
```

Expected: FAIL (ImportError)

**Step 2: logger.py 구현**

```python
# pipeline/utils/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime

def get_logger(name: str, log_dir: Path = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # stdout handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # file handler
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{name}_{datetime.now():%Y%m%d}.log"
        fh = logging.FileHandler(log_file)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
```

**Step 3: 테스트 재실행**

```bash
pytest pipeline/tests/test_logger.py -v
```

Expected: 2 passed

**Step 4: Commit**

```bash
git add pipeline/utils/logger.py pipeline/tests/test_logger.py
git commit -m "feat: add logger utility"
```

---

## Task 4: 유틸리티 — state_manager.py (진행 상태 추적)

**Files:**
- Create: `pipeline/utils/state_manager.py`
- Test: `pipeline/tests/test_state_manager.py`

**Step 1: 실패하는 테스트 작성**

```python
# pipeline/tests/test_state_manager.py
import pytest
from pathlib import Path

STATES = ["NOT_STARTED", "DOWNLOADED", "TRANSCRIBED", "SUBTITLED",
          "AUDIO_EDITED", "DUBBED", "SYNTHESIZED", "DONE"]

def test_initial_state_is_not_started(tmp_path):
    from pipeline.utils.state_manager import StateManager
    sm = StateManager(tmp_path / "progress.json")
    assert sm.get_state("lecture_01") == "NOT_STARTED"

def test_save_and_load_state(tmp_path):
    from pipeline.utils.state_manager import StateManager
    sm = StateManager(tmp_path / "progress.json")
    sm.set_state("lecture_01", "DOWNLOADED")
    sm2 = StateManager(tmp_path / "progress.json")
    assert sm2.get_state("lecture_01") == "DOWNLOADED"

def test_state_index_ordering(tmp_path):
    from pipeline.utils.state_manager import StateManager, state_index
    assert state_index("NOT_STARTED") < state_index("DOWNLOADED")
    assert state_index("DOWNLOADED") < state_index("DONE")

def test_is_before(tmp_path):
    from pipeline.utils.state_manager import StateManager
    sm = StateManager(tmp_path / "progress.json")
    sm.set_state("lecture_01", "TRANSCRIBED")
    assert sm.is_before("lecture_01", "SUBTITLED")
    assert not sm.is_before("lecture_01", "DOWNLOADED")

def test_list_by_state(tmp_path):
    from pipeline.utils.state_manager import StateManager
    sm = StateManager(tmp_path / "progress.json")
    sm.set_state("lecture_01", "DONE")
    sm.set_state("lecture_02", "DOWNLOADED")
    done = sm.list_by_state("DONE")
    assert "lecture_01" in done
    assert "lecture_02" not in done
```

```bash
pytest pipeline/tests/test_state_manager.py -v
```

Expected: 5 FAIL

**Step 2: state_manager.py 구현**

```python
# pipeline/utils/state_manager.py
import json
from pathlib import Path
from typing import List

STATES = [
    "NOT_STARTED", "DOWNLOADED", "TRANSCRIBED", "SUBTITLED",
    "AUDIO_EDITED", "DUBBED", "SYNTHESIZED", "DONE"
]

def state_index(state: str) -> int:
    return STATES.index(state)

class StateManager:
    def __init__(self, progress_file: Path):
        self.path = Path(progress_file)
        self._data: dict = {}
        if self.path.exists():
            self._data = json.loads(self.path.read_text())

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, indent=2))

    def get_state(self, video_id: str) -> str:
        return self._data.get(video_id, "NOT_STARTED")

    def set_state(self, video_id: str, state: str):
        assert state in STATES, f"Invalid state: {state}"
        self._data[video_id] = state
        self._save()

    def is_before(self, video_id: str, target_state: str) -> bool:
        return state_index(self.get_state(video_id)) < state_index(target_state)

    def list_by_state(self, state: str) -> List[str]:
        return [vid for vid, s in self._data.items() if s == state]
```

**Step 3: 테스트 재실행**

```bash
pytest pipeline/tests/test_state_manager.py -v
```

Expected: 5 passed

**Step 4: Commit**

```bash
git add pipeline/utils/state_manager.py pipeline/tests/test_state_manager.py
git commit -m "feat: add state manager for resumable pipeline"
```

---

## Task 5: Module 01 — download.py

**Files:**
- Create: `pipeline/modules/01_download.py`
- Create: `data/video_list.csv`
- Test: `pipeline/tests/test_download.py`

**Step 1: video_list.csv 작성**

```csv
# data/video_list.csv
video_id,title,type,bilibili_url
lecture_01,Lecture 1 - Functions,lecture,https://www.bilibili.com/video/BV1GK411Q7qp
disc_01,Discussion 1,discussion,https://...
...
```

> 나머지 48개 URL은 Bilibili 채널에서 수동 또는 자동으로 수집

**Step 2: 실패하는 테스트 작성**

```python
# pipeline/tests/test_download.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

def test_download_skips_existing_file(tmp_path):
    from pipeline.modules.download import download_video
    output = tmp_path / "lecture_01.mp4"
    output.write_bytes(b"fake video")
    result = download_video("fake_url", output)
    assert result == output  # 다운로드 없이 기존 파일 반환

def test_download_calls_yt_dlp(tmp_path):
    from pipeline.modules.download import download_video
    output = tmp_path / "lecture_01.mp4"
    with patch("pipeline.modules.download.YoutubeDL") as mock_ydl:
        mock_ctx = MagicMock()
        mock_ydl.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        mock_ydl.return_value.__exit__ = MagicMock(return_value=False)
        mock_ctx.extract_info.return_value = {"duration": 3600}
        download_video("https://bilibili.com/video/test", output)
    mock_ydl.assert_called_once()

def test_build_output_path():
    from pipeline.modules.download import build_output_path
    path = build_output_path("lecture_01", "/data/00_raw")
    assert str(path).endswith("lecture_01.mp4")
```

```bash
pytest pipeline/tests/test_download.py -v
```

Expected: 3 FAIL

**Step 3: download.py 구현**

```python
# pipeline/modules/download.py
import os
from pathlib import Path
from yt_dlp import YoutubeDL
from pipeline.utils.logger import get_logger

logger = get_logger("download")

def build_output_path(video_id: str, raw_dir: str) -> Path:
    return Path(raw_dir) / f"{video_id}.mp4"

def download_video(url: str, output_path: Path) -> Path:
    output_path = Path(output_path)
    if output_path.exists():
        logger.info(f"[SKIP] Already downloaded: {output_path.name}")
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": str(output_path),
        "quiet": False,
        "no_warnings": False,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    logger.info(f"[DONE] Downloaded: {output_path.name}")
    return output_path

def download_all(video_list_csv: str, raw_dir: str):
    import csv
    with open(video_list_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("video_id", "").startswith("#"):
                continue
            output = build_output_path(row["video_id"], raw_dir)
            try:
                download_video(row["bilibili_url"], output)
            except Exception as e:
                logger.error(f"[FAIL] {row['video_id']}: {e}")
```

**Step 4: 테스트 재실행**

```bash
pytest pipeline/tests/test_download.py -v
```

Expected: 3 passed

**Step 5: Commit**

```bash
git add pipeline/modules/download.py pipeline/tests/test_download.py data/video_list.csv
git commit -m "feat: add download module with idempotent yt-dlp wrapper"
```

---

## Task 6: Module 02 — transcribe.py

**Files:**
- Create: `pipeline/modules/transcribe.py`
- Test: `pipeline/tests/test_transcribe.py`

**Step 1: 실패하는 테스트 작성**

```python
# pipeline/tests/test_transcribe.py
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

SAMPLE_WHISPERX_OUTPUT = {
    "segments": [
        {
            "start": 0.0, "end": 3.2,
            "text": "Welcome to CS61A.",
            "speaker": "SPEAKER_00",
            "words": [{"word": "Welcome", "start": 0.0, "end": 0.5}]
        },
        {
            "start": 3.5, "end": 6.0,
            "text": "Today we talk about functions.",
            "speaker": "SPEAKER_00",
            "words": []
        }
    ]
}

def test_transcript_json_structure(tmp_path):
    from pipeline.modules.transcribe import normalize_transcript
    result = normalize_transcript(SAMPLE_WHISPERX_OUTPUT)
    assert "segments" in result
    for seg in result["segments"]:
        assert "start" in seg
        assert "end" in seg
        assert "text" in seg
        assert "speaker" in seg

def test_unknown_speaker_tagged(tmp_path):
    from pipeline.modules.transcribe import normalize_transcript
    data = {"segments": [{"start": 0.0, "end": 1.0, "text": "hello"}]}
    result = normalize_transcript(data)
    assert result["segments"][0]["speaker"] == "SPEAKER_UNKNOWN"

def test_output_saved_as_json(tmp_path):
    from pipeline.modules.transcribe import save_transcript
    transcript = {"segments": []}
    output_path = tmp_path / "lecture_01.json"
    save_transcript(transcript, output_path)
    loaded = json.loads(output_path.read_text())
    assert "segments" in loaded
```

```bash
pytest pipeline/tests/test_transcribe.py -v
```

Expected: 3 FAIL

**Step 2: transcribe.py 구현**

```python
# pipeline/modules/transcribe.py
import json
import subprocess
from pathlib import Path
from typing import Optional
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
    output_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2))
    logger.info(f"[SAVED] {output_path.name}")

def transcribe_video(
    video_path: Path,
    output_path: Path,
    model_dir: str,
    hf_token: str,
    model: str = "large-v2",
) -> dict:
    video_path = Path(video_path)
    output_path = Path(output_path)

    if output_path.exists():
        logger.info(f"[SKIP] Transcript exists: {output_path.name}")
        return json.loads(output_path.read_text())

    import whisperx

    logger.info(f"[START] Transcribing {video_path.name}")
    device = "cuda" if _cuda_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    model_obj = whisperx.load_model(
        model, device, compute_type=compute_type,
        download_root=model_dir
    )
    audio = whisperx.load_audio(str(video_path))
    result = model_obj.transcribe(audio, language="en")

    # 단어 정렬
    align_model, metadata = whisperx.load_align_model(
        language_code="en", device=device
    )
    result = whisperx.align(
        result["segments"], align_model, metadata, audio, device
    )

    # 화자 분리
    diarize_model = whisperx.DiarizationPipeline(
        use_auth_token=hf_token, device=device
    )
    diarize_segments = diarize_model(
        audio, min_speakers=1, max_speakers=5
    )
    result = whisperx.assign_word_speakers(diarize_segments, result)

    normalized = normalize_transcript(result)
    save_transcript(normalized, output_path)
    logger.info(f"[DONE] Transcribed {len(normalized['segments'])} segments")
    return normalized

def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False
```

**Step 3: 테스트 재실행**

```bash
pytest pipeline/tests/test_transcribe.py -v
```

Expected: 3 passed

**Step 4: Commit**

```bash
git add pipeline/modules/transcribe.py pipeline/tests/test_transcribe.py
git commit -m "feat: add WhisperX transcription module with speaker diarization"
```

---

## Task 7: Module 03 — subtitle.py

**Files:**
- Create: `pipeline/modules/subtitle.py`
- Create: `pipeline/utils/cs_terms.yaml`
- Test: `pipeline/tests/test_subtitle.py`

**Step 1: CS 용어 사전 작성**

```yaml
# pipeline/utils/cs_terms.yaml
# 왼쪽: 영어, 오른쪽: 한국어 번역 (Claude 프롬프트에 주입됨)
function: 함수
recursion: 재귀
closure: 클로저
environment: 환경
frame: 프레임
binding: 바인딩
higher-order function: 고차 함수
tail call: 꼬리 호출
data abstraction: 데이터 추상화
object-oriented: 객체지향
inheritance: 상속
polymorphism: 다형성
interpreter: 인터프리터
linked list: 연결 리스트
tree: 트리
mutation: 변이
iteration: 반복
generator: 제너레이터
decorator: 데코레이터
lambda: 람다
scope: 스코프
memoization: 메모이제이션
```

**Step 2: 실패하는 테스트 작성**

```python
# pipeline/tests/test_subtitle.py
import pytest

SAMPLE_SEGMENTS = [
    {"start": 0.0, "end": 3.2, "text": "Welcome to CS61A.", "speaker": "SPEAKER_00"},
    {"start": 3.5, "end": 6.0, "text": "Today we talk about functions.", "speaker": "SPEAKER_00"},
    {"start": 6.5, "end": 9.0, "text": "What is a function?", "speaker": "SPEAKER_01"},
]

def test_segments_to_srt():
    from pipeline.modules.subtitle import segments_to_srt
    srt = segments_to_srt(SAMPLE_SEGMENTS)
    assert "1\n" in srt
    assert "00:00:00,000 --> 00:00:03,200" in srt
    assert "Welcome to CS61A." in srt

def test_srt_has_speaker_tag():
    from pipeline.modules.subtitle import segments_to_srt
    srt = segments_to_srt(SAMPLE_SEGMENTS, include_speaker=True)
    assert "[SPEAKER_00]" in srt
    assert "[SPEAKER_01]" in srt

def test_format_timestamp():
    from pipeline.modules.subtitle import format_timestamp
    assert format_timestamp(3661.5) == "01:01:01,500"
    assert format_timestamp(0.0) == "00:00:00,000"

def test_merge_short_segments():
    from pipeline.modules.subtitle import merge_segments
    short = [
        {"start": 0.0, "end": 0.3, "text": "Hello", "speaker": "SPEAKER_00"},
        {"start": 0.4, "end": 0.8, "text": "world", "speaker": "SPEAKER_00"},
    ]
    merged = merge_segments(short, min_duration=1.0)
    assert len(merged) == 1
    assert "Hello world" in merged[0]["text"]

def test_speaker_change_forces_split():
    from pipeline.modules.subtitle import merge_segments
    segs = [
        {"start": 0.0, "end": 0.3, "text": "Hello", "speaker": "SPEAKER_00"},
        {"start": 0.4, "end": 0.8, "text": "world", "speaker": "SPEAKER_01"},
    ]
    merged = merge_segments(segs, min_duration=1.0)
    assert len(merged) == 2  # 화자가 다르면 병합 안 함
```

```bash
pytest pipeline/tests/test_subtitle.py -v
```

Expected: 5 FAIL

**Step 3: subtitle.py 구현**

```python
# pipeline/modules/subtitle.py
import re
from pathlib import Path
from typing import List, Dict
from pipeline.utils.logger import get_logger

logger = get_logger("subtitle")

def format_timestamp(seconds: float) -> str:
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def merge_segments(segments: List[Dict], min_duration: float = 1.0,
                   max_duration: float = 5.0, max_chars: int = 42) -> List[Dict]:
    if not segments:
        return []
    merged = []
    current = dict(segments[0])
    for seg in segments[1:]:
        same_speaker = seg["speaker"] == current["speaker"]
        merged_text = current["text"] + " " + seg["text"]
        merged_dur = seg["end"] - current["start"]
        can_merge = (
            same_speaker
            and merged_dur <= max_duration
            and len(merged_text) <= max_chars
        )
        if can_merge:
            current["end"] = seg["end"]
            current["text"] = merged_text
        else:
            merged.append(current)
            current = dict(seg)
    merged.append(current)
    return merged

def segments_to_srt(segments: List[Dict], include_speaker: bool = False) -> str:
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        if include_speaker:
            text = f"[{seg['speaker']}]\n{text}"
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)

def translate_subtitles_with_claude(
    segments: List[Dict],
    api_key: str,
    cs_terms_path: str,
    batch_size: int = 30,
) -> List[Dict]:
    import anthropic
    import yaml

    with open(cs_terms_path) as f:
        terms = yaml.safe_load(f)
    terms_str = "\n".join(f"- {k} → {v}" for k, v in terms.items())

    client = anthropic.Anthropic(api_key=api_key)
    translated = []

    for i in range(0, len(segments), batch_size):
        batch = segments[i:i+batch_size]
        numbered = "\n".join(
            f"{j+1}. [{seg['speaker']}] {seg['text']}"
            for j, seg in enumerate(batch)
        )
        prompt = f"""다음 CS61A 강의 자막을 한국어로 번역하세요.

규칙:
1. 기술 용어는 아래 사전을 우선 참고하세요:
{terms_str}

2. 코드, 변수명, 함수명은 번역하지 말고 백틱으로 감싸세요 (예: `x = 5`)
3. 자연스러운 한국어 설명체로 번역하세요 (존댓말, 딱딱하지 않게)
4. 번호와 화자 태그는 그대로 유지하세요

자막:
{numbered}

번역 결과를 같은 번호 형식으로 출력하세요."""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        result_text = response.content[0].text
        translations = _parse_numbered_translations(result_text, len(batch))

        for j, seg in enumerate(batch):
            new_seg = dict(seg)
            new_seg["text"] = translations[j] if j < len(translations) else seg["text"]
            translated.append(new_seg)

    return translated

def _parse_numbered_translations(text: str, expected: int) -> List[str]:
    lines = []
    for line in text.strip().split("\n"):
        match = re.match(r"^\d+\.\s*(?:\[.*?\])?\s*(.+)$", line.strip())
        if match:
            lines.append(match.group(1).strip())
    while len(lines) < expected:
        lines.append("")
    return lines

def save_srt(srt_content: str, output_path: Path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(srt_content, encoding="utf-8")
    logger.info(f"[SAVED] {output_path.name}")
```

**Step 4: 테스트 재실행**

```bash
pytest pipeline/tests/test_subtitle.py -v
```

Expected: 5 passed

**Step 5: Commit**

```bash
git add pipeline/modules/subtitle.py pipeline/utils/cs_terms.yaml pipeline/tests/test_subtitle.py
git commit -m "feat: add subtitle generation module with Claude translation"
```

---

## Task 8: Module 04 — audio_edit.py

**Files:**
- Create: `pipeline/modules/audio_edit.py`
- Test: `pipeline/tests/test_audio_edit.py`

**Step 1: 실패하는 테스트 작성**

```python
# pipeline/tests/test_audio_edit.py
import pytest
import numpy as np
import soundfile as sf
from pathlib import Path

def _make_wav(path, duration=1.0, sr=44100):
    data = np.zeros(int(sr * duration), dtype=np.float32)
    sf.write(path, data, sr)
    return path

def test_extract_audio_creates_wav(tmp_path):
    from pipeline.modules.audio_edit import extract_audio
    # mp4가 없으면 ffmpeg 호출을 mock
    from unittest.mock import patch
    output = tmp_path / "audio.wav"
    with patch("pipeline.modules.audio_edit.ffmpeg") as mock_ff:
        mock_ff.input.return_value.output.return_value.run.return_value = None
        extract_audio(tmp_path / "video.mp4", output)
    mock_ff.input.assert_called_once()

def test_normalize_lufs(tmp_path):
    from pipeline.modules.audio_edit import normalize_lufs
    wav = _make_wav(tmp_path / "input.wav")
    output = tmp_path / "output.wav"
    normalize_lufs(wav, output, target_lufs=-18.0)
    assert output.exists()

def test_spleeter_output_paths(tmp_path):
    from pipeline.modules.audio_edit import get_spleeter_output_paths
    vocals, bgm = get_spleeter_output_paths("lecture_01", tmp_path)
    assert "vocals" in str(vocals)
    assert "bgm" in str(bgm)
```

```bash
pytest pipeline/tests/test_audio_edit.py -v
```

Expected: 3 FAIL

**Step 2: audio_edit.py 구현**

```python
# pipeline/modules/audio_edit.py
import subprocess
from pathlib import Path
from typing import Tuple
import ffmpeg
import soundfile as sf
import numpy as np
from pipeline.utils.logger import get_logger

logger = get_logger("audio_edit")

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
    data, sr = sf.read(str(input_path))
    rms = np.sqrt(np.mean(data**2))
    if rms < 1e-8:
        sf.write(str(output_path), data, sr)
        return
    # 근사 LUFS 정규화 (정밀한 LUFS는 loudnorm ffmpeg 필터 활용)
    (
        ffmpeg
        .input(str(input_path))
        .filter("loudnorm", I=target_lufs, LRA=11, TP=-1.5)
        .output(str(output_path))
        .run(overwrite_output=True, quiet=True)
    )
    logger.info(f"[NORM] Normalized to {target_lufs} LUFS: {output_path.name}")

def get_spleeter_output_paths(video_id: str, audio_dir: Path) -> Tuple[Path, Path]:
    audio_dir = Path(audio_dir)
    vocals = audio_dir / f"{video_id}_vocals.wav"
    bgm = audio_dir / f"{video_id}_bgm.wav"
    return vocals, bgm

def separate_audio(audio_path: Path, video_id: str, audio_dir: Path, model_dir: str):
    vocals_path, bgm_path = get_spleeter_output_paths(video_id, audio_dir)
    if vocals_path.exists() and bgm_path.exists():
        logger.info(f"[SKIP] Spleeter output exists for {video_id}")
        return vocals_path, bgm_path

    from spleeter.separator import Separator
    import os
    os.environ["MODEL_PATH"] = model_dir

    sep = Separator("spleeter:2stems")
    prediction = sep.separate(str(audio_path))

    audio_dir.mkdir(parents=True, exist_ok=True)
    import soundfile as sf
    sf.write(str(vocals_path), prediction["vocals"], 44100)
    sf.write(str(bgm_path), prediction["accompaniment"], 44100)

    normalize_lufs(vocals_path, vocals_path, target_lufs=-18.0)
    normalize_lufs(bgm_path, bgm_path, target_lufs=-25.0)

    logger.info(f"[DONE] Spleeter separation complete: {video_id}")
    return vocals_path, bgm_path
```

**Step 3: 테스트 재실행**

```bash
pytest pipeline/tests/test_audio_edit.py -v
```

Expected: 3 passed

**Step 4: Commit**

```bash
git add pipeline/modules/audio_edit.py pipeline/tests/test_audio_edit.py
git commit -m "feat: add Spleeter audio separation module"
```

---

## Task 9: Module 05 — tts_dub.py

**Files:**
- Create: `pipeline/modules/tts_dub.py`
- Test: `pipeline/tests/test_tts_dub.py`

**Step 1: 실패하는 테스트 작성**

```python
# pipeline/tests/test_tts_dub.py
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

SAMPLE_KO_SEGMENTS = [
    {"start": 0.0, "end": 3.2, "text": "CS61A에 오신 것을 환영합니다.", "speaker": "SPEAKER_00"},
    {"start": 3.5, "end": 6.0, "text": "오늘은 함수에 대해 이야기합니다.", "speaker": "SPEAKER_00"},
]

def test_chunk_filename_format():
    from pipeline.modules.tts_dub import chunk_filename
    name = chunk_filename(1, "SPEAKER_00")
    assert name == "chunk_0001_SPEAKER_00.wav"

def test_needs_speed_adjustment_within_tolerance():
    from pipeline.modules.tts_dub import needs_speed_adjustment
    assert not needs_speed_adjustment(original=3.2, generated=3.5, tolerance=0.25)
    assert needs_speed_adjustment(original=3.2, generated=5.0, tolerance=0.25)

def test_calculate_speed_ratio():
    from pipeline.modules.tts_dub import calculate_speed_ratio
    ratio = calculate_speed_ratio(original=4.0, generated=5.0)
    assert abs(ratio - 1.25) < 0.01  # 25% 빠르게 해야 함

def test_tts_called_with_correct_voice(tmp_path):
    from pipeline.modules.tts_dub import synthesize_chunk
    with patch("pipeline.modules.tts_dub.texttospeech") as mock_tts:
        mock_client = MagicMock()
        mock_tts.TextToSpeechClient.return_value = mock_client
        mock_response = MagicMock()
        mock_response.audio_content = b"fake_audio"
        mock_client.synthesize_speech.return_value = mock_response

        out = tmp_path / "chunk_0001.wav"
        synthesize_chunk(
            text="안녕하세요",
            output_path=out,
            voice_name="ko-KR-Neural2-C",
            speaking_rate=0.95,
            pitch=-1.0
        )
    mock_client.synthesize_speech.assert_called_once()
    assert out.exists()
```

```bash
pytest pipeline/tests/test_tts_dub.py -v
```

Expected: 4 FAIL

**Step 2: tts_dub.py 구현**

```python
# pipeline/modules/tts_dub.py
import os
import struct
from pathlib import Path
from typing import List, Dict, Tuple
from pipeline.utils.logger import get_logger

logger = get_logger("tts_dub")

def chunk_filename(seq: int, speaker: str) -> str:
    return f"chunk_{seq:04d}_{speaker}.wav"

def needs_speed_adjustment(original: float, generated: float,
                            tolerance: float = 0.25) -> bool:
    if original <= 0:
        return False
    ratio = generated / original
    return abs(ratio - 1.0) > tolerance

def calculate_speed_ratio(original: float, generated: float) -> float:
    return generated / original

def synthesize_chunk(text: str, output_path: Path, voice_name: str,
                     speaking_rate: float = 1.0, pitch: float = 0.0):
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name=voice_name,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=speaking_rate,
        pitch=pitch,
        sample_rate_hertz=24000,
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.audio_content)

def adjust_speed(input_path: Path, output_path: Path, ratio: float):
    """pyrubberband으로 피치 보존 속도 조정."""
    import soundfile as sf
    import pyrubberband as rb

    data, sr = sf.read(str(input_path))
    stretched = rb.time_stretch(data, sr, 1.0 / ratio)
    sf.write(str(output_path), stretched, sr)

def dub_segments(
    ko_segments: List[Dict],
    output_dir: Path,
    speaker_config: dict,
    tolerance: float = 0.25,
):
    output_dir = Path(output_dir)
    results = []
    for i, seg in enumerate(ko_segments):
        speaker = seg["speaker"]
        cfg = speaker_config.get(speaker, speaker_config.get("SPEAKER_UNKNOWN"))
        fname = chunk_filename(i + 1, speaker)
        chunk_path = output_dir / fname
        if chunk_path.exists():
            logger.info(f"[SKIP] Chunk exists: {fname}")
            results.append({"path": chunk_path, "start": seg["start"], "end": seg["end"]})
            continue
        synthesize_chunk(
            text=seg["text"],
            output_path=chunk_path,
            voice_name=cfg["voice"],
            speaking_rate=cfg.get("speaking_rate", 1.0),
            pitch=cfg.get("pitch", 0.0),
        )
        # 길이 검사 및 속도 조정
        import soundfile as sf
        data, sr = sf.read(str(chunk_path))
        generated_dur = len(data) / sr
        original_dur = seg["end"] - seg["start"]
        if needs_speed_adjustment(original_dur, generated_dur, tolerance):
            ratio = calculate_speed_ratio(original_dur, generated_dur)
            logger.info(f"[ADJUST] {fname}: speed ratio {ratio:.2f}")
            adjust_speed(chunk_path, chunk_path, ratio)

        results.append({"path": chunk_path, "start": seg["start"], "end": seg["end"]})
    return results
```

**Step 3: 테스트 재실행**

```bash
pytest pipeline/tests/test_tts_dub.py -v
```

Expected: 4 passed

**Step 4: Commit**

```bash
git add pipeline/modules/tts_dub.py pipeline/tests/test_tts_dub.py
git commit -m "feat: add Google Cloud TTS dubbing module with speed adjustment"
```

---

## Task 10: Module 06 — synthesize.py

**Files:**
- Create: `pipeline/modules/synthesize.py`
- Test: `pipeline/tests/test_synthesize.py`

**Step 1: 실패하는 테스트 작성**

```python
# pipeline/tests/test_synthesize.py
import pytest
import numpy as np
import soundfile as sf
from pathlib import Path

def _make_wav(path, duration=1.0, sr=44100, value=0.1):
    data = np.full(int(sr * duration), value, dtype=np.float32)
    sf.write(str(path), data, sr)
    return path

def test_place_chunks_on_timeline(tmp_path):
    from pipeline.modules.synthesize import place_chunks_on_timeline
    total_dur = 5.0
    chunks = [
        {"path": _make_wav(tmp_path / "c1.wav", 1.0), "start": 0.0, "end": 1.0},
        {"path": _make_wav(tmp_path / "c2.wav", 1.0), "start": 2.0, "end": 3.0},
    ]
    timeline = place_chunks_on_timeline(chunks, total_dur, sr=44100)
    assert len(timeline) == int(5.0 * 44100)

def test_mix_voice_and_bgm(tmp_path):
    from pipeline.modules.synthesize import mix_audio
    sr = 44100
    dur = 2.0
    voice = np.zeros(int(sr * dur), dtype=np.float32)
    bgm = np.full(int(sr * dur), 0.5, dtype=np.float32)
    has_voice = [True] * int(sr * 1.0) + [False] * int(sr * 1.0)
    mixed = mix_audio(voice, bgm, has_voice)
    assert mixed.shape == voice.shape
```

```bash
pytest pipeline/tests/test_synthesize.py -v
```

Expected: 2 FAIL

**Step 2: synthesize.py 구현**

```python
# pipeline/modules/synthesize.py
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Dict
import ffmpeg
from pipeline.utils.logger import get_logger

logger = get_logger("synthesize")

def place_chunks_on_timeline(
    chunks: List[Dict], total_duration: float, sr: int = 44100
) -> np.ndarray:
    timeline = np.zeros(int(total_duration * sr), dtype=np.float32)
    for chunk in chunks:
        data, chunk_sr = sf.read(str(chunk["path"]))
        if data.ndim > 1:
            data = data.mean(axis=1)
        if chunk_sr != sr:
            import librosa
            data = librosa.resample(data, orig_sr=chunk_sr, target_sr=sr)
        start_idx = int(chunk["start"] * sr)
        end_idx = min(start_idx + len(data), len(timeline))
        copy_len = end_idx - start_idx
        timeline[start_idx:end_idx] += data[:copy_len]
    return timeline

def mix_audio(
    voice: np.ndarray, bgm: np.ndarray, has_voice: List[bool]
) -> np.ndarray:
    mixed = np.zeros_like(voice)
    for i in range(len(mixed)):
        if i < len(has_voice) and has_voice[i]:
            mixed[i] = voice[i] + bgm[i] * 10 ** (-20 / 20)  # bgm -20dB
        else:
            mixed[i] = bgm[i] if i < len(bgm) else 0.0
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
):
    original_video = Path(original_video)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        logger.info(f"[SKIP] Output exists: {output_path.name}")
        return output_path

    total_dur = get_video_duration(original_video)
    logger.info(f"[SYNTH] Building timeline for {total_dur:.1f}s video")

    # 더빙 타임라인 생성
    voice_timeline = place_chunks_on_timeline(dubbed_chunks, total_dur, sr)

    # BGM 로드
    bgm_data, bgm_sr = sf.read(str(bgm_path))
    if bgm_data.ndim > 1:
        bgm_data = bgm_data.mean(axis=1)
    if bgm_sr != sr:
        import librosa
        bgm_data = librosa.resample(bgm_data, orig_sr=bgm_sr, target_sr=sr)
    bgm_data = bgm_data[:len(voice_timeline)]
    if len(bgm_data) < len(voice_timeline):
        bgm_data = np.pad(bgm_data, (0, len(voice_timeline) - len(bgm_data)))

    has_voice = [abs(v) > 1e-6 for v in voice_timeline]
    mixed = mix_audio(voice_timeline, bgm_data, has_voice)

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, mixed, sr)
        tmp_audio = tmp.name

    (
        ffmpeg
        .input(str(original_video))
        .input(tmp_audio)
        .output(str(output_path),
                vcodec="copy", acodec="aac", audio_bitrate="192k",
                map="0:v:0", **{"map": "1:a:0"})
        .run(overwrite_output=True, quiet=True)
    )

    import os
    os.unlink(tmp_audio)
    logger.info(f"[DONE] Final video: {output_path.name}")
    return output_path
```

**Step 3: 테스트 재실행**

```bash
pytest pipeline/tests/test_synthesize.py -v
```

Expected: 2 passed

**Step 4: Commit**

```bash
git add pipeline/modules/synthesize.py pipeline/tests/test_synthesize.py
git commit -m "feat: add audio synthesis module for final dubbing assembly"
```

---

## Task 11: Control Tower (control_tower.py)

**Files:**
- Create: `pipeline/control_tower.py`
- Test: `pipeline/tests/test_control_tower.py`

**Step 1: 실패하는 테스트 작성**

```python
# pipeline/tests/test_control_tower.py
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

def test_process_video_calls_all_stages(tmp_path):
    from pipeline.control_tower import ControlTower
    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)

    with patch.multiple(ct,
        run_download=MagicMock(),
        run_transcribe=MagicMock(),
        run_subtitle=MagicMock(),
        run_audio_edit=MagicMock(),
        run_tts_dub=MagicMock(),
        run_synthesize=MagicMock(),
    ):
        ct.process_video("lecture_01", "https://fake-url")
    ct.run_download.assert_called_once()
    ct.run_transcribe.assert_called_once()
    ct.run_subtitle.assert_called_once()

def test_process_video_resumes_from_state(tmp_path):
    from pipeline.control_tower import ControlTower
    from pipeline.utils.state_manager import StateManager
    sm = StateManager(tmp_path / "progress.json")
    sm.set_state("lecture_01", "TRANSCRIBED")
    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    ct.state_manager = sm

    with patch.multiple(ct,
        run_download=MagicMock(),
        run_transcribe=MagicMock(),
        run_subtitle=MagicMock(),
        run_audio_edit=MagicMock(),
        run_tts_dub=MagicMock(),
        run_synthesize=MagicMock(),
    ):
        ct.process_video("lecture_01", "https://fake-url")
    ct.run_download.assert_not_called()
    ct.run_transcribe.assert_not_called()
    ct.run_subtitle.assert_called_once()

def test_process_all_collects_failures(tmp_path):
    from pipeline.control_tower import ControlTower
    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    with patch.object(ct, "process_video", side_effect=Exception("fail")):
        ct.process_all([{"video_id": "lecture_01", "bilibili_url": "x"}])
    assert "lecture_01" in ct.failed_videos
```

```bash
pytest pipeline/tests/test_control_tower.py -v
```

Expected: 3 FAIL

**Step 2: control_tower.py 구현**

```python
# pipeline/control_tower.py
import os
import yaml
from pathlib import Path
from typing import List, Dict
from pipeline.utils.logger import get_logger
from pipeline.utils.state_manager import StateManager

logger = get_logger("control_tower")

class ControlTower:
    def __init__(self, config_path: str, data_dir: Path = None):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.data_dir = Path(data_dir or os.environ.get("USB_ROOT", ".") + "/data")
        self.state_manager = StateManager(self.data_dir / "progress.json")
        self.failed_videos: List[str] = []

    def run_download(self, video_id: str, url: str):
        from pipeline.modules.download import download_video, build_output_path
        raw_dir = self.data_dir / "00_raw"
        output = build_output_path(video_id, raw_dir)
        download_video(url, output)

    def run_transcribe(self, video_id: str):
        from pipeline.modules.transcribe import transcribe_video
        video_path = self.data_dir / "00_raw" / f"{video_id}.mp4"
        output_path = self.data_dir / "01_transcripts" / f"{video_id}.json"
        transcribe_video(
            video_path=video_path,
            output_path=output_path,
            model_dir=os.environ["WHISPER_MODEL_DIR"],
            hf_token=os.environ["HF_TOKEN"],
            model=self.config["whisperx"]["model"],
        )

    def run_subtitle(self, video_id: str):
        import json
        from pipeline.modules.subtitle import (
            merge_segments, segments_to_srt,
            translate_subtitles_with_claude, save_srt
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
            api_key=os.environ["ANTHROPIC_API_KEY"],
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
        separate_audio(wav_path, video_id, self.data_dir / "03_audio",
                       os.environ["SPLEETER_MODEL_DIR"])

    def run_tts_dub(self, video_id: str, ko_segments: list):
        from pipeline.modules.tts_dub import dub_segments
        import yaml
        with open("pipeline/utils/speaker_config.yaml") as f:
            speaker_cfg = yaml.safe_load(f)
        chunks_dir = self.data_dir / "04_dubbed_chunks" / video_id
        return dub_segments(
            ko_segments, chunks_dir, speaker_cfg,
            tolerance=self.config["tts"]["timing_tolerance"]
        )

    def run_synthesize(self, video_id: str, dubbed_chunks: list):
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
            import shutil
            shutil.rmtree(chunks_dir)
            logger.info(f"[CLEANUP] Removed chunks: {chunks_dir}")

    def process_video(self, video_id: str, url: str):
        sm = self.state_manager
        logger.info(f"[START] Processing {video_id}")

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
                import json
                from pipeline.modules.subtitle import merge_segments, translate_subtitles_with_claude
                # 이미 자막이 있을 경우 SRT에서 로드
                pass
            self.run_tts_dub(video_id, ko_segments or [])
            sm.set_state(video_id, "DUBBED")

        if sm.is_before(video_id, "SYNTHESIZED"):
            chunks_dir = self.data_dir / "04_dubbed_chunks" / video_id
            chunks = sorted([
                {"path": p, "start": 0.0, "end": 0.0}
                for p in chunks_dir.glob("*.wav")
            ], key=lambda x: x["path"].name)
            self.run_synthesize(video_id, chunks)
            sm.set_state(video_id, "DONE")

        logger.info(f"[COMPLETE] {video_id}")

    def process_all(self, video_list: List[Dict]):
        for item in video_list:
            try:
                self.process_video(item["video_id"], item["bilibili_url"])
            except Exception as e:
                logger.error(f"[FAIL] {item['video_id']}: {e}")
                self.failed_videos.append(item["video_id"])
```

**Step 3: 테스트 재실행**

```bash
pytest pipeline/tests/test_control_tower.py -v
```

Expected: 3 passed

**Step 4: 전체 테스트 실행**

```bash
pytest pipeline/tests/ -v --tb=short
```

Expected: 모든 테스트 통과

**Step 5: Commit**

```bash
git add pipeline/control_tower.py pipeline/tests/test_control_tower.py
git commit -m "feat: add Control Tower orchestrator with state machine and resume support"
```

---

## Task 12: 파일럿 테스트 — Lecture 01 전체 파이프라인

**사전 조건:**
- `.env` 파일 작성 완료
- `pipeline/gcp_key.json` 설치 완료
- `data/video_list.csv`에 Lecture 01 URL 입력 완료

**Step 1: 환경 변수 로드 확인**

```bash
source pipeline/venv/bin/activate
export $(cat .env | xargs)
echo $ANTHROPIC_API_KEY  # 값이 출력되어야 함
echo $USB_ROOT           # 경로가 출력되어야 함
```

**Step 2: WhisperX 모델 사전 다운로드**

```bash
python -c "
import whisperx, os
model = whisperx.load_model(
    'large-v2', 'cpu',
    compute_type='int8',
    download_root=os.environ['WHISPER_MODEL_DIR']
)
print('WhisperX model ready')
"
```

**Step 3: Google TTS 연결 테스트**

```python
# pipeline/tests/test_gcp_connection.py
def test_google_tts_connection():
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient()
    voices = client.list_voices(language_code="ko-KR")
    ko_voices = [v.name for v in voices.voices if "Neural2" in v.name]
    assert len(ko_voices) > 0, "Neural2 한국어 음성 없음"
    print(f"사용 가능한 음성: {ko_voices}")
```

```bash
pytest pipeline/tests/test_gcp_connection.py -v -s
```

**Step 4: Lecture 01 파이프라인 실행**

```bash
python -c "
import os, yaml
from pipeline.control_tower import ControlTower

ct = ControlTower(config_path='pipeline/config.yaml')
ct.process_video(
    video_id='lecture_01',
    url='https://www.bilibili.com/video/BV1GK411Q7qp'
)
print('파일럿 완료!')
"
```

**Step 5: 출력 품질 수동 검증 체크리스트**

```
[ ] data/01_transcripts/lecture_01.json 열어서 화자 분리 확인 (SPEAKER_00/01 구분 OK?)
[ ] data/02_subtitles/lecture_01_en.srt 샘플 10개 자막 청취 확인
[ ] data/02_subtitles/lecture_01_ko.srt CS 용어 번역 품질 확인 (function→함수, recursion→재귀)
[ ] data/03_audio/lecture_01_vocals.wav 재생 (배경음 누수 여부)
[ ] data/05_output/lecture_01_ko.mp4 재생 (더빙과 영상 동기화)
[ ] VLC 또는 mpv로 전체 5분 시청 및 자연스러움 평가
```

**Step 6: 비용 확인**

```bash
cat logs/cost_report.json
# Google TTS, Claude API 사용량 및 비용 확인
# 예상: Lecture 01 1개 → $0.5 미만
```

**Step 7: 파일럿 통과 후 배치 실행**

```bash
python -c "
import csv
from pipeline.control_tower import ControlTower

ct = ControlTower(config_path='pipeline/config.yaml')
with open('data/video_list.csv') as f:
    videos = [row for row in csv.DictReader(f)
              if not row['video_id'].startswith('#')]
ct.process_all(videos)
print(f'완료. 실패: {ct.failed_videos}')
"
```

**Step 8: Commit**

```bash
git add data/video_list.csv pipeline/tests/test_gcp_connection.py
git commit -m "test: add GCP connection test and pilot validation checklist"
```

---

## 전체 테스트 실행 명령

```bash
cd $USB_ROOT
source pipeline/venv/bin/activate
pytest pipeline/tests/ -v --ignore=pipeline/tests/test_gcp_connection.py
# (GCP 연결 테스트는 실제 API 키가 필요하므로 CI에서 제외)
```

Expected: 모든 유닛 테스트 통과

---

## 완성 기준

| 항목 | 기준 |
|------|------|
| Lecture 01 전체 파이프라인 완료 | `data/05_output/lecture_01_ko.mp4` 생성 |
| 자막 정확도 | CS 용어 오류 < 5개 (수동 검증) |
| 더빙 동기화 | 타임스탬프 오차 < 0.3초 평균 |
| 화자 분리 | 교수/학생 구분 정확도 ≥ 90% |
| 재현성 | USB를 다른 PC에 꽂아도 동일 실행 |
| 유닛 테스트 | 전체 통과 |
