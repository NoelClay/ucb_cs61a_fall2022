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


def translate_subtitles_with_claude(
    segments: List[Dict],
    api_key: str,
    cs_terms_path: str,
    batch_size: int = 30,
) -> List[Dict]:
    import anthropic
    import yaml

    with open(cs_terms_path, encoding="utf-8") as f:
        terms = yaml.safe_load(f)
    terms_str = "\n".join(f"- {k} → {v}" for k, v in terms.items())

    client = anthropic.Anthropic(api_key=api_key)
    translated = []

    for i in range(0, len(segments), batch_size):
        batch = segments[i:i + batch_size]
        numbered = "\n".join(
            f"{j + 1}. [{seg['speaker']}] {seg['text']}"
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
            messages=[{"role": "user", "content": prompt}],
        )
        translations = _parse_numbered_translations(
            response.content[0].text, len(batch)
        )
        for j, seg in enumerate(batch):
            new_seg = dict(seg)
            new_seg["text"] = translations[j] if j < len(translations) else seg["text"]
            translated.append(new_seg)
        logger.info(f"[TRANSLATED] batch {i // batch_size + 1}: {len(batch)} segments")

    return translated


def _parse_numbered_translations(text: str, expected: int) -> List[str]:
    lines = []
    for line in text.strip().split("\n"):
        m = re.match(r"^\d+\.\s*(?:\[.*?\])?\s*(.+)$", line.strip())
        if m:
            lines.append(m.group(1).strip())
    while len(lines) < expected:
        lines.append("")
    return lines


def save_srt(srt_content: str, output_path: Path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(srt_content, encoding="utf-8")
    logger.info(f"[SAVED] {output_path.name}")
