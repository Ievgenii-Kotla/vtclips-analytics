from os import makedirs
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from time import gmtime
from datetime import date

def setup_logger():
    makedirs("logs", exist_ok=True)
    log_filename_info = "logs/info"
    log_filename_warning = "logs/warning"
    log_filename_error = "logs/error"
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
