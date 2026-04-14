"""Tests for modern View/Node/Connection/Profile implementations.

These tests MUST FAIL until T021 replaces the legacy-facade shim in
src/pyArchimate/view.py with full modern implementations that have
zero _legacy imports.
"""
import inspect
import sys

import pytest


def test_view_importable():
    """View, Node, Connection, Profile are importable from src.pyArchimate.view."""
    from src.pyArchimate.view import Connection, Node, Profile, View

    assert View is not None
    assert Node is not None
    assert Connection is not None
    assert Profile is not None


def test_view_no_legacy_dependency():
    """view.py must not import from _legacy — fails until T021 is complete."""
    import src.pyArchimate.view as view_module

    source = inspect.getsource(view_module)
    assert "_legacy" not in source, (
        "view.py still imports from _legacy; replace the shim with modern "
        "implementations that have no _legacy dependency (T021)"
    )


def test_view_instantiates_without_legacy():
    """View must be importable with _legacy absent from sys.modules."""
    legacy_keys = [k for k in sys.modules if "_legacy" in k]
    backups = {k: sys.modules.pop(k) for k in legacy_keys}
    view_backup = sys.modules.pop("src.pyArchimate.view", None)

    try:
        from src.pyArchimate.view import View  # noqa: F401
    except ImportError as exc:
        pytest.fail(f"view.py cannot import without _legacy: {exc}")
    finally:
        sys.modules.update(backups)
        if view_backup is not None:
            sys.modules["src.pyArchimate.view"] = view_backup
