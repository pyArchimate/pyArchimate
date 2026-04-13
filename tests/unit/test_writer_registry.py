"""Tests that the writer registry lives in modern code."""


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
