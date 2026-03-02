# CS61A Fall 2022 Korean Localization Pipeline — Design Document

**Date**: 2026-03-02
**Author**: Claude Code (Control Tower)
**Status**: Approved

---

## 1. 목표

UC Berkeley CS61A Fall 2022 강의 49개 영상(Bilibili)을 한국 글로벌 컴퓨터공학 학습자를 위한 고품질 한국어 자막 및 자연스러운 더빙 영상으로 변환하여 YouTube에 배포한다.

### 성공 기준

- 네이티브 한국인이 자막/더빙을 통해 내용을 막힘없이 이해할 수 있을 것
- 컴퓨터공학 전문 용어가 정확하게 번역/음역될 것
- 화자(교수 / 학생)가 구분된 자막과 더빙이 제공될 것
- USB 한 개만 있으면 어떤 환경에서도 파이프라인을 재실행할 수 있을 것

---

## 2. 기술 스택

| 역할 | 도구 | 이유 |
|------|------|------|
| 음성 인식 + 화자 분리 | WhisperX | 오픈소스, 로컬 실행, diarization 지원 |
| 한국어 번역 / 자막 정제 | Claude API (claude-sonnet-4-6) | CS 용어 이해, 자연스러운 번역 |
| 배경음 분리 | Spleeter (2-stem) | 오픈소스, vocals/accompaniment 분리 |
| 한국어 TTS 더빙 | Google Cloud TTS | 자연스러운 한국어 Neural2 음성 |
| 영상/오디오 편집 | ffmpeg, rubberband | 동기화 조정 및 최종 합성 |
| 파이프라인 오케스트레이션 | Claude Code (Control Tower) | 자동화, 오류 복구, 상태 관리 |

---

## 3. 작업 환경 (USB 기반)

### 3-1. 디렉토리 구조

```
$USB_ROOT/  (예: /media/namykim/391B-C6F7/workspace/c61a/)
├── pipeline/
│   ├── config.yaml              # 중앙 설정 (경로, API 키 참조, 파라미터)
│   ├── requirements.txt         # Python 의존성
│   ├── venv/                    # Python 가상환경 (USB 자급자족)
│   ├── modules/
│   │   ├── 01_download.py       # Bilibili 영상 다운로드
│   │   ├── 02_transcribe.py     # WhisperX 전사 + 화자 분리
│   │   ├── 03_subtitle.py       # 영어 SRT 생성 + Claude 번역
│   │   ├── 04_audio_edit.py     # Spleeter 배경음 분리
│   │   ├── 05_tts_dub.py        # Google Cloud TTS 청크 더빙
│   │   └── 06_synthesize.py     # 최종 더빙 합성 + ffmpeg
│   ├── control_tower.py         # 전체 파이프라인 오케스트레이터
│   └── utils/
│       ├── logger.py            # 표준 로깅
│       ├── cost_tracker.py      # Google TTS 비용 추적
│       ├── quality_check.py     # 자동 품질 검증
│       └── speaker_config.yaml  # 화자별 TTS 음성 프로필
├── models/
│   ├── whisperx/                # WhisperX 모델 캐시 (USB 내)
│   └── spleeter/                # Spleeter pretrained 모델 (USB 내)
├── data/
│   ├── 00_raw/                  # Bilibili 원본 영상 (mp4)
│   ├── 01_transcripts/          # WhisperX 출력 (JSON) ← 영구 보존
│   ├── 02_subtitles/            # 자막 파일 (SRT, VTT) ← 영구 보존
│   ├── 03_audio/                # vocals.wav + bgm.wav ← 영구 보존
│   ├── 04_dubbed_chunks/        # TTS 청크 WAV ← 합성 완료 후 삭제
│   ├── 05_output/               # 최종 완성 영상 (MP4)
│   └── progress.json            # 처리 상태 추적 (재개 가능)
└── logs/
    ├── pipeline.log             # 전체 실행 로그
    ├── errors.log               # 오류 로그
    └── cost_report.json         # API 비용 누적
```

### 3-2. 환경 변수

```bash
# .env (USB 루트에 위치, git에 커밋 안 함)
USB_ROOT=/media/namykim/391B-C6F7/workspace/c61a
GOOGLE_APPLICATION_CREDENTIALS=$USB_ROOT/pipeline/gcp_key.json
ANTHROPIC_API_KEY=sk-...
HF_TOKEN=...  # pyannote diarization 모델 접근용
WHISPER_MODEL_DIR=$USB_ROOT/models/whisperx
SPLEETER_MODEL_DIR=$USB_ROOT/models/spleeter
```

---

## 4. 데이터 플로우

```
[Bilibili 영상 URL 리스트 — video_list.csv]
        │
        ▼ Module 01: download.py (yt-dlp)
[data/00_raw/lecture_01.mp4]
        │
        ├──────────────────────────────────────────┐
        ▼                                          ▼
Module 02: transcribe.py (WhisperX)        Module 04: audio_edit.py (Spleeter)
[data/01_transcripts/lecture_01.json]      [data/03_audio/lecture_01_vocals.wav]
{                                          [data/03_audio/lecture_01_bgm.wav]
  "segments": [                                    │
    {                                              │
      "start": 0.0, "end": 3.2,                   │
      "text": "Welcome to CS61A",                  │
      "speaker": "SPEAKER_00"                      │
    }, ...                                         │
  ]                                                │
}                                                  │
        │                                          │
        ▼ Module 03: subtitle.py (Claude API)      │
[data/02_subtitles/lecture_01_en.srt]              │
[data/02_subtitles/lecture_01_ko.srt]              │
        │                                          │
        └──────────────┬───────────────────────────┘
                       ▼ Module 05: tts_dub.py (Google Cloud TTS)
           [data/04_dubbed_chunks/lecture_01/
              chunk_0001_SPEAKER_00.wav
              chunk_0002_SPEAKER_00.wav
              chunk_0003_SPEAKER_01.wav  ...]
                       │
                       ▼ Module 06: synthesize.py (ffmpeg + rubberband)
           [data/05_output/lecture_01_ko.mp4]  ← 최종 완성
                       │
                       ▼ cleanup: dubbed_chunks 삭제 (USB 절약)
```

---

## 5. 모듈 상세 명세

### Module 01 — download.py

```
입력: video_list.csv (video_id, title, type[lecture/disc/project])
출력: data/00_raw/{type}_{id}.mp4
도구: yt-dlp
```

**핵심 로직:**
- Bilibili 영상 URL 구성 → `yt-dlp --format best -o {output_path}`
- 이미 다운로드된 파일은 건너뜀 (멱등성)
- 영상 메타데이터(제목, 길이) 추출하여 `progress.json` 업데이트

---

### Module 02 — transcribe.py

```
입력: data/00_raw/{video}.mp4
출력: data/01_transcripts/{video}.json
도구: WhisperX (large-v2 모델, diarization 활성화)
```

**핵심 로직:**
1. MP4 → WAV 추출 (16kHz, mono)
2. WhisperX 실행: `whisperx audio.wav --model large-v2 --diarize --hf_token {HF_TOKEN} --model_dir {WHISPER_MODEL_DIR}`
3. 출력 JSON 구조 표준화
4. 화자 수 자동 감지 (`min_speakers=1, max_speakers=5`)

**품질 기준:**
- 화자 분리 신뢰도 < 0.5인 segment는 `speaker: "UNKNOWN"` 표시
- 단어 수준 타임스탬프 보존 (자막 동기화에 활용)

---

### Module 03 — subtitle.py

```
입력: data/01_transcripts/{video}.json
출력: data/02_subtitles/{video}_en.srt
       data/02_subtitles/{video}_ko.srt
도구: Claude API (claude-sonnet-4-6)
```

**핵심 로직:**

**Step A — 영어 SRT 생성:**
- segment를 의미 단위로 병합 (최소 1초, 최대 5초, 최대 42자/줄)
- 화자 변경 시 강제 분할 → SRT에 화자 태그 삽입
  ```
  [SPEAKER_00 - DeNero]
  Welcome to CS61A.
  ```

**Step B — 한국어 번역 (Claude API):**
- 배치 처리 (30개 자막 청크씩)
- 시스템 프롬프트에 CS61A 전용 용어 사전 주입:
  ```
  function → 함수 / closure → 클로저 / recursion → 재귀
  environment → 환경 / frame → 프레임 / binding → 바인딩
  higher-order function → 고차 함수 / tail call → 꼬리 호출
  ...
  ```
- 번역 톤: 친근한 설명체 (반말 아님, 딱딱한 직역 아님)
- 코드/변수명은 번역하지 않고 백틱으로 감쌈: `` `x = 5` ``

---

### Module 04 — audio_edit.py

```
입력: data/00_raw/{video}.mp4
출력: data/03_audio/{video}_vocals.wav
       data/03_audio/{video}_bgm.wav
도구: Spleeter (2-stems)
```

**핵심 로직:**
1. MP4 → WAV (44.1kHz, stereo — Spleeter 최적 포맷)
2. Spleeter 실행: `spleeter separate -p spleeter:2stems -o {output_dir} audio.wav`
3. 출력 음량 정규화: vocals → -18dB LUFS, bgm → -25dB LUFS
4. 품질 검증: vocals 파일에서 무음 구간 비율이 90% 초과 시 경고 (분리 실패 가능성)

---

### Module 05 — tts_dub.py

```
입력: data/02_subtitles/{video}_ko.srt
       data/01_transcripts/{video}.json (화자 ID 참조)
출력: data/04_dubbed_chunks/{video}/chunk_{seq}_{speaker}.wav
도구: Google Cloud TTS (Neural2 한국어)
```

**화자 프로필 (speaker_config.yaml):**
```yaml
SPEAKER_00:  # DeNero 교수 (주 강의자)
  voice: ko-KR-Neural2-C  # 차분하고 명확한 남성 음성
  speaking_rate: 0.95
  pitch: -1.0

SPEAKER_01:  # TA / 보조 강의자
  voice: ko-KR-Neural2-B
  speaking_rate: 1.0
  pitch: 0.0

SPEAKER_UNKNOWN:  # 학생 질문 등 미식별 화자
  voice: ko-KR-Neural2-A
  speaking_rate: 1.05
  pitch: 1.0
```

**타임스탬프 동기화 전략:**
- TTS 생성 결과 길이 vs 원본 segment 길이 비교
- 허용 범위 ±25% → `rubberband` 라이브러리로 피치 보존 속도 조정
- ±25% 초과 시 Claude API가 해당 문장을 재분할하여 재생성

---

### Module 06 — synthesize.py

```
입력: data/04_dubbed_chunks/{video}/  (모든 WAV 청크)
       data/03_audio/{video}_bgm.wav
       data/02_subtitles/{video}_ko.srt
출력: data/05_output/{video}_ko.mp4
도구: ffmpeg, rubberband
```

**핵심 로직:**
1. 모든 더빙 청크를 타임스탬프 순서대로 타임라인에 배치
2. 청크 사이 침묵 구간은 0dB 무음으로 채움
3. 배경음(bgm) + 더빙 오디오 믹싱:
   - 더빙 음성이 있는 구간: bgm -20dB (배경으로), 더빙 0dB
   - 더빙 없는 구간 (침묵/음악 전용): bgm 0dB
4. 최종 영상 생성:
   ```bash
   ffmpeg -i original_video.mp4 -i final_audio.wav \
     -c:v copy -c:a aac -b:a 192k \
     -map 0:v:0 -map 1:a:0 \
     output_ko.mp4
   ```
5. 한국어 자막 파일 임베드 (소프트 자막, 선택 가능)

---

## 6. Control Tower (control_tower.py)

```python
# 상태 머신 기반 오케스트레이터

STATES = [
    "NOT_STARTED", "DOWNLOADED", "TRANSCRIBED",
    "SUBTITLED", "AUDIO_EDITED", "DUBBED", "SYNTHESIZED", "DONE"
]

def process_video(video_id: str):
    state = load_state(video_id)  # progress.json에서 로드

    runners = [
        ("DOWNLOADED",   run_download),
        ("TRANSCRIBED",  run_transcribe),
        ("SUBTITLED",    run_subtitle),
        ("AUDIO_EDITED", run_audio_edit),
        ("DUBBED",       run_tts_dub),
        ("SYNTHESIZED",  run_synthesize),
    ]

    for target_state, runner in runners:
        if state_index(state) < state_index(target_state):
            try:
                runner(video_id)
                state = target_state
                save_state(video_id, state)
            except Exception as e:
                log_error(video_id, e)
                # Claude Code가 오류 분석 후 재시도 또는 skip 결정
                raise

    cleanup_dubbed_chunks(video_id)  # 최종 완성 후 청크 삭제
    save_state(video_id, "DONE")
```

**재개 가능성**: `progress.json`에 각 영상의 현재 상태 저장. 중단 후 재실행 시 완료된 단계는 건너뜀.

**오류 처리**:
- 자동 재시도: 최대 3회 (네트워크 오류, API 일시적 실패)
- 재시도 실패 시: 해당 영상을 `failed` 상태로 기록하고 다음 영상으로 진행
- 오류 로그 + Claude Code 분석으로 근본 원인 파악

---

## 7. USB 용량 관리

### 예상 용량 (영상 1개 기준 — 약 60분)

| 파일 | 예상 용량 | 보존 여부 |
|------|----------|---------|
| 원본 MP4 (`00_raw`) | ~500MB | 보존 |
| 전사 JSON (`01_transcripts`) | ~500KB | 영구 보존 |
| 자막 SRT (`02_subtitles`) | ~100KB | 영구 보존 |
| vocals + bgm WAV (`03_audio`) | ~600MB | 영구 보존 |
| TTS 청크 WAV (`04_dubbed_chunks`) | ~200MB | **합성 후 삭제** |
| 최종 MP4 (`05_output`) | ~500MB | 보존 |
| **영구 보존 합계** | ~1.6GB/영상 | |
| **49개 영상 총합** | ~78GB | |

> USB 루트가 약 400GB (`391B-C6F7` 드라이브 이름에서 추정)로 충분한 여유 있음.

---

## 8. 비용 추정

| 서비스 | 계산 | 예상 비용 |
|--------|------|----------|
| Google Cloud TTS (Neural2) | 49개 × 60분 × ~150 단어/분 × ~5자/단어 = 2.2M 문자 / $16/1M | **~$35** |
| Claude API (번역) | 2.2M 영어 입력 + 2.2M 한국어 출력 ≈ 4.4M 토큰 / $3/1M | **~$13** |
| Google Cloud TTS (Standard 대역 포함) | 무료 티어 100만 자/월 적용 시 | 절감 가능 |
| **합계** | | **~$48** |

---

## 9. 파일럿 테스트 계획

**대상**: Lecture 01 (CS61A 첫 강의, 약 60분)

**단계:**
1. 전체 파이프라인 1회 실행
2. 각 모듈 출력 품질 수동 검증:
   - 전사 정확도: 영어 transcript 샘플링 청취
   - 화자 분리: 교수/학생 구분 정확도
   - 번역 자연스러움: CS 용어 + 대화체 확인
   - 배경음 분리: vocals 누수 여부
   - 더빙 동기화: 영상과 음성 일치 여부
3. 발견된 문제 기록 → 파라미터 조정 후 재실행
4. 파일럿 통과 기준 충족 시 나머지 48개 영상 배치 처리 시작

**파일럿 통과 기준:**
- 화자 분리 정확도 ≥ 90%
- 번역 CS 용어 오류 < 5개
- 더빙 타임스탬프 오차 < 0.3초 평균
- 최종 영상이 일반 플레이어에서 문제없이 재생

---

## 10. 구현 순서 (Module-First)

```
Phase 1: 환경 설정          → USB 기반 venv, 모델 다운로드, API 연결 테스트
Phase 2: Module 02 구현     → WhisperX transcribe (가장 기반이 되는 모듈)
Phase 3: Module 01 구현     → 다운로드 (02 테스트용 영상 확보)
Phase 4: Module 03 구현     → 자막 생성 + Claude 번역
Phase 5: Module 04 구현     → Spleeter 음성 분리
Phase 6: Module 05 구현     → Google Cloud TTS 더빙
Phase 7: Module 06 구현     → ffmpeg 합성
Phase 8: Control Tower      → 상태 머신 + 오케스트레이션
Phase 9: 파일럿 테스트      → Lecture 01 전체 파이프라인
Phase 10: 배치 처리         → 나머지 48개 영상
```
