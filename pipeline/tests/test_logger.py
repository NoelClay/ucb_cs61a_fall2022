from pathlib import Path


def test_logger_creates_log_file(tmp_path):
    from pipeline.utils.logger import get_logger
    logger = get_logger("test", log_dir=tmp_path)
    logger.info("test message")
    log_files = list(tmp_path.glob("*.log"))
    assert len(log_files) == 1


def test_logger_writes_to_stdout(tmp_path, capsys):
    from pipeline.utils.logger import get_logger
    logger = get_logger("test_stdout", log_dir=tmp_path)
    logger.info("hello world")
    captured = capsys.readouterr()
    assert "hello world" in captured.out


def test_logger_same_name_returns_same_instance(tmp_path):
    from pipeline.utils.logger import get_logger
    a = get_logger("same_name", log_dir=tmp_path)
    b = get_logger("same_name", log_dir=tmp_path)
    assert a is b
