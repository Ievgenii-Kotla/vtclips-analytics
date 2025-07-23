import unittest
import os
import glob
from pathlib import Path

from src.vtc import vtc_logging
from unittest.mock import patch


class TestSetupLogger(unittest.TestCase):
    def setUp(self):
        # Clean up log files inside the 'logs' folder
        files = glob.glob("logs/*")
        print("Deleted files: ", files)
        for file in files:
            if os.path.isfile(file):
                os.remove(file)

    @patch("logging.StreamHandler.emit")
    def test_stream_handler_output(self, mock_emit):
        """ Basic test for streamHandler. """
        logger = vtc_logging.setup_logger()

        logger.debug("debug")
        mock_emit.assert_not_called()

        logger.info("info")
        log_record = mock_emit.call_args[0][0]
        self.assertEqual("info", log_record.getMessage())

        logger.warning("warning")
        log_record = mock_emit.call_args[0][0]
        self.assertEqual("warning", log_record.getMessage())

        logger.error("error")
        log_record = mock_emit.call_args[0][0]
        self.assertEqual("error", log_record.getMessage())

        logger.critical("critical")
        log_record = mock_emit.call_args[0][0]
        self.assertEqual('critical', log_record.getMessage())

        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def test_file_handler_output(self):
        """ Basic test for fileHandler. """
        logger = vtc_logging.setup_logger()
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")
        logger.critical("critical")

        path = Path(logger.handlers[0].baseFilename).parent
        with open(path / "info.log", "r") as file:
            lines = file.readlines()

        self.assertIn("info", lines[0])
        self.assertIn("warning", lines[1])
        self.assertIn("error", lines[2])
        self.assertIn("critical", lines[3])

        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


