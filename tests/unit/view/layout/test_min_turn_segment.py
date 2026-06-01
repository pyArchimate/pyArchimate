"""Tests for geometry utilities including _enforce_min_turn_segment (FR-024, SC-012).

Verify that segments following 90° bends are enforced to minimum length,
except the terminal arrival segment.
"""

from src.pyArchimate.view.layout.routing.segment_separation import _enforce_min_turn_segment
from src.pyArchimate.view.layout.utils.geometry import Point


class TestEnforceMinTurnSegment40px:
    """Default min_turn_segment is 40px per FR-024."""

    def test_l_shape_short_post_turn_extended_to_40px(self) -> None:
        """L-shape with short middle post-turn segment extended to 40px.

        Path: (0,0) → (100,0) [horizontal 100px]
                    → (100,30) [vertical 30px—short post-turn, NOT terminal]
                    → (150,30) [horizontal—terminal, not extended]

        After enforce: middle segment extended to 40px:
          (0,0) → (100,0) → (100,40) → (150,40)
        """
        waypoints = [
            Point(0, 0),
            Point(100, 0),
            Point(100, 30),  # First L-turn post-turn — 30px, should extend to 40px
            Point(150, 30),  # Terminal segment — should NOT be extended even if short
        ]

        result = _enforce_min_turn_segment(waypoints, min_len=40)

        assert len(result) == 4
        assert result[0] == Point(0, 0)
        assert result[1] == Point(100, 0)
        # First L-turn post-turn (not terminal) should extend to 40px
        assert result[2] == Point(100, 40), f"First post-turn segment should extend to 40px, got {result[2]}"
        # Second L-turn IS terminal — should NOT be extended
        assert result[3] == Point(150, 30), f"Terminal segment should NOT be extended, got {result[3]}"

    def test_conforming_path_unchanged(self) -> None:
        """Path with post-turn segment ≥ 40px unchanged."""
        waypoints = [
            Point(0, 0),
            Point(100, 0),
            Point(100, 50),  # 50px post-turn — already good
        ]

        result = _enforce_min_turn_segment(waypoints, min_len=40)

        # Should be unchanged
        assert result == waypoints, "Conforming path should remain unchanged"

    def test_consecutive_l_turns_first_enforced(self) -> None:
        """First L-turn enforced, second (terminal) L-turn NOT enforced.

        Path: (0,0) → (100,0) → (100,30) → (200,30) → (200,50)
        First L-turn post-turn: 30px (short—should extend)
        Second L-turn: terminal (should NOT extend even if short)

        After enforce: (0,0) → (100,0) → (100,40) → (200,40) → (200,50)
        """
        waypoints = [
            Point(0, 0),
            Point(100, 0),
            Point(100, 30),  # First post-turn — 30px, should extend to 40px
            Point(200, 30),  # Intermediate
            Point(200, 50),  # Terminal L-turn — do NOT extend
        ]

        result = _enforce_min_turn_segment(waypoints, min_len=40)

        # First L-turn: extends y=30 → y=40 at point 2
        assert result[2] == Point(100, 40), f"First post-turn should extend to 40px, got {result[2]}"
        # Intermediate point stays where it is (not moved by first extension)
        assert result[3] == Point(200, 30), f"Intermediate point unchanged, got {result[3]}"
        # Terminal segment: unchanged (do not extend short final segment)
        assert result[4] == Point(200, 50), f"Terminal segment should remain at 50, got {result[4]}"

    def test_terminal_arrival_segment_not_extended(self) -> None:
        """Terminal arrival segment (last segment) is NOT extended.

        Path: (0,0) → (100,0) → (100,30) [terminal—10px post-turn but do NOT extend]

        After enforce: (0,0) → (100,0) → (100,30) [unchanged]
        """
        waypoints = [
            Point(0, 0),
            Point(100, 0),
            Point(100, 30),  # Last segment — skip enforcement even if < 40px
        ]

        result = _enforce_min_turn_segment(waypoints, min_len=40)

        # Terminal segment should NOT be extended
        assert result[2] == Point(100, 30), f"Terminal segment should NOT be extended; got {result[2]}"

    def test_single_segment_path_is_noop(self) -> None:
        """Single-segment path (no bends) is no-op."""
        waypoints = [
            Point(0, 0),
            Point(100, 0),  # Only one segment — no post-turn to enforce
        ]

        result = _enforce_min_turn_segment(waypoints, min_len=40)

        # Should be unchanged (no bends)
        assert result == waypoints, "Single segment path should be unchanged"


class TestEnforceMinTurnSegmentCustom:
    """Custom min_turn_segment values are honored."""

    def test_custom_20px_floor_not_40px(self) -> None:
        """Custom min_turn_segment=20 enforces 20px, not 40px (for non-terminal L-turns).

        Path: (0,0) → (100,0) → (100,15) → (200,15)
        First L-turn post-turn: 15px (should extend to 20px with min_len=20)
        Terminal segment: 0-100px horizontal (not extended)

        With min_turn_segment=20:
        Expected: (0,0) → (100,0) → (100,20) → (200,20) [20px floor, not 40px]
        """
        waypoints = [
            Point(0, 0),
            Point(100, 0),
            Point(100, 15),  # 15px post-turn — should extend to 20px
            Point(200, 15),  # Terminal — not extended
        ]

        result = _enforce_min_turn_segment(waypoints, min_len=20)

        # Should extend to 20px (not 40px) — respects custom min_len
        assert result[2] == Point(100, 20), f"With min_len=20, should extend to 20px; got {result[2]}"
        # Terminal segment: remains at original position
        assert result[3] == Point(200, 15), f"Terminal segment should remain unchanged; got {result[3]}"
