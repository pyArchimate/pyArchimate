import importlib
import sys
from importlib.machinery import PathFinder


def _import_with_blocked_relative_import(monkeypatch, module_name, blocked_relative):
    """Import `module_name` while blocking the relative import of `blocked_relative`."""
    original_find = PathFinder.find_spec

    def _blocked_find_spec(fullname, path=None, target=None):
        if fullname == blocked_relative:
            return None
        return original_find(fullname, path, target)

    monk = monkeypatch
    monk.setattr(PathFinder, "find_spec", _blocked_find_spec)

    sys.modules.pop(module_name, None)
    sys.modules.pop(blocked_relative, None)

    module = importlib.import_module(module_name)

    monk.setattr(PathFinder, "find_spec", original_find)
    sys.modules.pop(module_name, None)
    sys.modules.pop(blocked_relative, None)
    importlib.import_module(module_name)

    return module


def test_element_import_falls_back_to_top_level(monkeypatch):
    module = _import_with_blocked_relative_import(
        monkeypatch, "src.pyArchimate.element", "src.pyArchimate._legacy"
    )
    assert module.Element.__module__ == "_legacy"


def test_model_import_falls_back_to_top_level(monkeypatch):
    module = _import_with_blocked_relative_import(
        monkeypatch, "src.pyArchimate.model", "src.pyArchimate._legacy"
    )
    assert module.Model.__module__ == "_legacy"


def test_relationship_import_falls_back_to_top_level(monkeypatch):
    module = _import_with_blocked_relative_import(
        monkeypatch, "src.pyArchimate.relationship", "src.pyArchimate._legacy"
    )
    assert module.Relationship.__module__ == "_legacy"


def test_helpers_logging_import_falls_back_to_top_level(monkeypatch):
    module = _import_with_blocked_relative_import(
        monkeypatch, "src.pyArchimate.helpers.logging", "src.pyArchimate.logger"
    )
    assert module.log_set_level.__module__ == "logger"


def test_pyarchimate_import_falls_back_to_top_level(monkeypatch):
    module = _import_with_blocked_relative_import(
        monkeypatch, "src.pyArchimate.pyArchimate", "src.pyArchimate._legacy"
    )
    assert module.Model.__module__ == "_legacy"
