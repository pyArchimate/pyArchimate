"""Integration tests for View.duplicate() round-trip."""

import tempfile
from pathlib import Path

from src.pyArchimate import ArchiType, Model


class TestViewDuplicateRoundTrip:
    """Test View.duplicate() round-trip: save, reload, verify structure."""

    def test_duplicate_roundtrip_archimate_format(self):
        """P2-T53: Duplicate view survives archimate round-trip."""
        # Create original model with 2 nodes and 1 connection
        model = Model("Test")
        elem1 = model.add(ArchiType.ApplicationComponent, "App1")
        elem2 = model.add(ArchiType.ApplicationComponent, "App2")
        model.add_relationship(source=elem1, target=elem2, rel_type="Association")

        view1 = model.add(ArchiType.View, "Original")
        n1 = view1.add(elem1, x=0, y=0, w=120, h=55)
        n2 = view1.add(elem2, x=200, y=0, w=120, h=55)
        view1.add_connection(ref=model.relationships[0], source=n1, target=n2)

        # Duplicate the view
        view2 = view1.duplicate("Duplicate")
        assert len(view2.nodes) == 2
        assert len(view2.conns) == 1

        # Save model to temporary .archimate file
        with tempfile.TemporaryDirectory() as tmpdir:
            archimate_path = Path(tmpdir) / "test.archimate"
            model.write(str(archimate_path))

            # Reload model from file
            reloaded = Model("Reloaded")
            reloaded.read(str(archimate_path))

            # Verify both views present with correct element counts
            assert len(reloaded.views) >= 2, "Should have at least 2 views after reload"

            views_by_name = {v.name: v for v in reloaded.views}
            assert "Original" in views_by_name, "Original view should exist after reload"
            assert "Duplicate" in views_by_name, "Duplicate view should exist after reload"

            orig = views_by_name["Original"]
            dup = views_by_name["Duplicate"]

            assert len(orig.nodes) == 2, "Original view should have 2 nodes"
            assert len(dup.nodes) == 2, "Duplicate view should have 2 nodes"
            assert len(orig.conns) == 1, "Original view should have 1 connection"
            assert len(dup.conns) == 1, "Duplicate view should have 1 connection"
