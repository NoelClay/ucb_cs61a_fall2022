import re
from pathlib import Path
from typing import List, Dict
from pipeline.utils.logger import get_logger

logger = get_logger("subtitle")


def format_timestamp(seconds: float) -> str:
    ms = int(round((seconds % 1) * 1000))
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def merge_segments(
    segments: List[Dict],
    min_duration: float = 1.0,
    max_duration: float = 5.0,
    max_chars: int = 42,
) -> List[Dict]:
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
    blocks = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()
        if include_speaker:
            text = f"[{seg['speaker']}]\n{text}"
        blocks.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(blocks)


def generate_translation_input(
    segments: List[Dict],
    video_id: str,
    output_path: Path,
    cs_terms_path: str = "pipeline/utils/cs_terms.yaml",
):
    """Claude Code가 번역할 수 있도록 구조화된 입력 파일을 생성한다."""
    import yaml

    with open(cs_terms_path, encoding="utf-8") as f:
        terms = yaml.safe_load(f)
    terms_str = "\n".join(f"- {k} → {v}" for k, v in terms.items())

    numbered = "\n".join(
        f"{i + 1}. [{seg['speaker']}] {seg['text']}"
        for i, seg in enumerate(segments)
    )

    content = f"""# {video_id} 한국어 번역 요청

## CS61A 용어 사전
{terms_str}

## 번역 규칙
1. 기술 용어는 위 사전을 우선 참고하세요
2. 코드, 변수명, 함수명은 번역하지 말고 백틱으로 감싸세요 (예: `x = 5`)
3. 자연스러운 한국어 설명체로 번역하세요 (존댓말, 딱딱하지 않게)
4. 번호와 화자 태그 [SPEAKER_XX]는 그대로 유지하세요
5. 한 줄에 한 항목만 출력하세요

## 영어 자막 목록 (총 {len(segments)}개)
{numbered}

## 번역 완료 후
아래 경로에 한국어 SRT 파일을 저장하세요:
`data/02_subtitles/{video_id}_ko.srt`

형식 예시:
```
1
00:00:00,000 --> 00:00:03,200
[SPEAKER_00]
CS61A에 오신 것을 환영합니다.

2
00:00:03,500 --> 00:00:06,000
[SPEAKER_00]
오늘은 함수에 대해 이야기하겠습니다.
```
"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"[TRANSLATION INPUT] {output_path.name} ({len(segments)} segments)")


def save_srt(srt_content: str, output_path: Path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(srt_content, encoding="utf-8")
    logger.info(f"[SAVED] {output_path.name}")
