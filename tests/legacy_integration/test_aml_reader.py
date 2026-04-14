
from pathlib import Path

import pytest

from src.pyArchimate.pyArchimate import Model, ArchiType
from src.pyArchimate.readers.arisAMLreader import aris_reader
from src.pyArchimate.constants import ARIS_TYPE_MAP # Import the ARIS_TYPE_MAP


def test_aris_aml_reader(tmp_path: Path):
    fixtures_dir = Path(__file__).parent.with_name("fixtures")
    aml_file = fixtures_dir / "aris.aml"
    if not aml_file.exists():
        pytest.skip("aris.aml fixture is not present")

    # Create a new model and read the ARIS AML file
    model = Model("imported_aris_model")
    model.read(str(aml_file), reader=aris_reader)

    # --- Assertions for Model ---
    assert model.name == "imported_aris_model"

    # --- Assertions for Elements ---
    # Expected elements from aris.aml:
    # Business Service (ST_ARCHIMATE_BUSINESS_SERVICE)
    # Application Component (ST_ARCHIMATE_APPLICATION_COMPONENT)
    # Capability2 (ST_ARCHIMATE_CAPABILITY)
    # Capability (ST_ARCHIMATE_CAPABILITY)

    assert len(model.elements) == 4, f"Expected 4 elements, but got {len(model.elements)}"

    # Get elements by their UUIDs (generated from ObjDef.ID)
    business_service_uuid = "id-3fADlu5of3O-p-L"
    application_component_uuid = "id-5ZULEobGx8p-p-L"
    capability2_uuid = "id--1hsqjqHaKFx-p-L"
    capability_uuid = "id-7cWWqQ_hE13-p-L"

    # Assert Business Service
    business_service = model.elems_dict[business_service_uuid]
    assert business_service is not None
    assert business_service.name.strip() == "Business Service"
    assert business_service.type == ARIS_TYPE_MAP["ST_ARCHIMATE_BUSINESS_SERVICE"]
    # Check if a property exists and its content - AT_DESC is stored in .desc, not .props
    assert business_service.desc is not None
    assert "à vérifier" in business_service.desc
    assert business_service.prop('GUID') == "aceaa063-4abf-11ed-722e-0050568b2437" # Check a different property

    # Assert Application Component
    application_component = model.elems_dict[application_component_uuid]
    assert application_component is not None
    assert application_component.name.strip() == "Application Component"
    assert application_component.type == ARIS_TYPE_MAP["ST_ARCHIMATE_APPLICATION_COMPONENT"]

    # Assert Capability2
    capability2 = model.elems_dict[capability2_uuid]
    assert capability2 is not None
    assert capability2.name.strip() == "Capability2"
    assert capability2.type == ARIS_TYPE_MAP["ST_ARCHIMATE_CAPABILITY"]

    # Assert Capability
    capability = model.elems_dict[capability_uuid]
    assert capability is not None
    assert capability.name.strip() == "Capability"
    assert capability.type == ARIS_TYPE_MAP["ST_ARCHIMATE_CAPABILITY"]


    # --- Assertions for Relationships ---
    # Expected relationships from aris.aml:
    # Realizes from Business Service to Capability2 (CT_ARCHIMATE_REALIZES)
    # Realizes from Application Component to Business Service (CT_ARCHIMATE_REALIZES)
    # Composed Of from Capability to Capability2 (CT_ARCHIMATE_IS_COMPOSED_OF)

    assert len(model.relationships) == 3, f"Expected 3 relationships, but got {len(model.relationships)}"

    # Get relationships by their UUIDs (generated from CxnDef.ID)
    rel1_uuid = "id--13T5HDMwnWv-q-L" # Business Service -> Capability2 (Realizes)
    rel2_uuid = "id-4AlC6ZcCkkG-q-L" # Application Component -> Business Service (Realizes)
    rel3_uuid = "id--4ifXQL4Hsbj-q-L" # Capability -> Capability2 (Composed Of)

    # Assert Realizes relationship (Business Service -> Capability2)
    rel1 = model.rels_dict[rel1_uuid]
    assert rel1 is not None
    assert rel1.type == ARIS_TYPE_MAP["CT_ARCHIMATE_REALIZES"]
    assert rel1.source.uuid == business_service.uuid
    assert rel1.target.uuid == capability2.uuid

    # Assert Realizes relationship (Application Component -> Business Service)
    rel2 = model.rels_dict[rel2_uuid]
    assert rel2 is not None
    assert rel2.type == ARIS_TYPE_MAP["CT_ARCHIMATE_REALIZES"]
    assert rel2.source.uuid == application_component.uuid
    assert rel2.target.uuid == business_service.uuid

    # Assert Composed Of relationship (Capability -> Capability2)
    rel3 = model.rels_dict[rel3_uuid]
    assert rel3 is not None
    assert rel3.type == ARIS_TYPE_MAP["CT_ARCHIMATE_IS_COMPOSED_OF"]
    assert rel3.source.uuid == capability.uuid
    assert rel3.target.uuid == capability2.uuid

    # --- Assertions for Views ---
    assert len(model.views) == 1, f"Expected 1 view, but got {len(model.views)}"
    default_view_uuid = "id--7joDNmLaWQa-u-L"
    default_view = model.views_dict[default_view_uuid]
    assert default_view is not None
    assert default_view.name.strip() == "Default View"

    # Check some nodes in the view
    # ObjOcc.-7joDNmLaWQa-u-L-1d68ZS-zST--x-L-33-c refers to Business Service
    node1_uuid = "id--7joDNmLaWQa-u-L-1d68ZS-zST--x-L-33-c"
    # node1 (Business Service) is a direct child of default_view
    node1 = default_view.nodes_dict[node1_uuid]
    assert node1 is not None
    assert node1.ref == business_service_uuid # The node refers to the element
    # Check scaled coordinates (261 * 0.3 = 78.3 -> 78, 1072 * 0.3 = 321.6 -> 321)
    assert node1.x == 78
    assert node1.y == 321
    assert node1.w == 126 # 423 * 0.3 = 126.9 -> 126
    assert node1.h == 58 # 194 * 0.3 = 58.2 -> 58

    # ObjOcc.-7joDNmLaWQa-u-L--7Zggq7GS4PW-x-L-33-c refers to Capability
    # node2 (Capability) is a direct child of default_view
    node2_uuid = "id--7joDNmLaWQa-u-L--7Zggq7GS4PW-x-L-33-c"
    node2 = default_view.nodes_dict[node2_uuid]
    assert node2 is not None
    assert node2.ref == capability_uuid
    assert node2.x == 12 # 42 * 0.3 = 12.6 -> 12
    assert node2.y == 38 # 127 * 0.3 = 38.1 -> 38
    assert node2.w == 218 # 727 * 0.3 = 218.1 -> 218
    assert node2.h == 150 # 501 * 0.3 = 150.3 -> 150

    # ObjOcc.-7joDNmLaWQa-u-L--1mxwuFYG4oT-x-L-33-c refers to Capability2
    # node3 (Capability2) is moved to be a child of node2 (Capability)
    node3_uuid = "id--7joDNmLaWQa-u-L--1mxwuFYG4oT-x-L-33-c"

    # Assert that node3 is NOT in default_view.nodes_dict after being moved
    assert node3_uuid not in default_view.nodes_dict

    # Access node3 from its new parent node2's nodes_dict
    node3 = node2.nodes_dict[node3_uuid]
    assert node3 is not None
    assert node3.ref == capability2_uuid
    assert node3.x == 63 # 212 * 0.3 = 63.6 -> 63
    assert node3.y == 88 # 296 * 0.3 = 88.8 -> 88
    assert node3.w == 126 # 423 * 0.3 = 126.9 -> 126
    assert node3.h == 58 # 194 * 0.3 = 58.2 -> 58

    # Test nested connections and embedding logic
    # This comes from CxnOcc.-7joDNmLaWQa-u-L-7mqe2qyCIzs-y-L-34-c which is an embedding relationship
    # between Capability (node2) and Capability2 (node3)
    # The aris_reader should handle this embedding.
    # Here, node3 should be a child of node2 in the view.
    assert node3.parent.uuid == node2.uuid

    # Ensure the output file still exists and is not empty
    output_file = tmp_path / "out.xml"
    model.write(str(output_file))
    assert output_file.exists()
    assert output_file.stat().st_size > 0

