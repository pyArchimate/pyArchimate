"""Integration tests: stereotype colors round-trip through both supported file formats (US3, SC-003)."""

import tempfile

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


def test_archi_native_roundtrip_preserves_stereotype_color():
    m1 = Model("roundtrip-archi")
    profile = m1.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m1.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")

    with tempfile.NamedTemporaryFile(suffix=".archimate", delete=False) as f:
        path = f.name
    m1.write(path)

    m2 = Model("roundtrip-archi-reload")
    m2.read(path)

    reloaded_profile = m2.get_profile("Threat")
    assert reloaded_profile is not None
    assert reloaded_profile.fill_color == "#e8453c"


def test_exchange_xml_roundtrip_preserves_stereotype_color():
    m1 = Model("roundtrip-exchange")
    profile = m1.add_profile(name="Threat", concept=ArchiType.Driver)
    profile.fill_color = "#E8453C"
    elem = m1.add(ArchiType.Driver, "D1")
    elem.set_profile("Threat")

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        path = f.name
    m1.write(path)

    m2 = Model("roundtrip-exchange-reload")
    m2.read(path)

    reloaded_elem = m2.elems_dict[elem.uuid]
    reloaded_profile = reloaded_elem.get_profile()
    assert reloaded_profile is not None
    assert reloaded_profile.name == "Threat"
    assert reloaded_profile.fill_color == "#e8453c"


def test_exchange_xml_roundtrip_keeps_same_named_profiles_distinct():
    """Two stereotypes sharing a name but specializing different concept types
    must not merge on reload (2026-11-28 clarification): kept distinct by profileId.
    """
    m1 = Model("roundtrip-exchange-distinct")
    profile_driver = m1.add_profile(name="Security", concept=ArchiType.Driver)
    profile_driver.fill_color = "#E8453C"
    profile_actor = m1.add_profile(name="Security", concept=ArchiType.BusinessActor)
    profile_actor.fill_color = "#2E8B57"

    elem_driver = m1.add(ArchiType.Driver, "D1")
    elem_driver._profile = profile_driver.uuid
    elem_actor = m1.add(ArchiType.BusinessActor, "A1")
    elem_actor._profile = profile_actor.uuid

    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
        path = f.name
    m1.write(path)

    m2 = Model("roundtrip-exchange-distinct-reload")
    m2.read(path)

    reloaded_driver = m2.elems_dict[elem_driver.uuid].get_profile()
    reloaded_actor = m2.elems_dict[elem_actor.uuid].get_profile()
    assert reloaded_driver is not None
    assert reloaded_actor is not None
    assert reloaded_driver.uuid != reloaded_actor.uuid
    assert reloaded_driver.fill_color == "#e8453c"
    assert reloaded_actor.fill_color == "#2e8b57"


def test_pre_existing_fixture_still_loads_with_no_profile_color():
    """A fixture created before this feature existed must still load cleanly,
    with every profile's fill_color reading None (SC-005, FR-014).
    """
    m = Model("legacy-fixture")
    m.read("tests/fixtures/valid_model.xml")
    for profile in m.profiles:
        assert profile.fill_color is None
    for view in m.elements:
        if view.type == "ArchimateDiagramModel" and hasattr(view, "to_svg"):
            assert view.to_svg()
