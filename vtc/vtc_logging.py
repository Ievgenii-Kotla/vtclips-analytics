from os import makedirs
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from time import gmtime


def setup_logger(log_filename="logs/vtc.log", log_to_file=True):
    makedirs("logs", exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if log_to_file:
        logging.Formatter.converter = gmtime

        file_handler = TimedRotatingFileHandler(
            log_filename, when='D', interval=1, backupCount=31, encoding="utf-8", utc=True)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(name)s - %(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        file_handler.doRollover()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    return logger
