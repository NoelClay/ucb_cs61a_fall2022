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


def test_state_index_ordering():
    from pipeline.utils.state_manager import state_index
    assert state_index("NOT_STARTED") < state_index("DOWNLOADED")
    assert state_index("DOWNLOADED") < state_index("TRANSCRIBED")
    assert state_index("TRANSCRIBED") < state_index("DONE")


def test_is_before(tmp_path):
    from pipeline.utils.state_manager import StateManager
    sm = StateManager(tmp_path / "progress.json")
    sm.set_state("lecture_01", "TRANSCRIBED")
    assert sm.is_before("lecture_01", "SUBTITLED")
    assert not sm.is_before("lecture_01", "DOWNLOADED")
    assert not sm.is_before("lecture_01", "TRANSCRIBED")


def test_list_by_state(tmp_path):
    from pipeline.utils.state_manager import StateManager
    sm = StateManager(tmp_path / "progress.json")
    sm.set_state("lecture_01", "DONE")
    sm.set_state("lecture_02", "DOWNLOADED")
    assert "lecture_01" in sm.list_by_state("DONE")
    assert "lecture_02" not in sm.list_by_state("DONE")


def test_invalid_state_raises(tmp_path):
    from pipeline.utils.state_manager import StateManager
    sm = StateManager(tmp_path / "progress.json")
    try:
        sm.set_state("lecture_01", "INVALID_STATE")
        assert False, "Should have raised"
    except AssertionError:
        pass
