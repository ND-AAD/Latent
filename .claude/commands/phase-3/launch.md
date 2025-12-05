# Launch Phase 3: Rhino Plugin Foundation

Launch 4 parallel agents to create the Rhino plugin with P/Invoke bindings, analysis client, commands, and data model.

## Pre-Launch Checklist

- [ ] Phase 2 gate tests passed
- [ ] C++ shared library built (`liblatent_core.dylib`)
- [ ] Analysis service tests pass
- [ ] .NET 4.8 or higher installed
- [ ] Rhino 8 installed
- [ ] Working directory is `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Agent Overview

| Agent | File | Objective |
|-------|------|-----------|
| 3A | `phase-3/agent-3a-pinvoke.md` | P/Invoke bindings for C++ core |
| 3B | `phase-3/agent-3b-lens-client.md` | JSON-RPC client for analysis service |
| 3C | `phase-3/agent-3c-plugin-entry.md` | Plugin entry point and commands |
| 3D | `phase-3/agent-3d-data-model.md` | Data model with Rhino undo integration |

## Dependencies

```
Agent 3A (P/Invoke)      ───┐
                            │
Agent 3B (Lens Client)   ───┼──► Agent 3C (Plugin Entry) ──► Phase 3 Complete
                            │
Agent 3D (Data Model)    ───┘
```

**Parallel execution strategy:**
- All 4 agents can start immediately
- Agent 3C depends on 3A, 3B, 3D at integration time
- Each agent works on separate files
- Consolidation step will verify integration

**File isolation:**
- 3A: `rhino_plugin/Interop/`
- 3B: `rhino_plugin/Analysis/`
- 3C: `rhino_plugin/Commands/`, `LatentPlugin.cs`
- 3D: `rhino_plugin/Geometry/`

## Launch Instructions

Launch 4 agents in parallel using the Task tool:

### Agent 3A
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-3/agent-3a-pinvoke.md`

### Agent 3B
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-3/agent-3b-lens-client.md`

### Agent 3C
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-3/agent-3c-plugin-entry.md`

### Agent 3D
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-3/agent-3d-data-model.md`

## Post-Phase Consolidation

After all agents complete:

```bash
cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Restore NuGet packages
dotnet restore

# Build the plugin
dotnet build

# Run all tests
dotnet test --logger "console;verbosity=detailed"

# Verify plugin assembly
ls -la bin/Debug/net48/*.dll

# If all pass, commit
cd ..
git add -A
git commit -m "feat: Phase 3 - Rhino plugin foundation

- Add P/Invoke bindings for C++ core
- Add JSON-RPC client for analysis service
- Add ServiceManager for Python subprocess
- Create plugin entry point and commands
- Implement data model with Rhino undo integration
- Comprehensive unit tests"
```

## Phase 3 Gate Tests

All must pass before proceeding to Phase 4:

```bash
#!/bin/bash
set -e

echo "=== Phase 3 Gate Tests ==="

cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Test 3.1: Plugin builds
dotnet build
echo "✓ Plugin builds successfully"

# Test 3.2: Unit tests pass
dotnet test
echo "✓ Unit tests pass"

# Test 3.3: Plugin assembly exists
if [ -f bin/Debug/net48/LatentPlugin.dll ]; then
    echo "✓ Plugin assembly exists"
else
    echo "✗ Plugin assembly not found"
    exit 1
fi

# Test 3.4: Native library can be loaded (manual verification)
echo ""
echo "MANUAL VERIFICATION REQUIRED:"
echo "1. Load the plugin in Rhino 8"
echo "2. Run 'LatentAnalyze' command"
echo "3. Verify the analysis service starts"
echo ""

# Test 3.5: Data model tests
dotnet test --filter "FullyQualifiedName~RegionManagerTests"
echo "✓ Data model tests pass"

echo ""
echo "=== Phase 3 PASSED - Ready for Phase 4 ==="
echo "(Pending manual verification in Rhino)"
```

## Visual Verification Checklist

After automated tests, verify in Rhino:

- [ ] Plugin loads without errors (check Rhino console)
- [ ] `LatentAnalyze` command appears in command list
- [ ] `LatentSelect` command appears in command list
- [ ] `LatentPin` command appears in command list
- [ ] `LatentRevert` command appears in command list
- [ ] Analysis service starts when running LatentAnalyze
- [ ] Ctrl+Z undoes pin/unpin operations

## Troubleshooting

### Native library not found
- Ensure `liblatent_core.dylib` is in the same directory as the plugin
- Or add the library directory to DYLD_LIBRARY_PATH

### Analysis service fails to start
- Check Python is in PATH
- Verify `analysis_service` directory exists
- Check port 5555 is not in use

### Rhino undo not working
- Ensure `RhinoDoc.ActiveDoc` is not null
- Check that undo events are registered correctly
- Verify the Changed event is firing

### P/Invoke crashes
- Check that array marshaling is correct
- Verify handle lifecycle (create/destroy pairs)
- Use try/catch around native calls for debugging
