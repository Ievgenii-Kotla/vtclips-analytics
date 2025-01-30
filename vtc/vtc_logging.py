from os import makedirs
import logging
from logging.handlers import TimedRotatingFileHandler
from time import gmtime


def setup_logger(log_filename="vtc.log"):
    logger = logging.getLogger("vtc_logger")
    logger.setLevel(logging.INFO)

    logging.Formatter.converter = gmtime
    file_handler = TimedRotatingFileHandler(
        log_filename, when='D', interval=1, backupCount=31, encoding="utf-8", utc=True)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


makedirs("logs", exist_ok=True)
logger = setup_logger()
