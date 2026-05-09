"""Unit tests for SVGExportService._clip_line_at_rectangle."""

import pytest

from src.pyArchimate.view.layout.export.svg_export import SVGExportService


@pytest.fixture
def svc() -> SVGExportService:
    return SVGExportService()


# Rectangle: x1=0, y1=0, x2=100, y2=80
RECT = (0.0, 0.0, 100.0, 80.0)


class TestClipLineAtRectangleExitFrom:
    """exit_from=True: find where line exits the rectangle."""

    def test_exits_right_edge(self, svc):
        # Line from inside (50,40) going right to (200,40)
        pt = svc._clip_line_at_rectangle((50, 40), (200, 40), RECT, exit_from=True)
        assert pt[0] == pytest.approx(100.0)
        assert pt[1] == pytest.approx(40.0)

    def test_exits_left_edge(self, svc):
        pt = svc._clip_line_at_rectangle((50, 40), (-100, 40), RECT, exit_from=True)
        assert pt[0] == pytest.approx(0.0)
        assert pt[1] == pytest.approx(40.0)

    def test_exits_top_edge(self, svc):
        pt = svc._clip_line_at_rectangle((50, 40), (50, -100), RECT, exit_from=True)
        assert pt[0] == pytest.approx(50.0)
        assert pt[1] == pytest.approx(0.0)

    def test_exits_bottom_edge(self, svc):
        pt = svc._clip_line_at_rectangle((50, 40), (50, 200), RECT, exit_from=True)
        assert pt[0] == pytest.approx(50.0)
        assert pt[1] == pytest.approx(80.0)

    def test_diagonal_exits_right(self, svc):
        # From center (50,40) going right+down at 45°, hits right edge at y=90 (outside)
        # but bottom edge at x=90 → exits bottom at (90, 80)
        pt = svc._clip_line_at_rectangle((50, 40), (150, 140), RECT, exit_from=True)
        # Line: y = 40 + (x-50), hits right x=100 at y=90 (outside), hits bottom y=80 at x=90
        assert pt[0] == pytest.approx(90.0)
        assert pt[1] == pytest.approx(80.0)

    def test_horizontal_line_exits_right(self, svc):
        pt = svc._clip_line_at_rectangle((10, 40), (300, 40), RECT, exit_from=True)
        assert pt[0] == pytest.approx(100.0)

    def test_vertical_line_exits_bottom(self, svc):
        pt = svc._clip_line_at_rectangle((50, 10), (50, 200), RECT, exit_from=True)
        assert pt[1] == pytest.approx(80.0)


class TestClipLineAtRectangleEnterFrom:
    """exit_from=False: find where line enters the rectangle."""

    def test_enters_left_edge_from_outside(self, svc):
        # Line from (-50, 40) going right to (150, 40) — enters at left edge x=0
        pt = svc._clip_line_at_rectangle((-50, 40), (150, 40), RECT, exit_from=False)
        assert pt[0] == pytest.approx(0.0)
        assert pt[1] == pytest.approx(40.0)

    def test_enters_top_edge_from_above(self, svc):
        pt = svc._clip_line_at_rectangle((50, -50), (50, 200), RECT, exit_from=False)
        assert pt[0] == pytest.approx(50.0)
        assert pt[1] == pytest.approx(0.0)

    def test_enters_right_edge_from_outside(self, svc):
        pt = svc._clip_line_at_rectangle((200, 40), (-50, 40), RECT, exit_from=False)
        assert pt[0] == pytest.approx(100.0)
        assert pt[1] == pytest.approx(40.0)


class TestClipLineAtRectangleDegenerateCases:
    """Edge cases."""

    def test_same_point_returns_that_point(self, svc):
        pt = svc._clip_line_at_rectangle((50, 40), (50, 40), RECT)
        assert pt == (50.0, 40.0)

    def test_horizontal_no_dy_skips_y_edges(self, svc):
        # dy=0 → top/bottom checks skipped, only left/right
        pt = svc._clip_line_at_rectangle((50, 40), (200, 40), RECT, exit_from=True)
        assert pt[1] == pytest.approx(40.0)

    def test_vertical_no_dx_skips_x_edges(self, svc):
        # dx=0 → left/right checks skipped, only top/bottom
        pt = svc._clip_line_at_rectangle((50, 40), (50, 200), RECT, exit_from=True)
        assert pt[0] == pytest.approx(50.0)
