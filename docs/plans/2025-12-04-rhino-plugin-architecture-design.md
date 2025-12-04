# Rhino Plugin Architecture Design

**Date**: 2025-12-04
**Status**: Approved Design
**Supersedes**: Standalone desktop app architecture (VTK-based)

---

## Executive Summary

Migrate from standalone PyQt6/VTK desktop application to a Rhino plugin that leverages Rhino's native SubD visualization while maintaining the lossless parametric workflow. The plugin uses boundary curves on the limit surface to define regions, with all geometry remaining mathematically exact until final fabrication export.

---

## Problem Statement

### Why Not Standalone Desktop App?

1. **VTK cannot display exact SubD geometry** - only tessellated meshes
2. **Users need to see the actual form** - not a mesh approximation
3. **Users need to interact with the exact form** - selection on limit surface, not mesh facets
4. **The concept requires revealing mathematical patterns** - impossible without exact visualization

### Why Rhino Plugin?

1. **Native SubD visualization** - Rhino displays exact limit surfaces
2. **Established interaction patterns** - selection filters, gumball, familiar UX
3. **No UI framework development** - Eto.Forms for panels
4. **Professional environment** - users already work in Rhino

### Why Not Pure Cage-Aligned Approach?

Mathematical lenses (curvature, spectral, etc.) produce boundaries that don't align with SubD control cage topology. The system must support arbitrary curves on the limit surface.

---

## Core Principles

### 1. Lossless Until Fabrication

```
SubD Geometry (exact, never modified)
    ↓
Boundary Curves (mathematical definitions on limit surface)
    ↓
Regions (areas bounded by curves)
    ↓
Analysis & Editing (all in parametric space)
    ↓
NURBS Mold Generation (exact)
    ↓
G-code Export (SINGLE APPROXIMATION POINT)
```

**No meshes in the data pipeline.** Display tessellation is temporary and never stored.

### 2. Geometry as Source of Truth

The SubD form is **fixed input** to an analytical process. Users discover and decompose; they don't modify the source geometry (except as a separate secondary workflow).

### 3. Mathematical Curves, Not Sampled Points

Boundary curves are defined mathematically:
- Implicit: from lens analysis (curvature threshold, eigenfunction zero-crossing)
- Explicit: user-edited splines in parametric space

---

## Data Model

### Vertex

```
Vertex {
    id: string
    position: (face_id, u, v)           // current parametric position
    implicit_position: (face_id, u, v) | null  // original lens position
    created_by: "lens" | "curve_modification" | "user_added"
    is_pinned: bool
}
```

### Edge (Boundary Curve)

```
Edge {
    id: string
    vertices: [vertex_id, ...]          // ordered control points
    curve_type: {
        type: "bezier" | "bspline" | "geodesic" | "implicit"
        degree: int
    }
    implicit_curve_type: { type, degree } | null  // original from lens
    implicit_definition: {              // for implicit curves
        lens: "curvature" | "spectral" | ...
        threshold: float
        parameters: {...}
    } | null
    is_pinned: bool
}
```

### Region

```
Region {
    id: string
    boundary_edges: [edge_id, ...]      // ordered, closed loop
    unity_principle: string             // mathematical description from lens
    resonance_score: float              // 0.0 - 1.0
    is_pinned: bool
}
```

---

## State Management

### Implicit vs Explicit

| State | Meaning | Transitions |
|-------|---------|-------------|
| **Implicit** | Defined by lens analysis | → Explicit (on any user edit) |
| **Explicit** | User-modified | → Implicit (on revert) |

### Pinned vs Unpinned

| State | Meaning | Behavior |
|-------|---------|----------|
| **Unpinned** | Subject to change | Re-analysis may modify |
| **Pinned** | Protected | Frozen regardless of re-analysis |

**These are independent.** All four combinations are valid:
- Implicit + Unpinned: lens-controlled, will update on re-analysis
- Implicit + Pinned: at lens position, frozen
- Explicit + Unpinned: user-edited, may be affected by adjacent changes
- Explicit + Pinned: user-edited, frozen

---

## Revert Hierarchy

**Prerequisite:** Must unpin before reverting.

### Top-Down Propagation

| Revert Target | Effect |
|---------------|--------|
| **Region** | All boundary edges revert → all vertices revert → curve types revert |
| **Edge** | Options: (1) curve type only, or (2) fully (type + all vertices) |
| **Vertex** | Position reverts; edge curve adjusts using current type |

### Vertex Revert Constraint

Vertices created by curve modification (e.g., degree 2 → degree 3) cannot be individually reverted.

**Flow:**
1. User attempts to revert added vertex
2. System prompts: "Revert curve type first?"
3. User confirms → curve reverts to original type → extra vertex removed
4. Original vertices now individually revertable

### Edge Revert Dialog

```
┌─────────────────────────────────────────────┐
│ Revert Edge                                 │
├─────────────────────────────────────────────┤
│ ○ Revert curve type only                    │
│   (keeps current vertex positions)          │
│                                             │
│ ○ Revert fully                              │
│   (curve type + all vertex positions)       │
│                                             │
│              [Cancel]  [Revert]             │
└─────────────────────────────────────────────┘
```

---

## Visualization

### What Rhino Displays

1. **SubD geometry** - exact, native Rhino rendering
2. **Boundary curves** - drawn on the limit surface
3. **Region state indicators** - selected/pinned/normal

### Region State Visualization (Toggleable Settings)

```
☐ Fill transparency (colored transparent overlay)
☐ Centroid marker (dot at region center on surface)
☐ Both
```

### Color Scheme

| State | Default Color |
|-------|---------------|
| Selected | Yellow |
| Pinned | Blue |
| Normal | White/Gray |

---

## Interaction Model

### Mode-Based Selection

| Mode | Click Selects | Gumball Behavior |
|------|--------------|------------------|
| **Panel** | Region | N/A (regions don't move) |
| **Edge** | Boundary curve | Moves all vertices on edge by same vector |
| **Vertex** | Curve control point | Moves single vertex |

### Surface-Constrained Movement

All vertex movement is constrained to the SubD limit surface:

1. User drags vertex with gumball (3D movement)
2. System intercepts new position
3. Project position onto limit surface
4. Update vertex parametric coordinates (face_id, u, v)

### Curve Editing

Users can:
- Add control points to a curve
- Remove control points from a curve
- Change curve degree
- Change curve type (bezier, bspline, geodesic)
- Drag control points along surface

**Any edit converts implicit → explicit.**

---

## Lens Integration

### How Lenses Produce Curves

| Lens | Curve Definition |
|------|-----------------|
| **Curvature** | Implicit contour: H(u,v) = threshold |
| **Spectral** | Nodal line: φₙ(u,v) = 0 |
| **Cage-Aligned** | Control cage edges (degenerate case) |

### Lens Workflow

```
1. User selects lens and parameters
2. Lens analyzes limit surface → produces implicit curves
3. Curves displayed on SubD
4. User reviews regions
5. User pins regions to keep
6. User edits curves (→ become explicit)
7. User re-runs lens (unpinned implicit regions update)
```

---

## Geometry List Panel

**Shows all elements in current mode with state and revert option:**

```
VERTEX MODE:
┌─────────────────────────────────────────────────────┐
│ Vertices                                            │
├─────────────────────────────────────────────────────┤
│ V1  [implicit]              [Revert]  ← grayed out  │
│ V2  [explicit]              [Revert]  ← active      │
│ V3  [explicit] 📌           [Revert]  ← must unpin  │
│ V4  [added by degree change][Revert]  ← shows error │
└─────────────────────────────────────────────────────┘

EDGE MODE:
┌─────────────────────────────────────────────────────┐
│ Edges                                               │
├─────────────────────────────────────────────────────┤
│ E1  Bezier°2 [implicit]     [Revert]                │
│ E2  BSpline°3 [explicit] 📌 [Revert]                │
└─────────────────────────────────────────────────────┘

PANEL MODE:
┌─────────────────────────────────────────────────────┐
│ Regions                                             │
├─────────────────────────────────────────────────────┤
│ R1  "Convex κ>0" [implicit] 0.87      [Revert]      │
│ R2  "Manual"     [explicit] 📌        [Revert]      │
└─────────────────────────────────────────────────────┘
```

---

## Technical Architecture

### C++ Core (Existing + Extensions)

**Keep:**
- SubDEvaluator (OpenSubdiv limit surface evaluation)
- CurvatureAnalyzer (differential geometry)
- Constraint validation (draft angles, undercuts)
- NURBS fitting (OpenCASCADE)

**Add:**
- Inverse evaluation: 3D point → (face_id, u, v)
- Curve-on-surface evaluation
- Point-in-region test in parametric space
- Curve projection to limit surface

### Rhino Plugin Layer (New)

**Language:** C# (primary) or Python 3 (Rhino 8+)

**Components:**
- DisplayConduit for curve/region visualization
- Custom GetPoint for surface-constrained dragging
- Eto.Forms panels for geometry list, lens controls, settings
- State management (mirrors existing ApplicationState logic)
- Bridge to C++ core via P/Invoke or Python bindings

### Data Flow

```
Rhino SubD Object
    ↓ (read control cage)
C++ Core: SubDEvaluator
    ↓ (exact limit surface)
C++ Core: Lens Analysis
    ↓ (implicit curves)
Plugin: State Management
    ↓ (vertices, edges, regions)
Plugin: DisplayConduit
    ↓ (visual representation)
Rhino Viewport
```

---

## Migration Path

### What Transfers From Current Codebase

| Component | Transfer Status |
|-----------|-----------------|
| C++ SubDEvaluator | Keep, add inverse evaluation |
| C++ CurvatureAnalyzer | Keep |
| C++ Constraints | Keep |
| C++ NURBS/Mold | Keep |
| Python LensManager | Port to C# or keep as subprocess |
| Python State Logic | Port to C# |
| Python UI | Replace with Eto.Forms |
| VTK Visualization | Discard (replaced by Rhino) |
| HTTP Bridge | Discard (direct Rhino access) |

### What's New

- Rhino plugin infrastructure
- DisplayConduit visualization
- Surface-constrained interaction
- Eto.Forms UI panels
- C++ inverse evaluation
- C++ curve-on-surface operations

---

## Open Questions

1. **C# vs Python for plugin?** C# has better RhinoCommon integration; Python 3 is faster to develop.

2. **State persistence?** Where to store region definitions - in Rhino document or external file?

3. **Multi-SubD support?** Can user analyze multiple SubDs in one session?

4. **Undo integration?** Use Rhino's undo system or separate internal undo?

---

## Success Criteria

1. User sees exact SubD geometry (Rhino native)
2. Boundary curves display correctly on limit surface
3. Selection works on exact geometry
4. Surface-constrained vertex dragging works smoothly
5. Implicit/explicit state transitions work correctly
6. Pin/unpin/revert workflow is intuitive
7. Multiple lenses produce correct implicit curves
8. Lossless export to NURBS molds

---

## References

- Current codebase: `/Users/NickDuch/.claude-worktrees/Latent/focused-robinson/`
- C++ core: `cpp_core/`
- Original UX design: `docs/reference/UX/`
- Lossless architecture: `CLAUDE.md`
