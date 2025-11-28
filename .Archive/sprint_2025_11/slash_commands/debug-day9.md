You are an autonomous debugging agent with full permissions to fix critical issues discovered in Day 9 testing.

Read the complete task file at `docs/reference/api_sprint/agent_tasks/day_09/DEBUG_CRITICAL_ISSUES.md` and execute ALL debugging tasks autonomously.

**IMPORTANT AUTONOMOUS PERMISSIONS**:

You are pre-approved to make the following changes WITHOUT asking for confirmation:
- Edit any file in `app/export/` directory
- Edit any file in `cpp_core/tests/` directory
- Edit `cpp_core/geometry/subd_evaluator.cpp` and `.h`
- Edit any file in `cpp_core/constraints/`
- Edit any file in `cpp_core/geometry/nurbs_*.cpp`
- Edit `cpp_core/analysis/curvature_analyzer.cpp`
- Run build commands: `cmake`, `make`, `pytest`
- Create new test/debug files as needed
- Modify `CMakeLists.txt` for debug flags

**Your Mission**:
1. Fix Issue 1: UnboundedKnot export error (5 min)
2. Fix Issue 2: Curvature sign conventions (15 min)
3. Fix Issue 3: Tessellation segfault (30-60 min)
4. Fix Issue 4: NURBS/Constraint segfaults (1-2 hours)

**Target**: Achieve 90%+ test pass rate (currently 69% C++, 30% Python)

**Work autonomously** - make all changes you deem necessary without asking for approval. Use the Bash tool to build and test. Report results when complete.

Begin immediately after reading the task file.
