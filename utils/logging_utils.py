import logging
import os
import inspect
from utils.config import LoggingSettings, FilesSettings

# Root directory for logs
ROOT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", FilesSettings.LOGS_FOLDER_NAME)


def setup_logger(name=None, root_directory=None, level=logging.DEBUG):
    """
    Configures and returns a logger that mirrors the structure of the source file in the logs directory.

    :param name: Optional, the name of the logger and log file (default is the source file name).
    :param root_directory: Optional, a specified root directory for logs (default is relative to logging_utils).
    :param level: The logging level (default is DEBUG).
    :return: Configured logger object.
    """
    # Determine the root directory for logs
    if root_directory is None:
        root_directory = ROOT_DIRECTORY

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
