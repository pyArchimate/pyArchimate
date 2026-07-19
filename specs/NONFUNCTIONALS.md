# Non-Functional Requirements

This document captures the quality attributes and system properties that must be preserved in every change, mapped back to the constitution’s principles of integrity, reliability, and consistency.

## Security

- Restrict secrets (SonarCloud token, PyPI credentials) to environment variables; never commit to source.
- Run `snyk test` and SonarCloud scans on every PR; zero BLOCKER/CRITICAL issues required before merge.
- Use `ruff S110` (suppress-exception) and `vulture --min-confidence 80` to catch dangerous patterns locally.

## Reliability & Correctness

- Round-trip fidelity is a hard requirement: export → re-import must reproduce the original model identically (same UUIDs, properties, relationships, bendpoints, annotation connectors).
- Annotation connectors (visual notes and labels) must round-trip correctly: export omits `archimateRelationship` attribute for non-backed connectors; re-import recovers Label nodes with correct positioning and styling.
- `check_invalid_conn()`, `check_invalid_nodes()`, and `check_invalid_relationships()` must pass clean before every write.
- All custom exceptions (`ArchimateConceptTypeError`, `ArchimateRelationshipError`) must propagate with a descriptive message; never swallow silently.

## Performance

- Core operations (model read/write, SVG export) should complete in under 200 ms for models up to ~500 elements; justify anything slower with async or batching.
- `auto_layout` + `auto_route` on a 100-node view should complete in under 2 seconds.

## Observability

- Use `pyArchimate.logger` (stdlib `logging`) for all diagnostic output; WARNING and above indicate actionable problems.
- Never call `logging.basicConfig()` inside library code — callers own the logging configuration.

## SVG and Visual Output

- SVG export must render all ArchiMate element types with correct symbols and positioning, including Label nodes as folded-corner sticky notes.
- Stereotype labels (`show_stereotypes=True`) must render above element names in smaller italic font without obscuring the element symbol.
- Profile styles (`apply_profile_styles`) must be applied consistently across all nodes in a view hierarchy, including nested and composite nodes.
- Annotation connectors must render correctly in SVG without throwing exceptions, even when they lack backing relationships.

## Maintainability & Testing

- Modularization is complete (`pyArchimate.py` is a shim); keep functions small and focused; cognitive complexity ≤ 15 (enforced by ruff C901 and SonarCloud S3776).
- Update `docs/diagrams/*.puml` and re-run `scripts/render_diagrams.sh` whenever module boundaries change.
- Target ≥ 80% line coverage on refactored files; enforce via `--cov-fail-under=79` in the push-stage pytest hook.
- Use conventional commits; trace every change to a feature spec/task matrix.

## Process & Automation

- Pre-commit hooks (commit-stage: ruff, ruff-format, pymarkdown, vulture; push-stage: pyright, mypy, layer-boundaries, behave, pytest) enforce quality before CI sees the code.
- `pyproject.toml` is the single source of truth for all tool configuration; CI and hooks must not duplicate or override its values.
- Use `poetry` for dependency management; keep `requirements.txt` in sync via the push-stage `requirements-sync` hook.

## Error Management

- Raise `ArchimateConceptTypeError` for invalid element/view type arguments; raise `ArchimateRelationshipError` for invalid relationship source/target combinations.
- Log warnings (not exceptions) for recoverable import issues (unknown node kinds, unrecognised XML attributes) so scripts can continue processing partial models.
