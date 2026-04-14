"""Tests that core modules are independent of _legacy.

These tests MUST FAIL until T022 removes the _legacy callbacks from
model.py, element.py, and relationship.py and inverts the registration
so that _legacy imports from the modern modules (not vice versa).
"""
import importlib
import inspect
import sys

import pytest

_LEGACY_KEY = "src.pyArchimate._legacy"
_PKG_KEY = "src.pyArchimate"

_INVERSION_ATTRS = [
    ("Element", "src.pyArchimate.element"),
    ("Model", "src.pyArchimate.model"),
    ("Relationship", "src.pyArchimate.relationship"),
]


def _repair_legacy_inversion():
    """Ensure _legacy.Element/Model/Relationship point to modern implementations."""
    _legacy = sys.modules.get(_LEGACY_KEY)
    if _legacy is None:
        return
    for attr, mod_key in _INVERSION_ATTRS:
        mod = sys.modules.get(mod_key)
        if mod and hasattr(mod, attr):
            setattr(_legacy, attr, getattr(mod, attr))
    pkg = sys.modules.get(_PKG_KEY)
    if pkg is not None:
        pkg._legacy = _legacy


def _import_without_legacy(module_path: str):
    """Import a module with all _legacy entries absent from sys.modules."""
    legacy_keys = [k for k in sys.modules if "_legacy" in k]
    backups = {k: sys.modules.pop(k) for k in legacy_keys}
    target_backup = sys.modules.pop(module_path, None)
    try:
        return importlib.import_module(module_path)
    finally:
        sys.modules.update(backups)
        if target_backup is not None:
            sys.modules[module_path] = target_backup
        # Re-apply the inversion after restoring backups.
        # The try block may have loaded a fresh _legacy whose inversion failed
        # (circular import).  Even if a backup is restored, the package attribute
        # may still point to the uninverted version — _repair_legacy_inversion()
        # fixes both sys.modules and the package attribute atomically.
        _repair_legacy_inversion()


def test_model_importable_without_legacy():
    """model.py imports cleanly without _legacy in sys.modules."""
    try:
        _import_without_legacy("src.pyArchimate.model")
    except Exception as exc:
        pytest.fail(f"model.py failed to import without _legacy: {exc}")


def test_element_importable_without_legacy():
    """element.py imports cleanly without _legacy in sys.modules."""
    try:
        _import_without_legacy("src.pyArchimate.element")
    except Exception as exc:
        pytest.fail(f"element.py failed to import without _legacy: {exc}")


def test_relationship_importable_without_legacy():
    """relationship.py imports cleanly without _legacy in sys.modules."""
    try:
        _import_without_legacy("src.pyArchimate.relationship")
    except Exception as exc:
        pytest.fail(f"relationship.py failed to import without _legacy: {exc}")


def test_model_has_no_legacy_callback():
    """model.py must not call _legacy_module.register_model — fails until T022."""
    import src.pyArchimate.model as model_module

    source = inspect.getsource(model_module)
    assert "_legacy_module.register_model" not in source, (
        "model.py still calls _legacy_module.register_model; "
        "invert the registration so _legacy imports from model (T022)"
    )


def test_element_has_no_legacy_callback():
    """element.py must not call _legacy_module.register_element — fails until T022."""
    import src.pyArchimate.element as element_module

    source = inspect.getsource(element_module)
    assert "_legacy_module.register_element" not in source, (
        "element.py still calls _legacy_module.register_element; "
        "invert the registration so _legacy imports from element (T022)"
    )


def test_relationship_has_no_legacy_callback():
    """relationship.py must not call _legacy_module.register_relationship — fails until T022."""
    import src.pyArchimate.relationship as relationship_module

    source = inspect.getsource(relationship_module)
    assert "_legacy_module.register_relationship" not in source, (
        "relationship.py still calls _legacy_module.register_relationship; "
        "invert the registration so _legacy imports from relationship (T022)"
    )
