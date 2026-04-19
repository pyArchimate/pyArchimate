"""Tests that the writer registry lives in modern code."""
import pytest


def test_register_writer_importable_from_writers():
    """register_writer is importable from src.pyArchimate.writers."""
    from src.pyArchimate.writers import register_writer

    assert callable(register_writer)


def test_resolve_writer_importable_from_writers():
    """_resolve_writer is importable from src.pyArchimate.writers."""
    from src.pyArchimate.writers import _resolve_writer

    assert callable(_resolve_writer)


def test_single_writer_registry():
    """Writers registered via register_writer are visible to _resolve_writer."""
    from src.pyArchimate.writers import _resolve_writer, register_writer

    sentinel = lambda m, f: None  # noqa: E731
    register_writer("_test_sentinel", sentinel)
    result = _resolve_writer("_test_sentinel")
    assert result is sentinel


def test_register_writer_non_callable_raises():
    from src.pyArchimate.writers import register_writer
    with pytest.raises(TypeError):
        register_writer("bad", "not_callable")


def test_resolve_writer_with_callable_returns_it():
    from src.pyArchimate.writers import _resolve_writer
    fn = lambda m, f: None  # noqa: E731
    assert _resolve_writer(fn) is fn


def test_resolve_writer_with_int_key():
    from src.pyArchimate.writers import _resolve_writer
    from src.pyArchimate.enums import Writers
    # Writers.archimate is enum value 1 — resolve by int value
    result = _resolve_writer(Writers.archimate.value)
    assert callable(result)


def test_resolve_writer_with_unknown_string_raises():
    from src.pyArchimate.writers import _resolve_writer
    with pytest.raises(ValueError):
        _resolve_writer("totally_unknown_writer")


def test_resolve_writer_with_invalid_int_raises():
    from src.pyArchimate.writers import _resolve_writer
    with pytest.raises(ValueError):
        _resolve_writer(99999)  # not a valid Writers enum value — hits except ValueError branch
