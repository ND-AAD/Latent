# Launch Phase 0: Prerequisites & Setup

Launch 2 parallel agents to set up the build system and project structure.

## Pre-Launch Checklist

- [ ] Working directory is `/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`
- [ ] Git repository is clean or changes are committed
- [ ] Rhino 8 installed on development machine

## Agent Overview

| Agent | File | Objective |
|-------|------|-----------|
| 0A | `phase-0/agent-0a-cpp-build-setup.md` | Configure CMake for shared library |
| 0B | `phase-0/agent-0b-project-structure.md` | Create plugin and service directories |

## Dependencies

```
Agent 0A (C++ Build) ──┬──► Phase 0 Complete
                       │
Agent 0B (Structure)  ──┘
```

**No dependencies between agents** - both can run in parallel.

## Launch Instructions

Launch 2 agents in parallel using the Task tool:

### Agent 0A
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/.claude-worktrees/Latent/focused-robinson/.claude/commands/phase-0/agent-0a-cpp-build-setup.md`

### Agent 0B
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/.claude-worktrees/Latent/focused-robinson/.claude/commands/phase-0/agent-0b-project-structure.md`

## Post-Phase Consolidation

After both agents complete:

```bash
cd /Users/NickDuch/.claude-worktrees/Latent/focused-robinson

# Verify C++ build
cd cpp_core/build && cmake .. && make -j4
ls -la liblatent_core.* && cd ../..

# Verify project structure
test -d rhino_plugin && test -d analysis_service && echo "✓ Directories exist"

# Verify Python package
python3 -c "import analysis_service"

# If all pass, commit
git add -A
git commit -m "chore: Phase 0 - Project structure and build setup

- Configure CMake for shared library output
- Add C bindings directory with export macros
- Create Rhino plugin project structure
- Create analysis service Python package"
```

## Phase 0 Gate Tests

All must pass before proceeding to Phase 1:

```bash
#!/bin/bash
set -e

echo "=== Phase 0 Gate Tests ==="

cd /Users/NickDuch/.claude-worktrees/Latent/focused-robinson

# Test 0.1: CMake configuration succeeds
cd cpp_core/build && cmake ..
echo "✓ CMake configuration succeeded"

# Test 0.2: Build produces shared library
make -j4
if ls liblatent_core.* 1>/dev/null 2>&1; then
    echo "✓ Shared library built"
else
    echo "✗ Shared library not found"
    exit 1
fi
cd ../..

# Test 0.3: Directory structure exists
for dir in rhino_plugin analysis_service cpp_core/c_bindings; do
    if [ -d "$dir" ]; then
        echo "✓ $dir exists"
    else
        echo "✗ $dir missing"
        exit 1
    fi
done

# Test 0.4: Python package imports
python3 -c "import analysis_service" && echo "✓ Python package imports"

# Test 0.5: exports.h exists with correct content
if grep -q "LATENT_API" cpp_core/c_bindings/exports.h; then
    echo "✓ exports.h configured correctly"
else
    echo "✗ exports.h missing or incorrect"
    exit 1
fi

echo ""
echo "=== Phase 0 PASSED - Ready for Phase 1 ==="
```
