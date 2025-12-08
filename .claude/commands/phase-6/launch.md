# Phase 6: UI Panels - Launch

## Pre-Launch Checklist

Before launching Phase 6 agents, verify:

- [ ] Phase 5 complete (all interaction handlers working)
- [ ] `dotnet build` succeeds in `rhino_plugin/`
- [ ] `RegionManager` fires `Changed` events correctly
- [ ] `LatentPlugin.Instance` provides access to all services
- [ ] `VisualizationSettings` exists in `Display/`

```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin
dotnet build

# Verify key dependencies exist
ls Geometry/RegionManager.cs
ls Display/VisualizationSettings.cs
ls Analysis/LensClient.cs
ls LatentPlugin.cs
```

---

## Agent Overview

| Agent | Objective | Files | Dependencies |
|-------|-----------|-------|--------------|
| **6A** | Geometry List Panel | `UI/GeometryListPanel.cs`, `UI/GeometryListItem.cs`, `UI/EdgeRevertDialog.cs` | RegionManager, IGeometryElement |
| **6B** | Lens Control Panel | `UI/LensPanel.cs`, `UI/LensParameterControl.cs` | LensClient, RegionManager |
| **6C** | Visualization Settings Panel | `UI/VisualizationPanel.cs` | VisualizationSettings, RegionConduit |

---

## Dependencies

```
Phase 5 (Interaction)
    │
    ▼
┌───────────────────────────────────────────────┐
│                  Phase 6                       │
│                                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Agent   │  │ Agent   │  │ Agent   │       │
│  │   6A    │  │   6B    │  │   6C    │       │
│  │Geometry │  │  Lens   │  │  Viz    │       │
│  │  List   │  │ Control │  │Settings │       │
│  └─────────┘  └─────────┘  └─────────┘       │
│       │            │            │             │
│       └────────────┼────────────┘             │
│                    ▼                          │
│            All Independent                    │
│         (can run in parallel)                 │
└───────────────────────────────────────────────┘
    │
    ▼
Phase 7 (Integration)
```

All Phase 6 agents are **independent** - they can run in parallel without conflicts.

---

## Launch Instructions

Launch all three agents in parallel:

### Agent 6A: Geometry List Panel
```
Use Task tool with:
- subagent_type: "general-purpose"
- prompt: "Read and execute: .claude/commands/phase-6/agent-6a-geometry-list.md"
```

### Agent 6B: Lens Control Panel
```
Use Task tool with:
- subagent_type: "general-purpose"
- prompt: "Read and execute: .claude/commands/phase-6/agent-6b-lens-panel.md"
```

### Agent 6C: Visualization Settings Panel
```
Use Task tool with:
- subagent_type: "general-purpose"
- prompt: "Read and execute: .claude/commands/phase-6/agent-6c-visualization-panel.md"
```

---

## Post-Phase Consolidation

After all agents complete:

### 1. Build and Test
```bash
cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

# Build
dotnet build

# Run all Phase 6 tests
dotnet test --filter "FullyQualifiedName~GeometryListPanel|FullyQualifiedName~LensPanel|FullyQualifiedName~VisualizationPanel"
```

### 2. Verify Panel Registration
```bash
# Check that panels are registered in LatentPlugin.cs
grep -n "RegisterPanel\|Panels\." LatentPlugin.cs
```

### 3. Git Commit
```bash
git add rhino_plugin/UI/
git add rhino_plugin/Tests/
git add rhino_plugin/LatentPlugin.cs

git commit -m "feat: Phase 6 - UI Panels

- GeometryListPanel with mode selector and revert workflow
- LensPanel with dynamic parameter controls
- VisualizationPanel with settings persistence

🤖 Generated with Claude Code"
```

---

## Gate Tests

Phase 6 is complete when ALL of the following pass:

```bash
#!/bin/bash
set -e

cd /Users/NickDuch/Desktop/Ind\ Designs/NDAAD/RhinoProjects/Latent/rhino_plugin

echo "=== Phase 6 Gate Tests ==="

# 1. Build succeeds
echo "Testing build..."
dotnet build --no-restore -v q
echo "✓ Build passed"

# 2. UI files exist
echo "Testing file existence..."
test -f UI/GeometryListPanel.cs && echo "✓ GeometryListPanel.cs exists"
test -f UI/GeometryListItem.cs && echo "✓ GeometryListItem.cs exists"
test -f UI/LensPanel.cs && echo "✓ LensPanel.cs exists"
test -f UI/VisualizationPanel.cs && echo "✓ VisualizationPanel.cs exists"

# 3. Unit tests pass
echo "Running unit tests..."
dotnet test --filter "FullyQualifiedName~Phase6|FullyQualifiedName~GeometryList|FullyQualifiedName~LensPanel|FullyQualifiedName~VisualizationPanel" --no-build -v q
echo "✓ Unit tests passed"

# 4. Panel registration exists
echo "Checking panel registration..."
grep -q "RegisterPanel" LatentPlugin.cs && echo "✓ Panel registration found"

echo ""
echo "=== All Phase 6 Gate Tests Passed ==="
```

---

## Troubleshooting

### Build Errors

**"Eto.Forms not found"**
- Ensure `Eto.Forms` NuGet package is referenced
- Check: `grep Eto rhino_plugin/Latent.csproj`

**"Panel abstract members not implemented"**
- Rhino panels require specific overrides
- Check agent files for complete implementation

### Runtime Issues

**"Panel not appearing in Rhino"**
- Verify `RegisterPanel` called in `OnLoad`
- Check Rhino's Panels menu

**"RegionManager.Changed not firing"**
- Ensure `OnChanged()` is called after mutations
- Verify event subscription in panel constructor

---

## File Ownership

| File | Owner Agent |
|------|-------------|
| `UI/GeometryListPanel.cs` | 6A |
| `UI/GeometryListItem.cs` | 6A |
| `UI/EdgeRevertDialog.cs` | 6A |
| `UI/LensPanel.cs` | 6B |
| `UI/LensParameterControl.cs` | 6B |
| `UI/VisualizationPanel.cs` | 6C |
| `Tests/GeometryListPanelTests.cs` | 6A |
| `Tests/LensPanelTests.cs` | 6B |
| `Tests/VisualizationPanelTests.cs` | 6C |
| `LatentPlugin.cs` (panel registration only) | All (merge carefully) |

---

## Notes

- All panels use Eto.Forms (cross-platform, Rhino-native)
- Panels subscribe to `RegionManager.Changed` for updates
- Settings persistence uses `PlugIn.Settings`
- Python `app/ui/` files provide reference implementations to port
