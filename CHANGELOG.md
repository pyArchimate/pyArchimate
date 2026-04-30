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
