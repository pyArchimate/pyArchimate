# Non-Beta (Production) Release Roadmap

**Current Status**: Beta-Ready ✅  
**Target**: Production Release (v1.0)  
**Estimated Effort**: 130-185 hours (4-6 weeks at current velocity)

---

## Gap Analysis: Beta → Production

### 1. Performance Requirements ⚠️ CRITICAL BLOCKER

**Current Status**:

```
✅ 50 nodes:   458ms (meets <2s target)
✅ 100 nodes:  1824ms (just within <2s budget)
✗ 300 nodes:  8500ms (4.2x over target)
✗ 500 nodes:  23.9s (unacceptable for production)
```

**Non-Beta Target**: All sizes must meet <2s for 300 nodes, <5s for 500 nodes

**Work Required** (T099-T103, extended):
- Implement spatial hashing or quad-tree for O(n²) → O(n log n) conversion
- Vectorize force calculations using NumPy/SIMD
- Profile and optimize inner loops
- Cache distance calculations
- **Effort**: 30-40 hours
- **Blocker Status**: YES - Required before production release

### 2. Code Coverage Gap

**Current**: 79%  
**Non-Beta Target**: 90%+ (production standard)  
**Gap**: +11% coverage needed

**Uncovered Areas**:
- `svg_export.py`: 9% coverage (453 lines, 411 missed)
- `hierarchical.py`: 11% uncovered (127 lines)
- `graph.py`: 77% uncovered (utility functions)
- Edge cases in force-directed algorithm

**Work Required**:
- Add unit tests for svg_export components
- Increase hierarchical algorithm test coverage
- Test edge cases and error paths
- **Effort**: 20-30 hours

### 3. BDD Acceptance Test Coverage

**Current**: 52 scenarios passing, 309 undefined steps

**Missing Step Implementations by Feature**:
| Feature | Total Steps | Undefined | Priority |
|---------|------------|-----------|----------|
| auto_format.feature | 20 | 12 | High |
| auto_layout.feature | 27 | 18 | High |
| customize_layout.feature | 25 | 15 | High |
| svg_export.feature | 45 | 30 | High |
| P3 features | 150+ | 100+ | Medium |
| Business interaction | 60 | 50 | Medium |
| Relationship documentation | 30 | 20 | Low |
| Other features | 309 | 309 | Medium |

**Work Required**:
- Implement step definitions for all features
- Ensure acceptance criteria are testable
- Create step helper functions to reduce duplication
- **Effort**: 40-60 hours

### 4. Phase 8 Features (Not Required for Core, but Expected in v1.0)

**T106-T109: Locked Element Support**
- Enable users to pin elements during layout
- Respect locked positions in both force-directed and hierarchical algorithms
- **Effort**: 15-20 hours

**T110-T114: Label Collision Avoidance**
- Detect overlapping connection labels
- Reposition labels to avoid collisions
- Fallback strategies for constrained layouts
- **Effort**: 15-20 hours

### 5. Documentation Completion

**Current**: 96% (4 major documents complete)  
**Missing**:
- T091: Update Sphinx index.rst to include layout feature
- T092: Update Sphinx API documentation
- T093: Build Sphinx HTML docs
- T094: Verify build output and links

**Effort**: 5-10 hours

### 6. Security & Quality Infrastructure

**Currently Disabled** (commented out in pre_push_checks.sh):
- SonarQube code quality audit
- Snyk security vulnerability scanning

**Work Required**:
- Configure SonarQube integration
- Enable and pass security scanning
- Address any flagged issues
- **Effort**: 5-10 hours

---

## Implementation Roadmap

### Phase 1: Performance (Weeks 1-2) - CRITICAL PATH
**T099-T103 Extended**: Algorithm optimization
- [ ] Profile force-directed for bottlenecks
- [ ] Implement spatial hashing (O(n log n))
- [ ] Vectorize distance calculations
- [ ] Cache and optimize inner loops
- [ ] Validate <2s target for 300 nodes
- [ ] Benchmark 500 nodes <5s
- **Effort**: 30-40 hours

### Phase 2: Coverage & Quality (Weeks 2-3)
- [ ] Add svg_export unit tests (11 hours)
- [ ] Increase hierarchical coverage (8 hours)
- [ ] Test graph utilities (5 hours)
- [ ] Test edge cases and error paths (6 hours)
- [ ] Enable SonarQube + fix issues (5 hours)
- [ ] Achieve 90%+ coverage
- **Effort**: 35 hours

### Phase 3: BDD Acceptance Tests (Weeks 3-5)
**High Priority** (30 hours):
- [ ] auto_format.feature steps (8 hours)
- [ ] auto_layout.feature steps (10 hours)
- [ ] customize_layout.feature steps (7 hours)
- [ ] svg_export.feature steps (5 hours)

**Medium Priority** (20 hours):
- [ ] P3 features steps (12 hours)
- [ ] Business interaction steps (8 hours)

**Total Effort**: 40-60 hours

### Phase 4: Phase 8 Features (Weeks 5-6)
- [ ] T106-T109: Locked element support (15-20 hours)
- [ ] T110-T114: Label collision avoidance (15-20 hours)
- **Total Effort**: 30-40 hours

### Phase 5: Documentation & Polish (Week 6)
- [ ] T091-T094: Complete Sphinx docs (5-10 hours)
- [ ] Enable full security scanning (5 hours)
- [ ] Final validation and release prep (5 hours)
- **Total Effort**: 15 hours

---

## Success Criteria for Production Release

### Mandatory (Blocking)
- [ ] Performance: ✅ <2s for 300 nodes, <5s for 500 nodes
- [ ] Coverage: ✅ 90%+ test coverage
- [ ] Pre-push checks: ✅ All tests passing
- [ ] Code quality: ✅ SonarQube Grade A
- [ ] Security: ✅ Zero critical vulnerabilities (Snyk)

### Expected (High Value)
- [ ] BDD tests: ✅ 100% scenarios with step definitions (52+ scenarios)
- [ ] Phase 8 features: ✅ Locked elements + label collision
- [ ] Documentation: ✅ Complete Sphinx HTML build

### Nice-to-Have (Low Priority)
- [ ] Advanced optimizations (caching, parallelization)
- [ ] Extended BDD scenarios for edge cases
- [ ] Performance benchmarking dashboard

---

## Effort Summary

```
Performance Optimization (CRITICAL)  : 30-40 hours
Code Coverage Increase               : 20-30 hours
BDD Step Implementations             : 40-60 hours
Phase 8 Features                     : 30-40 hours
Documentation & Security             : 10-15 hours
---
TOTAL                                : 130-185 hours (4-6 weeks)
```

### Velocity Baseline
- Current: ~25 hours per week
- Projected: 5-7 weeks for full production readiness

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Performance optimization complex | High | Start early, use profiling tools, consider external libraries |
| BDD step implementations scope creep | Medium | Prioritize high-value scenarios first, reuse step helpers |
| Spatial hashing implementation difficulty | High | Consider using existing library (e.g., spatial-hash) |
| Integration with security tools | Low | Use documented integrations (SonarQube, Snyk) |

---

## Recommendations

1. **Start with Performance** (blocking criterion)
   - Cannot ship production without meeting performance targets
   - Allocate 30-40 hours upfront

2. **Parallel Path**: Coverage & Documentation
   - Can be done independently
   - Unblock other teams while performance optimization ongoing

3. **BDD Tests**: Incremental Implementation
   - Implement highest-value scenarios first
   - Build helper functions to reduce duplication
   - Can run in parallel with other work

4. **Security Infrastructure**: Enable Early
   - Integrate SonarQube and Snyk from week 2
   - Address findings as they arise
   - Prevents last-minute surprises

---

## References

- Beta Release Scope: `specs/011-view-auto-layout/tasks.md`
- Current Performance: `specs/011-view-auto-layout/tasks.md` (Performance Characteristics)
- Architecture: `specs/011-view-auto-layout/ARCHITECTURE.md`
- API Documentation: `LAYOUT_QUICKSTART.md`
