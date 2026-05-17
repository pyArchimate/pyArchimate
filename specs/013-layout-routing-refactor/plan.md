# Implementation Plan: Auto-Layout and Auto-Routing Separation

**Branch**: `013-layout-routing-refactor` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-layout-routing-refactor/spec.md`

## Summary

Phase 2 quality improvements for `auto_layout` / `auto_route` plus new `View.duplicate()` method. Remediates all CRITICAL, HIGH, and MEDIUM findings from `/speckit-analyze` (2026-05-15). Core changes: multi-pass routing (FR-016), 25px node avoidance zone (FR-013 updated), 20px min segment gap (FR-015 updated), 40px post-L-turn floor (FR-024 new), `View.duplicate()` (FR-025 new).

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: lxml (XML I/O), existing pyArchimate view model (`src/pyArchimate/`)  
**Storage**: File I/O only — `.archimate` archives (zip+XML)  
**Testing**: pytest (unit/integration), behave (BDD acceptance)  
**Target Platform**: Cross-platform library (Linux/macOS/Windows)  
**Project Type**: Library  
**Performance Goals**: `auto_layout` ≤ 2s / 500 nodes (SC-001); `auto_route` ≤ 3s / 500 nodes + 1000 connections (SC-005; all multi-pass passes combined)  
**Constraints**: No external solver deps; pure-Python geometry; deterministic output  
**Scale/Scope**: Views up to 500 nodes / 1000 connections

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| I. Code Quality | PASS | Geometry helpers extracted to focused modules; `_enforce_min_turn_segment` ≤ 30 lines |
| **II. Testing Standards** | **FIXED** | All task groups now TDD-ordered (tests-first, confirm-fail, implement, confirm-pass). Previously CRITICAL violation; resolved in task reorder. |
| III. UX Consistency | PASS | `RoutingConfig` defaults backward-compat; new fields optional with documented defaults |
| IV. Performance | PASS | SC-005 target 3s retained; P2-T21 updated to assert ≤ 3s |
| V–IX | PASS | No violations detected |

## Analysis Remediation Log

Findings from `/speckit-analyze` run 2026-05-15 and how each was resolved:

| Finding | Severity | Resolution | Artifact(s) Updated |
|---------|----------|------------|---------------------|
| C1: TDD order violated across all fix groups | CRITICAL | Reordered all task tables: test tasks before impl tasks | phase2-routing-quality.md, tasks.md |
| C2: SC-005 (3s) conflicts with P2-T21 (5s) | CRITICAL | Updated P2-T21 target to ≤ 3s; added SC-005 clarifying note about multi-pass | spec.md, phase2-routing-quality.md |
| H1: tasks.md Phase 2 not in checklist format | HIGH | Added Phases 2E–2I as `- [ ]` checklist blocks to tasks.md; parseable by /speckit-implement | tasks.md |
| H2: data-model.md RoutingConfig stale | HIGH | Replaced RoutingConfig block with all 9 fields + validation rules | data-model.md |
| M1: _detect_node_crossings must use inflated AABB | MEDIUM | Added dependency note to P2-T14; flagged `dict[str, InflatedAABB]` type annotation | phase2-routing-quality.md |
| M2: _enforce_min_turn_segment breaks on terminal arrival segment | MEDIUM | Added FR-024 exception clause; updated SC-012; added test case in P2-T46(d) | spec.md, phase2-routing-quality.md, tasks.md |
| M3: ObstacleMap stale after node move | MEDIUM | Added P2-T55 `rebuild_for_moved_nodes`; updated `_apply_node_move` to call it; added to data-model.md | spec.md (auto_route flow), data-model.md, phase2-routing-quality.md, tasks.md |
| M4: View.duplicate() model=None unspecified | MEDIUM | Added FR-025 exception clause (`ValueError`); added edge case test in P2-T52(e) | spec.md, tasks.md |
| M5: ObstacleMap._routed field missing from data-model | MEDIUM | Added `_routed` field + `mark/unmark_routed_segment` + `rebuild_for_moved_nodes` to ObstacleMap entity | data-model.md |
| M6: Second _enforce_min_turn_segment pass needed after _fix_u_turns | MEDIUM | Added pipeline order note; wired P2-T45 to call helper twice; updated auto_route flow diagram | spec.md (data-model), phase2-routing-quality.md (Fix 9), tasks.md (Phase 2G) |

## Project Structure

### Documentation (this feature)

```text
specs/013-layout-routing-refactor/
├── plan.md                    # This file
├── spec.md                    # Feature spec (updated with FR-024, FR-025, SC-012, SC-013)
├── research.md                # Phase 0 research (stable)
├── data-model.md              # Updated: RoutingConfig (9 fields), ObstacleMap (_routed, rebuild)
├── quickstart.md              # API usage examples
├── phase2-routing-quality.md  # Phase 2 design rationale + TDD-ordered task tables (P2-T01–T55)
└── tasks.md                   # Authoritative checklist (T001–T059 complete; P2-T32–T55 pending)
```

### Source Code

```text
src/pyArchimate/
├── layout/
│   ├── auto_layout.py          # FR-001–008 (Phase 1 complete)
│   ├── auto_route.py           # FR-010–023; Phase 2: multi-pass, clearance, gap, turn pipeline
│   ├── routing_config.py       # RoutingConfig: 9 fields with __post_init__ validation
│   └── geometry.py             # _enforce_min_turn_segment, _merge_collinear_adjacent, _fix_u_turns
├── view.py                     # FR-025: View.duplicate()
└── ...

tests/
├── unit/
│   ├── test_node_clearance.py  # P2-T34, T36
│   ├── test_segment_separation.py  # P2-T40, T41
│   ├── test_geometry.py        # P2-T46, T47
│   └── test_view_duplicate.py  # P2-T51, T52
├── integration/
│   ├── test_tutorial_svg_requirements.py  # P2-T35, T48 — SC-006, SC-008, SC-012
│   └── test_view_duplicate.py  # P2-T53
└── features/
    ├── routing/
    │   ├── node_clearance.feature   # P2-T37
    │   ├── segment_gap.feature      # P2-T42
    │   └── turn_segment.feature     # P2-T49
    └── view/
        └── view_duplicate.feature   # P2-T54
```

**Structure Decision**: Single project layout. Routing logic in `src/pyArchimate/layout/`; `View.duplicate()` in existing `view.py`.

## Phase 0: Research Decisions

| Question | Decision | Rationale |
|----------|----------|-----------|
| SC-005 vs multi-pass overhead | Keep 3s target; multi-pass re-routes conflicted connections only (~10–20% of typical diagram) so overhead is < 20% | Avoids spec regression; verified by P2-T21 |
| Terminal arrival segment exception (M2) | Skip `_enforce_min_turn_segment` on last segment to avoid displacing endpoint | Extending the arrival segment pushes the endpoint off the target node attachment point |
| ObstacleMap stale after node move (M3) | `rebuild_for_moved_nodes` patches `cells` in-place (remove old AABB, insert new AABB) | Full rebuild is O(n nodes) every move; patch is O(node_clearance²/resolution²) per moved node |
| `View.duplicate()` with model=None (M4) | Raise `ValueError` | Registering in model.views is the primary post-condition; silent skip would hide caller errors |
| Second enforce pass (M6) | Run `_enforce_min_turn_segment` after `_fix_u_turns` | U-turn fix can shorten a previously-conforming post-turn segment; second pass catches this |

## Phase 1: Design & Contracts

### Updated `RoutingConfig` (9 fields)

```python
@dataclass
class RoutingConfig:
    node_clearance: int = 25             # FR-013
    min_segment_gap: float = 20.0        # FR-015
    min_turn_segment: int = 40           # FR-024
    corner_clearance_pct: float = 0.10   # FR-017
    corner_clearance_min: float = 4.0    # FR-017
    crossing_penalty: float = 1.0        # FR-016
    max_routing_passes: int = 3          # implementation detail
    allow_node_move: bool = False        # FR-023
    max_node_displacement: int = 1       # FR-023
```

### Post-processing pipeline order (M6 resolved)

```
_merge_collinear_adjacent
  → _enforce_min_turn_segment (pass 1)
  → _fix_u_turns
  → _enforce_min_turn_segment (pass 2)
  → _displace_collinear_overlaps
```

### `View.duplicate()` contract

```python
def duplicate(self, name: str | None = None) -> "View":
    """
    Raises: ValueError if self.model is None.
    Returns: new View registered in self.model.views, with new UUID.
    Guarantees: len(dup.nodes)==len(orig.nodes), len(dup.connections)==len(orig.connections),
                waypoints deep-copied, original view unchanged.
    """
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| Two `_enforce_min_turn_segment` calls per route (M6) | `_fix_u_turns` can shorten post-turn segments | Single pass misses segments shortened by U-turn fix; O(segments) cost is negligible |
| `ObstacleMap.rebuild_for_moved_nodes` (M3) | Node moves invalidate static obstacle cells | Full map rebuild is O(n) per move; patch is O(clearance_area) per moved node |
