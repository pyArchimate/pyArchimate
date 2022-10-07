import logging
from logging.handlers import RotatingFileHandler

log = logging.getLogger()
log.setLevel(logging.WARNING)
formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)


def log_set_level(lvl):
    """
    Change the logging level for all handlers at once
    :param lvl: logging level
    :type lvl: logging.LEVEL enumeration
    """
    log.setLevel(lvl)
    for h in log.handlers:
        if h.name == 'file':
            continue
        h.setLevel(lvl)


def log_to_file(log_file):
    """
    Add a log handler to save log to file
    :param log_file: path to the log file
    :type log_file: str

    """
    if log_file is not None:
        handler_file = RotatingFileHandler(
            log_file,
            mode='a',
            maxBytes=200000,
            backupCount=9,
            encoding='UTF-8',
            delay=True
        )
        handler_file.setLevel(logging.WARNING)
        handler_file.setFormatter(formatter)
        handler_file.name = 'file'
        log.addHandler(handler_file)


def log_to_stderr():
    """
    Add a logging handler to the standard error output

    """
    handler_stdout = logging.StreamHandler()
    handler_stdout.setLevel(log.level)
    handler_stdout.setFormatter(formatter)
    handler_stdout.name = 'stderr'
    log.addHandler(handler_stdout)


