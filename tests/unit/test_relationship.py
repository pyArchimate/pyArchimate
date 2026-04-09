from src.pyArchimate._legacy import Relationship as LegacyRelationship
from src.pyArchimate.relationship import Relationship


def test_relationship_module_reexports_legacy_relationship_class():
    assert Relationship is LegacyRelationship
