## v1.3.0 (2026-05-01)

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
