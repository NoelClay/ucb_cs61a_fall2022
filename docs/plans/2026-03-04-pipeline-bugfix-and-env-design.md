# Pipeline Bugfix & Environment Setup Design

Date: 2026-03-04
Branch: claude/pipeline-dev

## Context

Pipeline code is complete (56 tests passing) but has 5 issues blocking pilot execution:
- 2 bugs in `_load_ko_segments()`
- requirements file inconsistency
- stale `.env` entry
- missing ffmpeg binary
- missing runtime packages

## Issue 1: `_load_ko_segments()` Speaker Parsing Bug

### Problem

`control_tower.py:_load_ko_segments()` has two bugs:

**Bug A** (line 201): `"speaker": "SPEAKER_UNKNOWN"` is hardcoded for every segment, ignoring the `[SPEAKER_XX]` tag present in the Korean SRT. All TTS dubbing uses the wrong voice (SPEAKER_UNKNOWN fallback = ko-KR-SunHiNeural at 1.05x) instead of mapping SPEAKER_00 and SPEAKER_01 to their configured voices.

**Bug B** (line 200): `" ".join(parts[2:])` includes the `[SPEAKER_00]` tag line in the text field. This literal string is passed to edge-tts, which will vocalize "open bracket SPEAKER underscore 00 close bracket" before the Korean sentence.

### SRT Format Produced by `segments_to_srt(include_speaker=True)`

```
1
00:00:00,000 --> 00:00:03,200
[SPEAKER_00]
CS61A에 오신 것을 환영합니다.

2
00:00:03,500 --> 00:00:06,000
[SPEAKER_01]
오늘은 함수에 대해 이야기하겠습니다.
```

Each block has 4 lines: sequence, timestamp, speaker tag, text.

### Fix

Extract SRT parsing into a testable utility function `parse_srt_with_speaker()` in `control_tower.py`. The function:
1. Splits SRT into blocks by `\n\n`
2. For each block, checks if `parts[2]` matches `\[(\w+)\]`
3. If match: extract speaker from group(1), text from `parts[3:]`
4. If no match: speaker = `SPEAKER_UNKNOWN`, text from `parts[2:]`

### Tests

- Speaker tag present → correct speaker + clean text
- Speaker tag absent → SPEAKER_UNKNOWN + full text
- Multiple blocks with different speakers → each correctly parsed

## Issue 2: Requirements Files Inconsistency

### Problem

| File | Issue |
|------|-------|
| `requirements.txt` | Lists `google-cloud-texttospeech` (removed from code), missing `edge-tts` |
| `requirements-dev.txt` | Lists `anthropic` (no longer used in pipeline scripts) |
| `requirements-runtime.txt` | Correct (edge-tts 6.1.9 verified on PyPI) |

### Fix

- **Delete** `requirements.txt` (ambiguous role, dev+runtime混在)
- **Update** `requirements-dev.txt`: remove `anthropic`
- **Update** `setup.sh`: change reference from `requirements.txt` to `requirements-dev.txt`
- **Update** `test_environment.py`: remove `test_anthropic_importable()`
- **Keep** `requirements-runtime.txt` as-is

## Issue 3: `.env` Stale Entry

### Problem

`.env` contains `ANTHROPIC_API_KEY=여기에_Anthropic_API_키_입력`. No pipeline code references this variable (confirmed by grep across `pipeline/modules/*.py` and `pipeline/control_tower.py`).

### Fix

- Remove `ANTHROPIC_API_KEY` line from `.env`
- Update `.env.example` accordingly

## Issue 4: ffmpeg Binary Missing

### Problem

`which ffmpeg` returns nothing. Three modules depend on it:
- `audio_edit.py` → `extract_audio()` (MP4→WAV)
- `tts_dub.py` → `_mp3_to_wav()` (edge-tts MP3→WAV)
- `synthesize.py` → final video composition

No sudo access available.

### Fix

- Download ffmpeg static binary (x86_64 Linux) to `pipeline/bin/ffmpeg`
- Update `run.sh` to prepend `pipeline/bin/` to PATH
- Add `pipeline/bin/` to `.gitignore` (binary too large to commit)

### Source

https://johnvansickle.com/ffmpeg/ — ffmpeg-release-amd64-static.tar.xz (~80MB)

## Issue 5: Runtime Packages Not Installed

### Problem

`pipeline/packages/` has dev dependencies but missing runtime packages:
edge-tts, whisperx, spleeter, soundfile, pyrubberband, librosa.

### Fix

```bash
pip install --target=pipeline/packages --no-cache-dir -r pipeline/requirements-runtime.txt
```

Verify with import checks for each package.

## Execution Order

1. Fix `_load_ko_segments()` bug (TDD)
2. Clean up requirements files
3. Clean up `.env`
4. Install ffmpeg static binary
5. Install runtime packages
6. Verify all 58+ tests pass + runtime import checks
