from src.pyArchimate import Element as PackageElement
from src.pyArchimate.element import Element


def test_element_importable_from_element_module():
    assert Element is not None


def test_element_exported_from_package():
    assert PackageElement is Element
