# ruff: noqa: N999  # legacy module name preserved for API compatibility
"""
Writer registry helpers extracted from the legacy module.
"""

from collections.abc import Callable
from typing import Any

from ..enums import Writers

_writer_registry: dict[Writers, Callable[..., Any]] = {}
_default_writers_initialized = False


def register_writer(key, writer_callable):
    if not callable(writer_callable):
        raise TypeError('writer must be callable')
    _writer_registry[key] = writer_callable


def _ensure_default_writers():
    global _default_writers_initialized
    if _default_writers_initialized:
        return
    # Import lazily to avoid circular imports during Model module load
    from .archimateWriter import (
        archimate_writer,  # noqa: PLC0415  # circular: writers import model types at module level
    )
    from .archiWriter import archi_writer  # noqa: PLC0415  # circular: writers import model types at module level
    from .csvWriter import csv_writer  # noqa: PLC0415  # circular: writers import model types at module level

    register_writer(Writers.archimate, archimate_writer)
    register_writer(Writers.archi, archi_writer)
    register_writer(Writers.csv, csv_writer)
    _default_writers_initialized = True


def _detect_writer_from_extension(file_path):
    """Auto-detect writer based on file extension.

    Args:
        file_path: Path to file being written

    Returns:
        Writers enum value (archimate for .archimate, archi for .xml, default archimate)
    """
    if not file_path:
        return Writers.archimate

    file_path_lower = str(file_path).lower()
    if file_path_lower.endswith('.archimate'):
        return Writers.archi
    elif file_path_lower.endswith('.xml'):
        return Writers.archimate

    return Writers.archimate


def _resolve_writer(writer):
    if callable(writer):
        return writer

    _ensure_default_writers()
    key = writer
    if isinstance(writer, Writers):
        key = writer
    elif isinstance(writer, str):
        try:
            key = Writers[writer]
        except KeyError:  # noqa: S110
            pass
    elif isinstance(writer, int):
        try:
            key = Writers(writer)
        except ValueError:  # noqa: S110
            pass

    if key in _writer_registry:
        return _writer_registry[key]

    raise ValueError(f"Unknown writer '{writer}'. Registered writers: {list(_writer_registry.keys())}")


__all__ = ["register_writer", "_resolve_writer", "_ensure_default_writers", "_detect_writer_from_extension"]
