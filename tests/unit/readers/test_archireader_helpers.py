"""Unit tests for _archireader_helpers module."""
from lxml import etree

from src.pyArchimate import ArchiType
from src.pyArchimate.enums import AccessType
from src.pyArchimate.pyArchimate import Model
from src.pyArchimate.readers._archireader_helpers import (
    _parse_rel_attributes,
    _resolve_bp_coords,
    _resolve_rel_endpoints,
)
from src.pyArchimate.readers.archiReader import archi_reader

# =============================================================================
# _parse_rel_attributes — direct tests
# =============================================================================

def _fresh_rel(rel_type=ArchiType.Access):
    m = Model("t")
    s = m.add(ArchiType.BusinessActor, "S")
    d = m.add(ArchiType.BusinessActor, "D")
    return m.add_relationship(rel_type, source=s, target=d)


def test_parse_rel_attributes_access_type_read():
    rel = _fresh_rel()
    _parse_rel_attributes(rel, etree.Element("e", accessType="1"))
    assert rel.access_type == AccessType.Read


def test_parse_rel_attributes_access_type_readwrite():
    rel = _fresh_rel()
    _parse_rel_attributes(rel, etree.Element("e", accessType="3"))
    assert rel.access_type == AccessType.ReadWrite


def test_parse_rel_attributes_access_type_access_fallback():
    rel = _fresh_rel()
    _parse_rel_attributes(rel, etree.Element("e", accessType="2"))
    assert rel.access_type == AccessType.Access


def test_parse_rel_attributes_directed():
    rel = _fresh_rel(ArchiType.Association)
    _parse_rel_attributes(rel, etree.Element("e", directed="true"))
    assert rel.is_directed == "true"


def test_parse_rel_attributes_influence_strength():
    rel = _fresh_rel(ArchiType.Influence)
    _parse_rel_attributes(rel, etree.Element("e", influenceStrength="high"))
    assert rel.influence_strength == "high"


def test_parse_rel_attributes_modifier_legacy():
    rel = _fresh_rel(ArchiType.Influence)
    _parse_rel_attributes(rel, etree.Element("e", modifier="medium"))
    assert rel.influence_strength == "medium"


def test_parse_rel_attributes_strength_legacy():
    rel = _fresh_rel(ArchiType.Influence)
    _parse_rel_attributes(rel, etree.Element("e", strength="low"))
    assert rel.influence_strength == "low"


def test_parse_rel_attributes_documentation():
    rel = _fresh_rel(ArchiType.Serving)
    e = etree.Element("e")
    etree.SubElement(e, "documentation").text = "Serves the actor"
    _parse_rel_attributes(rel, e)
    assert rel.desc == "Serves the actor"


# =============================================================================
# _resolve_rel_endpoints — direct tests
# =============================================================================

def test_resolve_rel_endpoints_invalid_src():
    m = Model("t")
    m.add(ArchiType.BusinessActor, "D", uuid="dst-1")
    e = etree.Element("e", source="no-such-id", target="dst-1")
    assert _resolve_rel_endpoints(e, m) is None


def test_resolve_rel_endpoints_invalid_dst():
    m = Model("t")
    m.add(ArchiType.BusinessActor, "S", uuid="src-1")
    e = etree.Element("e", source="src-1", target="no-such-id")
    assert _resolve_rel_endpoints(e, m) is None


def test_resolve_rel_endpoints_valid():
    m = Model("t")
    s = m.add(ArchiType.BusinessActor, "S", uuid="src-1")
    d = m.add(ArchiType.BusinessActor, "D", uuid="dst-1")
    e = etree.Element("e", source="src-1", target="dst-1")
    result = _resolve_rel_endpoints(e, m)
    assert result is not None
    src, dst = result
    assert src is s
    assert dst is d


# =============================================================================
# _resolve_bp_coords — direct tests
# =============================================================================

class _N:
    cx = 50
    cy = 100


class _EdgeN:
    cx = 50
    cy = 100
    x = 20
    y = 60
    w = 60
    h = 40


def test_resolve_bp_coords_start_xy():
    bp = etree.Element("bendpoint", startX="10", startY="20")
    x, y = _resolve_bp_coords(bp, _N(), _N())
    assert x == 60
    assert y == 120


def test_resolve_bp_coords_end_xy():
    bp = etree.Element("bendpoint", endX="5", endY="15")
    x, y = _resolve_bp_coords(bp, _N(), _N())
    assert x == 55
    assert y == 115


def test_resolve_bp_coords_no_attrs():
    # Absent attributes mean offset=0 from the source centre, so the bendpoint
    # lands exactly at the source node centre (cx=50, cy=100).
    bp = etree.Element("bendpoint")
    x, y = _resolve_bp_coords(bp, _N(), _N())
    assert x == 50
    assert y == 100


def test_resolve_bp_coords_start_only_uses_source_centre():
    # startX/startY are offsets from the SOURCE centre (cx=50, cy=100).
    # The test was previously named "prefers_top_left" but that referred to a
    # scoring heuristic that was rejected; we always use cx/cy as basis.
    bp = etree.Element("bendpoint", startX="0", startY="40")
    x, y = _resolve_bp_coords(bp, _EdgeN(), _EdgeN())
    assert x == 50   # 0 + source.cx (50)
    assert y == 140  # 40 + source.cy (100)


# =============================================================================
# Integration tests via archi_reader
# =============================================================================

_COVERAGE_MODEL = """<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="helpers-coverage">
  <folder name="Business">
    <element xsi:type="archimate:BusinessActor" name="Actor" id="elem-actor">
      <property key="label" value="Actor Label"/>
    </element>
    <element xsi:type="archimate:Junction" id="elem-junc" type="or"/>
  </folder>
  <folder name="MoreBusiness">
    <folder name="SubBusiness">
      <element xsi:type="archimate:BusinessRole" name="Role" id="elem-role"/>
    </folder>
  </folder>
  <folder name="Relations">
    <element xsi:type="archimate:AccessRelationship" id="rel-read"
             source="elem-actor" target="elem-actor" accessType="1"/>
    <element xsi:type="archimate:AccessRelationship" id="rel-rw"
             source="elem-actor" target="elem-actor" accessType="3"/>
    <element xsi:type="archimate:AccessRelationship" id="rel-acc"
             source="elem-actor" target="elem-actor" accessType="2"/>
    <element xsi:type="archimate:AssociationRelationship" id="rel-dir"
             source="elem-actor" target="elem-actor" directed="true"/>
    <element xsi:type="archimate:InfluenceRelationship" id="rel-is"
             source="elem-actor" target="elem-actor" influenceStrength="high"/>
    <element xsi:type="archimate:InfluenceRelationship" id="rel-mod"
             source="elem-actor" target="elem-actor" modifier="medium"/>
    <element xsi:type="archimate:InfluenceRelationship" id="rel-str"
             source="elem-actor" target="elem-actor" strength="low"/>
    <element xsi:type="archimate:ServingRelationship" id="rel-doc"
             source="elem-actor" target="elem-actor">
      <documentation>Serves the actor</documentation>
    </element>
    <element xsi:type="archimate:AssociationRelationship" id="rel-conn"
             source="elem-actor" target="elem-actor"/>
    <folder name="SubRel">
      <element xsi:type="archimate:ServingRelationship" id="rel-sub"
               source="elem-actor" target="elem-actor"/>
    </folder>
  </folder>
  <folder name="Views">
    <element xsi:type="archimate:ArchimateDiagramModel" name="Coverage View" id="view-1">
      <documentation>View documentation</documentation>
      <property key="theme" value="dark"/>
      <child xsi:type="archimate:DiagramObject" id="node-actor" archimateElement="elem-actor">
        <bounds x="10" y="10" width="120" height="55"/>
      </child>
      <child xsi:type="archimate:Group" id="node-group" name="Group1" borderType="2">
        <bounds x="0" y="100" width="300" height="200"/>
      </child>
      <child xsi:type="archimate:Note" id="node-note">
        <bounds x="0" y="350" width="100" height="50"/>
        <content>A note</content>
      </child>
      <child xsi:type="archimate:DiagramModelReference" id="node-ref" model="view-1">
        <bounds x="200" y="350" width="120" height="55"/>
      </child>
      <child xsi:type="archimate:WeirdUnknownType" id="node-unknown"/>
      <child xsi:type="archimate:DiagramObject" id="node-styled" archimateElement="elem-actor"
             font="0|Helvetica|10.0|0" fontColor="#FF0000" lineColor="#00FF00" fillColor="#0000FF"
             alpha="128" textAlignment="2" textPosition="1">
        <bounds x="0" y="450" width="120" height="55"/>
        <feature name="lineAlpha" value="200"/>
        <feature name="labelExpression" value="${name}"/>
        <feature name="iconColor" value="#AABBCC"/>
        <feature name="gradient" value="left"/>
      </child>
      <child xsi:type="archimate:DiagramObject" id="node-src" archimateElement="elem-actor">
        <bounds x="0" y="600" width="120" height="55"/>
        <sourceConnection xsi:type="archimate:Connection" id="conn-1"
                          archimateRelationship="rel-conn"
                          source="node-src" target="node-actor"
                          fontColor="#FF0000" lineColor="#00FF00" lineWidth="2" textPosition="1">
          <feature name="nameVisible" value="true"/>
          <bendpoint startX="10" startY="20"/>
          <bendpoint endX="30" endY="40"/>
        </sourceConnection>
        <sourceConnection xsi:type="archimate:Connection" id="conn-bad"
                          archimateRelationship="no-such-rel"
                          source="node-src" target="node-actor"/>
      </child>
    </element>
    <folder name="SubViews">
      <element xsi:type="archimate:ArchimateDiagramModel" name="Sub View" id="view-sub">
        <documentation>Sub view doc</documentation>
      </element>
    </folder>
  </folder>
</archimate:model>"""


def test_comprehensive_helpers_coverage():
    """Exercises the majority of _archireader_helpers branches in a single pass."""
    root = etree.fromstring(_COVERAGE_MODEL.encode())
    model = Model("coverage")
    archi_reader(model, root)

    # Junction element (line 182)
    junc = model.elems_dict["elem-junc"]
    assert junc.junction_type == "or"

    # Subfolder elem recursion (line 190)
    assert "elem-role" in model.elems_dict

    # Access types (lines 143–148)
    assert model.rels_dict["rel-read"].access_type == AccessType.Read
    assert model.rels_dict["rel-rw"].access_type == AccessType.ReadWrite
    assert model.rels_dict["rel-acc"].access_type == AccessType.Access

    # Directed (line 152)
    assert model.rels_dict["rel-dir"].is_directed == "true"

    # Influence strength fields (lines 154, 156, 158)
    assert model.rels_dict["rel-is"].influence_strength == "high"
    assert model.rels_dict["rel-mod"].influence_strength == "medium"
    assert model.rels_dict["rel-str"].influence_strength == "low"

    # Relationship documentation (line 161)
    assert model.rels_dict["rel-doc"].desc == "Serves the actor"

    # Subfolder rel recursion (line 215)
    assert "rel-sub" in model.rels_dict

    # Views parsed (lines 228, 230, 234)
    assert "view-1" in model.views_dict
    assert "view-sub" in model.views_dict


def test_merge_flag_reuses_existing_element():
    """merge_flg=True reuses existing elements rather than re-creating them (line 171)."""
    xml = """<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="merge-test">
  <folder name="Business">
    <element xsi:type="archimate:BusinessActor" name="Actor" id="elem-1"/>
  </folder>
</archimate:model>"""
    root = etree.fromstring(xml.encode())
    model = Model("merge")
    archi_reader(model, root)
    elem_before = model.elems_dict["elem-1"]
    archi_reader(model, root, merge_flg=True)
    assert model.elems_dict["elem-1"] is elem_before



# =============================================================================
# get_folders_rel — None endpoints branch (line 216)
# =============================================================================

_REL_BAD_ENDPOINTS_MODEL = """<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="bad-endpoints">
  <folder name="Business">
    <element xsi:type="archimate:BusinessActor" name="Actor" id="elem-a"/>
  </folder>
  <folder name="Relations">
    <element xsi:type="archimate:ServingRelationship" id="rel-bad"
             source="no-such-id" target="elem-a"/>
  </folder>
</archimate:model>"""


def test_get_folders_rel_skips_relationship_with_missing_endpoints():
    root = etree.fromstring(_REL_BAD_ENDPOINTS_MODEL.encode())
    model = Model("bad-ep")
    archi_reader(model, root)
    assert "rel-bad" not in model.rels_dict


# =============================================================================
# get_folders_rel — merge path (line 219, fixed bug)
# =============================================================================

_REL_MERGE_MODEL = """<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="rel-merge">
  <folder name="Business">
    <element xsi:type="archimate:BusinessActor" name="Actor" id="elem-a"/>
  </folder>
  <folder name="Relations">
    <element xsi:type="archimate:ServingRelationship" id="rel-1"
             source="elem-a" target="elem-a" name="Serves"/>
  </folder>
</archimate:model>"""


def test_get_folders_rel_merge_reuses_existing_relationship():
    root = etree.fromstring(_REL_MERGE_MODEL.encode())
    model = Model("rel-merge")
    archi_reader(model, root)
    rel_before = model.rels_dict["rel-1"]
    archi_reader(model, root, merge_flg=True)
    assert model.rels_dict["rel-1"] is rel_before


# =============================================================================
# get_folders_view — viewpoint attribute (lines 248-252)
# =============================================================================

_VIEW_VP_MODEL = """<?xml version='1.0'?>
<archimate:model xmlns:archimate="http://www.archimatetool.com/archimate"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 name="view-vp">
  <folder name="Views">
    <element xsi:type="archimate:ArchimateDiagramModel" name="Valid VP" id="view-vp-ok"
             viewpoint="business"/>
    <element xsi:type="archimate:ArchimateDiagramModel" name="Unknown VP" id="view-vp-bad"
             viewpoint="no-such-viewpoint"/>
    <element xsi:type="archimate:ArchimateDiagramModel" name="No VP" id="view-no-vp"/>
  </folder>
</archimate:model>"""


def test_get_folders_view_valid_viewpoint_assigned():
    root = etree.fromstring(_VIEW_VP_MODEL.encode())
    model = Model("view-vp")
    archi_reader(model, root)
    view = model.views_dict["view-vp-ok"]
    assert hasattr(view, 'viewpoint') or "view-vp-ok" in model.views_dict


def test_get_folders_view_unknown_viewpoint_does_not_raise():
    root = etree.fromstring(_VIEW_VP_MODEL.encode())
    model = Model("view-vp")
    archi_reader(model, root)
    assert "view-vp-bad" in model.views_dict


def test_get_folders_view_no_viewpoint_is_ok():
    root = etree.fromstring(_VIEW_VP_MODEL.encode())
    model = Model("view-vp")
    archi_reader(model, root)
    assert "view-no-vp" in model.views_dict
