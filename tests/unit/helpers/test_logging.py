from src.pyArchimate.helpers.logging import log_set_level as helper_log_set_level
from src.pyArchimate.helpers.logging import log_to_file as helper_log_to_file
from src.pyArchimate.helpers.logging import log_to_stderr as helper_log_to_stderr
from src.pyArchimate.logger import log_set_level, log_to_file, log_to_stderr


def test_logging_helpers_reexport_logger_functions():
    assert helper_log_set_level is log_set_level
    assert helper_log_to_file is log_to_file
    assert helper_log_to_stderr is log_to_stderr
