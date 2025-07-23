import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from time import gmtime
from pathlib import Path
from datetime import date

def setup_logger():
    log_dir_path = Path(__file__).resolve().parents[2] / "logs"
    log_dir_path.mkdir(parents=True, exist_ok=True)
    log_filename_info = log_dir_path / "info.log"
    log_filename_warning = log_dir_path / "warning.log"
    log_filename_error = log_dir_path / "error.log"
    formatter = logging.Formatter("%(name)s - %(asctime)s - %(levelname)s - %(message)s")
    suffix = "%Y-%m-%d"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.Formatter.converter = gmtime

    for level, filename in (
        (logging.INFO, log_filename_info),
        (logging.WARNING, log_filename_warning),
        (logging.ERROR, log_filename_error),
    ):
        handler = TimedRotatingFileHandler(
            filename, when="midnight", interval=1, backupCount=30, encoding="utf-8", utc=True)
        handler.suffix = suffix
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    return logger
