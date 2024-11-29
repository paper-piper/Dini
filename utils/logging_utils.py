import logging
import os
from utils.config import LoggingSettings

# Calculate the absolute path of the logs directory based on this file's location
ROOT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")


def setup_logger(name, root_directory=None, level=logging.DEBUG, test_logger=False):
    """
    Configures and returns a logger.

    :param name: The name of the logger (typically the file name).
    :param root_directory: Optional, a specified root directory.
    :param level: The logging level (default is DEBUG).
    :param test_logger: is the logger from a test file (should be in another directory)
    :return: Configured logger object.
    """
    if root_directory is None:
        root_directory = ROOT_DIRECTORY
    if test_logger:
        root_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..\\tests", "logs")
    if not os.path.exists(root_directory):
        os.makedirs(root_directory)
    log_file = os.path.join(root_directory, f"{name}.log")
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if LoggingSettings.REWRITE:
        # Clear the log file content by opening it in write mode
        with open(log_file, 'w'):
            pass

    # Check if the logger already has handlers to prevent duplicate handlers
    if not logger.hasHandlers():
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Create a formatter and attach it to the handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

    return logger
