"""Element module extracted from the legacy monolith."""

try:
    from ._legacy import Element
except ImportError:
    from _legacy import Element

__all__ = ["Element"]
