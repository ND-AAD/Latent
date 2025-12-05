# Launch Phase 1: C++ Core Extensions

Launch 4 parallel agents to extend the C++ core with inverse evaluation, surface curves, and C bindings.

## Pre-Launch Checklist

- [ ] Phase 0 gate tests passed
- [ ] Shared library builds successfully (`liblatent_core.dylib`)
- [ ] Working directory is `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Agent Overview

| Agent | File | Objective |
|-------|------|-----------|
| 1A | `phase-1/agent-1a-inverse-eval.md` | 3D point → (face_id, u, v) projection |
| 1B | `phase-1/agent-1b-surface-curve.md` | Parametric curves on limit surface |
| 1C | `phase-1/agent-1c-c-bindings-core.md` | C wrapper for evaluator functions |
| 1D | `phase-1/agent-1d-c-bindings-extended.md` | C wrapper for curves and analysis |

## Dependencies

```
Agent 1A (Inverse Eval) ───┐
                          ├──► Agent 1C (C Bindings Core)
Agent 1B (Surface Curve) ──┤
                          └──► Agent 1D (C Bindings Extended)
```

**Parallel execution strategy:**
- Agents 1A, 1B can start immediately (independent)
- Agent 1C can start immediately but stubs `project_point` until 1A completes
- Agent 1D can start immediately but stubs curve functions until 1B completes
- All agents work on separate files - no merge conflicts

## Launch Instructions

Launch 4 agents in parallel using the Task tool:

### Agent 1A
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-1/agent-1a-inverse-eval.md`

### Agent 1B
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-1/agent-1b-surface-curve.md`

### Agent 1C
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-1/agent-1c-c-bindings-core.md`

### Agent 1D
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-1/agent-1d-c-bindings-extended.md`

## Post-Phase Consolidation

After all agents complete:

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent

# Full build
cd cpp_core/build
cmake .. && make -j4

# Run all tests
ctest --output-on-failure

# Verify exports
echo "=== Exported Symbols ==="
nm -gU liblatent_core.dylib | grep latent_

# Integration test
./test_c_bindings

cd ../..

# If all pass, commit
git add -A
git commit -m "feat: Phase 1 - C++ core extensions

- Add inverse surface evaluation (Newton-Raphson)
- Add SurfaceCurve class (Bezier, B-spline, linear)
- Add C bindings for evaluator functions
- Add C bindings for curve and analysis functions
- Comprehensive unit tests for all components"
```

## Phase 1 Gate Tests

All must pass before proceeding to Phase 2:

```bash
#!/bin/bash
set -e

echo "=== Phase 1 Gate Tests ==="

cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/cpp_core/build

# Test 1.1: Full build succeeds
cmake .. && make -j4
echo "✓ Build succeeded"

# Test 1.2: Unit tests pass
ctest --output-on-failure
echo "✓ Unit tests passed"

# Test 1.3: Inverse evaluation works
./test_inverse_eval && echo "✓ Inverse evaluation tests passed"

# Test 1.4: Surface curves work
./test_surface_curve && echo "✓ Surface curve tests passed"

# Test 1.5: C bindings work
./test_c_bindings && echo "✓ C bindings tests passed"

# Test 1.6: All expected exports present
EXPORTS=$(nm -gU liblatent_core.dylib | grep latent_ | wc -l)
if [ "$EXPORTS" -ge 15 ]; then
    echo "✓ Found $EXPORTS exported symbols"
else
    echo "✗ Only found $EXPORTS exports (expected >= 15)"
    exit 1
fi

# Test 1.7: Round-trip accuracy test
echo "
#include <cstdio>
#include \"c_bindings/latent_core.h\"

int main() {
    auto eval = latent_evaluator_create();
    float verts[] = {-1,-1,-1, 1,-1,-1, 1,1,-1, -1,1,-1, -1,-1,1, 1,-1,1, 1,1,1, -1,1,1};
    int faces[] = {0,1,2,3, 4,7,6,5, 0,4,5,1, 2,6,7,3, 0,3,7,4, 1,5,6,2};
    int sizes[] = {4,4,4,4,4,4};
    latent_evaluator_initialize(eval, verts, 8, faces, sizes, 6, 0, 0, 0);

    float x, y, z;
    latent_evaluate_point(eval, 0, 0.5, 0.5, &x, &y, &z);

    int face; float u, v;
    if (latent_project_point(eval, x, y, z, &face, &u, &v)) {
        if (face == 0 && fabs(u - 0.5) < 0.01 && fabs(v - 0.5) < 0.01) {
            printf(\"Round-trip OK\\n\");
            latent_evaluator_destroy(eval);
            return 0;
        }
    }
    printf(\"Round-trip FAILED\\n\");
    latent_evaluator_destroy(eval);
    return 1;
}
" > /tmp/test_roundtrip.cpp

g++ -std=c++17 -I.. /tmp/test_roundtrip.cpp -L. -llatent_core -o /tmp/test_roundtrip
DYLD_LIBRARY_PATH=. /tmp/test_roundtrip && echo "✓ Round-trip accuracy test passed"

echo ""
echo "=== Phase 1 PASSED - Ready for Phase 2 ==="
```

## Troubleshooting

### Agent 1C/1D report missing dependencies
- This is expected if 1A/1B haven't completed yet
- Agents should stub functions with TODO comments
- Consolidation step will integrate all components

### Linker errors for missing symbols
- Ensure all source files are added to CMakeLists.txt
- Check that `target_sources` includes all .cpp files

### Test failures in round-trip
- Check that Newton-Raphson converges (Agent 1A)
- May need to adjust tolerance or iteration count
