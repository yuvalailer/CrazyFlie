import logging, os, sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")  # Set the logging format
LOG_FOLDER = "log"
LOG_FILE = "{}/crazy_game.log".format(LOG_FOLDER)

DEFAULT_LOGGING_LEVEL = logging.DEBUG

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    if not os.path.isdir(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", utc=True)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def set_default_logging_level(logging_level):
    global DEFAULT_LOGGING_LEVEL
    DEFAULT_LOGGING_LEVEL = logging_level


def get_logger(logger_name, logging_level=None):
    logger = logging.getLogger(logger_name)  # debug(), info(), warning(), error(), exception(), critical()
    logging_level = DEFAULT_LOGGING_LEVEL if not logging_level else logging_level
    logger.setLevel(logging_level)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False  # With this pattern, it's rarely necessary to propagate the error up to parent
    return logger


if __name__ == "__main__":
    print("This is not the way to do it...")
