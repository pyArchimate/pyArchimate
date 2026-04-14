import logging

from src.pyArchimate.logger import log, log_set_level, log_to_file, log_to_stderr


def test_log_set_level_is_restorable():
    original_level = log.level
    log_set_level(logging.ERROR)
    try:
        assert log.level == logging.ERROR
    finally:
        log_set_level(original_level)


def test_log_to_file(tmp_path):
    log_file = tmp_path / "pyarchimate.log"
    log_to_file(str(log_file))
    log.warning("exercise logging handler")
    assert log_file.exists()
    for handler in list(log.handlers):
        if handler.name == 'file':
            log.removeHandler(handler)
            handler.close()


def test_log_to_stderr_adds_a_handler():
    before = len(log.handlers)
    log_to_stderr()
    assert len(log.handlers) == before + 1
    handler = log.handlers.pop()
    handler.close()
