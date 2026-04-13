from src.pyArchimate import Relationship as PackageRelationship
from src.pyArchimate.relationship import Relationship


def test_relationship_importable_from_relationship_module():
    assert Relationship is not None


def test_relationship_exported_from_package():
    assert PackageRelationship is Relationship
