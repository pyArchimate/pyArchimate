## v1.5.0 (2026-05-03)

### Feat

- **feature-007**: Complete format selection and ARIS deprecation
- **writers**: implement smart file format selection and deprecate ARIS
- Add `ipykernel` dependency to `pyproject.toml` and update `poetry.lock`

### Fix

- **reader**: restore helper functions lost during rebase onto develop
- **test**: update BDD tests to handle .archimate ZIP archives
- **archimate**: preserve image associations in DiagramObject round-trip
- resolve pre-commit check failures (linting and imports)
- **writers**: correct schema location in archimateWriter OpenGroup Exchange format
- **writers**: correct OpenGroup Exchange format structure in archimateWriter
- **docs**: fix readthedocs.yaml indentation and update conf.py version

### Refactor

- Extract helper functions in _process_folder_element to reduce cognitive complexity

## v1.4.2 (2026-05-02)

### Feat

- **feature-007**: Implement smart file format selection based on file extension (.archimate for Archi native, .xml for OpenGroup Exchange)
- **feature-007**: Add comprehensive integration tests for format selection and round-trip fidelity

### Fix

- **feature-008**: Fix .archimate format reading by detecting and extracting XML from ZIP archives
- **feature-008**: Add _detect_zip_file() and _extract_xml_from_zip() methods for ZIP archive handling
- **feature-008**: Improve error messages for corrupted archives and missing model.xml entries
- **feature-008**: Preserve image associations in DiagramObject round-trip (imagePath, imagePosition, type, imageSource)
- **feature-008**: Add image properties to Node class for complete image metadata preservation
- **feature-008**: Fix visual style property preservation (fillColor, lineColor, lineWidth, transparency)
- **feature-008**: Fix junction type preservation for and/or/xor types with new junctionType property
- **feature-008**: Add backward compatibility for old xsi:type formats (AndJunction/OrJunction)
- **test**: Update BDD acceptance tests to handle .archimate ZIP archives in test parsing
- **ci**: guard publish job to only run on tag pushes
- **ci**: apply same Poetry/encoding fixes to release workflow
- **feature-007**: Fix OpenGroup Exchange XML schema location (archimate3.xsd at 3.0 namespace)

### Deprecated

- **ARIS AML format**: ARIS format support (arisAMLreader) is deprecated and will be removed in v1.5.0
  - Legacy tests moved to test_legacy_* files
  - Use archimateReader (OpenGroup format, .xml) or archiReader (Archi native, .archimate) instead
  - ARIS_type_map removed from public API

## v1.4.1 (2026-05-02)

### Fix

- **ci**: fix Windows Python version mismatch and behave UTF-8 encoding

## v1.4.0 (2026-05-02)

### Feat

- **T001**: Create parse_bool() and image helpers in parsing module

### Fix

- extend ruff linting to tests and fix exception handling
- **ci**: Update CI workflows to specify Python 3.12 and improve caching strategy
- **typing**: Add type annotation for element parameter in extract_images_from_archimate
- **exports**: Export parse_bool from helpers.parsing in __init__.py
- **T002,T003**: Fix label visibility boolean parsing in reader and writer
- **ci**: update cache condition for Python versions below 3.14 fix(release): correct tag pattern to match patch versions

## v1.3.0 (2026-05-02)

### Feat

- enhance model initialization and relationship handling with edge case tests
- Complete BDD test implementations for visual styling and integration
- Complete Phase 8 - Sphinx Documentation for P3 Features
- Complete Phase 7 - BDD Acceptance Tests & Documentation
- Phase 6 - Advanced features and performance optimization
- Phase 5 - Complete junction semantics implementation
- Complete Phase 4 - Writer Integration & Round-Trip Fidelity Validation
- Complete Phase 3 - Reader Integration for hierarchy and visual styles
- Implement XML import/export for element hierarchy and visual styling
- Complete P3 Phase 2 — Core Element Grouping & Visual Style Implementation
- Complete ArchiMate v3.x specification compliance (P1+P2)
- **ai-docs**: implement US2–US4 — tutorial, idempotency test, README links, maintainer docs
- **ai-docs**: implement US1 — AI.md, generation script, and test suite

### Fix

- **scripts**: make ANTHROPIC_API_KEY optional when claude CLI is already authenticated
- **element**: use startswith instead of slice comparison to resolve S6659
- **view**: rename iconColor field to snake_case icon_color to resolve S116
- **view**: use union type expression for type hints to resolve S6546
- Resolve ambiguous BDD steps and fix get_ancestors() semantics
- Add type annotation to results list in find_by_hierarchy_path
- **ci**: suppress SonarCloud version-pinning warnings and fix S8541 with --no-root
- reverse broken tests
- **meta**: correct license to GPL-3.0, Python badge to 3.10+, add SonarCloud/RTD badges, fix RTD theme dep
- **ci**: suppress SonarCloud version-pinning warnings and fix S8541 with --no-root

### Refactor

- remove unused variables in view tests for clarity
- remove unused variables in tests and update pyproject.toml for ruff compatibility
- **writers**: extract helpers to reduce S3776 complexity in _write_elements
- **readers**: extract helpers to reduce S3776 complexity in _read_elements and _read_views
- **readers**: extract _apply_elem_property to reduce S3776 complexity in _archireader_helpers

## v1.2.1 (2026-05-01)

### Feat

- **P3: Complete ArchiMate Notation Support** - Major feature release with element grouping, visual styling, junction semantics, and advanced queries

#### Element Hierarchy & Grouping
- Parent-child relationships for organizing elements into logical groups
- `Model.add_child()`, `Model.remove_child()` with automatic cycle detection
- Orphaning on deletion: children remain when parent is deleted
- Max depth limit (default 5 levels, configurable)

#### Hierarchy Queries
- `Model.get_parent()`, `Model.get_children()`, `Model.get_ancestors()`, `Model.get_descendants()`
- `Model.get_depth()`, `Model.get_root_elements()`, `Model.get_leaf_elements()`

#### Advanced Queries  
- `Model.get_siblings(elem_uuid)` - get elements with same parent
- `Model.find_by_hierarchy_path(path)` - hierarchy path queries with wildcard support

#### Visual Styling (Colors & Transparency)
- `Element.set_fill_color()`, `Element.set_line_color()` - hex or named colors
- `Element.set_line_width()`, `Element.set_transparency()` - numeric properties
- `Element.set_visual_style()`, `Element.get_visual_style()` - bulk operations
- `Element.reset_visual_style()` - reset to defaults
- Support for hex (#RRGGBB) and named colors with automatic normalization

#### Junction Type Semantics
- `Element.set_junction_type()`, `Element.get_junction_type()` - AND/OR/XOR support
- Case-insensitive validation for junction types
- Round-trip preservation in XML export/import

#### Round-Trip Fidelity & Testing
- 100% preservation of all P3 features (hierarchy, visual styles, junction types)
- 115+ comprehensive unit tests covering all features
- 15+ BDD acceptance tests validating user workflows
- 10 performance benchmark tests (cycle detection <1ms, queries <10ms)
- Integration tests for complex scenarios with mixed features

### Breaking Changes

None. All new features are additive and fully backward compatible.

### Technical Details

- Full mypy/pyright type annotation compliance
- 95%+ code coverage for new features
- Performance optimized: O(depth) cycle detection, O(n) sibling/path queries
- XML round-trip validation: all properties preserved exactly

## v1.2.0 (2026-05-01)

### Feat

- Complete ArchiMate v3.x specification compliance (P1+P2) (#51)

## v1.1.0 (2026-05-01)

### Feat

- enable ArchiMate 3.x spec compliance

### Fix

- **test**: resolve all 18 open SonarCloud issues on PR #47
- **test**: add missing NOSONAR tags in test_archimateWriter
- **test**: mark SonarCloud false positives in business_interaction_steps
- **test**: mark SonarCloud false positives in test_archiWriter
- **test**: correct namespace assertion in BDD ArchiMate export step
- **compliance**: address SonarCloud hotspots and add helper coverage
- **ci**: set PYTHONUTF8=1 to prevent UnicodeEncodeError on Windows
- **tests**: replace unused local variables with _ (S1481)
- resolve SonarCloud CRITICAL and MAJOR issues

### Refactor

- rename spec from 003 to 004
- **tests**: suppress S5332 false positives for XML namespace URIs
- modernize bash scripts and update poetry.lock

## v1.0.1 (2026-04-30)

### Fix

- resolve 5 major SonarQube violations
- resolve 3 critical SonarQube violations
- suppress S5332 false positive on XML namespace URIs
- sonarqube errors
- restore Model expand_props support broken during S3776 refactoring
- **security**: resolve S5852 ReDoS hotspot in model.py
- resolve 3 new SonarQube violations introduced in PR #37
- resolve S3776 cognitive complexity violations across all modules
- **tests**: resolve S5727 identity check violations in unit tests
- legacy tests missed by pre-push hook

### Refactor

- complete decommissioning of _legacy.py and update dependencies

## v1.0.0 (2026-04-20)

### Feat

- add view facade and prep legacy extraction
- add modularize model spec
- add pluggable writer registry

### Fix

- **writers**: use startswith instead of slice comparison (S6659)
- resolve MAJOR code smell violations (S3358 S1172)
- **readers**: extract duplicate error string to constant (S1192)
- **bdd**: add comment to placeholder step function (S1186) (T017)
- **writers**: extract duplicate string literal to constant (S1192) (T015)
- **tests**: suppress S5727 false positives on lxml find() assertions (T004/T005)
- **sonar**: exclude legacy tests from sonarcloud analysis (T001)
- eliminate stale Relationship class cache in embed_props/expand_props
- **deps**: upgrade requests to 2.33.1 and remove pysonar
- resolve all linting, type-checking, and test failures
- **aml_reader**: correct type casting for position and size calculations in ARIS AML reader test
- **model**: stop implicit defaultdict creation
- use doc entity in decription field if exists

### Refactor

- reduce cognitive complexity in helpers and writers (S3776 S1192)
- **readers**: reduce cognitive complexity below 15 (S3776) (T013-T014)
- **writers**: reduce cognitive complexity below 15 (S3776) (T011-T012)
- **element,view**: reduce cognitive complexity below 15 (S3776) (T006-T010)
- complete modular model split with full linting compliance
- import statements and add relationship module
- consolidate model reader logic
