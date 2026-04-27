from src.pyArchimate import Model as PackageModel
from src.pyArchimate.element import Element
from src.pyArchimate.model import Model
from src.pyArchimate.relationship import Relationship


def test_modular_imports_expose_public_api_surface():
    assert Model is PackageModel
    assert Model.__name__ == "Model"
    assert Element.__name__ == "Element"
    assert Relationship.__name__ == "Relationship"
