# Ceramic Mold Analyzer - Project Status

**Last Updated**: 2025-11-28
**Status**: Post-Sprint, Consolidation Phase

---

## Quick Start

```bash
python3 launch.py
```

---

## Component Status

### Working (Production-Ready)

| Component | Location | Status |
|-----------|----------|--------|
| SubDEvaluator | [cpp_core/geometry/](cpp_core/geometry/) | OpenSubdiv integration, exact limit surface evaluation |
| CurvatureAnalyzer | [cpp_core/analysis/](cpp_core/analysis/) | Full differential geometry (κ₁, κ₂, K, H) |
| Constraint Validation | [cpp_core/constraints/](cpp_core/constraints/) | Draft angles, undercut detection |
| Python Bindings | [cpp_core/python_bindings/](cpp_core/python_bindings/) | All core classes, zero-copy numpy |
| ApplicationState | [app/state/](app/state/) | Undo/redo, signals, serialization |
| Edit Modes | [app/state/](app/state/) | SOLID/PANEL/EDGE/VERTEX selection |
| Parametric Regions | [app/state/](app/state/) | (face_id, u, v) lossless representation |
| Differential Lens | [app/analysis/](app/analysis/) | Curvature-based region discovery |
| Spectral Lens | [app/analysis/](app/analysis/) | Eigenfunction decomposition |
| VTK Viewport | [app/ui/](app/ui/) | Rhino-compatible controls |
| Rhino Bridge | [app/bridge/](app/bridge/) | Control cage transfer (lossless) |

### Incomplete (Stubs)

| Component | Location | Status | Needed |
|-----------|----------|--------|--------|
| NURBS Fitting | [cpp_core/geometry/nurbs_fitting.cpp](cpp_core/geometry/nurbs_fitting.cpp) | ~30% | OpenCASCADE integration |
| Draft Transform | [cpp_core/geometry/draft_transform.cpp](cpp_core/geometry/draft_transform.cpp) | ~40% | Complete implementation |
| Mold Solid | [cpp_core/geometry/mold_solid.cpp](cpp_core/geometry/mold_solid.cpp) | ~30% | Boolean operations |

### UX Gap

| Aspect | Status |
|--------|--------|
| **Designed** | 4-sided tab-based architecture (see [docs/reference/UX/](reference/UX/)) |
| **Implemented** | Phase 0 single-panel layout |
| **Gap** | Desktop app not migrated to v2.0 UX design |

---

## Build Artifacts

| Artifact | Size | Status |
|----------|------|--------|
| cpp_core.cpython-312-darwin.so | 532KB | Python extension (built) |
| libcpp_core.a | 200KB | Static library (built) |

### Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| OpenSubdiv | Required | Found, working |
| pybind11 | Required | Found, working |
| OpenCASCADE | Optional | NOT FOUND (NURBS features disabled) |
| PyQt6 | Required | 6.9.1 |
| VTK | Required | 9.3.0 |

---

## Test Coverage

- **77 test files** across unit, integration, and validation
- Run tests: `python3 -m pytest tests/`
- C++ tests: `cd cpp_core/build && ctest`

---

## Architecture Verification

| Principle | Status |
|-----------|--------|
| Lossless until fabrication | ✅ Correctly implemented |
| Control cage transfer (not mesh) | ✅ Working |
| Parametric regions in (face_id, u, v) space | ✅ Working |
| Display meshes separate from data pipeline | ✅ Working |

---

## File Structure

```
Latent/
├── main.py                    # Application entry point
├── launch.py                  # Quick launcher (Qt config)
├── app/                       # Python application
│   ├── state/                 # State management, edit modes, regions
│   ├── bridge/                # Rhino/Grasshopper communication
│   ├── analysis/              # Mathematical lenses
│   ├── ui/                    # PyQt6/VTK interface
│   └── export/                # NURBS serialization
├── cpp_core/                  # C++ geometry kernel
│   ├── geometry/              # SubD evaluator, NURBS (stubs)
│   ├── analysis/              # Curvature analyzer
│   ├── constraints/           # Draft/undercut validation
│   └── python_bindings/       # pybind11 bindings
├── rhino/                     # Grasshopper server components
├── tests/                     # Test suite (77 files)
└── docs/
    ├── PROJECT_STATUS.md      # This file (single source of truth)
    ├── UX_GUIDE.md            # UX implementation guide
    └── reference/
        ├── UX/                # React prototype (UX source of truth)
        └── *.md               # Technical specifications
```

---

## Known Issues

1. **OpenCASCADE not installed** - NURBS features are stubs
2. **UX not migrated** - Desktop still using Phase 0 layout
3. **Region visualization TODOs** - Highlighting and pinned state indicators pending
4. **Viewport TODOs** - Control net extraction needs rhino3dm integration

---

## Next Steps (Prioritized)

1. **Install OpenCASCADE** - Enable NURBS fitting
2. **Complete NURBS stubs** - ~200 lines of implementation needed
3. **UX migration** - Implement v2.0 tab-based architecture
4. **End-to-end workflow** - Test full SubD → Mold pipeline
