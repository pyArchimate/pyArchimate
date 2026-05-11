"""Tests for LayoutResult.warnings field."""

from src.pyArchimate.view.layout.core import LayoutResult


class TestLayoutResultWarnings:
    def test_warnings_field_exists_with_empty_default(self) -> None:
        result = LayoutResult(
            success=True,
            view_id="v1",
            algorithm_used="auto_layout",
            elements_processed=5,
            connections_processed=3,
            layout_time_ms=10.0,
        )
        assert hasattr(result, "warnings")
        assert result.warnings == []

    def test_warnings_can_be_appended(self) -> None:
        result = LayoutResult(
            success=True,
            view_id="v1",
            algorithm_used="auto_layout",
            elements_processed=0,
            connections_processed=0,
            layout_time_ms=0.0,
        )
        result.warnings.append("skipped connection abc")
        assert len(result.warnings) == 1
        assert result.warnings[0] == "skipped connection abc"

    def test_warnings_do_not_mutate_across_instances(self) -> None:
        r1 = LayoutResult(
            success=True, view_id="v1", algorithm_used="a",
            elements_processed=0, connections_processed=0, layout_time_ms=0.0,
        )
        r2 = LayoutResult(
            success=True, view_id="v2", algorithm_used="a",
            elements_processed=0, connections_processed=0, layout_time_ms=0.0,
        )
        r1.warnings.append("warn1")
        assert r2.warnings == [], "LayoutResult.warnings must not share state across instances"

    def test_warnings_accepts_explicit_list(self) -> None:
        result = LayoutResult(
            success=True,
            view_id="v1",
            algorithm_used="auto_route",
            elements_processed=2,
            connections_processed=1,
            layout_time_ms=5.0,
            warnings=["conn1 skipped", "conn2 skipped"],
        )
        assert len(result.warnings) == 2
