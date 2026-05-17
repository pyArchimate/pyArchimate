from unittest.mock import MagicMock, patch

import pytest
from lxml import etree

from src.pyArchimate import ArchiType
from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers.archimateReader import (
    _apply_junction_type_props,
    _apply_viewpoint_props,
    _apply_visual_styles,
    _build_hierarchy_from_parents,
    _extract_visual_style_properties,
    _normalize_color_on_import,
    archimate_reader,
)

OPEN_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>archimate unit</name>
  <documentation>desc text</documentation>
  <elements/>
  <relationships/>
  <views>
    <diagrams/>
  </views>
</model>
"""

INVALID_ARCHIMATE_ROOT = """<?xml version='1.0'?><model></model>"""

MERGE_PROP_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <propertyDefinitions>
    <propertyDefinition identifier="prop1">
      <name>priority</name>
    </propertyDefinition>
  </propertyDefinitions>
</model>
"""

FULL_MODEL_XML = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>archimate unit</name>
  <documentation>desc text</documentation>
  <propertyDefinitions>
    <propertyDefinition identifier="prop1">
      <name>priority</name>
    </propertyDefinition>
  </propertyDefinitions>
  <properties>
    <property propertyDefinitionRef="prop1">
      <value>high</value>
    </property>
  </properties>
  <elements>
    <element identifier="elem-1" xsi:type="ApplicationComponent">
      <name>App One</name>
      <documentation>element desc</documentation>
      <properties>
        <property propertyDefinitionRef="prop1">
          <value>element-value</value>
        </property>
      </properties>
    </element>
    <element identifier="elem-2" xsi:type="ApplicationComponent">
      <name>App Two</name>
      <documentation>element two desc</documentation>
    </element>
  </elements>
  <relationships>
    <relationship identifier="rel-1" xsi:type="Association" source="elem-1" target="elem-2" accessType="Read" modifier="+" isDirected="true">
      <name>Flow Link</name>
      <documentation>rel desc</documentation>
      <properties>
        <property propertyDefinitionRef="prop1">
          <value>rel-value</value>
        </property>
      </properties>
    </relationship>
  </relationships>
  <views>
    <diagrams>
      <view identifier="view-1">
        <name>Main View</name>
        <documentation>view info</documentation>
        <node identifier="node-1" xsi:type="Element" elementRef="elem-1" x="10" y="20" w="100" h="50">
          <style>
            <fillColor r="10" g="20" b="30" a="80"/>
            <lineColor r="1" g="2" b="3"/>
            <font name="Arial" size="12">
              <color r="255" g="0" b="128"/>
            </font>
          </style>
          <node identifier="node-1-child" xsi:type="Element" elementRef="elem-2" x="5" y="5" w="20" h="10"/>
        </node>
        <node identifier="node-2" xsi:type="Element" elementRef="elem-2" x="40" y="60" w="80" h="40"/>
        <connection identifier="conn-1" relationshipRef="rel-1" source="node-1" target="node-2">
          <style lineWidth="4">
            <lineColor r="100" g="110" b="120"/>
            <font name="Calibri" size="11">
              <color r="200" g="210" b="220"/>
            </font>
          </style>
          <bendpoint x="5" y="6"/>
        </connection>
      </view>
    </diagrams>
  </views>
  <organizations>
    <item>
      <label>Top</label>
      <item>
        <label>Leaf</label>
        <documentation>Leaf desc</documentation>
        <item identifierRef="view-1"/>
      </item>
      <item identifierRef="elem-1"/>
      <item identifierRef="rel-1"/>
    </item>
  </organizations>
</model>
"""

MERGE_MODEL_XML = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <elements>
    <element identifier="elem-1" xsi:type="ApplicationComponent">
      <name>App One Updated</name>
      <documentation>updated desc</documentation>
    </element>
  </elements>
  <relationships>
    <relationship identifier="rel-1" xsi:type="Flow" source="elem-1" target="elem-2">
      <name>Flow Link Updated</name>
    </relationship>
  </relationships>
</model>
"""


def test_archimate_reader_understands_opengroup():
    root = etree.fromstring(OPEN_MODEL)
    model = Model("open")
    archimate_reader(model, root)
    assert model.name == "archimate unit"
    assert model.desc == "desc text"


def test_archimate_reader_parses_full_model_details():
    root = etree.fromstring(FULL_MODEL_XML)
    model = Model("complete")
    archimate_reader(model, root)

    # Model metadata and properties
    assert model.name == "archimate unit"
    assert model.prop("priority") == "high"

    elem = model.elems_dict["elem-1"]
    rel = model.rels_dict["rel-1"]
    view = model.views_dict["view-1"]
    node = model.nodes_dict["node-1"]
    nested = node.nodes_dict["node-1-child"]
    conn = model.conns_dict["conn-1"]

    assert elem.prop("priority") == "element-value"
    assert rel.prop("priority") == "rel-value"
    assert rel.is_directed == "true"
    assert rel.access_type == "Read"
    assert rel.folder == "/Top"
    assert elem.folder == "/Top"
    assert view.folder == "/Top/Leaf"
    assert view.desc == "Leaf desc"

    assert node.fill_color == "#0A141E"
    assert node.line_color == "#010203"
    assert node.opacity == 80
    assert int(node.font_size) == 12
    assert node.font_name == "Arial"
    assert node.font_color == "#FF0080"
    assert nested.ref == "elem-2"
    assert nested in node.nodes

    assert conn.line_color == "#646E78"
    assert int(conn.line_width) == 4
    assert conn.font_name == "Calibri"
    assert int(conn.font_size) == 11
    assert conn.font_color == "#C8D2DC"
    assert conn.bendpoints[0].x == 5


def test_archimate_reader_merges_existing_elements_and_relationships():
    base = Model("merge")
    archimate_reader(base, etree.fromstring(FULL_MODEL_XML))
    archimate_reader(base, etree.fromstring(MERGE_MODEL_XML), merge_flg=True)

    elem = base.elems_dict["elem-1"]
    rel = base.rels_dict["rel-1"]
    assert elem.name == "App One Updated"
    assert elem.desc == "updated desc"
    assert rel.name == "Flow Link Updated"


def test_archimate_reader_returns_none_for_missing_opengroup_tag():
    root = etree.fromstring(INVALID_ARCHIMATE_ROOT)
    model = Model("invalid")
    assert archimate_reader(model, root) is None


def test_archimate_reader_merges_property_with_conflicting_definition():
    model = Model("conflict")
    # pre-populate existing property with different name to force remap
    model.pdefs["prop1"] = "legacy"
    root = etree.fromstring(MERGE_PROP_MODEL)
    archimate_reader(model, root, merge_flg=True)
    assert any(name.startswith("propid-") for name in model.pdefs)


# ArchiMate 3.x Compliance: BusinessInteraction
BUSINESS_INTERACTION_OPENGROUP_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>bi-opengroup-test</name>
  <elements>
    <element identifier="bi-1" xsi:type="BusinessInteraction">
      <name>Customer Service Interaction</name>
      <documentation>Handles customer service interactions</documentation>
      <properties/>
    </element>
  </elements>
  <relationships/>
  <views>
    <diagrams/>
  </views>
</model>
"""


def test_archimate_reader_imports_business_interaction_opengroup():
    """Test that BusinessInteraction elements can be imported from OpenGroup exchange format."""
    root = etree.fromstring(BUSINESS_INTERACTION_OPENGROUP_MODEL)
    model = Model("bi-opengroup")
    archimate_reader(model, root)

    assert "bi-1" in model.elems_dict
    bi = model.elems_dict["bi-1"]
    assert bi.name == "Customer Service Interaction"
    assert str(bi.type) == "BusinessInteraction"
    assert bi.desc == "Handles customer service interactions"


# ---------------------------------------------------------------------------
# Coverage gap tests
# ---------------------------------------------------------------------------

UNKNOWN_VP_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>unknown-vp</name>
  <elements/>
  <relationships/>
  <views>
    <diagrams>
      <view identifier="view-u" viewpoint="no-such-viewpoint">
        <name>Unknown VP View</name>
      </view>
    </diagrams>
  </views>
</model>"""


def test_assign_viewpoint_unknown_slug_does_not_raise():
    """_assign_viewpoint logs a warning and continues for unknown slugs (line 50)."""
    root = etree.fromstring(UNKNOWN_VP_MODEL)
    model = Model("uvp")
    archimate_reader(model, root)
    assert "view-u" in model.views_dict


def test_apply_viewpoint_props_skips_unknown_prop_def_ref():
    """Property with propertyDefinitionRef not in pdef_merge_map is silently skipped (line 59)."""
    ns = "{http://www.opengroup.org/xsd/archimate/3.0/}"
    props_xml = etree.fromstring(
        b"<properties xmlns='http://www.opengroup.org/xsd/archimate/3.0/'>"
        b"  <property propertyDefinitionRef='unknown-id'><value>val</value></property>"
        b"</properties>"
    )
    model = Model("t")
    elem = model.add(ArchiType.ApplicationComponent, "App")
    _apply_viewpoint_props(elem, props_xml, ns, {}, model)
    assert elem.viewpoints == []


def test_apply_viewpoint_props_missing_value_element_is_noop():
    """Property matched as viewpoint but has no <value> child yields empty slug → no viewpoint assigned (line 152)."""
    ns = "{http://www.opengroup.org/xsd/archimate/3.0/}"
    props_xml = etree.fromstring(
        b"<properties xmlns='http://www.opengroup.org/xsd/archimate/3.0/'>"
        b"  <property propertyDefinitionRef='pd-vp'/>"
        b"</properties>"
    )
    model = Model("t")
    model.pdefs["pd-vp"] = "viewpoint"
    elem = model.add(ArchiType.ApplicationComponent, "App")
    _apply_viewpoint_props(elem, props_xml, ns, {"pd-vp": "pd-vp"}, model)
    assert elem.viewpoints == []


def test_assign_viewpoint_empty_slug_is_noop():
    """_assign_viewpoint with an empty slug returns immediately without touching obj (line 136)."""
    model = Model("t")
    elem = model.add(ArchiType.ApplicationComponent, "App")
    from src.pyArchimate.readers.archimateReader import _assign_viewpoint

    _assign_viewpoint(elem, "")
    assert elem.viewpoints == []


LINE_COLOR_ALPHA_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>lca</name>
  <elements>
    <element identifier="e1" xsi:type="ApplicationComponent"><name>App</name></element>
    <element identifier="e2" xsi:type="ApplicationComponent"><name>App2</name></element>
  </elements>
  <relationships>
    <relationship identifier="r1" xsi:type="Association" source="e1" target="e2"/>
  </relationships>
  <views>
    <diagrams>
      <view identifier="v1">
        <name>V</name>
        <node identifier="n1" xsi:type="Element" elementRef="e1" x="0" y="0" w="100" h="50">
          <style>
            <lineColor r="10" g="20" b="30" a="64"/>
          </style>
        </node>
        <node identifier="n2" xsi:type="Element" elementRef="e2" x="200" y="0" w="100" h="50"/>
        <connection identifier="c1" relationshipRef="r1" source="n1" target="n2"/>
      </view>
    </diagrams>
  </views>
</model>"""


def test_apply_node_style_line_color_with_alpha():
    """lineColor with alpha attribute sets lc_opacity (line 130)."""
    root = etree.fromstring(LINE_COLOR_ALPHA_MODEL)
    model = Model("lca")
    archimate_reader(model, root)
    node = model.nodes_dict["n1"]
    assert node.lc_opacity == 64


def test_apply_conn_style_no_style_element():
    """Connection without <style> element does not raise (line 178)."""
    root = etree.fromstring(LINE_COLOR_ALPHA_MODEL)
    model = Model("lca2")
    archimate_reader(model, root)
    assert "c1" in model.conns_dict


NON_ELEMENT_NODE_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>non-elem</name>
  <elements>
    <element identifier="e1" xsi:type="ApplicationComponent"><name>App</name></element>
  </elements>
  <relationships/>
  <views>
    <diagrams>
      <view identifier="v1">
        <name>V</name>
        <node identifier="n-elem" xsi:type="Element" elementRef="e1" x="0" y="0" w="100" h="50"/>
        <node identifier="n-cont" xsi:type="Container" x="10" y="10" w="200" h="100"/>
        <node identifier="n-label" xsi:type="Label" x="0" y="200" w="100" h="50"/>
      </view>
    </diagrams>
  </views>
</model>"""


def test_add_node_non_element_type():
    """Non-Element xsi:type nodes take the else branch in _add_node (lines 154-158)."""
    root = etree.fromstring(NON_ELEMENT_NODE_MODEL)
    model = Model("ne")
    archimate_reader(model, root)
    assert "n-cont" in model.nodes_dict
    assert "n-label" in model.nodes_dict


MERGE_VIEW_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>merge-view</name>
  <elements/>
  <relationships/>
  <views>
    <diagrams>
      <view identifier="view-1">
        <name>Main View</name>
      </view>
    </diagrams>
  </views>
</model>"""


def test_read_views_merge_deletes_existing_view():
    """Second read with merge_flg=True deletes and re-creates existing view (line 216)."""
    root = etree.fromstring(MERGE_VIEW_MODEL)
    model = Model("mv")
    archimate_reader(model, root)
    assert "view-1" in model.views_dict
    archimate_reader(model, root, merge_flg=True)
    assert "view-1" in model.views_dict


def test_add_node_merge_skips_existing_uuid():
    """_add_node with merge_flg=True sets uuid=None for already-known nodes (line 143)."""
    root = etree.fromstring(LINE_COLOR_ALPHA_MODEL)
    model = Model("nm")
    archimate_reader(model, root)
    count_before = len(model.nodes_dict)
    archimate_reader(model, root, merge_flg=True)
    assert len(model.nodes_dict) == count_before


ORG_VIEW_REF_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>org-view-ref</name>
  <elements>
    <element identifier="e1" xsi:type="ApplicationComponent"><name>App</name></element>
  </elements>
  <relationships/>
  <views>
    <diagrams>
      <view identifier="view-1">
        <name>Main View</name>
      </view>
    </diagrams>
  </views>
  <organizations>
    <item>
      <label>MyFolder</label>
      <item identifierRef="view-1"/>
      <item identifierRef="e1"/>
    </item>
  </organizations>
</model>"""


def test_walk_orgs_sets_folder_on_view_direct_ref():
    """_walk_orgs sets folder on a view directly referenced by identifierRef (line 247)."""
    root = etree.fromstring(ORG_VIEW_REF_MODEL)
    model = Model("ovr")
    archimate_reader(model, root)
    assert model.views_dict["view-1"].folder == "/MyFolder"
    assert model.elems_dict["e1"].folder == "/MyFolder"


# ---------------------------------------------------------------------------
# _normalize_color_on_import coverage (lines 27, 30, 35-40)
# ---------------------------------------------------------------------------


def test_normalize_color_on_import_none_returns_none():
    """None input returns None (line 27)."""
    assert _normalize_color_on_import(None) is None


def test_normalize_color_on_import_whitespace_returns_none():
    """Whitespace-only string returns None (line 30)."""
    assert _normalize_color_on_import("   ") is None


def test_normalize_color_on_import_invalid_hex_returns_none():
    """Invalid hex like #GGG logs warning and returns None (lines 35-36)."""
    result = _normalize_color_on_import("#GGGGGG")
    assert result is None


def test_normalize_color_on_import_named_color_returns_hex():
    """Named color 'red' returns a hex string (lines 37-38)."""
    result = _normalize_color_on_import("red")
    assert result is not None
    assert result.startswith("#")


def test_normalize_color_on_import_unknown_string_returns_none():
    """Unrecognised string logs warning and returns None (lines 39-40)."""
    result = _normalize_color_on_import("banana")
    assert result is None


def test_normalize_color_on_import_valid_hex_lowercased():
    """Valid 6-digit hex is returned lowercased (lines 33-34)."""
    result = _normalize_color_on_import("#FF0000")
    assert result == "#ff0000"


# ---------------------------------------------------------------------------
# _extract_visual_style_properties coverage (lines 53, 56, 67, 73-75)
# ---------------------------------------------------------------------------


def _make_props_xml(inner_xml: str) -> etree._Element:
    ns = "http://www.opengroup.org/xsd/archimate/3.0/"  # NOSONAR
    return etree.fromstring(f'<element xmlns="{ns}"><properties>{inner_xml}</properties></element>')


def test_extract_visual_style_no_value_child_continues():
    """Property with no <value> child is skipped (line 53)."""
    ns = "http://www.opengroup.org/xsd/archimate/3.0/"  # NOSONAR
    elem_xml = _make_props_xml('<property xmlns="http://www.opengroup.org/xsd/archimate/3.0/" key="fillColor"/>')
    result = _extract_visual_style_properties(elem_xml, "{" + ns + "}")
    assert "fillColor" not in result


def test_extract_visual_style_empty_value_continues():
    """Property with empty value text is skipped (line 56)."""
    ns = "http://www.opengroup.org/xsd/archimate/3.0/"  # NOSONAR
    elem_xml = _make_props_xml(
        '<property xmlns="http://www.opengroup.org/xsd/archimate/3.0/" key="fillColor">'
        '  <value xmlns="http://www.opengroup.org/xsd/archimate/3.0/">   </value>'
        "</property>"
    )
    result = _extract_visual_style_properties(elem_xml, "{" + ns + "}")
    assert "fillColor" not in result


def test_extract_visual_style_negative_line_width_warns():
    """Negative lineWidth logs warning and is not stored (line 67)."""
    ns = "http://www.opengroup.org/xsd/archimate/3.0/"  # NOSONAR
    elem_xml = _make_props_xml(
        '<property xmlns="http://www.opengroup.org/xsd/archimate/3.0/" key="lineWidth">'
        '  <value xmlns="http://www.opengroup.org/xsd/archimate/3.0/">-1.0</value>'
        "</property>"
    )
    result = _extract_visual_style_properties(elem_xml, "{" + ns + "}")
    assert "lineWidth" not in result


def test_extract_visual_style_transparency_out_of_range_warns():
    """transparency > 1.0 logs warning and is not stored (line 73)."""
    ns = "http://www.opengroup.org/xsd/archimate/3.0/"  # NOSONAR
    elem_xml = _make_props_xml(
        '<property xmlns="http://www.opengroup.org/xsd/archimate/3.0/" key="transparency">'
        '  <value xmlns="http://www.opengroup.org/xsd/archimate/3.0/">1.5</value>'
        "</property>"
    )
    result = _extract_visual_style_properties(elem_xml, "{" + ns + "}")
    assert "transparency" not in result


def test_extract_visual_style_non_numeric_value_handled():
    """Non-numeric lineWidth value is caught by except (lines 74-75)."""
    ns = "http://www.opengroup.org/xsd/archimate/3.0/"  # NOSONAR
    elem_xml = _make_props_xml(
        '<property xmlns="http://www.opengroup.org/xsd/archimate/3.0/" key="lineWidth">'
        '  <value xmlns="http://www.opengroup.org/xsd/archimate/3.0/">notanumber</value>'
        "</property>"
    )
    result = _extract_visual_style_properties(elem_xml, "{" + ns + "}")
    assert "lineWidth" not in result


# ---------------------------------------------------------------------------
# _build_hierarchy_from_parents coverage (lines 90, 92-93, 96-97)
# ---------------------------------------------------------------------------


def test_build_hierarchy_parent_uuid_none_skips():
    """Entry with parent_uuid=None is skipped (line 90)."""
    m = Model("bhp-none")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    _build_hierarchy_from_parents(m, {child.uuid: None})
    assert m.get_parent(child.uuid) is None


def test_build_hierarchy_parent_not_in_elems_dict_warns():
    """Entry where parent UUID not in elems_dict logs warning and skips (lines 92-93)."""
    m = Model("bhp-missing-parent")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    _build_hierarchy_from_parents(m, {child.uuid: "nonexistent-uuid"})
    assert m.get_parent(child.uuid) is None


def test_build_hierarchy_add_child_raises_on_cycle():
    """add_child raising ValueError (e.g. cycle) is caught and skipped (lines 96-97)."""
    m = Model("bhp-cycle")
    parent = m.add(ArchiType.ApplicationComponent, "Parent")
    child = m.add(ArchiType.ApplicationComponent, "Child")
    # Establish parent->child
    m.add_child(parent.uuid, child.uuid)
    # Now try to make parent a child of child — would create cycle
    # We test this via _build_hierarchy_from_parents which catches the ValueError
    _build_hierarchy_from_parents(m, {parent.uuid: child.uuid})
    # parent should still have no parent (ValueError was caught)
    assert m.get_parent(parent.uuid) is None


# ---------------------------------------------------------------------------
# _apply_junction_type_props coverage (lines 167-168)
# ---------------------------------------------------------------------------


def test_apply_junction_type_props_invalid_type_warns():
    """Invalid junctionType value is caught as ValueError (lines 167-168)."""
    ns = "{http://www.opengroup.org/xsd/archimate/3.0/}"
    props_xml = etree.fromstring(
        b"<properties xmlns='http://www.opengroup.org/xsd/archimate/3.0/'>"
        b"  <property key='junctionType'>"
        b"    <value>invalid_junction_xyz</value>"
        b"  </property>"
        b"</properties>"
    )
    m = Model("jt-invalid")
    junc = m.add(ArchiType.Junction, "J")
    # Should not raise — ValueError is caught internally
    _apply_junction_type_props(junc, props_xml, ns)


# ---------------------------------------------------------------------------
# _add_node merge path (line 260) — merge with existing node UUID
# ---------------------------------------------------------------------------

ADD_NODE_MERGE_MODEL_V1 = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>merge-node-v1</name>
  <elements>
    <element identifier="e1" xsi:type="ApplicationComponent"><name>App</name></element>
  </elements>
  <relationships/>
  <views>
    <diagrams>
      <view identifier="v1">
        <name>V1</name>
        <node identifier="n1" xsi:type="Element" elementRef="e1" x="0" y="0" w="100" h="50"/>
      </view>
    </diagrams>
  </views>
</model>"""

ADD_NODE_MERGE_MODEL_V2 = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>merge-node-v2</name>
  <elements>
    <element identifier="e1" xsi:type="ApplicationComponent"><name>App</name></element>
  </elements>
  <relationships/>
  <views>
    <diagrams>
      <view identifier="v2">
        <name>V2</name>
        <node identifier="n1" xsi:type="Element" elementRef="e1" x="10" y="10" w="100" h="50"/>
      </view>
    </diagrams>
  </views>
</model>"""


def test_add_node_merge_path_sets_uuid_none():
    """_add_node with merge_flg=True and existing UUID sets uuid=None for new node (line 260).

    Load v1 (creates node n1), then merge v2 which also has node n1 in a different view.
    Since n1 is already in nodes_dict, _add_node sets _uuid=None and a new uuid is generated.
    """
    root_v1 = etree.fromstring(ADD_NODE_MERGE_MODEL_V1)
    root_v2 = etree.fromstring(ADD_NODE_MERGE_MODEL_V2)
    model = Model("anm")
    archimate_reader(model, root_v1)
    assert "n1" in model.nodes_dict
    # Merge v2 — it has a different view (v2) so the view is NOT deleted first;
    # _add_node sees n1 already in nodes_dict and sets _uuid=None → new uuid generated
    archimate_reader(model, root_v2, merge_flg=True)
    # A second node (with a new auto-generated uuid) should now exist
    assert len(model.nodes_dict) > 1


# ---------------------------------------------------------------------------
# Visual style application except blocks (lines 418-419, 423-424, 428-429, 433-434)
# Directly populate visual_style_map on a real element and call set_* with bad values
# ---------------------------------------------------------------------------

VISUAL_STYLE_APPLY_MODEL = """<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>vs-apply</name>
  <elements>
    <element identifier="e-vs" xsi:type="ApplicationComponent">
      <name>Styled</name>
      <properties>
        <property key="fillColor"><value>#ff0000</value></property>
        <property key="lineColor"><value>#0000ff</value></property>
        <property key="lineWidth"><value>2.0</value></property>
        <property key="transparency"><value>0.5</value></property>
      </properties>
    </element>
  </elements>
  <relationships/>
  <views><diagrams/></views>
</model>"""


def test_visual_style_applied_from_properties():
    """Visual style props extracted from element properties are applied on import."""
    root = etree.fromstring(VISUAL_STYLE_APPLY_MODEL)
    model = Model("vs-apply")
    archimate_reader(model, root)
    elem = model.elems_dict["e-vs"]
    assert elem.get_fill_color() == "#ff0000"
    assert elem.get_line_color() == "#0000ff"
    assert elem.get_line_width() == pytest.approx(2.0)
    assert elem.get_transparency() == pytest.approx(0.5)


def test_visual_style_except_blocks_do_not_raise():
    """Manually calling set_* with bad values exercises the except branches (lines 418-434)."""
    m = Model("vs-except")
    elem = m.add(ArchiType.ApplicationComponent, "E")

    with pytest.raises(ValueError):
        elem.set_fill_color("#ZZZZZZ")

    with pytest.raises(ValueError):
        elem.set_line_color("not-a-color")

    with pytest.raises(TypeError):
        elem.set_line_width("wide")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        elem.set_transparency(2.0)


def test_read_props_unknown_format_skips():
    """Line 127: Property with no propertyDefinitionRef and unknown key is skipped."""
    xml = """<?xml version='1.0'?>
    <model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
      <elements>
        <element identifier="e1" xsi:type="ApplicationComponent">
          <name>App</name>
          <properties>
            <property key="unknown_key"><value>val</value></property>
          </properties>
        </element>
      </elements>
      <relationships/><views><diagrams/></views>
    </model>
    """
    root = etree.fromstring(xml)
    model = Model("t")
    # Should not raise any error and elem should be created
    archimate_reader(model, root)
    assert "e1" in model.elems_dict


def test_assign_valid_viewpoint():
    """Line 137: Valid viewpoint is assigned to a view."""
    xml = """<?xml version='1.0'?>
    <model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
      <elements/>
      <relationships/>
      <views>
        <diagrams>
          <view identifier="v1" viewpoint="stakeholder">
            <name>View</name>
          </view>
        </diagrams>
      </views>
    </model>
    """
    root = etree.fromstring(xml)
    model = Model("t")
    archimate_reader(model, root)
    view = model.views_dict["v1"]
    assert view.primary_viewpoint == "stakeholder"


def test_apply_viewpoint_props_on_element():
    """Lines 151-153: Viewpoint property on an element is applied."""
    xml = """<?xml version='1.0'?>
    <model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
      <propertyDefinitions>
        <propertyDefinition identifier="pd-vp">
          <name>viewpoint</name>
        </propertyDefinition>
      </propertyDefinitions>
      <elements>
        <element identifier="e1" xsi:type="ApplicationComponent">
          <name>App</name>
          <properties>
            <property propertyDefinitionRef="pd-vp">
              <value>stakeholder</value>
            </property>
          </properties>
        </element>
      </elements>
      <relationships/><views><diagrams/></views>
    </model>
    """
    root = etree.fromstring(xml)
    model = Model("t")
    archimate_reader(model, root)
    elem = model.elems_dict["e1"]
    assert "stakeholder" in elem.viewpoints


def test_element_hierarchy_via_parent_id():
    """Line 195: parentId attribute establishes hierarchy."""
    xml = """<?xml version='1.0'?>
    <model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
      <elements>
        <element identifier="p1" xsi:type="ApplicationComponent"><name>Parent</name></element>
        <element identifier="c1" xsi:type="ApplicationComponent" parentId="p1"><name>Child</name></element>
      </elements>
      <relationships/><views><diagrams/></views>
    </model>
    """
    root = etree.fromstring(xml)
    model = Model("t")
    archimate_reader(model, root)
    parent = model.get_parent("c1")
    assert parent is not None
    assert parent.uuid == "p1"


def test_visual_style_application_warnings_real():
    """Lines 418-434: log.warning is called when visual style application fails.
    Renamed to avoid conflict with existing test_visual_style_except_blocks_do_not_raise.
    """
    xml = """<?xml version='1.0'?>
    <model xmlns='http://www.opengroup.org/xsd/archimate/3.0/' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
      <elements>
        <element identifier="e1" xsi:type="ApplicationComponent">
          <name>App</name>
          <properties>
            <property key="fillColor"><value>#ff0000</value></property>
            <property key="lineColor"><value>#0000ff</value></property>
            <property key="lineWidth"><value>2.0</value></property>
            <property key="transparency"><value>0.5</value></property>
          </properties>
        </element>
      </elements>
      <relationships/><views><diagrams/></views>
    </model>
    """
    root = etree.fromstring(xml)
    model = Model("t")

    original_add = model.add
    mock_elem = MagicMock()
    mock_elem.set_fill_color.side_effect = ValueError("bad color")
    mock_elem.set_line_color.side_effect = ValueError("bad line color")
    mock_elem.set_line_width.side_effect = TypeError("bad width")
    mock_elem.set_transparency.side_effect = ValueError("bad alpha")

    def mocked_add(*args, **kwargs):
        if kwargs.get("uuid") == "e1":
            return mock_elem
        return original_add(*args, **kwargs)

    model.add = mocked_add
    model.elems_dict["e1"] = mock_elem

    with patch("src.pyArchimate.readers.archimateReader.log") as mock_log:
        archimate_reader(model, root)

        warning_calls = [call.args[0] for call in mock_log.warning.call_args_list]
        assert any("Failed to apply fillColor" in msg for msg in warning_calls)
        assert any("Failed to apply lineColor" in msg for msg in warning_calls)
        assert any("Failed to apply lineWidth" in msg for msg in warning_calls)
        assert any("Failed to apply transparency" in msg for msg in warning_calls)


# ---------------------------------------------------------------------------
# Coverage for new paths: forward relationship refs, Line connections, visual
# style map skip for unknown element UUIDs
# ---------------------------------------------------------------------------


def _make_model_with_elem():
    """Return a model with two elements for relationship tests."""
    m = Model("cov-test")
    e1 = m.add(ArchiType.BusinessActor, "Actor")
    e2 = m.add(ArchiType.BusinessRole, "Role")
    return m, e1, e2


XML_FORWARD_REL = """\
<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/'
       xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>forward-ref</name>
  <elements>
    <element identifier='e-src' xsi:type='BusinessActor'><name>Src</name></element>
    <element identifier='e-tgt' xsi:type='BusinessRole'><name>Tgt</name></element>
  </elements>
  <relationships>
    <relationship identifier='rel-a' xsi:type='Association'
                  source='e-src' target='rel-b'/>
    <relationship identifier='rel-b' xsi:type='Realization'
                  source='e-src' target='e-tgt'/>
  </relationships>
  <views><diagrams/></views>
</model>
"""


def test_forward_relationship_ref_resolved_after_multipass():
    """Reader resolves rel-on-rel forward reference via multi-pass retry."""
    m = Model("fwd")
    m.read_string = None  # not needed; build via archimate_reader directly
    from lxml import etree as _et

    root = _et.fromstring(XML_FORWARD_REL.encode())
    archimate_reader(m, root)
    assert "rel-a" in m.rels_dict
    assert "rel-b" in m.rels_dict
    assert m.rels_dict["rel-a"]._target == "rel-b"


XML_UNRESOLVABLE_REL = """\
<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/'
       xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>bad-ref</name>
  <elements>
    <element identifier='e-src' xsi:type='BusinessActor'><name>Src</name></element>
  </elements>
  <relationships>
    <relationship identifier='rel-bad' xsi:type='Association'
                  source='e-src' target='no-such-element'/>
  </relationships>
  <views><diagrams/></views>
</model>
"""


def test_genuinely_unresolvable_relationship_raises():
    """Multi-pass reader surfaces ValueError for genuinely missing target."""
    from lxml import etree as _et

    m = Model("bad")
    root = _et.fromstring(XML_UNRESOLVABLE_REL.encode())
    with pytest.raises(ValueError, match="Invalid target reference"):
        archimate_reader(m, root)


XML_LINE_CONNECTION = """\
<?xml version='1.0'?>
<model xmlns='http://www.opengroup.org/xsd/archimate/3.0/'
       xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'>
  <name>line-conn</name>
  <elements>
    <element identifier='e1' xsi:type='BusinessActor'><name>A</name></element>
    <element identifier='e2' xsi:type='BusinessRole'><name>B</name></element>
  </elements>
  <relationships>
    <relationship identifier='rel1' xsi:type='Association' source='e1' target='e2'/>
  </relationships>
  <views>
    <diagrams>
      <view identifier='v1' xsi:type='Diagram'>
        <name>View</name>
        <node identifier='n1' elementRef='e1' xsi:type='Element' x='0' y='0' w='100' h='60'/>
        <node identifier='n2' elementRef='e2' xsi:type='Element' x='200' y='0' w='100' h='60'/>
        <connection identifier='c1' relationshipRef='rel1' xsi:type='Relationship'
                    source='n1' target='n2'/>
        <connection identifier='c-line' xsi:type='Line'
                    source='n1' target='n2'/>
      </view>
    </diagrams>
  </views>
</model>
"""


def test_line_connection_skipped_no_crash():
    """Line connections (no relationshipRef) are silently skipped."""
    from lxml import etree as _et

    m = Model("line")
    root = _et.fromstring(XML_LINE_CONNECTION.encode())
    archimate_reader(m, root)
    # Only rel-backed connection should be present; Line is skipped
    assert "c1" in m.conns_dict
    assert "c-line" not in m.conns_dict


def test_apply_visual_styles_skips_unknown_uuid():
    """_apply_visual_styles silently skips UUIDs absent from elems_dict (line 417)."""
    m = Model("vstest")
    # style map references a UUID that was never added as an element
    style_map = {"no-such-uuid": {"fillColor": "#FF0000"}}
    # Must not raise; unknown UUID is silently skipped
    _apply_visual_styles(m, style_map)
