from src.pyArchimate._legacy import Element as LegacyElement
from src.pyArchimate.element import Element


def test_element_module_reexports_legacy_element_class():
    assert Element is LegacyElement
