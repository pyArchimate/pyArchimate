# pyArchimate vs ArchiMate v3 Gap Analysis

This note summarizes how `pyArchimate` aligns with the ArchiMate 3.x specification and where it falls short.

## Overall Assessment

`pyArchimate` covers the core ArchiMate 3 metamodel well enough for model scripting, file exchange, and diagram round-tripping. The implementation includes:

- the main ArchiMate concept set in `ArchiType`
- relationship validity rules in `checker_rules.yml`
- read/write support for the Open Group exchange format
- read/write support for Archi `.archimate`
- basic diagram layout, style, and organization support

It is not fully conformant to the full ArchiMate 3.x specification yet. The main gaps are:

1. one missing concept/category mapping
2. no first-class perspective/viewpoint model
3. a round-trip mismatch for influence strength metadata
4. one Archi reader bug that can drop documentation text

## Findings

### 1. Missing `BusinessInteraction` category mapping

`ArchiType` includes `BusinessInteraction`, and the relationship rules already reference it, but `checker_rules.yml` comments it out in `archi_category`.

Impact:

- `Element.__init__` checks `ARCHI_CATEGORY[elem_type]`
- creating or importing a `BusinessInteraction` can fail
- this is a real conformance gap because the concept exists in ArchiMate 3.x

Relevant code:

- `src/pyArchimate/enums.py`
- `src/pyArchimate/checker_rules.yml`
- `src/pyArchimate/element.py`

### 2. Perspectives / viewpoints are not first-class concepts

The `Model` class explicitly says perspectives are not handled. The library stores diagrams as generic `View` objects with nodes and connections, but it does not model ArchiMate viewpoints as a separate semantic layer.

Impact:

- usable for diagrams and exchange files
- not a full viewpoint-aware ArchiMate implementation
- custom viewpoints in the exchange format are not represented as domain objects

Relevant code:

- `src/pyArchimate/model.py`
- `src/pyArchimate/view.py`

### 3. Influence strength round-trip mismatch

The Open Group reader path reads `modifier` for influence strength, but the writer emits `influenceStrength`.

Impact:

- influence strength may not survive a read/write round trip consistently
- interoperability depends on which source tool produced the file

Relevant code:

- `src/pyArchimate/readers/archimateReader.py`
- `src/pyArchimate/writers/archimateWriter.py`

### 4. Archi reader drops documentation text for relationships

In `_archireader_helpers.py`, the relationship parser finds the `<documentation>` element but assigns `elem.desc = e.text` instead of `doc.text`.

Impact:

- relationship documentation can be lost or read incorrectly from Archi `.archimate` files
- this is a fidelity bug rather than a metamodel gap, but it affects actual exchange behavior

Relevant code:

- `src/pyArchimate/readers/_archireader_helpers.py`

### 5. Notation support is partial

The library preserves many diagram-level attributes such as:

- node position and size
- line and fill colors
- font settings
- bendpoints
- grouping and note nodes
- label visibility and text position

But it does not model the full ArchiMate notation surface as first-class language objects.

Impact:

- sufficient for scripting and round-tripping many diagrams
- not a complete notation engine
- some spec-level visual semantics are still abstracted away

Relevant code:

- `src/pyArchimate/view.py`
- `src/pyArchimate/writers/archimateWriter.py`
- `src/pyArchimate/readers/archimateReader.py`
- `src/pyArchimate/writers/archiWriter.py`

## Conclusion

`pyArchimate` is a practical ArchiMate 3.x model library, but it is not fully conformant yet.

The highest-priority fix is the missing `BusinessInteraction` category mapping, because it can break creation or import of a valid ArchiMate concept. After that, the round-trip fidelity issues in the readers/writers should be corrected, followed by any deeper work on viewpoints and richer notation support.
