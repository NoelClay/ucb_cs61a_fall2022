# 파일럿 테스트 체크리스트 (Lecture 01)

## 사전 준비

- [ ] `.env` 파일 작성 (`.env.example` 참고)
- [ ] `pipeline/gcp_key.json` 설치 (Google Cloud TTS 서비스 계정 키)
- [ ] `HF_TOKEN` 환경변수 설정 (pyannote diarization 접근용)
- [ ] `pipeline/video_list.csv`에 Lecture 01 실제 Bilibili URL 입력

## 런타임 패키지 설치

```bash
cd /media/namykim/391B-C6F7/workspace/c61a
pip install --target=pipeline/packages --no-cache-dir \
    -r pipeline/requirements-runtime.txt
```

## GCP 연결 테스트

```bash
export $(grep -v '^#' .env | xargs)
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -c "
from google.cloud import texttospeech
client = texttospeech.TextToSpeechClient()
voices = client.list_voices(language_code='ko-KR')
ko = [v.name for v in voices.voices if 'Neural2' in v.name]
print('사용 가능한 한국어 Neural2 음성:', ko)
"
```

## WhisperX 모델 사전 다운로드

```bash
PYTHONPATH=pipeline/packages:. PYTHONNOUSERSITE=1 python3 -c "
import os, whisperx
model = whisperx.load_model(
    'large-v2', 'cpu', compute_type='int8',
    download_root=os.environ['WHISPER_MODEL_DIR']
)
print('WhisperX large-v2 준비 완료')
"
```

## Lecture 01 파이프라인 실행

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
