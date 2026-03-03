# Pipeline Bugfix & Environment Setup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 2 bugs in `_load_ko_segments()`, clean up stale dependencies/config, install ffmpeg and runtime packages so pilot can run.

**Architecture:** TDD for the bug fix. Direct edits for config cleanup. Shell commands for environment setup. All changes on `claude/pipeline-dev` branch.

**Tech Stack:** Python 3.10, pytest, pip --target, ffmpeg static binary (x86_64 Linux)

---

### Task 1: Fix `_load_ko_segments()` speaker parsing bug (TDD)

**Files:**
- Modify: `pipeline/control_tower.py:187-203`
- Modify: `pipeline/tests/test_control_tower.py`

**Step 1: Write failing tests**

Add these 3 tests to `pipeline/tests/test_control_tower.py`:

```python
def test_load_ko_segments_parses_speaker_tag(tmp_path):
    from pipeline.control_tower import ControlTower

    srt_dir = tmp_path / "02_subtitles"
    srt_dir.mkdir(parents=True)
    (srt_dir / "lecture_01_ko.srt").write_text(
        "1\n00:00:00,000 --> 00:00:03,200\n[SPEAKER_00]\nCS61A에 오신 것을 환영합니다.\n\n"
        "2\n00:00:03,500 --> 00:00:06,000\n[SPEAKER_01]\n오늘은 함수에 대해 이야기하겠습니다.\n",
        encoding="utf-8",
    )
    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    segments = ct._load_ko_segments("lecture_01")

    assert len(segments) == 2
    assert segments[0]["speaker"] == "SPEAKER_00"
    assert segments[1]["speaker"] == "SPEAKER_01"
    assert "[SPEAKER" not in segments[0]["text"]
    assert "[SPEAKER" not in segments[1]["text"]
    assert "CS61A에 오신 것을 환영합니다." in segments[0]["text"]


def test_load_ko_segments_no_speaker_tag(tmp_path):
    from pipeline.control_tower import ControlTower

    srt_dir = tmp_path / "02_subtitles"
    srt_dir.mkdir(parents=True)
    (srt_dir / "lecture_01_ko.srt").write_text(
        "1\n00:00:00,000 --> 00:00:03,200\n태그 없는 자막입니다.\n",
        encoding="utf-8",
    )
    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    segments = ct._load_ko_segments("lecture_01")

    assert len(segments) == 1
    assert segments[0]["speaker"] == "SPEAKER_UNKNOWN"
    assert segments[0]["text"] == "태그 없는 자막입니다."


def test_load_ko_segments_timestamps_correct(tmp_path):
    from pipeline.control_tower import ControlTower

    srt_dir = tmp_path / "02_subtitles"
    srt_dir.mkdir(parents=True)
    (srt_dir / "lecture_01_ko.srt").write_text(
        "1\n01:02:03,456 --> 01:02:06,789\n[SPEAKER_00]\n테스트\n",
        encoding="utf-8",
    )
    ct = ControlTower(config_path="pipeline/config.yaml", data_dir=tmp_path)
    segments = ct._load_ko_segments("lecture_01")

    assert abs(segments[0]["start"] - 3723.456) < 0.01
    assert abs(segments[0]["end"] - 3726.789) < 0.01
```

**Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -m pytest pipeline/tests/test_control_tower.py::test_load_ko_segments_parses_speaker_tag pipeline/tests/test_control_tower.py::test_load_ko_segments_no_speaker_tag pipeline/tests/test_control_tower.py::test_load_ko_segments_timestamps_correct -v`

Expected: 2 FAIL (speaker tag test, no-tag test), 1 PASS (timestamps).
- `test_load_ko_segments_parses_speaker_tag`: FAIL — `segments[0]["speaker"]` is `"SPEAKER_UNKNOWN"` not `"SPEAKER_00"`, and `"[SPEAKER"` is in text
- `test_load_ko_segments_no_speaker_tag`: FAIL — text contains nothing (parts[2:] is empty when only 3 lines in block)

**Step 3: Fix `_load_ko_segments()` in `pipeline/control_tower.py`**

Add `import re` at the top of the file (line 1 area, alongside existing imports).

Replace lines 187-203 with:

```python
    def _load_ko_segments(self, video_id: str) -> List[Dict]:
        srt_path = self.data_dir / "02_subtitles" / f"{video_id}_ko.srt"
        if not srt_path.exists():
            return []
        blocks = srt_path.read_text(encoding="utf-8").strip().split("\n\n")
        segments = []
        for block in blocks:
            parts = block.strip().split("\n")
            if len(parts) >= 3:
                times = parts[1].split(" --> ")
                # parts[2]가 [SPEAKER_XX] 패턴이면 speaker 추출, 아니면 SPEAKER_UNKNOWN
                speaker_match = re.match(r"^\[(\w+)\]$", parts[2].strip())
                if speaker_match:
                    speaker = speaker_match.group(1)
                    text = " ".join(parts[3:])
                else:
                    speaker = "SPEAKER_UNKNOWN"
                    text = " ".join(parts[2:])
                segments.append({
                    "start": _srt_time_to_sec(times[0]),
                    "end": _srt_time_to_sec(times[1]),
                    "text": text.strip(),
                    "speaker": speaker,
                })
        return segments
```

**Step 4: Run all control_tower tests**

Run: `PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -m pytest pipeline/tests/test_control_tower.py -v`

Expected: 9 PASSED (6 existing + 3 new)

**Step 5: Run full test suite**

Run: `PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -m pytest pipeline/tests/ -v`

Expected: 59 passed, 2 skipped

**Step 6: Commit**

```bash
git add pipeline/control_tower.py pipeline/tests/test_control_tower.py
git commit -m "fix: parse speaker tag from Korean SRT in _load_ko_segments

Previously all segments used SPEAKER_UNKNOWN and the [SPEAKER_XX] tag
leaked into TTS text. Now regex extracts speaker ID and keeps text clean."
```

---

### Task 2: Clean up requirements files

**Files:**
- Delete: `pipeline/requirements.txt`
- Modify: `pipeline/requirements-dev.txt:1`
- Modify: `pipeline/tests/test_environment.py:1-3`

**Step 1: Delete `pipeline/requirements.txt`**

This file's role is ambiguous (mixes dev + runtime deps) and still references `google-cloud-texttospeech`. The project uses `requirements-dev.txt` + `requirements-runtime.txt` for a clear separation.

```bash
git rm pipeline/requirements.txt
```

**Step 2: Update `requirements-dev.txt` — remove `anthropic`**

No pipeline code imports anthropic anymore. The `anthropic` package in `pipeline/packages/` is an unused leftover.

New content for `pipeline/requirements-dev.txt`:

```
# 개발 필수 (코드 작성 및 테스트용)
python-dotenv==1.0.1
pyyaml==6.0.1
pydantic==2.7.1
pytest==8.2.0
pytest-mock==3.14.0
tqdm==4.66.4
```

**Step 3: Update `test_environment.py` — remove anthropic test**

New content for `pipeline/tests/test_environment.py`:

```python
def test_yaml_importable():
    import yaml
    assert yaml.__version__

def test_pydantic_importable():
    import pydantic
    assert pydantic.__version__

def test_dotenv_importable():
    import dotenv
    assert dotenv

def test_tqdm_importable():
    import tqdm
    assert tqdm.__version__
```

**Step 4: Run tests**

Run: `PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -m pytest pipeline/tests/ -v`

Expected: 58 passed, 2 skipped (1 fewer test than before)

**Step 5: Commit**

```bash
git add pipeline/requirements-dev.txt pipeline/tests/test_environment.py
git commit -m "chore: remove stale google-cloud-texttospeech and anthropic from requirements

Delete ambiguous requirements.txt, remove anthropic from dev deps,
remove test_anthropic_importable test."
```

---

### Task 3: Clean up `.env` and `.env.example`

**Files:**
- Modify: `.env`
- Modify: `.env.example`

**Step 1: Update `.env`**

Remove `ANTHROPIC_API_KEY` line. New content:

```
USB_ROOT=/path/to/your/workspace

HF_TOKEN=hf_여기에_HuggingFace_토큰_입력

WHISPER_MODEL_DIR=${USB_ROOT}/models/whisperx
SPLEETER_MODEL_DIR=${USB_ROOT}/models/spleeter
```

**Step 2: Update `.env.example`**

Remove `GOOGLE_APPLICATION_CREDENTIALS` and `ANTHROPIC_API_KEY`. New content:

```
USB_ROOT=/path/to/your/workspace

HF_TOKEN=hf_여기에_HuggingFace_토큰_입력

WHISPER_MODEL_DIR=${USB_ROOT}/models/whisperx
SPLEETER_MODEL_DIR=${USB_ROOT}/models/spleeter
```

**Step 3: Commit**

`.env` is gitignored, so only `.env.example` is committed:

```bash
git add .env.example
git commit -m "chore: remove GCP and Anthropic entries from .env.example"
```

---

### Task 4: Install ffmpeg static binary

**Files:**
- Create: `pipeline/bin/ffmpeg` (downloaded binary, NOT committed)
- Modify: `pipeline/run.sh:10`
- Modify: `.gitignore`

**Step 1: Download ffmpeg static binary**

```bash
mkdir -p /path/to/your/workspace/pipeline/bin
cd /tmp
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xf ffmpeg-release-amd64-static.tar.xz
cp ffmpeg-*-amd64-static/ffmpeg /path/to/your/workspace/pipeline/bin/ffmpeg
cp ffmpeg-*-amd64-static/ffprobe /path/to/your/workspace/pipeline/bin/ffprobe
chmod +x /path/to/your/workspace/pipeline/bin/ffmpeg
chmod +x /path/to/your/workspace/pipeline/bin/ffprobe
rm -rf ffmpeg-*-amd64-static* ffmpeg-release-amd64-static.tar.xz
```

**Step 2: Update `pipeline/run.sh` — add bin/ to PATH**

Add `export PATH="$USB_ROOT/pipeline/bin:$PATH"` after line 10. New `run.sh`:

```bash
#!/bin/bash
# 파이프라인 스크립트 실행 래퍼
# Usage: bash pipeline/run.sh modules/01_download.py
# Usage: bash pipeline/run.sh control_tower.py

USB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACKAGES_DIR="$USB_ROOT/pipeline/packages"

export USB_ROOT
export PYTHONPATH="$PACKAGES_DIR:$USB_ROOT:$PYTHONPATH"
export PYTHONNOUSERSITE=1  # 홈 디렉토리 손상 패키지 무시
export PATH="$USB_ROOT/pipeline/bin:$PATH"

if [ -f "$USB_ROOT/.env" ]; then
    export $(grep -v '^#' "$USB_ROOT/.env" | xargs)
fi

echo "[run] USB_ROOT=$USB_ROOT"
python3 "$USB_ROOT/pipeline/$1" "${@:2}"
```

**Step 3: Add `pipeline/bin/` to `.gitignore`**

Add after the `pipeline/packages/` line:

```
pipeline/bin/
```

**Step 4: Verify ffmpeg works**

```bash
/path/to/your/workspace/pipeline/bin/ffmpeg -version | head -1
```

Expected: `ffmpeg version N.N-static ...`

**Step 5: Commit**

```bash
git add pipeline/run.sh .gitignore
git commit -m "feat: add ffmpeg static binary support to pipeline

Add pipeline/bin/ to PATH in run.sh for portable ffmpeg.
Add pipeline/bin/ to .gitignore (binary not committed)."
```

---

### Task 5: Install runtime packages

**Step 1: Install**

```bash
cd /path/to/your/workspace
pip install --target=pipeline/packages --no-cache-dir -r pipeline/requirements-runtime.txt
```

This installs: whisperx, spleeter, edge-tts, ffmpeg-python, pyrubberband, soundfile, librosa, numpy.

**Step 2: Verify imports**

```bash
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -c "
import edge_tts; print(f'edge-tts OK')
import soundfile; print(f'soundfile OK')
import numpy; print(f'numpy {numpy.__version__} OK')
import ffmpeg; print(f'ffmpeg-python OK')
print('All runtime imports OK')
"
```

Expected: All OK lines printed.

Note: `import whisperx` and `import spleeter` may fail without GPU/torch. That is expected — they are tested at actual runtime, not during dev.

**Step 3: Run full test suite**

```bash
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -m pytest pipeline/tests/ -v
```

Expected: 58 passed, 2 skipped

---

### Task 6: Final verification

**Step 1: Verify git status is clean (no untracked junk)**

```bash
git status
```

Expected: clean working tree.

**Step 2: Verify test count and results**

```bash
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -m pytest pipeline/tests/ -q
```

Expected: `58 passed, 2 skipped`

**Step 3: Verify ffmpeg is callable**

```bash
PATH=pipeline/bin:$PATH ffmpeg -version | head -1
```

Expected: version string output.

**Step 4: Log final commit count**

```bash
git log --oneline main..HEAD | wc -l
```

Expected: 18+ commits ahead of main.
