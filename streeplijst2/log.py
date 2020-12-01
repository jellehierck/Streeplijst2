from logging import FileHandler, Formatter, getLogger, DEBUG, WARNING
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from pathlib import Path
import os
# from flask import Flask
from flask.logging import default_handler as flask_default_handler

LOGS_DIR = 'logs'
FULL_LOG_DIR = 'full'
FULL_LOG_FILE = 'full.log'
WARN_ERR_LOG_FILE = 'warn_err.log'
DEFAULT_FORMAT_STR = '[%(asctime)s] %(levelname)s %(name)s in %(module)s: %(message)s'

# All logs are handled by the root logger of logging.py. Calling streeplijst2.log.getLogger() in another module lets you
# log with all coupled handlers.
getLogger = getLogger


def init_app(app, config: dict = None) -> None:
    """
    Initialize the logging for the flask app.

    :param app: Flask app to initialize.
    :param config: When passed in, use this configuration.
    """
    # Do not change logging when the DISABLE_LOGGING flag is set to True
    if config is not None and 'DISABLE_LOGGING' in config and config['DISABLE_LOGGING'] is True:
        return

    # Disable the default handler and set the level to DEBUG
    app.logger.removeHandler(flask_default_handler)
    app.logger.setLevel(DEBUG)

    # Check the logging file paths.
    logs_dir = Path(app.instance_path) / LOGS_DIR
    full_log_dir = logs_dir / FULL_LOG_DIR
    full_log_file = full_log_dir / FULL_LOG_FILE
    warn_err_log_file = logs_dir / WARN_ERR_LOG_FILE

    # Check if the logging paths need to be changed due to the passed config
    if config is not None:
        # Set any of the fields from the config dict. If they do not exist in config, use the default instead.
        logs_dir = Path(str(config.get('LOGS_DIR', logs_dir)))
        full_log_dir = config.get('FULL_LOG_DIR', logs_dir / FULL_LOG_DIR)
        full_log_file = config.get('FULL_LOG_FILE', full_log_dir / FULL_LOG_FILE)
        warn_err_log_file = config.get('WARN_ERR_LOG_FILE', logs_dir / WARN_ERR_LOG_FILE)

    # Create the directories if they do not exist yet
    try:
        os.makedirs(logs_dir)
        os.makedirs(full_log_dir)
    except OSError:
        pass

    # Configure the different log handlers
    # The full logs are stored per day. A max of 30 days are kept.
    full_log_file_handler = TimedRotatingFileHandler(full_log_file, when='midnight', backupCount=30)
    full_log_file_handler.setLevel(DEBUG)

    # TODO: Change warn_err_log_file_handler to RotatingFileHandler to store files > 4MB in size
    warn_err_log_file_handler = FileHandler(warn_err_log_file)
    warn_err_log_file_handler.setLevel(WARNING)

    # Configure and set the formatter
    default_formatter = Formatter(DEFAULT_FORMAT_STR)
    full_log_file_handler.setFormatter(default_formatter)
    warn_err_log_file_handler.setFormatter(default_formatter)

    # Change the default handler added by Flask
    flask_default_handler.setFormatter(default_formatter)

    # Add all different loggers to the root logger
    root_logger = getLogger()
    root_logger.setLevel(DEBUG)
    root_logger.addHandler(full_log_file_handler)
    root_logger.addHandler(warn_err_log_file_handler)
    root_logger.addHandler(flask_default_handler)
    # app.logger.addHandler(full_log_file_handler)
    # app.logger.addHandler(warn_err_log_file_handler)
    # app.logger.addHandler(flask_default_handler)

    # Notify that the loggers have started
    app.logger.warning('Loggers initialized. Output in %s' % str(logs_dir))

    # TODO: Do something with the config (maybe remove the default flask handler entirely as it can break the app)
