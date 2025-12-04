# Ceramic Mold Analyzer - Project Status

**Last Updated**: 2025-12-04
**Status**: Architectural Pivot - Migrating to Rhino Plugin

---

## Architectural Direction

**Decision**: Migrate from standalone PyQt6/VTK desktop application to **Rhino plugin with parametric regions**.

**Rationale**:
- VTK cannot display exact SubD geometry (only tessellated meshes)
- Users need to see AND interact with the exact mathematical form
- Rhino provides native SubD visualization and selection
- Regions are defined by parametric curves, not cage topology

**See**:
- [Architecture Design](plans/2025-12-04-rhino-plugin-architecture-design.md)
- [Implementation Plan](plans/2025-12-04-rhino-plugin-implementation-plan.md)

---

## Component Status

### C++ Core (Keep & Extend)

| Component | Location | Status | Plugin Changes |
|-----------|----------|--------|----------------|
| SubDEvaluator | cpp_core/geometry/ | ✅ Production | Add inverse evaluation |
| CurvatureAnalyzer | cpp_core/analysis/ | ✅ Production | Keep as-is |
| Constraint Validation | cpp_core/constraints/ | ✅ Production | Keep as-is |
| Python Bindings | cpp_core/python_bindings/ | ✅ Production | Keep for analysis service |
| **C Bindings** | cpp_core/c_bindings/ | ❌ New | Create for P/Invoke |
| **Surface Curves** | cpp_core/geometry/ | ❌ New | Parametric curve evaluation |
| **Inverse Mapping** | cpp_core/geometry/ | ❌ New | 3D point → (face_id, u, v) |

### Python Analysis (Keep as Service)

| Component | Location | Status | Plugin Changes |
|-----------|----------|--------|----------------|
| LensManager | app/analysis/ | ✅ Working | Expose via JSON-RPC |
| DifferentialLens | app/analysis/ | ✅ Working | Add boundary curve extraction |
| SpectralLens | app/analysis/ | ✅ Working | Add nodal curve extraction |
| **Analysis Service** | analysis_service/ | ❌ New | JSON-RPC server for lenses |

### Rhino Plugin (New)

| Component | Status | Purpose |
|-----------|--------|---------|
| Plugin Foundation | ❌ New | C# plugin entry, commands |
| P/Invoke Layer | ❌ New | Managed wrappers for cpp_core |
| DisplayConduit | ❌ New | Region/curve visualization |
| Interaction Handlers | ❌ New | Surface-constrained picking |
| Eto.Forms Panels | ❌ New | Geometry list, lens controls |
| State Management | ❌ New | RegionManager, undo/redo |

### Deprecated (Phase Out)

| Component | Reason |
|-----------|--------|
| PyQt6 UI (app/ui/) | Replaced by Eto.Forms panels |
| VTK Viewport | Replaced by Rhino viewport |
| HTTP Bridge (app/bridge/) | Direct Rhino access in plugin |
| Desktop ApplicationState | Rebuilt for plugin context |

---

## Data Model (New)

### Vertices
```
Position: (face_id, u, v) on limit surface
Implicit Position: Original lens-computed position (or null if user-created)
Created By: lens | curve_modification | user_added
Pinned: Frozen regardless of re-analysis
```

### Edges (Boundary Curves)
```
Vertices: Ordered control points
Curve Type: bezier | bspline | geodesic (with degree)
Implicit Definition: Lens parameters (if lens-generated)
Pinned: Frozen regardless of re-analysis
```

### Regions
```
Boundary Edges: Closed loop of edges
Unity Principle: Mathematical description
Resonance Score: 0.0 - 1.0
Pinned: Frozen regardless of re-analysis
```

---

## Implementation Phases

| Phase | Duration | Status | Key Work |
|-------|----------|--------|----------|
| 0. Setup | 1 week | ❌ Not started | Dev environment, project structure |
| 1. C++ Extensions | 1 week | ❌ Not started | Inverse eval, curves, C bindings |
| 2. Python Service | 1 week | ❌ Not started | JSON-RPC, boundary extraction |
| 3. Plugin Foundation | 1.5 weeks | ❌ Not started | P/Invoke, wrappers, lens client |
| 4. Display | 1 week | ❌ Not started | RegionConduit, curve sampling |
| 5. Interaction | 1 week | ❌ Not started | Constrained GetPoint, drag handlers |
| 6. UI Panels | 1 week | ❌ Not started | Geometry list, lens panel, settings |
| 7. State | 0.5 weeks | ❌ Not started | RegionManager, undo/redo |
| 8. Testing | 1 week | ❌ Not started | Integration, performance, UAT |

**Total Estimated**: 8 weeks

---

## Key Decisions Made

1. **Curves define regions, not faces**: Boundaries are parametric curves on limit surface
2. **Implicit → Explicit on edit**: Any user modification converts lens-generated to user-controlled
3. **Pin ≠ Explicit**: Pinning protects from re-analysis, independent of implicit/explicit state
4. **Revert hierarchy**: Region → Edge → Vertex (top-down propagation)
5. **Two-step revert for modified curves**: Must revert curve type before reverting added vertices
6. **Visualization**: Curve display + optional fill transparency + centroid markers
7. **C# for plugin, Python for analysis**: Best of both ecosystems

---

## Build Artifacts (Current)

| Artifact | Status | Plugin Use |
|----------|--------|------------|
| cpp_core.cpython-312-darwin.so | ✅ Built | Analysis service |
| libcpp_core.a | ✅ Built | Base for shared library |
| **latent_core.dll/.dylib** | ❌ New | P/Invoke target |

---

## Dependencies

| Dependency | Current | Plugin |
|------------|---------|--------|
| OpenSubdiv | ✅ Required | ✅ Required |
| pybind11 | ✅ Required | ✅ For Python service |
| OpenCASCADE | Optional | Optional (NURBS export) |
| PyQt6 | Required | ❌ Not needed |
| VTK | Required | ❌ Not needed |
| RhinoCommon | N/A | ✅ Required |
| Eto.Forms | N/A | ✅ Required |

---

## File Structure (Planned)

```
Latent/
├── cpp_core/                    # C++ geometry kernel
│   ├── geometry/                # SubD evaluator + NEW: curves, inverse
│   ├── analysis/                # Curvature analyzer
│   ├── constraints/             # Draft/undercut validation
│   ├── python_bindings/         # pybind11 (keep for analysis)
│   └── c_bindings/              # NEW: P/Invoke layer
├── rhino_plugin/                # NEW: C# Rhino plugin
│   ├── Commands/                # Rhino commands
│   ├── UI/                      # Eto.Forms panels
│   ├── Display/                 # DisplayConduit
│   ├── Geometry/                # Region/vertex/edge logic
│   ├── Analysis/                # Lens client
│   └── Interop/                 # P/Invoke wrappers
├── analysis_service/            # NEW: Python JSON-RPC server
│   ├── service.py
│   └── protocol.py
├── app/                         # DEPRECATED: Desktop app
├── rhino/                       # DEPRECATED: HTTP bridge
├── tests/                       # Test suite
└── docs/
    ├── PROJECT_STATUS.md        # This file
    └── plans/                   # Architecture & implementation plans
```

---

## Next Steps

1. **Set up Rhino plugin development environment**
2. **Implement C++ inverse evaluation** (project_point_onto_surface)
3. **Create C bindings** for P/Invoke compatibility
4. **Build cross-platform shared library** (latent_core.dll/.dylib)
5. **Prototype DisplayConduit** with simple curve drawing
