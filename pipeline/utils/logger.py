import logging
import sys
from datetime import datetime
from pathlib import Path


def get_logger(name: str, log_dir: Path = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{name}_{datetime.now():%Y%m%d}.log"
        fh = logging.FileHandler(log_file)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
