from os import makedirs
import sys
import logging
from time import gmtime
from datetime import date

log_filename = "logs/vtc.log." + str(date.today())


def setup_logger(log_filename=log_filename, log_to_file=True):
    makedirs("logs", exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if log_to_file:
        logging.Formatter.converter = gmtime

        file_handler = logging.FileHandler(log_filename, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(name)s - %(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    return logger
