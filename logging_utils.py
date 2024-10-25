import logging
import os
ROOT_DIRECTORY = "..\\logs\\"


def setup_logger(name, level=logging.DEBUG):
    """
    Configures and returns a logger.

    :param name: The name of the logger (typically the file name).
    :param level: The logging level (default is DEBUG).
    :return: Configured logger object.
    """
    if not os.path.exists(ROOT_DIRECTORY):
        os.makedirs(ROOT_DIRECTORY)
    log_file = ROOT_DIRECTORY + name + ".log"
    logger = logging.getLogger(name)
    logger.setLevel(level)

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
