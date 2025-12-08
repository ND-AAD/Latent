# Phase 7: Final Integration - Launch

## Pre-Launch Checklist

Before launching Phase 7 agents, verify:

- [ ] Phase 6 complete (all UI panels working)
- [ ] `dotnet build` succeeds in `rhino_plugin/`
- [ ] `dotnet test` passes all existing tests
- [ ] All panel registrations in `LatentPlugin.cs`
- [ ] C++ core builds and exports all symbols

```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent

# Verify C++ core
cd cpp_core/build && cmake .. && make -j4
./tests/test_c_bindings
cd ../..

# Verify plugin builds and tests pass
cd rhino_plugin
dotnet build
dotnet test
cd ..

# Verify key files exist
ls rhino_plugin/Geometry/RegionManager.cs
ls rhino_plugin/Display/RegionConduit.cs
ls rhino_plugin/Interaction/VertexDragHandler.cs
ls rhino_plugin/UI/GeometryListPanel.cs
ls rhino_plugin/UI/LensPanel.cs
ls rhino_plugin/UI/VisualizationPanel.cs
```

---

## Agent Overview

| Agent | Objective | Files | Dependencies |
|-------|-----------|-------|--------------|
| **7A** | End-to-End Integration Tests | `Tests/TestHelpers.cs`, `Tests/IntegrationTests.cs`, `Tests/WorkflowTests.cs` | All previous phases |
| **7B** | Documentation & Code Quality | `docs/RHINO_PLUGIN_USER_GUIDE.md`, `rhino_plugin/README.md`, XML docs | All previous phases |

---

## Dependencies

```
Phase 6 (UI Panels)
    │
    ▼
┌───────────────────────────────────────────────┐
│                  Phase 7                       │
│                                               │
│      ┌─────────────┐    ┌─────────────┐       │
│      │   Agent     │    │   Agent     │       │
│      │     7A      │    │     7B      │       │
│      │ Integration │    │Documentation│       │
│      │   Tests     │    │  & Quality  │       │
│      └─────────────┘    └─────────────┘       │
│            │                  │               │
│            └──────────────────┘               │
│                    │                          │
│              All Independent                  │
│           (can run in parallel)               │
└───────────────────────────────────────────────┘
    │
    ▼
  RELEASE
```

Both Phase 7 agents are **independent** - they can run in parallel without conflicts.

---

## Launch Instructions

Launch both agents in parallel:

### Agent 7A: Integration Tests
```
Use Task tool with:
- subagent_type: "general-purpose"
- prompt: "Read and execute: /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-7/agent-7a-integration-tests.md"
```

### Agent 7B: Documentation & Code Quality
```
Use Task tool with:
- subagent_type: "general-purpose"
- prompt: "Read and execute: /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-7/agent-7b-documentation.md"
```

---

## Post-Phase Consolidation

After all agents complete:

### 1. Build and Run All Tests
```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build
dotnet build

# Run ALL tests including new integration tests
dotnet test --logger "console;verbosity=detailed"

# Run integration tests specifically
dotnet test --filter "FullyQualifiedName~IntegrationTests|FullyQualifiedName~WorkflowTests"
```

### 2. Verify Documentation
```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent

# Check documentation files exist
ls -la docs/RHINO_PLUGIN_USER_GUIDE.md
ls -la rhino_plugin/README.md

# Verify PROJECT_STATUS.md was updated
grep -A 5 "Rhino Plugin Status" docs/PROJECT_STATUS.md
```

### 3. Final Verification
```bash
# Count test files (should have 15+)
ls -1 rhino_plugin/Tests/*.cs | wc -l

# Verify all public classes have documentation (check for /// comments)
grep -l "/// <summary>" rhino_plugin/Geometry/*.cs rhino_plugin/Interop/*.cs | wc -l
```

### 4. Git Commit
```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent

git add rhino_plugin/Tests/
git add docs/RHINO_PLUGIN_USER_GUIDE.md
git add rhino_plugin/README.md
git add docs/PROJECT_STATUS.md
git add rhino_plugin/Geometry/*.cs
git add rhino_plugin/Interop/*.cs

git commit -m "$(cat <<'EOF'
feat: Phase 7 - Final Integration

- Add comprehensive integration tests (TestHelpers, IntegrationTests, WorkflowTests)
- Add workflow tests for analyze→select→edit→revert cycle
- Add performance benchmarks (100 regions < 1s, 100 selections < 100ms)
- Create user guide documentation
- Update README with current project structure
- Add XML documentation to public APIs
- Update PROJECT_STATUS.md with completion status

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Gate Tests

Phase 7 is complete when ALL of the following pass:

```bash
#!/bin/bash
set -e

echo "=== Phase 7 Gate Tests ==="

cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Test 7.1: Plugin builds
echo "Testing build..."
dotnet build --no-restore -v q
echo "✓ Build passed"

# Test 7.2: All unit tests pass
echo "Running all unit tests..."
dotnet test --no-build -v q
echo "✓ All unit tests passed"

# Test 7.3: Integration tests pass
echo "Running integration tests..."
dotnet test --filter "FullyQualifiedName~IntegrationTests" --no-build -v q
echo "✓ Integration tests passed"

# Test 7.4: Workflow tests pass
echo "Running workflow tests..."
dotnet test --filter "FullyQualifiedName~WorkflowTests" --no-build -v q
echo "✓ Workflow tests passed"

# Test 7.5: Documentation files exist
echo "Checking documentation..."
test -f ../docs/RHINO_PLUGIN_USER_GUIDE.md && echo "✓ User guide exists"
test -f README.md && echo "✓ README exists"

# Test 7.6: Test file count (should have at least 15 test files)
TEST_COUNT=$(ls -1 Tests/*.cs 2>/dev/null | wc -l | tr -d ' ')
if [ "$TEST_COUNT" -ge 15 ]; then
    echo "✓ Test coverage adequate ($TEST_COUNT test files)"
else
    echo "✗ Insufficient test files ($TEST_COUNT < 15)"
    exit 1
fi

# Test 7.7: Key test files exist
echo "Checking required test files..."
test -f Tests/TestHelpers.cs && echo "✓ TestHelpers.cs exists"
test -f Tests/IntegrationTests.cs && echo "✓ IntegrationTests.cs exists"
test -f Tests/WorkflowTests.cs && echo "✓ WorkflowTests.cs exists"

# Test 7.8: PROJECT_STATUS.md updated
echo "Checking PROJECT_STATUS.md..."
grep -q "Rhino Plugin Status" ../docs/PROJECT_STATUS.md && echo "✓ PROJECT_STATUS.md updated"

echo ""
echo "=== Phase 7 PASSED - Plugin Ready for Release ==="
```

---

## Troubleshooting

### Build Errors

**"Missing type or namespace"**
- Ensure all previous phases completed successfully
- Check that all required files exist from Phases 1-6

**"Test project doesn't build"**
- Verify NUnit package reference in `.csproj`
- Check: `grep NUnit rhino_plugin/Latent.csproj`

### Test Failures

**"Integration tests fail with null reference"**
- Ensure `LatentPlugin.Instance` is properly initialized in tests
- May need mock plugin setup

**"Workflow tests timeout"**
- Check that async operations complete
- Increase test timeout if needed

### Documentation Issues

**"User guide references missing features"**
- Cross-reference with actual implemented commands
- Update guide to match current functionality

---

## File Ownership

| File | Owner Agent |
|------|-------------|
| `Tests/TestHelpers.cs` | 7A |
| `Tests/IntegrationTests.cs` | 7A |
| `Tests/WorkflowTests.cs` | 7A |
| `docs/RHINO_PLUGIN_USER_GUIDE.md` | 7B |
| `rhino_plugin/README.md` | 7B |
| `docs/PROJECT_STATUS.md` (update only) | 7B |
| `Geometry/*.cs` (XML docs only) | 7B |
| `Interop/*.cs` (XML docs only) | 7B |
| `Tests/ApiDocumentationTests.cs` | 7B |

---

## Notes

- This is the final phase before release
- Focus on verification and documentation, not new features
- All tests must pass before considering phase complete
- Integration tests should cover the complete user workflow
- Documentation should be accurate for current implementation state
