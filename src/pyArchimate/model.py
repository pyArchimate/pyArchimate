"""Model module extracted from the legacy monolith."""

try:
    from ._legacy import Model
except ImportError:
    from _legacy import Model

__all__ = ["Model"]
