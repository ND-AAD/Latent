# Launch Phase 4: Display & Visualization

Launch 3 parallel agents to create the display conduit system for region visualization in Rhino 8.

## Pre-Launch Checklist

- [ ] Phase 3 gate tests passed
- [ ] Plugin builds successfully (`dotnet build`)
- [ ] Data model classes exist (`RegionManager`, `Region`, `Edge`, `Vertex`)
- [ ] P/Invoke bindings work (`SubDEvaluator`, `SurfaceCurve`)
- [ ] Working directory is `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent`

## Agent Overview

| Agent | File | Objective |
|-------|------|-----------|
| 4A | `phase-4/agent-4a-region-conduit.md` | DisplayConduit for region visualization |
| 4B | `phase-4/agent-4b-curve-sampler.md` | Curve sampling with caching |
| 4C | `phase-4/agent-4c-region-fill.md` | Region fills and centroid markers |

## Dependencies

```
Agent 4A (RegionConduit) ──┐
                          │
Agent 4B (CurveSampler)  ──┼──► Phase 4 Complete
                          │
Agent 4C (RegionFill)    ──┘
```

**Parallel execution strategy:**
- All 3 agents can start immediately
- Agent 4A provides the main conduit shell
- Agent 4B provides curve sampling used by 4A
- Agent 4C provides fill rendering used by 4A
- Consolidation step integrates components

**File isolation:**
- 4A: `rhino_plugin/Display/RegionConduit.cs`, `rhino_plugin/Display/VisualizationSettings.cs`
- 4B: `rhino_plugin/Display/CurveSampler.cs`, `rhino_plugin/Display/CurveCache.cs`
- 4C: `rhino_plugin/Display/RegionFill.cs`, `rhino_plugin/Display/CentroidMarker.cs`

## Launch Instructions

Launch 3 agents in parallel using the Task tool:

### Agent 4A
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-4/agent-4a-region-conduit.md`

### Agent 4B
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-4/agent-4b-curve-sampler.md`

### Agent 4C
- **Subagent Type**: `general-purpose`
- **Prompt**: Read and execute `/Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/.claude/commands/phase-4/agent-4c-region-fill.md`

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
ls -la Display/*.cs

# If all pass, commit
cd ..
git add -A
git commit -m "feat: Phase 4 - Display & Visualization

- Add RegionConduit for region visualization
- Add VisualizationSettings for display configuration
- Add CurveSampler for parametric curve sampling
- Add CurveCache for performance optimization
- Add RegionFill for transparent region fills
- Add CentroidMarker for region centroid display
- Comprehensive unit tests"
```

## Phase 4 Gate Tests

All must pass before proceeding to Phase 5:

```bash
#!/bin/bash
set -e

echo "=== Phase 4 Gate Tests ==="

cd /Users/NickDuch/Desktop/Ind Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Test 4.1: Plugin builds
dotnet build
echo "✓ Plugin builds successfully"

# Test 4.2: Unit tests pass
dotnet test
echo "✓ Unit tests pass"

# Test 4.3: Display files exist
if [ -f Display/RegionConduit.cs ] && \
   [ -f Display/VisualizationSettings.cs ] && \
   [ -f Display/CurveSampler.cs ] && \
   [ -f Display/CurveCache.cs ] && \
   [ -f Display/RegionFill.cs ] && \
   [ -f Display/CentroidMarker.cs ]; then
    echo "✓ All display files exist"
else
    echo "✗ Missing display files"
    exit 1
fi

# Test 4.4: CurveSampler tests
dotnet test --filter "FullyQualifiedName~CurveSamplerTests"
echo "✓ CurveSampler tests pass"

# Test 4.5: RegionConduit tests
dotnet test --filter "FullyQualifiedName~RegionConduitTests"
echo "✓ RegionConduit tests pass"

# Test 4.6: CurveCache tests
dotnet test --filter "FullyQualifiedName~CurveCacheTests"
echo "✓ CurveCache tests pass"

echo ""
echo "=== Phase 4 PASSED - Ready for Phase 5 ==="
echo "(Pending visual verification in Rhino)"
```

## Visual Verification Checklist

After automated tests, verify in Rhino 8:

- [ ] Plugin loads without errors
- [ ] Regions display with boundary curves
- [ ] Curves appear smooth at all zoom levels
- [ ] Selection highlighting works (yellow for selected)
- [ ] Pinned elements show in blue
- [ ] Region fills render with transparency
- [ ] Centroid markers appear at region centers
- [ ] Performance acceptable with 20+ regions

## Troubleshooting

### Conduit not drawing
- Ensure `conduit.Enabled = true` is set
- Check that `RhinoDoc.ActiveDoc` is not null
- Verify conduit is added to document after plugin load

### Curves appear jagged
- Increase sample count in CurveSampler
- Check adaptive sampling is working
- Verify curvature-based refinement

### Fill transparency not working
- Check alpha channel in Color.FromArgb
- Verify DrawForeground is being called
- Try different blend modes

### Cache not invalidating
- Ensure Changed events are wired up
- Check that InvalidateCache is called on region changes
- Verify WeakReference cleanup

### Performance issues
- Reduce sample count for curves
- Increase cache size
- Profile with Rhino performance tools
- Consider level-of-detail based on zoom

## Integration Notes

The display components integrate with Phase 3:

```csharp
// In LatentPlugin.cs OnLoad():
var regionManager = new RegionManager();
var settings = new VisualizationSettings();
var conduit = new RegionConduit(regionManager, settings);
conduit.Enabled = true;

// Wire up to analysis results:
lensClient.AnalysisComplete += (sender, result) => {
    regionManager.LoadFromAnalysisResult(result);
    conduit.InvalidateCache();
    RhinoDoc.ActiveDoc?.Views.Redraw();
};
```
