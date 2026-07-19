from typing import cast

import pytest

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model, default_color
from src.pyArchimate.view import View
from tests._helpers import model_with_views

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def simple_model():
    """A model with two elements and one relationship."""
    m = Model("test")
    src = m.add(ArchiType.ApplicationComponent, "App")
    dst = m.add(ArchiType.ApplicationService, "Svc")
    rel = m.add_relationship(rel_type=ArchiType.Serving, source=src, target=dst, name="serves")
    return m, src, dst, rel


# ---------------------------------------------------------------------------
# Existing test
# ---------------------------------------------------------------------------


def test_model_roundtrip_preserves_properties(tmp_path):
    model = Model("unit test")
    model.prop("custom", "value")
    model.add(ArchiType.ApplicationComponent, "UnitElement")
    destination = tmp_path / "unit-model.archimate"
    model.write(str(destination))

    reloaded = Model("reload")
    reloaded.read(str(destination))
    assert reloaded.prop("custom") == "value"
    assert any(elem.name == "UnitElement" for elem in reloaded.elements)


# ---------------------------------------------------------------------------
# default_color
# ---------------------------------------------------------------------------


def test_default_color_archi_theme():
    assert default_color("ApplicationComponent", "archi") == "#B5FFFF"


def test_default_color_aris_theme():
    assert default_color("ApplicationComponent", "aris") == "#00A0FF"


def test_default_color_none_theme():
    result = default_color("BusinessActor", None)
    assert result.startswith("#")


def test_default_color_custom_theme_dict():
    custom = {"business": "#AABBCC"}
    assert default_color("BusinessActor", custom) == "#AABBCC"


def test_default_color_custom_theme_missing_key():
    # KeyError fallback → returns archi default
    result = default_color("BusinessActor", {})
    assert result.startswith("#")


def test_default_color_unknown_type():
    assert default_color("NotAType") == "#FFFFFF"


# ---------------------------------------------------------------------------
# Model.type property
# ---------------------------------------------------------------------------


def test_model_type_is_model():
    m = Model("x")
    assert m.type == "Model"


# ---------------------------------------------------------------------------
# Model.prop / remove_prop
# ---------------------------------------------------------------------------


def test_model_remove_prop(simple_model):
    m, *_ = simple_model
    m.prop("tmp", "1")
    m.remove_prop("tmp")
    assert m.prop("tmp") is None


def test_model_remove_prop_missing_key_is_noop():
    m = Model("x")
    m.remove_prop("no_such_key")  # must not raise


# ---------------------------------------------------------------------------
# Model.add_profile / get_profile
# ---------------------------------------------------------------------------


def test_model_get_profile_found(simple_model):
    m, *_ = simple_model
    p = m.add_profile(name="MyProfile", concept="ApplicationComponent")
    assert m.get_profile("MyProfile") is p


def test_model_get_profile_not_found():
    m = Model("x")
    assert m.get_profile("ghost") is None


# ---------------------------------------------------------------------------
# Model.nodes / conns
# ---------------------------------------------------------------------------


def test_model_nodes_returns_list(simple_model):
    m, *_ = simple_model
    assert isinstance(m.nodes, list)


def test_model_conns_returns_list(simple_model):
    m, *_ = simple_model
    assert isinstance(m.conns, list)


# ---------------------------------------------------------------------------
# Model.filter_elements / find_elements
# ---------------------------------------------------------------------------


def test_filter_elements(simple_model):
    m, src, *_ = simple_model
    result = m.filter_elements(lambda e: e.type == ArchiType.ApplicationComponent)
    assert src in result


def test_find_elements_by_name(simple_model):
    m, src, *_ = simple_model
    assert m.find_elements(name="App") == [src]


def test_find_elements_by_type(simple_model):
    m, src, *_ = simple_model
    assert m.find_elements(elem_type=ArchiType.ApplicationComponent) == [src]


def test_find_elements_by_name_and_type(simple_model):
    m, src, *_ = simple_model
    assert m.find_elements(name="App", elem_type=ArchiType.ApplicationComponent) == [src]


def test_find_elements_no_criteria(simple_model):
    m, src, dst, *_ = simple_model
    result = m.find_elements()
    assert src in result and dst in result


# ---------------------------------------------------------------------------
# Model.find_relationships / filter_relationships
# ---------------------------------------------------------------------------


def test_find_relationships_with_type_both(simple_model):
    m, src, _, rel = simple_model
    result = m.find_relationships(ArchiType.Serving, src, direction="both")
    assert rel in result


def test_find_relationships_out_only(simple_model):
    m, src, _, rel = simple_model
    assert rel in m.find_relationships(ArchiType.Serving, src, direction="out")


def test_find_relationships_in_only(simple_model):
    m, _, dst, rel = simple_model
    assert rel in m.find_relationships(ArchiType.Serving, dst, direction="in")


def test_find_relationships_no_type(simple_model):
    m, src, _, rel = simple_model
    result = m.find_relationships(None, src, direction="both")
    assert rel in result


def test_find_relationships_none_elem(simple_model):
    m, *_ = simple_model
    assert m.find_relationships(ArchiType.Serving, None) is None


def test_filter_relationships(simple_model):
    m, _, _, rel = simple_model
    result = m.filter_relationships(lambda r: r.name == "serves")
    assert rel in result


# ---------------------------------------------------------------------------
# Model.filter_views / find_views
# ---------------------------------------------------------------------------


def test_filter_views(simple_model):
    m, *_ = simple_model
    v = m.add(ArchiType.View, "MyView")
    result = m.filter_views(lambda x: x.name == "MyView")
    assert v in result


def test_find_views(simple_model):
    m, *_ = simple_model
    v = m.add(ArchiType.View, "SearchView")
    assert m.find_views("SearchView") == [v]


# ---------------------------------------------------------------------------
# Model.merge
# ---------------------------------------------------------------------------


def test_model_merge_reads_data(tmp_path):
    m1 = Model("base")
    m1.add(ArchiType.ApplicationComponent, "CompA")
    f = tmp_path / "base.archimate"
    m1.write(str(f))

    m2 = Model("target")
    m2.add(ArchiType.ApplicationComponent, "CompB")
    m2.merge(str(f))
    names = [e.name for e in m2.elements]
    assert "CompA" in names
    assert "CompB" in names


# ---------------------------------------------------------------------------
# Model.get_or_create_element
# ---------------------------------------------------------------------------


def test_get_or_create_element_empty_name(simple_model):
    m, *_ = simple_model
    assert m.get_or_create_element(ArchiType.ApplicationComponent, "") is None


def test_get_or_create_element_none_name(simple_model):
    m, *_ = simple_model
    assert m.get_or_create_element(ArchiType.ApplicationComponent, None) is None


def test_get_or_create_element_found(simple_model):
    m, src, *_ = simple_model
    result = m.get_or_create_element(ArchiType.ApplicationComponent, "App")
    assert result is src


def test_get_or_create_element_create_true(simple_model):
    m, *_ = simple_model
    result = m.get_or_create_element(ArchiType.ApplicationComponent, "Brand New", create_elem=True)
    assert result is not None
    assert result.name == "Brand New"


def test_get_or_create_element_not_found_no_create(simple_model):
    m, *_ = simple_model
    assert m.get_or_create_element(ArchiType.ApplicationComponent, "Ghost") is None


# ---------------------------------------------------------------------------
# Model.get_or_create_relationship
# ---------------------------------------------------------------------------


def test_get_or_create_relationship_none_source(simple_model):
    m, _, dst, *_ = simple_model
    assert m.get_or_create_relationship(ArchiType.Serving, None, None, dst) is None


def test_get_or_create_relationship_found_unnamed(simple_model):
    m, src, dst, rel = simple_model
    result = m.get_or_create_relationship(ArchiType.Serving, None, src, dst)
    assert result is rel


def test_get_or_create_relationship_found_named(simple_model):
    m, src, dst, rel = simple_model
    result = m.get_or_create_relationship(ArchiType.Serving, "serves", src, dst)
    assert result is rel


def test_get_or_create_relationship_create(simple_model):
    m, src, dst, _ = simple_model
    result = m.get_or_create_relationship(ArchiType.Association, "new-rel", src, dst, create_rel=True)
    assert result is not None
    assert result.name == "new-rel"


def test_get_or_create_relationship_not_found_no_create(simple_model):
    m, src, dst, _ = simple_model
    result = m.get_or_create_relationship(ArchiType.Association, "ghost", src, dst)
    assert result is None


# ---------------------------------------------------------------------------
# Model.get_or_create_view
# ---------------------------------------------------------------------------


def test_get_or_create_view_found(simple_model):
    m, *_ = simple_model
    v = m.add(ArchiType.View, "MyView")
    assert m.get_or_create_view("MyView") is v


def test_get_or_create_view_not_found_create(simple_model):
    m, *_ = simple_model
    v = m.get_or_create_view("NewView", create_view=True)
    assert v is not None and v.name == "NewView"


def test_get_or_create_view_not_found_no_create(simple_model):
    m, *_ = simple_model
    assert m.get_or_create_view("Ghost") is None


def test_get_or_create_view_object_passthrough(simple_model):
    m, *_ = simple_model
    v = m.add(ArchiType.View, "ObjView")
    assert m.get_or_create_view(v) is v


# ---------------------------------------------------------------------------
# Model.check_invalid_conn / check_invalid_nodes
# ---------------------------------------------------------------------------


def test_check_invalid_conn_empty_model():
    assert Model("x").check_invalid_conn() == []


def test_check_invalid_nodes_empty_model():
    assert Model("x").check_invalid_nodes() == []


def test_check_invalid_conn_with_views():
    m = model_with_views()
    result = m.check_invalid_conn()
    assert isinstance(result, list)


def test_check_invalid_nodes_with_views():
    m = model_with_views()
    result = m.check_invalid_nodes()
    assert isinstance(result, list)


def test_check_invalid_relationships_empty_model():
    assert Model("x").check_invalid_relationships() == []


def test_check_invalid_relationships_all_valid():
    m = Model("x")
    a = m.add(ArchiType.Requirement, "A")
    b = m.add(ArchiType.Requirement, "B")
    m.add_relationship(ArchiType.Influence, source=a, target=b)
    assert m.check_invalid_relationships() == []


def test_check_invalid_relationships_detects_corrupted_relationship():
    m = Model("x")
    a = m.add(ArchiType.Requirement, "A")
    b = m.add(ArchiType.Requirement, "B")
    rel = m.add_relationship(ArchiType.Influence, source=a, target=b)
    # Requirement->Requirement Realization is not allowed by the metamodel;
    # corrupt the type directly to bypass the constructor-time check.
    rel._type = "Realization"
    assert m.check_invalid_relationships() == [rel.uuid]


# ---------------------------------------------------------------------------
# Model.default_theme
# ---------------------------------------------------------------------------


def test_model_default_theme_sets_theme():
    m = model_with_views()
    m.default_theme("archi")
    assert m.theme == "archi"


def test_model_default_theme_colors_nodes():
    m = model_with_views()
    m.default_theme("aris")
    # All element nodes should now have a fill color set
    for n in m.nodes:
        if n.cat == "Element":
            assert n.fill_color is not None


# ---------------------------------------------------------------------------
# Model.embed_props / expand_props
# ---------------------------------------------------------------------------


def test_model_embed_props_element():
    m = Model("ep-test")
    a = m.add(ArchiType.ApplicationComponent, "App")
    a.prop("owner", "team")
    m.embed_props()
    assert a.desc is not None and "properties" in a.desc


def test_model_embed_props_view():
    m = Model("ep-view")
    v = cast(View, m.add(ArchiType.View, "V"))
    v.prop("color", "blue")
    m.embed_props()
    assert v.desc is not None and "properties" in v.desc


def test_model_embed_props_model_level():
    m = Model("ep-model")
    m.prop("env", "prod")
    m.embed_props()
    assert m.desc is not None and "properties" in m.desc


def test_model_embed_props_relationship():
    m = Model("ep-rel")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b, name="serves")
    m.embed_props()
    assert rel.prop("Identifier") == "serves"


def test_model_embed_props_remove_props():
    m = Model("ep-rm")
    a = m.add(ArchiType.ApplicationComponent, "A")
    a.prop("x", "1")
    m.embed_props(remove_props=True)
    assert a.prop("x") is None


def test_model_expand_props_restores_element():
    m = Model("ex-elem")
    a = m.add(ArchiType.ApplicationComponent, "App")
    a.prop("k", "v")
    m.embed_props()
    m.expand_props()
    assert a.prop("k") == "v"


def test_model_expand_props_view():
    m = Model("ex-view")
    v = cast(View, m.add(ArchiType.View, "V"))
    v.prop("key", "val")
    m.embed_props()
    m.expand_props()
    assert v.prop("key") == "val"


def test_model_expand_props_relationship():
    m = Model("ex-rel")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b, name="r1")
    m.embed_props()
    m.expand_props()
    assert rel.name is not None


# ---------------------------------------------------------------------------
# Model.add_relationship with Node sources/targets
# ---------------------------------------------------------------------------


def test_get_or_create_relationship_with_node_source_and_target():
    m = Model("node-rel")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    v = cast(View, m.add(ArchiType.View, "V"))
    na = v.add(ref=a.uuid, x=10, y=10)
    nb = v.add(ref=b.uuid, x=200, y=10)
    # Passing Nodes directly — get_or_create_relationship converts them to concepts
    rel = m.get_or_create_relationship(ArchiType.Serving, None, na, nb, create_rel=True)
    assert rel is not None


# ---------------------------------------------------------------------------
# Model._prepare_reader — unknown XML format (lines 355, 363-364)
# ---------------------------------------------------------------------------


def test_model_read_unknown_xml_format_returns_none(tmp_path):
    """Reading an XML file with an unrecognised root tag returns silently (lines 355, 363-364)."""
    xml_file = tmp_path / "unknown.xml"
    xml_file.write_text("<UnknownRoot><element/></UnknownRoot>", encoding="utf-8")
    m = Model("unknown-xml")
    # read() calls _prepare_reader which returns None for unknown root tag
    m.read(str(xml_file))  # should not raise; just logs and returns


def test_model_merge_unknown_xml_format_returns_none(tmp_path):
    """Merging an XML file with an unrecognised root tag returns silently (line 399)."""
    xml_file = tmp_path / "unknown_merge.xml"
    xml_file.write_text("<Unrecognised><item/></Unrecognised>", encoding="utf-8")
    m = Model("merge-unknown")
    m.merge(str(xml_file))  # should not raise


# ---------------------------------------------------------------------------
# _matches_rel — fallthrough (line 37)
# ---------------------------------------------------------------------------


def test_matches_rel_no_match_returns_false():
    """Relationship that is neither source nor target of elem returns nothing."""
    m = Model("no-match")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    c = m.add(ArchiType.ApplicationComponent, "C")
    m.add_relationship(ArchiType.Serving, source=a, target=b)
    # c is not involved in any relationship — list must be empty
    result = m.find_relationships(None, c, direction="both")
    assert result == []


# ---------------------------------------------------------------------------
# _find_props_block — edge cases (lines 54, 58-59)
# ---------------------------------------------------------------------------

from src.pyArchimate.model import _find_props_block, _strip_props_block  # noqa: E402


def test_find_props_block_marker_no_brace_returns_none():
    """Marker found but no '{' afterwards → line 54 continue."""
    assert _find_props_block("properties = no_brace_here") is None


def test_find_props_block_malformed_json_returns_none():
    """Marker + brace found but JSON is malformed → line 58-59 pass."""
    assert _find_props_block("properties = {not valid json}") is None


def test_find_props_block_hash_prefix():
    """'#properties={...}' variant is found."""
    result = _find_props_block('#properties={"key": "val"}')
    assert result is not None
    _, _, parsed = result
    assert parsed == {"key": "val"}


def test_strip_props_block_no_block_returns_original():
    """Text without a block is returned unchanged."""
    text = "just some description"
    assert _strip_props_block(text) == text


# ---------------------------------------------------------------------------
# _apply_rel_identity_props / _expand_relationship (lines 87-107)
# ---------------------------------------------------------------------------


def test_expand_props_relationship_with_embedded_json():
    """Relationship with JSON in Identifier restores name and desc (lines 87-107)."""
    import json as _json

    m = Model("rel-expand")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(ArchiType.Association, source=a, target=b)
    # Manually place a JSON properties block in the Identifier prop
    payload = _json.dumps({"name": "restored-name", "documentation": "restored-doc"})
    rel.prop("Identifier", f"properties = {payload}")
    m.expand_props()
    assert rel.name == "restored-name"
    assert rel.desc == "restored-doc"


def test_expand_props_relationship_is_directed():
    """isDirected field is applied to Association relationship (line 92)."""
    import json as _json

    m = Model("rel-directed")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(ArchiType.Association, source=a, target=b)
    payload = _json.dumps({"isDirected": "true"})
    rel.prop("Identifier", f"properties = {payload}")
    m.expand_props()
    assert rel.is_directed is not None


def test_expand_props_relationship_access_type():
    """access field is applied to Access relationship (line 94)."""
    import json as _json

    m = Model("rel-access")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b2 = m.add(ArchiType.DataObject, "D")
    rel = m.add_relationship(ArchiType.Access, source=a, target=b2)
    payload = _json.dumps({"access": "Read"})
    rel.prop("Identifier", f"properties = {payload}")
    m.expand_props()
    assert rel.access_type == "Read"


def test_expand_props_relationship_influence_strength():
    """influence_strength field is applied to Influence relationship (line 96)."""
    import json as _json

    m = Model("rel-influence")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(ArchiType.Influence, source=a, target=b)
    payload = _json.dumps({"influence_strength": "5"})
    rel.prop("Identifier", f"properties = {payload}")
    m.expand_props()
    assert rel.influence_strength == "5"


# ---------------------------------------------------------------------------
# ArchiMate 3.x Compliance: Viewpoint filtering queries
# ---------------------------------------------------------------------------


def test_viewpoint_filtering_queries(simple_model):
    m, *_ = simple_model
    a = m.add(ArchiType.BusinessActor, "Actor A")
    b = m.add(ArchiType.BusinessActor, "Actor B")
    a.assign_viewpoint("stakeholder")
    b.assign_viewpoint("capability")
    result = m.get_elements_by_viewpoint("stakeholder")
    assert a in result
    assert b not in result


def test_get_viewpoints_returns_all(simple_model):
    m, *_ = simple_model
    vps = m.get_viewpoints()
    assert len(vps) == 13


def test_get_views_by_viewpoint(simple_model):
    m, *_ = simple_model
    v1 = cast(View, m.add(ArchiType.View, "View Tech"))
    v2 = cast(View, m.add(ArchiType.View, "View Cap"))
    v1.set_primary_viewpoint("technology")
    v2.set_primary_viewpoint("capability")
    result = m.get_views_by_viewpoint("technology")
    assert v1 in result
    assert v2 not in result


def test_get_elements_by_viewpoint_invalid_slug(simple_model):
    m, *_ = simple_model
    with pytest.raises(ValueError):
        m.get_elements_by_viewpoint("not_a_slug")


def test_get_views_by_viewpoint_invalid_slug(simple_model):
    m, *_ = simple_model
    with pytest.raises(ValueError):
        m.get_views_by_viewpoint("not_a_slug")


# ---------------------------------------------------------------------------
# _apply_rel_identity_props with None (line 89)
# ---------------------------------------------------------------------------


def test_apply_rel_identity_props_none_is_noop():
    """_apply_rel_identity_props(o, None) returns immediately (line 89)."""
    from src.pyArchimate.model import _apply_rel_identity_props

    m = Model("ari-none")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b, name="before")
    _apply_rel_identity_props(rel, None)
    assert rel.name == "before"


# ---------------------------------------------------------------------------
# _load_file_contents IOError → sys.exit(1) (lines 493-495)
# ---------------------------------------------------------------------------


def test_load_file_contents_missing_file_exits():
    """Reading a non-existent file calls sys.exit(1) (lines 493-495)."""
    m = Model("missing-file")
    with pytest.raises(SystemExit):
        m.read("/nonexistent/path/to/file.archimate")


# ---------------------------------------------------------------------------
# merge() when format doesn't support merge (lines 549-550)
# ---------------------------------------------------------------------------


def test_model_merge_aml_format_not_supported(tmp_path):
    """Merging an AML file logs error and returns without raising (lines 549-550).

    AML reader has supports_merge=False in the registry.
    We create a minimal valid AML XML file so _prepare_reader succeeds but
    entry.supports_merge is False.
    """
    aml_content = '<?xml version="1.0" encoding="UTF-8"?><AML><Group ID="G1" Name="Root"/></AML>'
    aml_file = tmp_path / "test.aml"
    aml_file.write_text(aml_content, encoding="utf-8")
    m = Model("aml-merge")
    # Should return without raising; the merge is silently skipped
    m.merge(str(aml_file))


# ---------------------------------------------------------------------------
# check_connection / check_connections_validity (lines 778, 794-825)
# ---------------------------------------------------------------------------


def test_check_connections_validity_with_valid_model():
    """check_invalid_conn on a well-formed model returns a list (lines 778, 794-825)."""
    from tests._helpers import model_with_views

    m = model_with_views()
    result = m.check_invalid_conn()
    assert isinstance(result, list)


def test_check_connection_orphan_ref_error():
    """check_connection logs error for orphan relationship reference (lines 793-795).

    We call check_connection() directly to exercise the orphan-_ref branch.
    Since c.concept raises KeyError when _ref is missing, we wrap in try/except.
    """
    from tests._helpers import model_with_views

    m = model_with_views()
    for conn in m.conns_dict.values():
        old_ref = conn._ref
        conn._ref = "nonexistent-rel-uuid"
        # check_connection raises KeyError at concept._source (line 800) after logging
        # line 794 error, so catch the exception
        try:
            m.check_connection(conn)
        except (KeyError, AttributeError):  # noqa: S110
            pass
        conn._ref = old_ref
        break


# ---------------------------------------------------------------------------
# _would_create_cycle max-depth path (line 909-910)
# ---------------------------------------------------------------------------


def test_would_create_cycle_max_depth():
    """_would_create_cycle returns True when visited set exceeds MAX_DEPTH (line 909-910)."""
    from src.pyArchimate.constants import MAX_DEPTH

    m = Model("cycle-depth")
    # Create a long chain in _element_hierarchy (beyond MAX_DEPTH) without going through add_child
    uuids = [m.add(ArchiType.ApplicationComponent, f"E{i}").uuid for i in range(MAX_DEPTH + 3)]
    # Build a chain: uuids[0]->uuids[1]->...->uuids[MAX_DEPTH+1]
    for i in range(len(uuids) - 1):
        m._element_hierarchy[uuids[i]] = uuids[i + 1]
    # Now _would_create_cycle(uuids[MAX_DEPTH+2], uuids[0]) should detect max-depth exceeded
    result = m._would_create_cycle(uuids[0], uuids[MAX_DEPTH + 2])
    assert result is True


def test_would_create_cycle_visited_loop():
    """_would_create_cycle returns True when a visited node is encountered again (line 907)."""
    m = Model("cycle-visited")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationComponent, "B")
    c = m.add(ArchiType.ApplicationComponent, "C")
    # Build a real cycle in _element_hierarchy bypassing add_child
    # a -> b -> c -> b (cycle back to b)
    m._element_hierarchy[a.uuid] = b.uuid
    m._element_hierarchy[b.uuid] = c.uuid
    m._element_hierarchy[c.uuid] = b.uuid  # cycle
    # _would_create_cycle(a, new_elem) walks a->b->c->b and hits visited on 2nd visit to b
    d = m.add(ArchiType.ApplicationComponent, "D")
    result = m._would_create_cycle(a.uuid, d.uuid)
    assert result is True


# ---------------------------------------------------------------------------
# get_ancestors cycle break (line 996)
# ---------------------------------------------------------------------------


def test_get_ancestors_cycle_break():
    """get_ancestors breaks when visited cycle detected (line 996)."""
    m = Model("anc-cycle")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationComponent, "B")
    # Directly inject a cycle in _element_hierarchy bypassing add_child guards
    m._element_hierarchy[a.uuid] = b.uuid
    m._element_hierarchy[b.uuid] = a.uuid
    # Should not loop forever — cycle break prevents infinite loop
    ancestors = m.get_ancestors(a.uuid)
    assert isinstance(ancestors, list)


# ---------------------------------------------------------------------------
# get_descendants cycle continue (line 1016)
# ---------------------------------------------------------------------------


def test_get_descendants_cycle_continue():
    """get_descendants uses visited set to skip repeated nodes (line 1016)."""
    m = Model("desc-cycle")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationComponent, "B")
    # Inject a fake cycle in children without using add_child
    m._element_children[a.uuid] = {b.uuid}
    m._element_children[b.uuid] = {a.uuid}
    # Should terminate because visited guards the cycle
    descendants = m.get_descendants(a.uuid)
    assert isinstance(descendants, list)


# ---------------------------------------------------------------------------
# _traverse_by_path base case (lines 1087-1092)
# ---------------------------------------------------------------------------


def test_find_by_hierarchy_path_exact_match():
    """find_by_hierarchy_path('/Parent/Child') returns the child element (lines 1087-1104)."""
    m = Model("path-exact")
    parent = m.add(ArchiType.ApplicationComponent, "Parent")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    m.add_child(parent.uuid, child.uuid)
    result = m.find_by_hierarchy_path("/Parent/Child")
    assert child in result


def test_find_by_hierarchy_path_wildcard():
    """find_by_hierarchy_path('/Parent/*') returns all children (lines 1087-1092)."""
    m = Model("path-wildcard")
    parent = m.add(ArchiType.ApplicationComponent, "Parent")
    child1 = m.add(ArchiType.ApplicationComponent, "Child1")
    child2 = m.add(ArchiType.ApplicationComponent, "Child2")
    m.add_child(parent.uuid, child1.uuid)
    m.add_child(parent.uuid, child2.uuid)
    result = m.find_by_hierarchy_path("/Parent/*")
    assert child1 in result
    assert child2 in result


def test_find_by_hierarchy_path_single_level_no_wildcard():
    """find_by_hierarchy_path('/RootElem') hits base case non-wildcard (line 1091)."""
    m = Model("path-single")
    root_elem = m.add(ArchiType.ApplicationComponent, "RootElem")
    result = m.find_by_hierarchy_path("/RootElem")
    assert root_elem in result


# ---------------------------------------------------------------------------
# Model.__init__ edge cases
# ---------------------------------------------------------------------------


def test_model_init_with_none_name():
    """Model.__init__ should handle None name gracefully."""
    m = Model(None)
    assert m.name is None
    assert m.uuid is not None


def test_model_init_with_empty_name():
    """Model.__init__ should handle empty string name."""
    m = Model("")
    assert m.name == ""
    assert m.uuid is not None


def test_model_init_with_custom_uuid():
    """Model.__init__ should accept custom UUID."""
    custom_uuid = "test-uuid-123"
    m = Model("test", uuid=custom_uuid)
    assert m.uuid == custom_uuid


# ---------------------------------------------------------------------------
# Model.add_relationship parameter combinations and edge cases
# ---------------------------------------------------------------------------


def test_add_relationship_minimal_params():
    """add_relationship with minimal required parameters."""
    m = Model("rel-test")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(ArchiType.Serving, source=a, target=b)
    assert rel is not None
    assert rel.type == ArchiType.Serving
    assert rel.source == a
    assert rel.target == b


def test_add_relationship_all_params():
    """add_relationship with all possible parameters."""
    m = Model("rel-all")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationService, "B")
    rel = m.add_relationship(
        rel_type=ArchiType.Access,
        source=a,
        target=b,
        uuid="custom-rel-uuid",
        name="test-access",
        access_type="Read",
        influence_strength="5",
        desc="Test relationship",
        is_directed=True,
    )
    assert rel.uuid == "custom-rel-uuid"
    assert rel.name == "test-access"
    assert rel.access_type == "Read"
    assert rel.influence_strength == "5"
    assert rel.desc == "Test relationship"
    assert rel.is_directed is True


def test_add_relationship_invalid_source():
    """add_relationship with invalid source should raise TypeError."""
    m = Model("rel-invalid")
    b = m.add(ArchiType.ApplicationService, "B")
    with pytest.raises(ValueError):
        m.add_relationship(ArchiType.Serving, source="invalid", target=b)


def test_add_relationship_invalid_target():
    """add_relationship with invalid target should raise TypeError."""
    m = Model("rel-invalid")
    a = m.add(ArchiType.ApplicationComponent, "A")
    with pytest.raises(ValueError):
        m.add_relationship(ArchiType.Serving, source=a, target="invalid")


def test_add_relationship_none_source():
    """add_relationship with None source should raise TypeError."""
    m = Model("rel-none")
    b = m.add(ArchiType.ApplicationService, "B")
    with pytest.raises(ValueError):
        m.add_relationship(ArchiType.Serving, source=None, target=b)


def test_add_relationship_none_target():
    """add_relationship with None target should raise TypeError."""
    m = Model("rel-none")
    a = m.add(ArchiType.ApplicationComponent, "A")
    with pytest.raises(ValueError):
        m.add_relationship(ArchiType.Serving, source=a, target=None)


# ---------------------------------------------------------------------------
# Model.embed_props / expand_props error cases
# ---------------------------------------------------------------------------


def test_embed_props_with_malformed_desc():
    """embed_props should handle malformed descriptions gracefully."""
    m = Model("embed-error")
    a = m.add(ArchiType.ApplicationComponent, "A")
    a.desc = "properties = {invalid json"
    # Should not raise exception
    m.embed_props()
    assert a.desc is not None


def test_expand_props_with_malformed_json():
    """expand_props should handle malformed JSON in descriptions."""
    m = Model("expand-error")
    a = m.add(ArchiType.ApplicationComponent, "A")
    a.desc = "properties = {invalid json}"
    # Should not raise exception
    m.expand_props()
    # Properties should remain unchanged
    assert a.prop("test") is None


def test_expand_props_with_no_properties_block():
    """expand_props should handle descriptions without properties blocks."""
    m = Model("expand-no-props")
    a = m.add(ArchiType.ApplicationComponent, "A")
    a.desc = "Just a regular description"
    original_desc = a.desc
    m.expand_props()
    assert a.desc == original_desc


# ---------------------------------------------------------------------------
# Hierarchy methods edge cases
# ---------------------------------------------------------------------------


def test_add_child_invalid_parent_uuid():
    """add_child with invalid parent UUID should raise KeyError."""
    m = Model("hierarchy-error")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    with pytest.raises(KeyError):
        m.add_child("invalid-parent-uuid", child.uuid)


def test_add_child_invalid_child_uuid():
    """add_child with invalid child UUID should raise KeyError."""
    m = Model("hierarchy-error")
    parent = m.add(ArchiType.ApplicationComponent, "Parent")
    with pytest.raises(KeyError):
        m.add_child(parent.uuid, "invalid-child-uuid")


def test_add_child_already_has_parent():
    """add_child when child already has parent should raise ValueError."""
    m = Model("hierarchy-error")
    parent1 = m.add(ArchiType.ApplicationComponent, "Parent1")
    parent2 = m.add(ArchiType.ApplicationComponent, "Parent2")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    m.add_child(parent1.uuid, child.uuid)
    with pytest.raises(ValueError):
        m.add_child(parent2.uuid, child.uuid)


def test_add_child_cycle_detection():
    """add_child that would create a cycle should raise ValueError."""
    m = Model("hierarchy-cycle")
    a = m.add(ArchiType.ApplicationComponent, "A")
    b = m.add(ArchiType.ApplicationComponent, "B")
    c = m.add(ArchiType.ApplicationComponent, "C")
    m.add_child(a.uuid, b.uuid)
    m.add_child(b.uuid, c.uuid)
    with pytest.raises(ValueError):
        m.add_child(c.uuid, a.uuid)  # Would create cycle


def test_remove_child_invalid_parent():
    """remove_child with invalid parent UUID should raise KeyError."""
    m = Model("remove-error")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    with pytest.raises(KeyError):
        m.remove_child("invalid-parent", child.uuid)


def test_remove_child_invalid_child():
    """remove_child with invalid child UUID should raise KeyError."""
    m = Model("remove-error")
    parent = m.add(ArchiType.ApplicationComponent, "Parent")
    with pytest.raises(KeyError):
        m.remove_child(parent.uuid, "invalid-child")


def test_remove_child_not_actual_child():
    """remove_child when child is not actually a child of parent should raise ValueError."""
    m = Model("remove-error")
    parent1 = m.add(ArchiType.ApplicationComponent, "Parent1")
    parent2 = m.add(ArchiType.ApplicationComponent, "Parent2")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    m.add_child(parent1.uuid, child.uuid)
    with pytest.raises(ValueError):
        m.remove_child(parent2.uuid, child.uuid)


def test_get_parent_invalid_uuid():
    """get_parent with invalid UUID should return None."""
    m = Model("get-parent-error")
    assert m.get_parent("invalid-uuid") is None


def test_get_children_invalid_uuid():
    """get_children with invalid UUID should return empty list."""
    m = Model("get-children-error")
    assert m.get_children("invalid-uuid") == []


def test_get_ancestors_invalid_uuid():
    """get_ancestors with invalid UUID should return empty list."""
    m = Model("get-ancestors-error")
    assert m.get_ancestors("invalid-uuid") == []


def test_get_descendants_invalid_uuid():
    """get_descendants with invalid UUID should return empty list."""
    m = Model("get-descendants-error")
    assert m.get_descendants("invalid-uuid") == []


def test_get_siblings_invalid_uuid():
    """get_siblings with invalid UUID should raise KeyError."""
    m = Model("get-siblings-error")
    with pytest.raises(KeyError):
        m.get_siblings("invalid-uuid")


# ---------------------------------------------------------------------------
# find_by_hierarchy_path complex paths and edge cases
# ---------------------------------------------------------------------------


def test_find_by_hierarchy_path_complex_nested():
    """find_by_hierarchy_path with deeply nested path."""
    m = Model("path-complex")
    root = m.add(ArchiType.ApplicationComponent, "Root")
    level1 = m.add(ArchiType.ApplicationComponent, "Level1")
    level2 = m.add(ArchiType.ApplicationComponent, "Level2")
    leaf = m.add(ArchiType.ApplicationComponent, "Leaf")
    m.add_child(root.uuid, level1.uuid)
    m.add_child(level1.uuid, level2.uuid)
    m.add_child(level2.uuid, leaf.uuid)
    result = m.find_by_hierarchy_path("/Root/Level1/Level2/Leaf")
    assert leaf in result


def test_find_by_hierarchy_path_intermediate_wildcard():
    """find_by_hierarchy_path with wildcard in middle of path."""
    m = Model("path-mid-wildcard")
    root = m.add(ArchiType.ApplicationComponent, "Root")
    branch1 = m.add(ArchiType.ApplicationComponent, "Branch1")
    branch2 = m.add(ArchiType.ApplicationComponent, "Branch2")
    leaf1 = m.add(ArchiType.ApplicationComponent, "Leaf1")
    leaf2 = m.add(ArchiType.ApplicationComponent, "Leaf2")
    m.add_child(root.uuid, branch1.uuid)
    m.add_child(root.uuid, branch2.uuid)
    m.add_child(branch1.uuid, leaf1.uuid)
    m.add_child(branch2.uuid, leaf2.uuid)
    result = m.find_by_hierarchy_path("/Root/*/Leaf1")
    assert leaf1 in result
    assert leaf2 not in result


def test_find_by_hierarchy_path_root_only():
    """find_by_hierarchy_path with just root path."""
    m = Model("path-root")
    root = m.add(ArchiType.ApplicationComponent, "Root")
    result = m.find_by_hierarchy_path("/Root")
    assert root in result


def test_find_by_hierarchy_path_nonexistent_path():
    """find_by_hierarchy_path with nonexistent path should return empty list."""
    m = Model("path-none")
    m.add(ArchiType.ApplicationComponent, "Root")
    result = m.find_by_hierarchy_path("/NonExistent")
    assert result == []


def test_find_by_hierarchy_path_multiple_matches():
    """find_by_hierarchy_path with multiple possible matches."""
    m = Model("path-multi")
    root = m.add(ArchiType.ApplicationComponent, "Root")
    child1 = m.add(ArchiType.ApplicationComponent, "Child")
    child2 = m.add(ArchiType.ApplicationComponent, "Child")  # Same name
    m.add_child(root.uuid, child1.uuid)
    m.add_child(root.uuid, child2.uuid)
    result = m.find_by_hierarchy_path("/Root/Child")
    assert len(result) == 2
    assert child1 in result
    assert child2 in result


# ---------------------------------------------------------------------------
# read() / merge() additional error handling
# ---------------------------------------------------------------------------


def test_model_read_invalid_xml(tmp_path):
    """read() with invalid XML should not raise exception."""
    xml_file = tmp_path / "invalid.xml"
    xml_file.write_text("<invalid><unclosed", encoding="utf-8")
    m = Model("invalid-xml")
    # Should not raise; XML parser is set to recover=True
    m.read(str(xml_file))


def test_model_merge_invalid_xml(tmp_path):
    """merge() with invalid XML should not raise exception."""
    xml_file = tmp_path / "invalid_merge.xml"
    xml_file.write_text("<invalid><unclosed", encoding="utf-8")
    m = Model("invalid-merge")
    # Should not raise; XML parser is set to recover=True
    m.merge(str(xml_file))


def test_model_read_empty_file(tmp_path):
    """read() with empty file should not raise exception."""
    xml_file = tmp_path / "empty.xml"
    xml_file.write_text("", encoding="utf-8")
    m = Model("empty-xml")
    # Should not raise
    m.read(str(xml_file))


def test_model_merge_empty_file(tmp_path):
    """merge() with empty file should not raise exception."""
    xml_file = tmp_path / "empty_merge.xml"
    xml_file.write_text("", encoding="utf-8")
    m = Model("empty-merge")
    # Should not raise
    m.merge(str(xml_file))


# ---------------------------------------------------------------------------
# Test check_connection() error cases (lines 805-827)
# ---------------------------------------------------------------------------


def test_check_connection_orphan_source_node():
    """Connection with orphan source node should fail."""
    m = Model("orphan-test")
    src = m.add(ArchiType.ApplicationComponent, "Src")
    dst = m.add(ArchiType.ApplicationService, "Dst")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)

    v = cast(View, m.add(ArchiType.View, "V"))
    n_src = v.add(ref=src.uuid, x=10, y=10)
    n_dst = v.add(ref=dst.uuid, x=200, y=10)
    conn = v.add_connection(rel, n_src, n_dst)

    # Corrupt source after construction
    conn._source = "missing-node-uuid"
    assert m.check_connection(conn) is False


def test_check_connection_orphan_source_concept():
    """Connection with orphan source concept should fail."""
    m = Model("orphan-concept-test")
    src = m.add(ArchiType.ApplicationComponent, "Src")
    dst = m.add(ArchiType.ApplicationService, "Dst")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)

    v = cast(View, m.add(ArchiType.View, "V"))
    n_src = v.add(ref=src.uuid, x=10, y=10)
    n_dst = v.add(ref=dst.uuid, x=200, y=10)
    conn = v.add_connection(rel, n_src, n_dst)

    # Corrupt relationship source after construction
    rel._source = "missing-element-uuid"
    assert m.check_connection(conn) is False


def test_check_connection_orphan_target_node():
    """Connection with orphan target node should fail."""
    m = Model("orphan-target-node")
    src = m.add(ArchiType.ApplicationComponent, "Src")
    dst = m.add(ArchiType.ApplicationService, "Dst")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)

    v = cast(View, m.add(ArchiType.View, "V"))
    n_src = v.add(ref=src.uuid, x=10, y=10)
    n_dst = v.add(ref=dst.uuid, x=200, y=10)
    conn = v.add_connection(rel, n_src, n_dst)

    # Corrupt target after construction
    conn._target = "missing-target-uuid"
    assert m.check_connection(conn) is False


def test_check_connection_orphan_target_concept():
    """Connection with orphan target concept should fail."""
    m = Model("orphan-target-concept")
    src = m.add(ArchiType.ApplicationComponent, "Src")
    dst = m.add(ArchiType.ApplicationService, "Dst")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)

    v = cast(View, m.add(ArchiType.View, "V"))
    n_src = v.add(ref=src.uuid, x=10, y=10)
    n_dst = v.add(ref=dst.uuid, x=200, y=10)
    conn = v.add_connection(rel, n_src, n_dst)

    # Corrupt relationship target after construction
    rel._target = "missing-element-uuid"
    assert m.check_connection(conn) is False


def test_check_connection_target_is_view():
    """Connection with missing target node returns False."""
    m = Model("view-as-target")
    src = m.add(ArchiType.ApplicationComponent, "Src")
    dst = m.add(ArchiType.ApplicationService, "Dst")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)

    v = cast(View, m.add(ArchiType.View, "V"))
    n_src = v.add(ref=src.uuid, x=10, y=10)
    n_dst = v.add(ref=dst.uuid, x=200, y=10)
    conn = v.add_connection(rel, n_src, n_dst)

    # Corrupt target to point to a view uuid (not a node)
    v2 = cast(View, m.add(ArchiType.View, "V2"))
    conn._target = v2.uuid
    assert m.check_connection(conn) is False


def test_check_connection_source_is_view():
    """Connection with missing source node returns False."""
    m = Model("view-as-source")
    src = m.add(ArchiType.ApplicationComponent, "Src")
    dst = m.add(ArchiType.ApplicationService, "Dst")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)

    v = cast(View, m.add(ArchiType.View, "V"))
    n_src = v.add(ref=src.uuid, x=10, y=10)
    n_dst = v.add(ref=dst.uuid, x=200, y=10)
    conn = v.add_connection(rel, n_src, n_dst)

    # Corrupt source to point to a view uuid (not a node)
    v2 = cast(View, m.add(ArchiType.View, "V2"))
    conn._source = v2.uuid
    assert m.check_connection(conn) is False


def test_check_connection_source_element_mismatch():
    """Connection source node element doesn't match relationship source."""
    m = Model("source-mismatch")
    src = m.add(ArchiType.ApplicationComponent, "Src")
    dst = m.add(ArchiType.ApplicationService, "Dst")
    wrong = m.add(ArchiType.ApplicationComponent, "Wrong")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)

    v = cast(View, m.add(ArchiType.View, "V"))
    n_src = v.add(ref=src.uuid, x=10, y=10)
    n_dst = v.add(ref=dst.uuid, x=200, y=10)
    conn = v.add_connection(rel, n_src, n_dst)

    # Point node at wrong element after construction
    n_src._ref = wrong.uuid
    assert m.check_connection(conn) is False


def test_check_connection_target_element_mismatch():
    """Connection target node element doesn't match relationship target."""
    m = Model("target-mismatch")
    src = m.add(ArchiType.ApplicationComponent, "Src")
    dst = m.add(ArchiType.ApplicationService, "Dst")
    wrong = m.add(ArchiType.ApplicationService, "Wrong")
    rel = m.add_relationship(ArchiType.Serving, source=src, target=dst)

    v = cast(View, m.add(ArchiType.View, "V"))
    n_src = v.add(ref=src.uuid, x=10, y=10)
    n_dst = v.add(ref=dst.uuid, x=200, y=10)
    conn = v.add_connection(rel, n_src, n_dst)

    # Point target node at wrong element after construction
    n_dst._ref = wrong.uuid
    assert m.check_connection(conn) is False


# ---------------------------------------------------------------------------
# Test check_invalid_nodes() error logging (lines 842-846)
# ---------------------------------------------------------------------------


def test_check_invalid_nodes_with_orphan_node():
    """check_invalid_nodes detects orphan nodes with unknown references."""
    m = Model("orphan-nodes")
    elem = m.add(ArchiType.ApplicationComponent, "Elem")
    v = cast(View, m.add(ArchiType.View, "V"))

    n_orphan = v.add(ref=elem.uuid, x=10, y=10)
    # Point its ref to a non-existent element to simulate orphan
    n_orphan._ref = "unknown-uuid"

    invalids = m.check_invalid_nodes()
    assert n_orphan.uuid in invalids


# ---------------------------------------------------------------------------
# Test hierarchy operations error cases (lines 948, 965-969)
# ---------------------------------------------------------------------------


def test_add_child_max_depth_exceeded():
    """add_child should raise when max depth would be exceeded."""
    from src.pyArchimate.constants import MAX_DEPTH

    m = Model("depth-test")

    # Create a chain of elements up to depth MAX_DEPTH - 1
    elem = m.add(ArchiType.ApplicationComponent, "Root")
    for i in range(MAX_DEPTH - 1):
        child = m.add(ArchiType.ApplicationComponent, f"Level{i}")
        m.add_child(elem.uuid, child.uuid)
        elem = child

    # Try to add one more child - should exceed max depth
    final = m.add(ArchiType.ApplicationComponent, "Toodeep")
    with pytest.raises(ValueError, match="Max nesting depth"):
        m.add_child(elem.uuid, final.uuid)


def test_remove_child_cleans_up_empty_parent_entry():
    """Removing last child should clean up parent's children set."""
    m = Model("cleanup-test")
    parent = m.add(ArchiType.ApplicationComponent, "Parent")
    child = m.add(ArchiType.ApplicationComponent, "Child")

    m.add_child(parent.uuid, child.uuid)
    assert parent.uuid in m._element_children

    m.remove_child(parent.uuid, child.uuid)
    # Parent entry should be removed when no more children
    assert parent.uuid not in m._element_children


def test_remove_child_with_multiple_children():
    """Removing one child should keep parent entry if other children exist."""
    m = Model("multi-child-test")
    parent = m.add(ArchiType.ApplicationComponent, "Parent")
    child1 = m.add(ArchiType.ApplicationComponent, "Child1")
    child2 = m.add(ArchiType.ApplicationComponent, "Child2")

    m.add_child(parent.uuid, child1.uuid)
    m.add_child(parent.uuid, child2.uuid)

    m.remove_child(parent.uuid, child1.uuid)

    # Parent entry should still exist
    assert parent.uuid in m._element_children
    assert child2.uuid in m._element_children[parent.uuid]
    assert child1.uuid not in m._element_children[parent.uuid]


# ---------------------------------------------------------------------------
# Test get_siblings() error case (lines 1060-1064)
# ---------------------------------------------------------------------------


def test_get_siblings_invalid_element():
    """get_siblings raises KeyError for invalid element UUID."""
    m = Model("siblings-error")
    with pytest.raises(KeyError, match="not found"):
        m.get_siblings("unknown-uuid")


def test_get_siblings_with_multiple_siblings():
    """get_siblings returns all siblings except self."""
    m = Model("siblings-test")
    parent = m.add(ArchiType.ApplicationComponent, "Parent")
    child1 = m.add(ArchiType.ApplicationComponent, "Child1")
    child2 = m.add(ArchiType.ApplicationComponent, "Child2")
    child3 = m.add(ArchiType.ApplicationComponent, "Child3")

    m.add_child(parent.uuid, child1.uuid)
    m.add_child(parent.uuid, child2.uuid)
    m.add_child(parent.uuid, child3.uuid)

    siblings = m.get_siblings(child1.uuid)
    assert len(siblings) == 2
    assert child2 in siblings
    assert child3 in siblings
    assert child1 not in siblings


# ---------------------------------------------------------------------------
# Test find_by_hierarchy_path() edge cases (lines 1048, 1079, 1095)
# ---------------------------------------------------------------------------


def test_find_by_hierarchy_path_empty_path():
    """find_by_hierarchy_path with empty string returns empty list."""
    m = Model("empty-path")
    m.add(ArchiType.ApplicationComponent, "Root")
    result = m.find_by_hierarchy_path("")
    assert result == []


def test_find_by_hierarchy_path_no_matching_elements():
    """find_by_hierarchy_path returns empty list when path doesn't match."""
    m = Model("no-match-path")
    root = m.add(ArchiType.ApplicationComponent, "Root")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    m.add_child(root.uuid, child.uuid)

    result = m.find_by_hierarchy_path("/NonExistent/Path")
    assert result == []


def test_find_by_hierarchy_path_wildcard_at_root():
    """find_by_hierarchy_path with trailing wildcard returns all children."""
    m = Model("wildcard-root")
    root = m.add(ArchiType.ApplicationComponent, "Root")
    child1 = m.add(ArchiType.ApplicationComponent, "Child1")
    child2 = m.add(ArchiType.ApplicationComponent, "Child2")

    m.add_child(root.uuid, child1.uuid)
    m.add_child(root.uuid, child2.uuid)

    result = m.find_by_hierarchy_path("/Root/*")
    assert len(result) == 2
    assert child1 in result
    assert child2 in result


def test_find_by_hierarchy_path_complex_nesting():
    """find_by_hierarchy_path handles deeply nested hierarchies."""
    m = Model("deep-nesting")
    l1 = m.add(ArchiType.ApplicationComponent, "Level1")
    l2 = m.add(ArchiType.ApplicationComponent, "Level2")
    l3 = m.add(ArchiType.ApplicationComponent, "Level3")
    l4 = m.add(ArchiType.ApplicationComponent, "Level4")

    m.add_child(l1.uuid, l2.uuid)
    m.add_child(l2.uuid, l3.uuid)
    m.add_child(l3.uuid, l4.uuid)

    result = m.find_by_hierarchy_path("/Level1/Level2/Level3/Level4")
    assert len(result) == 1
    assert l4 in result
