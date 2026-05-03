"""View auto-layout and auto-format module for pyArchimate.

This module provides layout algorithms and formatting utilities for ArchiMate views.
"""

import time
from typing import Any, Optional
from .core import LayoutConfig, LayoutResult
from .format import FormatService


def apply_layout(view: Any, config: Optional[LayoutConfig] = None) -> LayoutResult:
    """Apply layout algorithm to a view.

    Args:
        view: View object to layout
        config: Layout configuration (uses defaults if None)

    Returns:
        LayoutResult with layout metrics
    """
    if config is None:
        config = LayoutConfig()

    start_time = time.time()

    try:
        # Placeholder: algorithm registry will be populated in Phase 3
        elements_count = len(getattr(view, "nodes", []))
        connections_count = len(getattr(view, "edges", []))

        elapsed_ms = (time.time() - start_time) * 1000

        return LayoutResult(
            success=True,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used=config.algorithm,
            elements_processed=elements_count,
            connections_processed=connections_count,
            layout_time_ms=elapsed_ms,
            quality_metrics={},
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=False,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used=config.algorithm,
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            error_message=str(e),
        )


def apply_format(view: Any, config: Optional[LayoutConfig] = None) -> LayoutResult:
    """Apply formatting to standardize view appearance.

    Standardizes element sizes, fonts, and alignment without repositioning elements.

    Args:
        view: View object to format
        config: Layout configuration with formatting options

    Returns:
        LayoutResult with formatting metrics
    """
    if config is None:
        config = LayoutConfig()

    start_time = time.time()

    try:
        service = FormatService()
        format_stats = service.format_view(
            view,
            alignment=config.alignment,
            grid_size=getattr(config, "grid_size", 10.0),
            excluded_element_ids=set(config.excluded_element_ids),
        )

        variance_before = service.calculate_size_variance(view)
        elapsed_ms = (time.time() - start_time) * 1000

        return LayoutResult(
            success=True,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used="format",
            elements_processed=format_stats["formatted"],
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            quality_metrics={
                "formatted": format_stats["formatted"],
                "skipped": format_stats["skipped"],
                "total": format_stats["total"],
                "size_variance": variance_before["std_dev"],
                "errors": format_stats.get("errors", []),
            },
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=False,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used="format",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            error_message=str(e),
        )


def undo_layout(view: Any) -> LayoutResult:
    """Undo the last layout operation on a view.

    Uses the existing pyArchimate transaction/undo system.

    Args:
        view: View object to undo layout on

    Returns:
        LayoutResult indicating success/failure
    """
    start_time = time.time()

    try:
        # Placeholder: integration with pyArchimate transaction system in Phase 2
        elapsed_ms = (time.time() - start_time) * 1000

        return LayoutResult(
            success=True,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used="undo",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000
        return LayoutResult(
            success=False,
            view_id=getattr(view, "id", "unknown"),
            algorithm_used="undo",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=elapsed_ms,
            error_message=str(e),
        )


__all__ = [
    "apply_layout",
    "apply_format",
    "undo_layout",
    "LayoutConfig",
    "LayoutResult",
]
