"""Unit tests for View.duplicate() method."""

import pytest

from src.pyArchimate import ArchiType, Model


class TestViewDuplicate:
    """Test View.duplicate() deep copy functionality."""

    @pytest.fixture
    def model_with_view(self):
        """Create model with 2 nodes and 1 connection."""
        model = Model("Test")
        elem1 = model.add(ArchiType.ApplicationComponent, "App1")
        elem2 = model.add(ArchiType.ApplicationComponent, "App2")
        model.add_relationship(source=elem1, target=elem2, rel_type="Association")

        view = model.add(ArchiType.View, "Original")
        n1 = view.add(elem1, x=0, y=0, w=120, h=55)
        n2 = view.add(elem2, x=200, y=0, w=120, h=55)
        view.add_connection(ref=model.relationships[0], source=n1, target=n2)

        return model, view

    def test_duplicate_node_count_equal(self, model_with_view):
        """P2-T51(a): Duplicated view has same node count."""
        _model, view = model_with_view
        dup = view.duplicate("copy")
        assert len(dup.nodes) == len(view.nodes)

    def test_duplicate_connection_count_equal(self, model_with_view):
        """P2-T51(b): Duplicated view has same connection count."""
        _model, view = model_with_view
        dup = view.duplicate("copy")
        assert len(dup.conns) == len(view.conns)

    def test_duplicate_waypoint_deep_copy(self, model_with_view):
        """P2-T51(c): Waypoint mutations in copy don't affect original."""
        _model, view = model_with_view
        dup = view.duplicate("copy")
        # Mutate a waypoint in the copy
        if dup.conns:
            orig_waypoints = list(view.conns[0].bendpoints) if view.conns[0].bendpoints else []
            dup.conns[0]._bendpoints = [object()]  # Force mutation
            # Original should be unchanged
            assert view.conns[0].bendpoints == orig_waypoints

    def test_duplicate_name_override(self, model_with_view):
        """P2-T51(d): Name override parameter works."""
        _model, view = model_with_view
        dup = view.duplicate("NewName")
        assert dup.name == "NewName"

    def test_duplicate_default_name_suffix(self, model_with_view):
        """P2-T51(e): Default name appends ' (copy)' suffix."""
        _model, view = model_with_view
        dup = view.duplicate()
        assert dup.name == f"{view.name} (copy)"

    def test_duplicate_registered_in_model(self, model_with_view):
        """P2-T51(f): Duplicate is registered in model.views."""
        model, view = model_with_view
        orig_count = len(model.views)
        dup = view.duplicate("copy")
        assert len(model.views) == orig_count + 1
        assert dup in model.views

    def test_duplicate_empty_view(self):
        """P2-T52(a): Empty view can be duplicated."""
        model = Model("Test")
        view = model.add(ArchiType.View, "Empty")
        dup = view.duplicate()
        assert len(dup.nodes) == 0
        assert len(dup.conns) == 0

    def test_duplicate_view_no_connections(self):
        """P2-T52(b): View with nodes but no connections can be duplicated."""
        model = Model("Test")
        elem = model.add(ArchiType.ApplicationComponent, "App")
        view = model.add(ArchiType.View, "NoConns")
        view.add(elem, x=0, y=0, w=120, h=55)
        dup = view.duplicate()
        assert len(dup.nodes) == 1
        assert len(dup.conns) == 0

    def test_duplicate_of_duplicate(self, model_with_view):
        """P2-T52(c): Duplicating a duplicate works."""
        _model, view = model_with_view
        dup1 = view.duplicate("copy1")
        dup2 = dup1.duplicate("copy2")
        assert len(dup2.nodes) == len(view.nodes)
        assert len(dup2.conns) == len(view.conns)

    def test_duplicate_zero_waypoint_connections(self):
        """P2-T52(d): Connections with zero waypoints can be duplicated."""
        model = Model("Test")
        elem1 = model.add(ArchiType.ApplicationComponent, "App1")
        elem2 = model.add(ArchiType.ApplicationComponent, "App2")
        model.add_relationship(source=elem1, target=elem2, rel_type="Association")

        view = model.add(ArchiType.View, "Test")
        n1 = view.add(elem1, x=0, y=0, w=120, h=55)
        n2 = view.add(elem2, x=200, y=0, w=120, h=55)
        view.add_connection(ref=model.relationships[0], source=n1, target=n2)

        dup = view.duplicate()
        assert len(dup.conns) == 1

    def test_duplicate_model_none_raises_error(self):
        """P2-T52(e): Duplicate raises ValueError if view.model is None."""
        model = Model("Test")
        view = model.add(ArchiType.View, "Test")
        # Manually sever the model connection to simulate orphan view
        view.model = None

        with pytest.raises(ValueError, match="View has no parent model"):
            view.duplicate()
