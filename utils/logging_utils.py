# logging_config.py
import inspect
import logging
import os
import shutil
from datetime import datetime

from utils.config import FilesSettings, LoggingSettings

LOGS_DIRECTORY = str(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    FilesSettings.LOGS_FOLDER_NAME
))


def clean_logs():
    if os.path.exists(LOGS_DIRECTORY):
        shutil.rmtree(LOGS_DIRECTORY)  # Delete all existing logs
    os.makedirs(LOGS_DIRECTORY)


def configure_logger(class_name, child_dir, instance_id) -> logging.Logger:
    """
    Configure and return a logger for `class_name`.
    `child_dir`   : The directory under logs/ where the file will go (e.g. "miner").
    `instance_id` : Unique ID (e.g. timestamp) to distinguish the file, e.g. "20250104_130045".

    The resulting log file path will be:
        logs/<child_dir>/<child_dir><instance_id>.log

    The logger's name is the class name (e.g. "Miner", "User").
    """

    # Build the logger name
    logger_name = class_name + instance_id

    # Get (or create) the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(LoggingSettings.LOGGING_LEVEL)  # Or any level you prefer

    # If this logger already has handlers, return it as is
    # (so we don't add multiple FileHandlers to the same logger)
    if logger.handlers:
        return logger

    # Ensure directory exists: logs/<child_dir>/
    directory_path = os.path.join(LOGS_DIRECTORY, child_dir.lower())
    os.makedirs(directory_path, exist_ok=True)

    # Build the log file path
    instance_id = instance_id or datetime.now().strftime("-%H-%M-%S")
    log_filename = f"{instance_id}.log"
    log_filepath = os.path.join(directory_path, log_filename)

    # Create the FileHandler
    fh = logging.FileHandler(log_filepath)
    fh.setLevel(logging.DEBUG)

    # Build a formatter that includes the logger name as your "class" tag
    # e.g. 2025-01-04 13:15:00,123 - INFO - [Miner] - Some log message
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(class)s] - %(message)s"
    )
    fh.setFormatter(formatter)

    # Add the file handler to this logger
    logger.addHandler(fh)

    # add filter to display to class name.
    class CustomFilter(logging.Filter):
        def filter(self, record):
            record.__dict__['class'] = class_name  # Set 'class' attribute
            return True

    logger.addFilter(CustomFilter())

    return logger


def setup_basic_logger(name=None, root_directory=None, level=logging.DEBUG):
    """
    Configures and returns a logger that mirrors the structure of the source file in the logs directory.

    :param name: Optional, the name of the logger and log file (default is the source file name).
    :param root_directory: Optional, a specified root directory for logs (default is relative to logging_utils).
    :param level: The logging level (default is DEBUG).
    :return: Configured logger object.
    """
    # Determine the root directory for logs
    if root_directory is None:
        root_directory = os.path.join(LOGS_DIRECTORY, LoggingSettings.BASIC_LOGS)

    # Get the calling file's absolute path and calculate its relative path within the project
    stack = inspect.stack()
    caller_file_path = os.path.abspath(stack[1].filename)  # Absolute path of the file that called setup_logger
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Project root
    relative_path = os.path.relpath(caller_file_path, start=project_root)  # Relative to the project root
    relative_dir = os.path.dirname(relative_path)  # Directory of the caller file within the project

    # Set the default logger name to the calling file's name (without extension)
    if name is None:
        name = os.path.splitext(os.path.basename(caller_file_path))[0]

    # Create the corresponding directory in the logs folder
    log_dir = os.path.join(root_directory, relative_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Define the log file path
    log_file = os.path.join(log_dir, f"{name}.log")

    # Create and configure the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if LoggingSettings.REWRITE:
        # Clear the log file content by opening it in write mode
        with open(log_file, 'w'):
            pass

    # Check if the logger already has handlers to prevent duplicates
    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Create a formatter and attach it to the handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(lineno)d - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

    return logger
