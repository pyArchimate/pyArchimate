Checked the Archi adapter pair as a translator between pyArchimate’s object model and Archi’s .archimate internal persistence format.
The good part is coverage is broad: archiReader.py and archiWriter.py handle model metadata, folders, elements, relationships, profiles, views, nested diagram objects, notes, groups, diagram references, bendpoints, and most of the styling state. That is enough to round-trip a lot of real Archi files.

## Status Update (Feature 004 — ArchiMate v3.x Compliance)

**Resolved Issues:**
✅ **BusinessInteraction** — Now mapped in checker_rules.yml:99 (uncommented)
✅ **Influence Strength** — Reader now handles multiple field names (influenceStrength, modifier, strength) at _archireader_helpers.py:153-158
✅ **Relationship Documentation** — Fixed for relationships and elements; doc.text correctly assigned at lines 161, 178

**Remaining Issues:**

## Label
The nameVisible flag is read incorrectly. `bool("false")` is still True, so hidden labels can come back visible. This affects diagram connections.

    ◦ src/pyArchimate/readers/_archireader_helpers.py:115-116
    ◦ Writer side is at src/pyArchimate/writers/archiWriter.py:149-151
    
**Fix needed**: Parse string "false"/"true" to Python bool before assignment.

## View Documentation
View-level documentation is parsed incorrectly. The code finds `<documentation>` but assigns `e.text` instead of `doc.text`, so the text can be lost.

    ◦ src/pyArchimate/readers/_archireader_helpers.py:237

## Other Gaps (Lower Priority — Not in Feature 004)

- **Version Preservation**: The writer hard-codes the Archi model version to 4.9.0, so it does not preserve the source document version.
    
    ◦ src/pyArchimate/writers/archiWriter.py:303-305

- **Folder Taxonomy**: The Archi writer normalizes folder taxonomy rather than preserving it exactly. Physical concepts are pushed into Technology, junctions into Other, and the writer always rebuilds the canonical top-level folders.

    ◦ src/pyArchimate/writers/archiWriter.py:23-40
    ◦ src/pyArchimate/writers/archiWriter.py:66-78

- **Diagram Node Kinds**: The reader only knows four diagram node kinds: DiagramObject, Group, Note, and DiagramModelReference. Anything else is logged and dropped.

    ◦ src/pyArchimate/readers/_archireader_helpers.py:14-32
  
## Conclusions

**Before Feature 004**: The Archi adapter was functionally useful but had three critical bugs blocking faithful round-trip support: missing BusinessInteraction support, asymmetric influence strength handling, and lost relationship documentation.

**After Feature 004 (in progress)**: Two of three critical P1 gaps are resolved (BusinessInteraction enabled, influence strength normalized). One P1 gap remains (relationship/view documentation edge cases), plus two P0 bugs in label visibility and view documentation parsing. The adapter remains a pragmatic subset translator, but with significantly improved metadata fidelity for core ArchiMate concepts.

**Recommended Next Steps**:
1. Fix the bool("false") → True bug for connection label visibility (quick fix)
2. Fix view documentation text extraction (doc.text instead of e.text)
3. Add round-trip fidelity tests to prevent regression
4. Consider P2 work: version preservation and folder taxonomy fidelity
