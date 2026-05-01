from lxml import etree

from src.pyArchimate import ArchiType
from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers.archimateReader import _apply_viewpoint_props, archimate_reader

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
    model = Model('open')
    archimate_reader(model, root)
    assert model.name == 'archimate unit'
    assert model.desc == 'desc text'


def test_archimate_reader_parses_full_model_details():
    root = etree.fromstring(FULL_MODEL_XML)
    model = Model('complete')
    archimate_reader(model, root)

    # Model metadata and properties
    assert model.name == 'archimate unit'
    assert model.prop('priority') == 'high'

    elem = model.elems_dict['elem-1']
    rel = model.rels_dict['rel-1']
    view = model.views_dict['view-1']
    node = model.nodes_dict['node-1']
    nested = node.nodes_dict['node-1-child']
    conn = model.conns_dict['conn-1']

    assert elem.prop('priority') == 'element-value'
    assert rel.prop('priority') == 'rel-value'
    assert rel.is_directed == 'true'
    assert rel.access_type == 'Read'
    assert rel.folder == '/Top'
    assert elem.folder == '/Top'
    assert view.folder == '/Top/Leaf'
    assert view.desc == 'Leaf desc'

    assert node.fill_color == '#0A141E'
    assert node.line_color == '#010203'
    assert node.opacity == 80
    assert int(node.font_size) == 12
    assert node.font_name == 'Arial'
    assert node.font_color == '#FF0080'
    assert nested.ref == 'elem-2'
    assert nested in node.nodes

    assert conn.line_color == '#646E78'
    assert int(conn.line_width) == 4
    assert conn.font_name == 'Calibri'
    assert int(conn.font_size) == 11
    assert conn.font_color == '#C8D2DC'
    assert conn.bendpoints[0].x == 5


def test_archimate_reader_merges_existing_elements_and_relationships():
    base = Model('merge')
    archimate_reader(base, etree.fromstring(FULL_MODEL_XML))
    archimate_reader(base, etree.fromstring(MERGE_MODEL_XML), merge_flg=True)

    elem = base.elems_dict['elem-1']
    rel = base.rels_dict['rel-1']
    assert elem.name == 'App One Updated'
    assert elem.desc == 'updated desc'
    assert rel.name == 'Flow Link Updated'


def test_archimate_reader_returns_none_for_missing_opengroup_tag():
    root = etree.fromstring(INVALID_ARCHIMATE_ROOT)
    model = Model('invalid')
    assert archimate_reader(model, root) is None


def test_archimate_reader_merges_property_with_conflicting_definition():
    model = Model('conflict')
    # pre-populate existing property with different name to force remap
    model.pdefs['prop1'] = 'legacy'
    root = etree.fromstring(MERGE_PROP_MODEL)
    archimate_reader(model, root, merge_flg=True)
    assert any(name.startswith('propid-') for name in model.pdefs)


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
    ns = '{http://www.opengroup.org/xsd/archimate/3.0/}'
    props_xml = etree.fromstring(
        b"<properties xmlns='http://www.opengroup.org/xsd/archimate/3.0/'>"
        b"  <property propertyDefinitionRef='unknown-id'><value>val</value></property>"
        b"</properties>"
    )
    model = Model("t")
    elem = model.add(ArchiType.ApplicationComponent, "App")
    _apply_viewpoint_props(elem, props_xml, ns, {}, model)
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
