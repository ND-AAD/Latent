# Master Orchestration Guide - 10-Day Sprint

**Quick Reference**: How to launch and manage all agents during the sprint

---

## Quick Start

### How to Launch an Agent

**Step 1**: Open the agent's task file
```
docs/reference/api_sprint/agent_tasks/day_XX/AGENT_XX_name.md
```

**Step 2**: Launch with this command:
```markdown
I need you to complete the task specified in this file:
docs/reference/api_sprint/agent_tasks/day_01/AGENT_01_types_data_structures.md

Please read the entire file and complete all deliverables.
Work autonomously and provide complete implementation.
```

**Step 3**: Wait for completion (check estimated duration in task file)

**Step 4**: Review output and integrate

---

## Parallel Launch Pattern

### Launching Multiple Agents (Day 1 Example)

**Single message with 6 Task tool calls**:

```markdown
I need to launch 6 agents in parallel for Day 1 morning. Each should read their task file and work autonomously.

Agent 1: Read and complete task in docs/reference/api_sprint/agent_tasks/day_01/AGENT_01_types_data_structures.md

Agent 2: Read and complete task in docs/reference/api_sprint/agent_tasks/day_01/AGENT_02_subd_evaluator_header.md

Agent 3: Read and complete task in docs/reference/api_sprint/agent_tasks/day_01/AGENT_03_cmakelists.md

Agent 4: Read and complete task in docs/reference/api_sprint/agent_tasks/day_01/AGENT_04_subd_evaluator_impl.md

Agent 5: Read and complete task in docs/reference/api_sprint/agent_tasks/day_01/AGENT_05_pybind11_bindings.md

Agent 6: Read and complete task in docs/reference/api_sprint/agent_tasks/day_01/AGENT_06_grasshopper_server.md

Launch all agents in parallel using the Task tool.
```

---

## Daily Schedule

### Day 1

**Morning (9am)**: Launch Agents 1-6 in parallel
- Agent 1: Types & Data Structures (2h, $2-3)
- Agent 2: SubDEvaluator Header (2h, $2-3)
- Agent 3: CMakeLists.txt (2-3h, $2-4)
- Agent 4: SubDEvaluator Implementation (4-5h, $5-8)
- Agent 5: pybind11 Bindings (3-4h, $4-6)
- Agent 6: Grasshopper Server (2-3h, $1-2)

**Afternoon (2pm)**: Review and integrate all morning agents

**Evening (6pm)**: Launch Agents 7-9 in parallel
- Agent 7: Complete Tessellation (5-6h, $6-10)
- Agent 8: Desktop Bridge (3-4h, $3-5)
- Agent 9: Basic Tests (2-3h, $1-2)

**Total Day 1**: 9 agents, $26-43

---

### Day 2

**Morning (9am)**: Launch Agents 10-15 in parallel
- Agent 10: Limit Surface Evaluation (5-6h, $6-10)
- Agent 11: VTK Viewport Base (4-5h, $5-8)
- Agent 12: VTK SubD Display (3-4h, $4-6)
- Agent 13: Multi-Viewport Layout (4-5h, $4-7)
- Agent 14: Application State (3-4h, $4-6)
- Agent 15: Main Window (3-4h, $3-5)

**Evening (6pm)**: Launch Agents 16-17 in parallel
- Agent 16: Lossless Validation (3-4h, $2-4)
- Agent 17: Phase 0 Docs (3-4h, $2-4)

**Total Day 2**: 8 agents, $30-50

---

### Day 3

**Morning (9am)**: Launch Agents 18-25 in parallel (8 agents!)
- Agent 18: Edit Mode Manager (3-4h, $3-5)
- Agent 19: Face Picker (3-4h, $4-6)
- Agent 20: Edge Picker (3-4h, $4-6)
- Agent 21: Vertex Picker (3-4h, $3-5)
- Agent 22: Edit Mode Toolbar (2-3h, $2-4)
- Agent 23: Parametric Region (3-4h, $3-5)
- Agent 24: Region List UI (3-4h, $4-6)
- Agent 25: Region Visualization (3-4h, $4-6)

**Total Day 3**: 8 agents, $27-47

---

### Day 4

**Morning (9am)**: Launch Agents 26-31 in parallel
- Agent 26: Curvature Analyzer Header (2-3h, $2-4)
- Agent 27: Curvature Implementation (6-7h, $7-12)
- Agent 28: Curvature Bindings (2-3h, $2-4)
- Agent 29: Curvature Viz (3-4h, $4-6)
- Agent 30: Curvature Tests (2-3h, $2-3)
- Agent 31: Analysis Panel UI (3-4h, $4-6)

**Evening (6pm)**: Launch Agents 32-33 in parallel
- Agent 32: Differential Decomposition (5-6h, $6-10)
- Agent 33: Iteration System (4-5h, $5-8)

**Total Day 4**: 8 agents, $32-53

---

### Day 5

**Morning (9am)**: Launch Agents 34-39 in parallel
- Agent 34: Laplacian Builder (4-5h, $4-7)
- Agent 35: Spectral Decomposition (5-6h, $5-9)
- Agent 36: Spectral Viz (3-4h, $4-6)
- Agent 37: Region Merge/Split (4-5h, $4-7)
- Agent 38: Lens Integration (3-4h, $4-6)
- Agent 39: Analysis Tests (3-4h, $2-4)

**Total Day 5**: 6 agents, $23-39

---

### Day 6

**Morning (9am)**: Launch Agents 40-45 in parallel
- Agent 40: Constraint Validator Header (2-3h, $3-5)
- Agent 41: Undercut Detection (5-6h, $6-10)
- Agent 42: Draft Angle Checker (4-5h, $5-8)
- Agent 43: Constraint Bindings (2-3h, $2-4)
- Agent 44: Constraint UI Panel (4-5h, $4-7)
- Agent 45: Constraint Viz (3-4h, $4-6)

**Total Day 6**: 6 agents, $24-40

---

### Day 7

**Morning (10am - after OpenCASCADE install)**: Launch Agents 46-51
- Agent 46: NURBS Generator Header (2-3h, $3-5)
- Agent 47: NURBS Surface Fitting (6-7h, $7-12)
- Agent 48: Draft Transformation (5-6h, $6-10)
- Agent 49: Solid Brep Creation (5-6h, $6-10)
- Agent 50: NURBS Bindings (2-3h, $3-5)
- Agent 51: NURBS Tests (3-4h, $2-4)

**Total Day 7**: 6 agents, $27-46

---

### Day 8

**Morning (9am)**: Launch Agents 52-57 in parallel
- Agent 52: NURBS Serialization (4-5h, $5-8)
- Agent 53: GH POST Endpoint (3-4h, $2-4)
- Agent 54: Mold Params Dialog (3-4h, $4-6)
- Agent 55: Mold Workflow (4-5h, $5-8)
- Agent 56: Progress UI (2-3h, $2-4)
- Agent 57: Export Tests (3-4h, $2-4)

**Total Day 8**: 6 agents, $20-34

---

### Day 9

**Morning (9am)**: Launch Agents 58-63 in parallel
- Agent 58: C++ Unit Tests (5-6h, $6-10)
- Agent 59: Python Unit Tests (5-6h, $3-6)
- Agent 60: Integration Tests (4-5h, $3-5)
- Agent 61: Performance Benchmarks (3-4h, $2-4)
- Agent 62: UI Polish (4-5h, $5-8)
- Agent 63: Error Handling (4-5h, $4-7)

**Total Day 9**: 6 agents, $23-40

---

### Day 10

**Morning (9am)**: Launch Agents 64-67 in parallel
- Agent 64: User Guide (6-8h, $3-6)
- Agent 65: Developer Docs (6-8h, $3-6)
- Agent 66: API Reference (5-6h, $2-4)
- Agent 67: Tutorial & Examples (5-6h, $2-4)

**Total Day 10**: 4 agents, $10-20

---

## Integration Workflow

### After Each Agent Completes

**1. Review** (5-10 minutes):
- Check code quality
- Verify all deliverables present
- Read integration notes

**2. Place Files** (2-5 minutes):
- Copy files to correct locations
- Update imports if needed

**3. Test** (5-15 minutes):
- Run provided tests
- Check compilation (C++)
- Check imports (Python)

**4. Commit** (2 minutes):
```bash
git add .
git commit -m "feat: [Agent X] - [feature name]"
```

**5. Update Tracker** (1 minute):
- Mark agent as complete
- Note any issues
- Update cost tracking

---

## Integration Checklist

After each batch of agents:

- [ ] All files in correct locations
- [ ] C++ code compiles (`cd cpp_core/build && make`)
- [ ] Python imports work
- [ ] Tests pass
- [ ] No integration conflicts
- [ ] Git committed
- [ ] Ready for next batch

---

## Cost Tracking

### Running Total

| Day | Agents | Estimated | Actual | Notes |
|-----|--------|-----------|--------|-------|
| 1   | 9      | $26-43    |        |       |
| 2   | 8      | $30-50    |        |       |
| 3   | 8      | $27-47    |        |       |
| 4   | 8      | $32-53    |        |       |
| 5   | 6      | $23-39    |        |       |
| 6   | 6      | $24-40    |        |       |
| 7   | 6      | $27-46    |        |       |
| 8   | 6      | $20-34    |        |       |
| 9   | 6      | $23-40    |        |       |
| 10  | 4      | $10-20    |        |       |
| **Total** | **67** | **$242-412** |  |  |

---

## Emergency Procedures

### If an Agent Fails

**1. Identify Issue**:
- Compilation error?
- Logic error?
- Missing context?

**2. Quick Fix Attempt** (15 minutes):
- Can you fix it manually?
- Is it a simple typo/import?

**3. Relaunch Agent** (if needed):
```markdown
Agent X failed with this error: [paste error]

Please re-read the task file and fix the issue:
docs/reference/api_sprint/agent_tasks/day_XX/AGENT_XX_name.md

Previous output was: [paste output]
Error: [paste error]

Please provide corrected implementation.
```

**Cost**: +$2-5 per fix

---

### If Behind Schedule

**End of Day 2**: Should have Phase 0 complete
- If not: Add 1 day, shift remaining schedule

**End of Day 5**: Should have analysis working
- If not: Skip spectral lens, continue

**End of Day 8**: Should have molds working
- If not: Simplify NURBS (skip draft initially)

---

## File Organization

```
docs/reference/api_sprint/
├── MASTER_ORCHESTRATION.md          # This file
├── 10_DAY_SPRINT_STRATEGY.md        # Overall strategy
├── IMPLEMENTATION_ROADMAP.md        # Detailed roadmap
├── agent_tasks/                     # Individual task files
│   ├── day_01/
│   │   ├── AGENT_01_types_data_structures.md
│   │   ├── AGENT_02_subd_evaluator_header.md
│   │   ├── AGENT_03_cmakelists.md
│   │   ├── AGENT_04_subd_evaluator_impl.md
│   │   ├── AGENT_05_pybind11_bindings.md
│   │   ├── AGENT_06_grasshopper_server.md
│   │   ├── AGENT_07_tessellation.md
│   │   ├── AGENT_08_desktop_bridge.md
│   │   └── AGENT_09_basic_tests.md
│   ├── day_02/
│   │   └── [Agents 10-17]
│   ├── day_03/
│   │   └── [Agents 18-25]
│   └── [days 04-10...]
└── progress/
    ├── DAILY_LOG.md                 # Track progress
    └── ISSUES.md                    # Track problems
```

---

## Success Metrics

### Daily Goals

**Day 1**: ✅ C++ module compiles, Python bindings work
**Day 2**: ✅ VTK displays SubD, lossless validated
**Day 3**: ✅ All edit modes functional
**Day 4**: ✅ Curvature analysis working
**Day 5**: ✅ Both lenses discovering regions
**Day 6**: ✅ Constraints detecting issues
**Day 7**: ✅ NURBS molds generating
**Day 8**: ✅ Export to Rhino working
**Day 9**: ✅ Tests passing, UI polished
**Day 10**: ✅ Complete documentation

---

## Tips for Maximum Velocity

1. **Launch agents immediately** - don't wait
2. **Review in batches** - more efficient than one-by-one
3. **Test incrementally** - catch issues early
4. **Commit often** - never lose work
5. **Stay organized** - use checklists
6. **Take breaks** - avoid burnout
7. **Ask for help** - if agent outputs unclear

---

**You've got this! Let's build Latent in 10 days!**
