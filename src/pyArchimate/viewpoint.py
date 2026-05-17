"""Viewpoint entity and association classes."""

from dataclasses import dataclass


@dataclass
class Viewpoint:
    """An ArchiMate 3.x viewpoint definition (immutable registry entry).

    :param id: Canonical string slug (e.g. 'stakeholder', 'technology')
    :param name: Human-readable viewpoint name
    :param description: Brief description of the viewpoint's purpose
    """

    id: str
    name: str
    description: str


__all__ = ["Viewpoint"]
