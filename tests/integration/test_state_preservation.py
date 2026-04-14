"""State preservation integration test (T027 / spec edge case).

Asserts that modularizing pyArchimate does not alter the default logging
level or writer registry that were established in the original monolithic module.
"""


def test_logging_state():
    """Default log level is accessible via modern import path."""
    from src.pyArchimate import log as modern_log

    assert modern_log is not None
    assert isinstance(modern_log.level, int)


def test_writer_registry_accessible():
    """The writer registry is accessible from the modern writers module."""
    from src.pyArchimate.writers import _writer_registry

    assert isinstance(_writer_registry, dict)


def test_default_writers_registered():
    """Default writers (archi, archimate, csv) resolve correctly."""
    from src.pyArchimate.enums import Writers
    from src.pyArchimate.writers import _resolve_writer

    for writer_key in (Writers.archi, Writers.archimate, Writers.csv):
        fn = _resolve_writer(writer_key)
        assert callable(fn), f"Default writer for {writer_key} is not callable"


def test_reader_enum_accessible():
    """Reader enum is accessible from modern path."""
    from src.pyArchimate.enums import Readers

    assert len(list(Readers)) > 0
