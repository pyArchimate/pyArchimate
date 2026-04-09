"""Relationship module extracted from the legacy monolith."""

try:
    from ._legacy import Relationship
except ImportError:
    from _legacy import Relationship

__all__ = ["Relationship"]
