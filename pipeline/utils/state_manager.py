import json
from pathlib import Path
from typing import List

STATES = [
    "NOT_STARTED", "DOWNLOADED", "TRANSCRIBED", "SUBTITLED",
    "AUDIO_EDITED", "DUBBED", "SYNTHESIZED", "DONE",
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
