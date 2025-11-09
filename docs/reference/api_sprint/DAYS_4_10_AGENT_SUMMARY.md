# Days 4-10 Agent Summary

Quick reference for remaining 42 agents. Full task files available in `agent_tasks/day_XX/` directories.

---

## **Day 4: Curvature Analysis** (8 agents, $32-53)

**Morning (9am)** - Agents 26-31:
- **Agent 26**: Curvature Analyzer Header (2-3h, $2-4) - C++ curvature interface
- **Agent 27**: Curvature Implementation (6-7h, $7-12) - Gaussian/mean/principal curvatures from second derivatives
- **Agent 28**: Curvature Python Bindings (2-3h, $2-4) - Expose to Python
- **Agent 29**: Curvature Visualization (3-4h, $4-6) - False-color curvature maps
- **Agent 30**: Curvature Tests (2-3h, $2-3) - Test on sphere/torus/saddle
- **Agent 31**: Analysis Panel UI (3-4h, $4-6) - Curvature display panel

**Evening (6pm)** - Agents 32-33:
- **Agent 32**: Differential Decomposition (5-6h, $6-10) - **First mathematical lens!** Ridge/valley finder
- **Agent 33**: Iteration System (4-5h, $5-8) - Design snapshot/history management

---

## **Day 5: Spectral Analysis** (6 agents, $23-39)

**Morning (9am)** - Agents 34-39:
- **Agent 34**: Laplacian Builder (4-5h, $4-7) - Cotangent-weight Laplacian matrix
- **Agent 35**: Spectral Decomposition (5-6h, $5-9) - **Second mathematical lens!** Laplace-Beltrami eigenfunctions
- **Agent 36**: Spectral Visualization (3-4h, $4-6) - Nodal line rendering
- **Agent 37**: Region Merge/Split (4-5h, $4-7) - Topological region editing
- **Agent 38**: Lens Integration (3-4h, $4-6) - Unified analysis interface for both lenses
- **Agent 39**: Analysis Tests (3-4h, $2-4) - Comprehensive lens testing

---

## **Day 6: Constraint Validation** (6 agents, $24-40)

**Morning (9am)** - Agents 40-45:
- **Agent 40**: Constraint Validator Header (2-3h, $3-5) - C++ constraint interface
- **Agent 41**: Undercut Detection (5-6h, $6-10) - Ray-casting demolding analysis
- **Agent 42**: Draft Angle Checker (4-5h, $5-8) - Normal deviation from pull direction
- **Agent 43**: Constraint Bindings (2-3h, $2-4) - Python exposure
- **Agent 44**: Constraint UI Panel (4-5h, $4-7) - Validation results display
- **Agent 45**: Constraint Visualization (3-4h, $4-6) - Color-coded pass/fail regions

---

## **Day 7: NURBS Generation** (6 agents, $27-46)

**Prep**: Install OpenCASCADE (`brew install opencascade`) - 1-2h

**Morning (10am)** - Agents 46-51:
- **Agent 46**: NURBS Generator Header (2-3h, $3-5) - OpenCASCADE interface
- **Agent 47**: NURBS Surface Fitting (6-7h, $7-12) - Exact limit points → NURBS surface
- **Agent 48**: Draft Transformation (5-6h, $6-10) - Apply draft angle to surfaces
- **Agent 49**: Solid Brep Creation (5-6h, $6-10) - Assemble mold solids
- **Agent 50**: NURBS Bindings (2-3h, $3-5) - Python exposure
- **Agent 51**: NURBS Tests (3-4h, $2-4) - Validate mold geometry

---

## **Day 8: Mold Export** (6 agents, $20-34)

**Morning (9am)** - Agents 52-57:
- **Agent 52**: NURBS Serialization (4-5h, $5-8) - 3dm file export
- **Agent 53**: GH POST Endpoint (3-4h, $2-4) - Send molds back to Grasshopper
- **Agent 54**: Mold Parameters Dialog (3-4h, $4-6) - Draft angle, wall thickness UI
- **Agent 55**: Mold Workflow (4-5h, $5-8) - Complete region → mold pipeline
- **Agent 56**: Progress UI (2-3h, $2-4) - Generation progress display
- **Agent 57**: Export Tests (3-4h, $2-4) - End-to-end mold generation

---

## **Day 9: Testing & Polish** (6 agents, $23-40)

**Morning (9am)** - Agents 58-63:
- **Agent 58**: C++ Unit Tests (5-6h, $6-10) - Complete C++ test coverage
- **Agent 59**: Python Unit Tests (5-6h, $3-6) - Complete Python test coverage
- **Agent 60**: Integration Tests (4-5h, $3-5) - Full pipeline tests
- **Agent 61**: Performance Benchmarks (3-4h, $2-4) - Profile and optimize
- **Agent 62**: UI Polish (4-5h, $5-8) - Final UX improvements
- **Agent 63**: Error Handling (4-5h, $4-7) - Robust error recovery

---

## **Day 10: Documentation** (4 agents, $10-20)

**Morning (9am)** - Agents 64-67:
- **Agent 64**: User Guide (6-8h, $3-6) - Complete user documentation
- **Agent 65**: Developer Docs (6-8h, $3-6) - Architecture and API reference
- **Agent 66**: API Reference (5-6h, $2-4) - Auto-generated API docs
- **Agent 67**: Tutorial & Examples (5-6h, $2-4) - Walkthrough examples

---

## Launch Commands

Use these slash commands:

**Day 4**:
- `/launch-day4-morning` - Agents 26-31 (6 in parallel)
- `/launch-day4-evening` - Agents 32-33 (2 in parallel)

**Day 5**:
- `/launch-day5-morning` - Agents 34-39 (6 in parallel)

**Day 6**:
- `/launch-day6-morning` - Agents 40-45 (6 in parallel)

**Day 7**:
- `/launch-day7-morning` - Agents 46-51 (6 in parallel)

**Day 8**:
- `/launch-day8-morning` - Agents 52-57 (6 in parallel)

**Day 9**:
- `/launch-day9-morning` - Agents 58-63 (6 in parallel)

**Day 10**:
- `/launch-day10-morning` - Agents 64-67 (4 in parallel)

---

## Critical Notes

**All agents use `cpp_core` module name** (not `latent_core`)

**Path conventions**:
- Use `app/` (NOT `ceramic_mold_analyzer/app/`)
- Use `cpp_core/` for C++ code
- Use `tests/` for test files
- Use `rhino/` for Grasshopper components

**Testing requirements**:
- Every agent MUST include tests
- Tests MUST pass before marking complete
- Performance targets documented in each task

**Dependencies**:
- Day 4 depends on Day 1-3 complete
- Day 7 requires OpenCASCADE installed
- Each day builds on previous

---

## Sprint Completion Checklist

After each day:
- [ ] All agents complete
- [ ] Integration tests pass
- [ ] Performance meets targets
- [ ] Documentation updated
- [ ] Git commit created
- [ ] Ready for next day

---

**Total Remaining: 42 agents, $216-369 estimated**
**With Days 1-3: 67 agents, $242-412 total**
