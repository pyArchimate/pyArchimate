"""Unit tests for apply_profile_styles helper."""

from typing import cast

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.helpers.diagram import apply_profile_styles
from src.pyArchimate.model import Model
from src.pyArchimate.view import View

COLOURS = {
    "Threat": "#ffcccc",
    "Control": "#bbdefb",
}


@pytest.fixture()
def model_with_view():
    m = Model("Test")
    v = cast(View, m.add(ArchiType.View, "V"))
    return m, v


# ---------------------------------------------------------------------------
# Increment 1 — empty view is a no-op
# ---------------------------------------------------------------------------


def test_apply_profile_styles_empty_view(model_with_view):
    _, v = model_with_view
    apply_profile_styles(v, COLOURS)  # must not raise


# ---------------------------------------------------------------------------
# Increment 2 — fill_color set on matched node
# ---------------------------------------------------------------------------


def test_apply_profile_styles_sets_fill_color(model_with_view):
    m, v = model_with_view
    elem = m.add(ArchiType.ApplicationComponent, "App")
    elem.set_profile("Threat")
    node = v.add(elem)
    apply_profile_styles(v, COLOURS)
    assert node.fill_color == "#ffcccc"


# ---------------------------------------------------------------------------
# Increment 3 — nodes with no profile are untouched
# ---------------------------------------------------------------------------


def test_apply_profile_styles_skips_no_profile(model_with_view):
    m, v = model_with_view
    elem = m.add(ArchiType.ApplicationComponent, "App")
    node = v.add(elem)
    node.fill_color = "#123456"
    apply_profile_styles(v, COLOURS)
    assert node.fill_color == "#123456"


# ---------------------------------------------------------------------------
# Increment 4 — nodes whose profile is not in mapping are untouched
# ---------------------------------------------------------------------------


def test_apply_profile_styles_skips_unmatched_profile(model_with_view):
    m, v = model_with_view
    elem = m.add(ArchiType.ApplicationComponent, "App")
    elem.set_profile("Unknown")
    node = v.add(elem)
    node.fill_color = "#abcdef"
    apply_profile_styles(v, COLOURS)
    assert node.fill_color == "#abcdef"


# ---------------------------------------------------------------------------
# Increment 5 — dict value applies line_color and font_color
# ---------------------------------------------------------------------------

RICH_COLOURS = {
    "Control": {
        "fill_color": "#bbdefb",
        "line_color": "#1565c0",
        "font_color": "#0d47a1",
    }
}


def test_apply_profile_styles_dict_fill_color(model_with_view):
    m, v = model_with_view
    elem = m.add(ArchiType.ApplicationComponent, "App")
    elem.set_profile("Control")
    node = v.add(elem)
    apply_profile_styles(v, RICH_COLOURS)
    assert node.fill_color == "#bbdefb"


def test_apply_profile_styles_dict_line_color(model_with_view):
    m, v = model_with_view
    elem = m.add(ArchiType.ApplicationComponent, "App")
    elem.set_profile("Control")
    node = v.add(elem)
    apply_profile_styles(v, RICH_COLOURS)
    assert node.line_color == "#1565c0"


def test_apply_profile_styles_dict_font_color(model_with_view):
    m, v = model_with_view
    elem = m.add(ArchiType.ApplicationComponent, "App")
    elem.set_profile("Control")
    node = v.add(elem)
    apply_profile_styles(v, RICH_COLOURS)
    assert node.font_color == "#0d47a1"


# ---------------------------------------------------------------------------
# Increment 7 — nested nodes (children of nodes, not direct view children)
# ---------------------------------------------------------------------------


def test_apply_profile_styles_child_node_styled(model_with_view):
    m, v = model_with_view
    parent_elem = m.add(ArchiType.ApplicationComponent, "Parent")
    child_elem = m.add(ArchiType.ApplicationComponent, "Child")
    child_elem.set_profile("Threat")
    parent_node = v.add(parent_elem)
    child_node = parent_node.add(child_elem)
    apply_profile_styles(v, COLOURS)
    assert child_node.fill_color == "#ffcccc"


def test_apply_profile_styles_grandchild_node_styled(model_with_view):
    m, v = model_with_view
    grandparent_elem = m.add(ArchiType.ApplicationComponent, "GP")
    parent_elem = m.add(ArchiType.ApplicationComponent, "P")
    grandchild_elem = m.add(ArchiType.ApplicationComponent, "GC")
    grandchild_elem.set_profile("Control")
    gp_node = v.add(grandparent_elem)
    p_node = gp_node.add(parent_elem)
    gc_node = p_node.add(grandchild_elem)
    apply_profile_styles(v, COLOURS)
    assert gc_node.fill_color == "#bbdefb"


# ---------------------------------------------------------------------------
# Increment 6 — importable from helpers package and public API
# ---------------------------------------------------------------------------


def test_apply_profile_styles_importable_from_helpers():
    from src.pyArchimate.helpers import apply_profile_styles as fn
    assert callable(fn)


def test_apply_profile_styles_importable_from_pyarchimate():
    from src.pyArchimate import apply_profile_styles as fn
    assert callable(fn)
