import pytest
from pathlib import Path

from streeplijst2.log import FULL_LOG_FILE, WARN_ERR_LOG_FILE, FULL_LOG_DIR, getLogger

debug_message = 'Debug Test Message'
info_message = 'Info Test Message'
warn_message = 'Warning Test Message'
err_message = 'Error Test Message'
critical_message = 'Critical Test Message'


def test_log_init(test_app_logging, logs_dir_str):
    with test_app_logging.app_context():  # Open test_app_logging which has logging enabled.
        # Print various messages to the logger
        test_app_logging.logger.debug(debug_message)
        test_app_logging.logger.info(info_message)
        test_app_logging.logger.warning(warn_message)
        test_app_logging.logger.error(err_message)
        test_app_logging.logger.critical(critical_message)

        # Check if all messages also appear in the full log file
        full_log_file = Path(logs_dir_str) / FULL_LOG_DIR / FULL_LOG_FILE
        with open(full_log_file) as file:
            file_contents = file.read()
            assert debug_message in file_contents
            assert info_message in file_contents
            assert warn_message in file_contents
            assert err_message in file_contents
            assert critical_message in file_contents

        warn_err_log_file = Path(logs_dir_str) / WARN_ERR_LOG_FILE
        with open(warn_err_log_file) as file:
            file_contents = file.read()
            assert debug_message not in file_contents
            assert info_message not in file_contents
            assert warn_message in file_contents
            assert err_message in file_contents
            assert critical_message in file_contents


def test_logger(test_app_logging, logs_dir_str):
    with test_app_logging.app_context():  # Open test_app_logging which has logging enabled.
        # Print various messages to the logger
        logger = getLogger()
        logger.debug(debug_message)
        logger.info(info_message)
        logger.warning(warn_message)
        logger.error(err_message)
        logger.critical(critical_message)

        # Check if all messages also appear in the full log file
        full_log_file = Path(logs_dir_str) / FULL_LOG_DIR / FULL_LOG_FILE
        with open(full_log_file) as file:
            file_contents = file.read()
            assert debug_message in file_contents
            assert info_message in file_contents
            assert warn_message in file_contents
            assert err_message in file_contents
            assert critical_message in file_contents

        warn_err_log_file = Path(logs_dir_str) / WARN_ERR_LOG_FILE
        with open(warn_err_log_file) as file:
            file_contents = file.read()
            assert debug_message not in file_contents
            assert info_message not in file_contents
            assert warn_message in file_contents
            assert err_message in file_contents
            assert critical_message in file_contents