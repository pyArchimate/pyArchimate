"""Integration tests for ArchiMate 3.x compliance round-trip fidelity.

Tests verify that elements and relationships with metadata survive
export/import cycles without loss or corruption.
"""

import tempfile
from pathlib import Path

from src.pyArchimate import ArchiType
from src.pyArchimate.model import Model


def test_business_interaction_roundtrip_archimate_format():
    """Test BusinessInteraction survives export/import cycle in .archimate format."""
    # Create: BusinessInteraction element
    m1 = Model('bi-roundtrip-archi')
    bi1 = m1.add(ArchiType.BusinessInteraction, 'Customer Interaction', desc='Main interaction')
    bi1.prop('priority', 'high')

    # Export to .archimate format
    with tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False) as f:
        temp_path = f.name
    try:
        m1.write(temp_path)

        # Import back
        m2 = Model('bi-roundtrip-reload')
        m2.read(temp_path)

        # Verify: Element exists with same properties
        assert bi1.uuid in m2.elems_dict
        bi2 = m2.elems_dict[bi1.uuid]
        assert bi2.name == 'Customer Interaction'
        assert str(bi2.type) == 'BusinessInteraction'
        assert bi2.desc == 'Main interaction'
        assert bi2.props['priority'] == 'high'
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_business_interaction_roundtrip_opengroup_format():
    """Test BusinessInteraction survives export/import cycle in OpenGroup format."""
    # Create: BusinessInteraction element
    m1 = Model('bi-roundtrip-og')
    bi1 = m1.add(ArchiType.BusinessInteraction, 'Service Interaction', desc='Service flows')

    # Export to OpenGroup exchange format
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        temp_path = f.name
    try:
        from src.pyArchimate.writers.archimateWriter import archimate_writer
        archimate_writer(m1, temp_path)

        # Import back
        m2 = Model('bi-roundtrip-og-reload')
        m2.read(temp_path)

        # Verify: Element exists with same properties
        assert bi1.uuid in m2.elems_dict
        bi2 = m2.elems_dict[bi1.uuid]
        assert bi2.name == 'Service Interaction'
        assert str(bi2.type) == 'BusinessInteraction'
        assert bi2.desc == 'Service flows'
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_influence_strength_roundtrip_archimate():
    """Test influence strength metadata survives export/import in .archimate format."""
    # Create: Influence relationship with strength
    m1 = Model('influence-roundtrip-archi')
    actor1 = m1.add(ArchiType.BusinessActor, 'Actor A')
    actor2 = m1.add(ArchiType.BusinessActor, 'Actor B')
    rel1 = m1.add_relationship(ArchiType.Influence, source=actor1, target=actor2)
    rel1.influence_strength = 'high'

    # Export to .archimate format
    with tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False) as f:
        temp_path = f.name
    try:
        m1.write(temp_path)

        # Import back
        m2 = Model('influence-roundtrip-reload')
        m2.read(temp_path)

        # Verify: Relationship has same strength
        assert rel1.uuid in m2.rels_dict
        rel2 = m2.rels_dict[rel1.uuid]
        assert rel2.influence_strength == 'high'
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_influence_strength_roundtrip_opengroup():
    """Test influence strength metadata survives export/import in OpenGroup format."""
    # Create: Influence relationship with strength
    m1 = Model('influence-roundtrip-og')
    actor1 = m1.add(ArchiType.BusinessActor, 'Actor X')
    actor2 = m1.add(ArchiType.BusinessActor, 'Actor Y')
    rel1 = m1.add_relationship(ArchiType.Influence, source=actor1, target=actor2)
    rel1.influence_strength = 'medium'

    # Export to OpenGroup format
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        temp_path = f.name
    try:
        from src.pyArchimate.writers.archimateWriter import archimate_writer
        archimate_writer(m1, temp_path)

        # Import back
        m2 = Model('influence-roundtrip-og-reload')
        m2.read(temp_path)

        # Verify: Relationship has same strength
        assert rel1.uuid in m2.rels_dict
        rel2 = m2.rels_dict[rel1.uuid]
        assert rel2.influence_strength == 'medium'
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_relationship_documentation_roundtrip():
    """Test relationship documentation survives export/import cycle."""
    # Create: Relationship with documentation
    m1 = Model('doc-roundtrip')
    elem1 = m1.add(ArchiType.ApplicationComponent, 'System A')
    elem2 = m1.add(ArchiType.ApplicationComponent, 'System B')
    rel1 = m1.add_relationship(ArchiType.Flow, source=elem1, target=elem2)
    rel1.desc = 'Handles data transfer between systems'

    # Export to .archimate format
    with tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False) as f:
        temp_path = f.name
    try:
        m1.write(temp_path)

        # Import back
        m2 = Model('doc-roundtrip-reload')
        m2.read(temp_path)

        # Verify: Relationship documentation is preserved
        assert rel1.uuid in m2.rels_dict
        rel2 = m2.rels_dict[rel1.uuid]
        assert rel2.desc == 'Handles data transfer between systems'
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_all_three_fixes_together():
    """Test all three compliance fixes working together in one model."""
    # Create model with all three features
    m1 = Model('all-features')

    # Feature 1: BusinessInteraction
    bi = m1.add(ArchiType.BusinessInteraction, 'Interaction', desc='Core interaction')

    # Feature 2: Influence relationship with strength
    actor = m1.add(ArchiType.BusinessActor, 'Actor')
    influence_rel = m1.add_relationship(ArchiType.Influence, source=bi, target=actor)
    influence_rel.influence_strength = 'high'

    # Feature 3: Relationship with documentation
    service = m1.add(ArchiType.BusinessService, 'Service')
    flow_rel = m1.add_relationship(ArchiType.Flow, source=bi, target=service)
    flow_rel.desc = 'Primary service flow'

    # Export and re-import
    with tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False) as f:
        temp_path = f.name
    try:
        m1.write(temp_path)
        m2 = Model('all-features-reload')
        m2.read(temp_path)

        # Verify all three features survived
        # Feature 1: BusinessInteraction
        assert bi.uuid in m2.elems_dict
        bi2 = m2.elems_dict[bi.uuid]
        assert str(bi2.type) == 'BusinessInteraction'
        assert bi2.desc == 'Core interaction'

        # Feature 2: Influence strength
        assert influence_rel.uuid in m2.rels_dict
        influence_rel2 = m2.rels_dict[influence_rel.uuid]
        assert influence_rel2.influence_strength == 'high'

        # Feature 3: Relationship documentation
        assert flow_rel.uuid in m2.rels_dict
        flow_rel2 = m2.rels_dict[flow_rel.uuid]
        assert flow_rel2.desc == 'Primary service flow'
    finally:
        Path(temp_path).unlink(missing_ok=True)
