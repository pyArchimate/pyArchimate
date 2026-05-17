"""Generate a synthetic ArchiMate model matching the IT4IT complexity profile.

Proportions derived from IT4IT reference architecture (The Open Group):
  ~1250 elements, ~3000 relationships, ~195 views, ~4400 nodes, ~3400 conns

Run once to regenerate:
    poetry run python tests/fixtures/generate_synthetic_model.py
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pyArchimate as pa  # noqa: E402,N813
from pyArchimate.helpers.logging import log_set_level  # noqa: E402
from pyArchimate.writers.archimateWriter import archimate_writer  # noqa: E402
from pyArchimate.writers.archiWriter import archi_writer  # noqa: E402

log_set_level("ERROR")
random.seed(42)

OUT_XML = Path(__file__).parent / "synthetic_large.xml"
OUT_ARCHIMATE = Path(__file__).parent / "synthetic_large.archimate"

# Element type distribution matching IT4IT proportions (type, count)
ELEM_DISTRIBUTION = [
    ("Requirement", 452),
    ("Resource", 177),
    ("ApplicationService", 88),
    ("Artifact", 60),
    ("ApplicationFunction", 54),
    ("DataObject", 50),
    ("Grouping", 47),
    ("Capability", 43),
    ("ValueStream", 39),
    ("BusinessService", 38),
    ("Outcome", 36),
    ("Node", 27),
    ("BusinessEvent", 26),
    ("Stakeholder", 25),
    ("BusinessObject", 17),
    ("BusinessProcess", 14),
    ("Goal", 8),
    ("Path", 7),
    ("CourseOfAction", 6),
    ("CommunicationNetwork", 6),
    ("Plateau", 6),
    ("BusinessActor", 5),
    ("WorkPackage", 5),
    ("Deliverable", 4),
    ("BusinessRole", 2),
    ("ApplicationInterface", 2),
    ("Value", 2),
    ("ApplicationCollaboration", 1),
    ("ApplicationInteraction", 1),
    ("TechnologyInterface", 1),
    ("ImplementationEvent", 1),
]

# Relationship type distribution (type, count)
REL_DISTRIBUTION = [
    ("Realization", 1083),
    ("Composition", 650),
    ("Association", 486),
    ("Assignment", 237),
    ("Flow", 179),
    ("Serving", 154),
    ("Aggregation", 94),
    ("Access", 58),
    ("Triggering", 34),
    ("Specialization", 24),
    ("Influence", 3),
]

LAYER_GROUPS = {
    "Strategy": ["Capability", "ValueStream", "Resource", "CourseOfAction", "Outcome"],
    "Business": [
        "BusinessActor",
        "BusinessRole",
        "BusinessProcess",
        "BusinessService",
        "BusinessEvent",
        "BusinessObject",
        "Stakeholder",
        "Goal",
        "Value",
    ],
    "Application": [
        "ApplicationService",
        "ApplicationFunction",
        "ApplicationInterface",
        "ApplicationCollaboration",
        "ApplicationInteraction",
        "DataObject",
        "Artifact",
    ],
    "Technology": ["Node", "Path", "CommunicationNetwork", "TechnologyInterface"],
    "Motivation": ["Requirement", "Outcome", "Goal", "Stakeholder"],
    "Migration": ["Plateau", "WorkPackage", "Deliverable", "ImplementationEvent"],
    "Other": ["Grouping"],
}

_LAYER_FOR_TYPE: dict[str, str] = {}
for layer, types in LAYER_GROUPS.items():
    for t in types:
        _LAYER_FOR_TYPE[t] = layer


def _layer(elem_type: str) -> str:
    return _LAYER_FOR_TYPE.get(elem_type, "Other")


def _words(n: int, prefix: str) -> str:
    adjectives = [
        "Core",
        "Advanced",
        "Primary",
        "Secondary",
        "Global",
        "Local",
        "Integrated",
        "Distributed",
        "Managed",
        "Automated",
        "Enterprise",
        "Strategic",
        "Operational",
        "Service",
        "Platform",
        "Digital",
    ]
    nouns = [
        "Framework",
        "Module",
        "Component",
        "Service",
        "Process",
        "Interface",
        "Layer",
        "Engine",
        "Pipeline",
        "Registry",
        "Gateway",
        "Controller",
        "Repository",
        "Manager",
        "Provider",
        "Handler",
        "Orchestrator",
    ]
    return f"{prefix} {random.choice(adjectives)} {random.choice(nouns)} {n}"


def build_model() -> pa.Model:
    m = pa.Model("Synthetic Enterprise Architecture")
    m.prop("author", "pyArchimate synthetic generator")
    m.prop("version", "1.0.0")

    # --- Create elements ---
    elems_by_type: dict[str, list] = {}
    idx = 0
    for elem_type, count in ELEM_DISTRIBUTION:
        elems_by_type[elem_type] = []
        for i in range(count):
            name = _words(i + 1, elem_type)
            desc = f"Synthetic {elem_type} element {i + 1} in the enterprise architecture model."
            e = m.add(getattr(pa.ArchiType, elem_type), name=name, desc=desc)
            e.prop("category", _layer(elem_type))
            e.prop("index", str(idx))
            elems_by_type[elem_type].append(e)
            idx += 1

    all_elems = [e for elems in elems_by_type.values() for e in elems]

    # --- Create relationships respecting ArchiMate validity rules ---
    added_rels: list = []

    def _try_add(rel_type: str, src, tgt) -> bool:
        try:
            r = m.add_relationship(rel_type=rel_type, source=src, target=tgt)
            added_rels.append(r)
            return True
        except Exception:
            return False

    # For each rel type, try random pairs until quota met (max attempts cap)
    for rel_type, quota in REL_DISTRIBUTION:
        added = 0
        attempts = 0
        max_attempts = quota * 20
        while added < quota and attempts < max_attempts:
            src = random.choice(all_elems)
            tgt = random.choice(all_elems)
            if src is not tgt and _try_add(rel_type, src, tgt):
                added += 1
            attempts += 1

    # --- One rel-on-rel (Association targeting a Realization) ---
    realization_rels = [r for r in added_rels if str(r.type) == "Realization"]
    assoc_sources = elems_by_type.get("Requirement", []) + elems_by_type.get("Resource", [])
    if realization_rels and assoc_sources:
        ror_target = random.choice(realization_rels)
        ror_source = random.choice(assoc_sources)
        try:
            m.add_relationship(
                rel_type="Association", source=ror_source, target=ror_target, name="cross-ref association"
            )
        except Exception:  # noqa: S110
            pass

    # --- Create views (~195, each with ~22 nodes and ~17 connections) ---
    _build_views(m, all_elems, elems_by_type, added_rels)

    return m


def _build_views(m, all_elems, elems_by_type, added_rels) -> None:
    layer_names = list(LAYER_GROUPS.keys())
    for v_idx in range(195):
        layer = layer_names[v_idx % len(layer_names)]
        view_name = f"{layer} View {v_idx + 1}"
        v = m.add(pa.ArchiType.View, name=view_name)

        # Pick 18-26 elements, biased toward this layer's types
        layer_types = LAYER_GROUPS[layer]
        candidates = []
        for t in layer_types:
            candidates.extend(elems_by_type.get(t, []))
        if len(candidates) < 10:
            candidates = all_elems
        pool = random.sample(candidates, min(22, len(candidates)))

        nodes = []
        cols = 4
        for i, elem in enumerate(pool):
            x = (i % cols) * 160 + 20
            y = (i // cols) * 100 + 20
            n = v.get_or_create_node(elem, x=x, y=y, w=140, h=80, create_elem=False, create_node=True)
            if n:
                nodes.append(n)

        _build_view_connections(m, v, nodes, added_rels)


def _build_view_connections(m, v, nodes, added_rels) -> None:
    conn_rel_types = [
        "Association",
        "Composition",
        "Realization",
        "Serving",
        "Flow",
        "Assignment",
        "Aggregation",
        "Triggering",
    ]
    conns_added = 0
    attempts = 0
    while conns_added < 17 and attempts < 80 and len(nodes) >= 2:
        attempts += 1
        src_node, tgt_node = random.sample(nodes, 2)
        src_elem = m.elems_dict.get(src_node._ref)
        tgt_elem = m.elems_dict.get(tgt_node._ref)
        if src_elem is None or tgt_elem is None:
            continue
        rel_type = random.choice(conn_rel_types)
        try:
            r = m.add_relationship(rel_type=rel_type, source=src_elem, target=tgt_elem)
            added_rels.append(r)
            rtype = str(r.type).split(".")[-1]
            v.get_or_create_connection(
                rel_type=getattr(pa.ArchiType, rtype), source=src_node, target=tgt_node, create_conn=True
            )
            conns_added += 1
        except Exception:  # noqa: S110
            pass


def main():
    print("Building synthetic model...")
    m = build_model()
    print(f"  Elements : {len(m.elems_dict)}")
    print(f"  Relations: {len(m.rels_dict)}")
    print(f"  Views    : {len(m.views_dict)}")
    print(f"  Nodes    : {len(m.nodes_dict)}")
    print(f"  Conns    : {len(m.conns_dict)}")

    print(f"\nWriting {OUT_XML}...")
    m.write(str(OUT_XML), writer=archimate_writer)

    print(f"Writing {OUT_ARCHIMATE}...")
    m.write(str(OUT_ARCHIMATE), writer=archi_writer)

    print("Done.")


if __name__ == "__main__":
    main()
