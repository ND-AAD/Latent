# Launch Phase 5: Interaction & Selection

Launch 3 parallel agents to create the interaction system for surface-constrained picking, dragging, and selection in Rhino 8.

## Pre-Launch Checklist

- [ ] Phase 4 gate tests passed
- [ ] Plugin builds successfully (`dotnet build`)
- [ ] Display conduit working (`RegionConduit`)
- [ ] Data model classes exist (`RegionManager`, `Region`, `Edge`, `Vertex`)
- [ ] P/Invoke bindings work (`SubDEvaluator.ProjectPoint()`)
- [ ] Working directory is `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Agent Overview

| Agent | File | Objective |
|-------|------|-----------|
| 5A | `phase-5/agent-5a-surface-getpoint.md` | Surface-constrained GetPoint with parametric tracking |
| 5B | `phase-5/agent-5b-drag-handlers.md` | Vertex and edge drag operations |
| 5C | `phase-5/agent-5c-element-picker.md` | Region, edge, and vertex picking |

## Dependencies

```
Agent 5A (SurfaceGetPoint) ───┐
                              │
Agent 5B (DragHandlers)    ───┼──► Phase 5 Complete
                              │
Agent 5C (ElementPicker)   ───┘
```

**Parallel execution strategy:**
- All 3 agents can start immediately
- Agent 5A provides base class used by 5B and 5C
- Agents create stubs for dependencies if needed
- Consolidation step integrates components

**File isolation:**
- 5A: `rhino_plugin/Interaction/SurfaceConstrainedGetPoint.cs`, `rhino_plugin/Interaction/ParametricPoint.cs`
- 5B: `rhino_plugin/Interaction/VertexDragHandler.cs`, `rhino_plugin/Interaction/EdgeDragHandler.cs`, `rhino_plugin/Interaction/DragPreview.cs`
- 5C: `rhino_plugin/Interaction/RegionPicker.cs`, `rhino_plugin/Interaction/ElementPicker.cs`, `rhino_plugin/Interaction/PickResult.cs`

## Launch Instructions

Launch 3 agents in parallel using the Task tool:

### Agent 5A
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-5/agent-5a-surface-getpoint.md`

### Agent 5B
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-5/agent-5b-drag-handlers.md`

### Agent 5C
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-5/agent-5c-element-picker.md`

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

# Verify new files exist
ls -la Interaction/*.cs

# If all pass, commit
cd ..
git add -A
git commit -m "feat: Phase 5 - Interaction & Selection

- Add SurfaceConstrainedGetPoint for surface-locked picking
- Add ParametricPoint struct for (faceId, u, v) coordinates
- Add VertexDragHandler with preview and undo integration
- Add EdgeDragHandler for moving entire edges
- Add DragPreview for visual feedback during drags
- Add RegionPicker for point-in-region selection
- Add ElementPicker for proximity-based edge/vertex picking
- Add PickResult for unified pick results
- Comprehensive unit tests"
```

## Phase 5 Gate Tests

All must pass before proceeding to Phase 6:

```bash
#!/bin/bash
set -e

echo "=== Phase 5 Gate Tests ==="

cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Test 5.1: Plugin builds
dotnet build
echo "✓ Plugin builds successfully"

# Test 5.2: Unit tests pass
dotnet test
echo "✓ Unit tests pass"

# Test 5.3: Interaction files exist
if [ -f Interaction/SurfaceConstrainedGetPoint.cs ] && \
   [ -f Interaction/ParametricPoint.cs ] && \
   [ -f Interaction/VertexDragHandler.cs ] && \
   [ -f Interaction/EdgeDragHandler.cs ] && \
   [ -f Interaction/DragPreview.cs ] && \
   [ -f Interaction/RegionPicker.cs ] && \
   [ -f Interaction/ElementPicker.cs ] && \
   [ -f Interaction/PickResult.cs ]; then
    echo "✓ All interaction files exist"
else
    echo "✗ Missing interaction files"
    exit 1
fi

# Test 5.4: Drag handler tests
dotnet test --filter "FullyQualifiedName~DragHandlerTests"
echo "✓ Drag handler tests pass"

# Test 5.5: Picker tests
dotnet test --filter "FullyQualifiedName~PickerTests"
echo "✓ Picker tests pass"

echo ""
echo "=== Phase 5 PASSED - Ready for Phase 6 ==="
echo "(Pending interactive verification in Rhino)"
```

## Interactive Verification Checklist

After automated tests, verify in Rhino 8:

- [ ] Plugin loads without errors
- [ ] Clicking on SubD surface returns parametric coordinates
- [ ] Vertex drag shows preview point
- [ ] Vertex drag updates position on release
- [ ] Vertex drag respects surface constraint
- [ ] Edge drag moves all edge vertices together
- [ ] Region picking highlights correct region
- [ ] Edge picking highlights nearest edge
- [ ] Vertex picking highlights nearest vertex
- [ ] Ctrl+Z undoes drag operations
- [ ] Pinned elements cannot be dragged

## Troubleshooting

### GetPoint not constraining to surface
- Ensure `Constrain(subd, false)` is called
- Check that SubD object is valid
- Verify SubD is in the document

### ProjectPoint returning wrong face
- Check that Newton-Raphson is converging
- May need to search all faces
- Tolerance might be too tight

### Drag preview not showing
- Ensure DynamicDraw event is wired up
- Check that display pipeline is valid
- Verify point coordinates are valid

### Undo not working
- Check RegionManager.MoveVertex creates undo record
- Verify RhinoDoc.ActiveDoc is available
- Ensure undo is not disabled

### Picking wrong element
- Adjust proximity tolerance
- Check z-depth sorting for overlaps
- Verify parametric point is correct

## Integration Notes

The interaction components integrate with Phase 3 and 4:

```csharp
// In a command:
var gp = new SurfaceConstrainedGetPoint(subd, evaluator);
gp.SetCommandPrompt("Pick point on surface");

if (gp.Get() == GetResult.Point)
{
    var param = gp.CurrentParametricPosition;

    // Use ElementPicker to find what's near this point
    var picker = new ElementPicker(regionManager, evaluator);
    var result = picker.PickAtPoint(param);

    if (result.Type == PickType.Vertex)
    {
        // Start vertex drag
        var dragHandler = new VertexDragHandler(regionManager, evaluator, subd);
        dragHandler.StartDrag(result.Vertex);
    }
}
```
