# Latent Plugin User Guide

**Version**: 1.0
**Last Updated**: 2025-12-08
**Compatibility**: Rhino 8 (macOS/Windows)

---

## Overview

The Latent Plugin for Rhino 8 enables mathematical decomposition of SubD surfaces for ceramic slip-casting mold design. It discovers regions where surfaces can be cleanly separated based on curvature analysis and spectral decomposition, revealing the inherent mathematical structure of forms.

> *"The seams are not flaws to hide but truths to celebrate"*

**Key Concept**: Regions are defined by boundary curves on the exact limit surface, maintaining mathematical precision until final fabrication export.

---

## Installation

### Requirements

- Rhino 8 (Windows or macOS)
- .NET Framework 4.8 or .NET 6+
- Python 3.8+ (for analysis service)

### Installation Steps

1. Copy `LatentPlugin.rhp` to your Rhino plugins folder:
   - **Windows**: `%APPDATA%\McNeel\Rhinoceros\8.0\Plug-ins\`
   - **macOS**: `~/Library/Application Support/McNeel/Rhinoceros/8.0/Plug-ins/`

2. Copy the native library to the same folder:
   - **Windows**: `latent_core.dll`
   - **macOS**: `liblatent_core.dylib`

3. Restart Rhino 8

4. Type `PlugInManager` and verify "Latent" is listed and enabled

---

## Quick Start

1. **Create or import a SubD surface** in Rhino
2. **Run `LatentAnalyze`** to discover regions
3. **Select lens type** (Differential, Spectral, or Cage-Aligned)
4. **Review discovered regions** in the viewport
5. **Pin regions** you want to keep
6. **Edit boundaries** by dragging vertices
7. **Export** when satisfied (future feature)

---

## Commands

### LatentAnalyze

Runs mathematical analysis on the selected SubD using the specified lens.

**Usage**: `LatentAnalyze`

**Steps**:
1. Select a SubD object when prompted
2. Choose lens type from options:
   - **Differential**: Finds regions based on curvature continuity (κ₁, κ₂)
   - **Spectral**: Finds regions based on Laplacian eigenfunction nodal lines
   - **Cage-Aligned**: Aligns regions with SubD control cage topology
3. Adjust lens parameters if needed
4. Click "Analyze" to run

**Output**: Boundary curves displayed on the SubD surface, regions listed in Geometry panel.

---

### LatentSelect

Selects regions, edges, or vertices for editing.

**Usage**: `LatentSelect`

**Behavior**:
- Click on **region interior** → selects the region
- Click **near an edge** → selects the boundary edge
- Click **near a vertex** → selects the control vertex

**Tip**: Use the Geometry List panel to see all elements and their states.

---

### LatentPin

Pins or unpins the currently selected element.

**Usage**: `LatentPin`

**Pinned elements**:
- Are protected from lens reanalysis
- Cannot be reverted
- Display in blue (configurable)
- Persist across multiple analysis runs

**Use pinning to**: Lock in decompositions you're satisfied with before experimenting with different lens parameters.

---

### LatentRevert

Reverts the selected element to its implicit (lens-defined) state.

**Usage**: `LatentRevert`

**Prerequisite**: Element must be unpinned first.

**Revert hierarchy**:

| Element | Revert Behavior |
|---------|-----------------|
| **Vertex** | Returns to original lens-computed position |
| **Edge** | Choice of "curve type only" or "fully revert" (see below) |
| **Region** | Reverts all boundary edges and their vertices |

**Edge Revert Options**:
- **Curve type only**: Restores original curve type (Bezier, B-spline) but keeps current vertex positions
- **Fully revert**: Restores both curve type AND all vertex positions

**Note**: Vertices created by curve degree changes cannot be individually reverted. You must revert the parent edge's curve type first.

---

### LatentSettings

Opens visualization settings (also accessible from Latent Display panel).

**Usage**: `LatentSettings`

---

## Panels

### Latent Lens Panel

Control panel for lens selection and analysis.

**Controls**:
- **Lens Selector**: Choose between Differential, Spectral, Cage-Aligned
- **Parameters**: Lens-specific settings (varies by lens type)
  - Differential: Curvature threshold, tolerance
  - Spectral: Eigenfunction index, smoothing
- **Analyze Button**: Run analysis with current parameters
- **Progress**: Shows analysis progress for large models

---

### Latent Geometry Panel

List of all vertices, edges, and regions with state management.

**Mode Selector**: Toggle between:
- **Regions**: Shows all discovered regions
- **Edges**: Shows all boundary curves
- **Vertices**: Shows all control points

**Columns**:
- **ID**: Element identifier
- **State**: `implicit`, `explicit`, or `📌 pinned`
- **Details**: Type-specific info (resonance score, curve type, origin)

**Buttons**:
- **📌 Pin / 📍 Unpin**: Toggle pinned state
- **↩ Revert**: Revert to implicit state (disabled when pinned)

**Behavior**:
- Single-click to select (syncs with viewport)
- Double-click to toggle pin state
- Selection in panel highlights in viewport

---

### Latent Display Panel

Visualization settings for the display conduit.

**Options**:
- **Show Region Fill**: Toggle semi-transparent region fills
- **Show Centroid Markers**: Toggle dot markers at region centers
- **Curve Sample Count**: Quality of boundary curve display (10-200)

**Colors**:
- **Selected Color**: Color for selected elements (default: Yellow)
- **Pinned Color**: Color for pinned elements (default: Light Blue)
- **Normal Color**: Color for normal elements (default: Gray)

**Opacity**: Slider for region fill transparency (0-100%)

---

## Concepts

### Implicit vs Explicit State

Every element has an **implicit** position/shape defined by the lens analysis.

| State | Meaning | Visual |
|-------|---------|--------|
| **Implicit** | At lens-defined position | Normal color |
| **Explicit** | User has modified | Normal color |
| **Pinned** | Protected from changes | Blue color |

**Transitions**:
- Any user edit → Implicit becomes Explicit
- Revert → Explicit becomes Implicit
- Pin/Unpin → Independent of implicit/explicit

### Pinning

Pinned elements are **frozen** and protected from any changes:

- They persist across lens reanalysis
- They cannot be dragged or edited
- They cannot be reverted (must unpin first)
- Adjacent unpinned elements respect pinned boundaries

**Workflow tip**: Run analysis, pin the good regions, re-run with different parameters to improve the rest.

### Revert Hierarchy

When reverting, changes propagate **top-down**:

```
Region Revert
    └── All Edges Revert
            └── All Vertices Revert
```

**Special case - curve modification vertices**:

When you change a curve's degree (e.g., quadratic → cubic), new control vertices are added. These vertices **cannot be individually reverted** because they're intrinsic to the curve type.

To remove them:
1. Select the edge
2. Run `LatentRevert`
3. Choose "Revert curve type only" or "Fully revert"

### Parametric Coordinates

All positions are stored as **parametric coordinates** `(face_id, u, v)` on the SubD limit surface:

- `face_id`: Which face of the control cage
- `u, v`: Position within that face's parameter domain [0,1] × [0,1]

This ensures positions remain valid even as the limit surface curves.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Z` | Undo last operation |
| `Ctrl+Y` | Redo |
| `Escape` | Cancel current operation |
| `Enter` | Accept/confirm selection |
| `Delete` | Delete selected user-added vertex (if allowed) |

---

## Troubleshooting

### "Analysis service failed to start"

**Cause**: Python analysis service couldn't start.

**Solutions**:
1. Ensure Python 3.8+ is installed and in PATH
2. Check that `analysis_service/` folder exists
3. Verify port 5555 is not in use by another application
4. Check Rhino command line for detailed error messages

### "Native library not found"

**Cause**: C++ core library not found.

**Solutions**:
1. Copy `liblatent_core.dylib` (macOS) or `latent_core.dll` (Windows) to plugin folder
2. On macOS: Allow in System Preferences > Security & Privacy
3. Verify library architecture matches Rhino (x64 vs ARM64)

### Curves appear jagged

**Cause**: Low curve sample count.

**Solution**: Increase "Curve Sample Count" in Latent Display panel (try 100+).

### Performance is slow with many regions

**Cause**: Display overhead with complex geometry.

**Solutions**:
1. Reduce "Curve Sample Count"
2. Disable "Show Region Fill"
3. Hide non-essential regions (future feature)

### "Cannot revert vertex"

**Cause**: Vertex was created by curve degree change.

**Solution**: Revert the parent edge's curve type first (use Edge mode in Geometry panel).

### Selection doesn't work on boundaries

**Cause**: Click tolerance may be too small.

**Solution**: Click closer to the boundary curve, or use Geometry panel for selection.

---

## Technical Notes

### Lossless Architecture

The plugin maintains **exact mathematical representation** throughout:

```
Rhino SubD (exact)
  → C++ OpenSubdiv (exact limit surface)
  → Parametric Regions (face_id, u, v)
  → Analysis (queries exact surface)
  → Display (temporary tessellation only)
```

Approximation occurs **only** at final G-code/STL export.

### Analysis Lenses

**Differential Lens**:
- Computes principal curvatures (κ₁, κ₂) across the surface
- Finds boundaries where curvature crosses thresholds
- Good for: convex/concave separation, draft angle regions

**Spectral Lens**:
- Computes Laplace-Beltrami eigenfunctions
- Finds nodal lines (where eigenfunction = 0)
- Good for: natural frequency-based decomposition, symmetric forms

**Cage-Aligned Lens**:
- Uses SubD control cage edges directly
- Simplest decomposition, aligned with mesh topology
- Good for: simple forms, predictable boundaries

---

## Workflows

### Workflow 1: Quick Analysis

1. Create/import SubD
2. `LatentAnalyze` -> Differential -> default parameters
3. Review discovered regions
4. Done!

### Workflow 2: Iterative Refinement

1. `LatentAnalyze` -> Spectral -> 3 eigenfunctions
2. Review regions - pin ones you like with `LatentPin`
3. `LatentAnalyze` -> Differential -> 0.2 tolerance
4. Unpinned regions update, pinned ones remain
5. Continue pinning good regions
6. Repeat with different lenses/parameters

### Workflow 3: Manual Adjustment

1. Run initial analysis
2. `LatentSelect` -> pick a vertex
3. Drag vertex to new position (becomes explicit)
4. Pin the modified element
5. Reanalyze - your changes are preserved

### Workflow 4: Recovering from Mistakes

1. Made unwanted changes? `LatentSelect` the element
2. If pinned: `LatentPin` to unpin first
3. `LatentRevert` to restore lens-computed state
4. For edges: choose "fully revert" to restore everything

---

## Support

For issues and feature requests:
- GitHub: https://github.com/ND-AAD/Latent/issues

For architecture documentation:
- [Architecture Design](plans/2025-12-04-rhino-plugin-architecture-design.md)
- [Implementation Plan](plans/2025-12-04-rhino-plugin-implementation-plan.md)

---

## Version History

- **1.0.0** (2025-12-08) - Complete Rhino 8 plugin with all phases implemented
  - Differential and Spectral lenses
  - Full state management (implicit/explicit/pinned)
  - Undo/redo integration with Rhino
  - Three UI panels (Lens, Geometry, Display)
  - Comprehensive test suite
- **0.1.0** - Initial development release
