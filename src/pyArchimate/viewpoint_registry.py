"""Registry of all 13 standard ArchiMate 3.x viewpoints."""
from __future__ import annotations

from .viewpoint import Viewpoint

STANDARD_VIEWPOINTS: list[Viewpoint] = [
    Viewpoint('stakeholder', 'Stakeholder Viewpoint',
              'Addresses stakeholder concerns and requirements'),
    Viewpoint('capability', 'Capability Viewpoint',
              'Shows capability maps and realisation'),
    Viewpoint('organization', 'Organization Viewpoint',
              'Shows the organizational structure'),
    Viewpoint('actor', 'Actor Cooperation Viewpoint',
              'Shows cooperation between business actors'),
    Viewpoint('technology', 'Technology Viewpoint',
              'Shows the technology infrastructure and platforms'),
    Viewpoint('physical', 'Physical Viewpoint',
              'Shows physical infrastructure and networks'),
    Viewpoint('service', 'Application Service Viewpoint',
              'Shows the application services and realisation'),
    Viewpoint('implementation', 'Implementation and Deployment Viewpoint',
              'Shows mapping of components to infrastructure'),
    Viewpoint('migration', 'Migration Viewpoint',
              'Shows transition between current and target states'),
    Viewpoint('strategy', 'Strategy Viewpoint',
              'Shows strategic goals, drivers, and principles'),
    Viewpoint('business', 'Business Process Viewpoint',
              'Shows business processes and their relationships'),
    Viewpoint('application', 'Application Cooperation Viewpoint',
              'Shows application component interactions'),
    Viewpoint('infrastructure', 'Infrastructure Viewpoint',
              'Shows the hardware and communication infrastructure'),
]

_REGISTRY: dict[str, Viewpoint] = {vp.id: vp for vp in STANDARD_VIEWPOINTS}


def get_viewpoint(slug: str) -> Viewpoint | None:
    """Return the Viewpoint for a canonical slug, or None if not found."""
    return _REGISTRY.get(slug)


def validate_viewpoint_slug(slug: str) -> None:
    """Raise ValueError if slug is not a recognised standard viewpoint."""
    if slug not in _REGISTRY:
        valid = ', '.join(sorted(_REGISTRY))
        raise ValueError(f"Unknown viewpoint slug '{slug}'. Valid slugs: {valid}")


__all__ = ['STANDARD_VIEWPOINTS', 'get_viewpoint', 'validate_viewpoint_slug']
