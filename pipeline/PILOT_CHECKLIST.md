# 파일럿 테스트 체크리스트 (Lecture 01)

## 사전 준비

- [ ] `.env` 파일 작성 (`.env.example` 참고)
- [ ] `HF_TOKEN` 환경변수 설정 (pyannote diarization 접근용)
- [ ] `pipeline/video_list.csv`에 Lecture 01 실제 Bilibili URL 입력

## 런타임 패키지 설치

```bash
cd /media/namykim/391B-C6F7/workspace/c61a
pip install --target=pipeline/packages --no-cache-dir \
    -r pipeline/requirements-runtime.txt
```

## WhisperX 모델 사전 다운로드

```bash
export $(grep -v '^#' .env | xargs)
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -c "
import os, whisperx
model = whisperx.load_model(
    'large-v2', 'cpu', compute_type='int8',
    download_root=os.environ['WHISPER_MODEL_DIR']
)
print('WhisperX large-v2 준비 완료')
"
```

## Lecture 01 — 1단계: 다운로드 + 전사 + 영어 자막 생성

```bash
export $(grep -v '^#' .env | xargs)
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -c "
from pipeline.control_tower import ControlTower, TranslationPendingError
ct = ControlTower(config_path='pipeline/config.yaml')
try:
    ct.process_video('lecture_01', 'https://www.bilibili.com/video/BV1GK411Q7qp')
except TranslationPendingError as e:
    print(e)
    print('→ 2단계: Claude Code로 번역을 진행하세요')
"
```

파이프라인이 자동으로 일시 중단되고 아래 파일이 생성됩니다:
- `data/02_subtitles/lecture_01_en.srt` — 영어 원본 자막
- `data/02_subtitles/lecture_01_translation_input.md` — 번역 입력 파일

## Lecture 01 — 2단계: Claude Code로 한국어 번역

Claude Code(이 세션)에서 아래 요청을 입력하세요:

```
data/02_subtitles/lecture_01_translation_input.md 파일을 읽고
CS61A 강의 자막을 한국어로 번역하여
data/02_subtitles/lecture_01_ko.srt 에 SRT 형식으로 저장하세요.
```

## Lecture 01 — 3단계: 더빙 합성 (번역 완료 후)

```bash
export $(grep -v '^#' .env | xargs)
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -c "
from pipeline.control_tower import ControlTower
ct = ControlTower(config_path='pipeline/config.yaml')
ct.process_video('lecture_01', 'https://www.bilibili.com/video/BV1GK411Q7qp')
print('파일럿 완료!')
"
```

## 품질 검증 체크리스트

- [ ] `data/01_transcripts/lecture_01.json` — 화자 분리 확인 (SPEAKER_00/01 구분)
- [ ] `data/02_subtitles/lecture_01_en.srt` — 영어 전사 샘플 10개 청취 대조
- [ ] `data/02_subtitles/lecture_01_ko.srt` — CS 용어 번역 품질 (function→함수 등)
- [ ] `data/03_audio/lecture_01_vocals.wav` — 재생: 배경음 누수 없는지
- [ ] `data/05_output/lecture_01_ko.mp4` — 영상 재생: 더빙-영상 동기화
- [ ] 전체 5분 시청: 자연스러운 한국어 더빙인지 확인

## 통과 기준

| 항목 | 기준 |
|------|------|
| 화자 분리 | 교수/학생 구분 ≥ 90% |
| CS 용어 오류 | < 5개 |
| 더빙 동기화 | 오차 < 0.3초 평균 |
| 최종 MP4 재생 | 일반 플레이어 정상 재생 |

## 배치 처리 (파일럿 통과 후)

```bash
export $(grep -v '^#' .env | xargs)
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -c "
from pipeline.control_tower import ControlTower
ct = ControlTower(config_path='pipeline/config.yaml')
ct.process_csv('pipeline/video_list.csv')
print(f'완료. 실패: {ct.failed_videos}')
"
```

> **배치 번역 워크플로**: 각 강의가 SUBTITLED 상태에서 자동 일시 중단됩니다.
> `data/02_subtitles/` 의 `*_translation_input.md` 파일들을 Claude Code로 순서대로 번역 후
> 파이프라인을 재실행하면 번역된 강의부터 더빙 합성이 재개됩니다.
