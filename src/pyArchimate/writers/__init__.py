"""
Writer registry helpers extracted from the legacy module.
"""

from ..enums import Writers

try:  # legacy enum compatibility
    from .._legacy import Writers as LegacyWriters  # type: ignore
except Exception:
    LegacyWriters = None

_writer_registry = {}
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
    from .archimateWriter import archimate_writer
    from .archiWriter import archi_writer
    from .csvWriter import csv_writer

    register_writer(Writers.archimate, archimate_writer)
    register_writer(Writers.archi, archi_writer)
    register_writer(Writers.csv, csv_writer)
    _default_writers_initialized = True


def _resolve_writer(writer):
    if callable(writer):
        return writer

    _ensure_default_writers()
    key = writer
    if isinstance(writer, Writers):
        key = writer
    elif LegacyWriters and isinstance(writer, LegacyWriters):
        try:
            key = Writers(writer.value)
        except Exception:
            key = writer
    elif isinstance(writer, str):
        try:
            key = Writers[writer]
        except KeyError:
            pass
    elif isinstance(writer, int):
        try:
            key = Writers(writer)
        except ValueError:
            pass

    if key in _writer_registry:
        return _writer_registry[key]

    raise ValueError(f"Unknown writer '{writer}'. Registered writers: {list(_writer_registry.keys())}")


__all__ = ["register_writer", "_resolve_writer", "_ensure_default_writers"]
