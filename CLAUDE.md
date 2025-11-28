# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

The **Ceramic Mold Analyzer** is a desktop application for discovering mathematical decompositions of SubD surfaces to create slip-casting ceramic molds. The project combines computational geometry, multiple mathematical analysis engines, and translucent porcelain artistry where "seams are not flaws to hide but truths to celebrate."

---

## ⚠️ CRITICAL: LOSSLESS UNTIL FABRICATION

**THIS IS THE MOST IMPORTANT PRINCIPLE OF THE ENTIRE PROJECT.**

The system maintains **exact mathematical representation** from input SubD through all analysis and region discovery. Approximation occurs **ONLY ONCE** at the final fabrication export (G-code/STL).

**NEVER convert SubD → mesh in the data pipeline.**

**Correct Architecture**:
```
Rhino SubD (exact)
  → HTTP Bridge (control cage: vertices, faces, creases as JSON)
  → C++ OpenSubdiv (exact limit surface evaluation via Stam eigenanalysis)
  → Parametric Regions (defined in parameter space: face_id, u, v)
  → Analysis (queries exact limit surface)
  → NURBS Surface Generation (analytical, exact)
  → Mold Solid (exact Brep operations)
  → G-code Export (SINGLE APPROXIMATION HAPPENS HERE)
```

**Display meshes** are generated on-demand for VTK viewport visualization ONLY.

**If you find yourself converting SubD to mesh anywhere before final export, STOP and reconsider.**

---

## ⚠️ CRITICAL: REFACTOR AS YOU GO & NO DOCUMENTATION CLUTTER

### Code Refactoring

Every change should leave the codebase cleaner. Technical debt compounds faster than interest.

**When touching code**:
- Remove dead code immediately
- Consolidate duplicate logic
- Improve unclear naming
- Add type hints to modified functions

**Code smell triggers**:
- Function > 50 lines → Extract
- Class > 300 lines → Split responsibilities
- Duplicate code in 2+ places → Abstract
- Magic numbers → Named constants

### Documentation Discipline

**DO NOT create .md files that will become stale.**

**Rules**:
1. **One source of truth**: `docs/PROJECT_STATUS.md` for status, `CLAUDE.md` for guidance
2. **Update, don't create**: Modify existing docs rather than creating new tracking files
3. **Delete when done**: Remove temporary docs immediately after use
4. **No completion reports**: Work is verified by tests, not by .md files
5. **No tracking documents**: Use git commits and PROJECT_STATUS.md instead

**Forbidden patterns**:
- ❌ AGENT_XX_COMPLETION.md
- ❌ DAY_X_SUMMARY.md
- ❌ BUILD_STATUS.md (use git)
- ❌ DEBUG_REPORT.md (fix the bug, don't document it)
- ❌ Any file that duplicates information elsewhere

---

## Current Status

See `docs/PROJECT_STATUS.md` for comprehensive implementation status.

**TL;DR**:
- ✅ C++ core working (SubD evaluation, curvature analysis, constraints)
- ✅ Python app working (state, UI, analysis lenses)
- ❌ NURBS/Mold generation (stubs, needs OpenCASCADE)
- ❌ UX v2.0 (designed in docs/reference/UX/, not implemented in desktop)

---

## Quick Start

```bash
# Launch the application
python3 launch.py

# Run tests
python3 -m pytest tests/

# Build C++ core
cd cpp_core/build && cmake .. && make
```

---

## Technology Stack

**C++ Core** (OpenSubdiv 3.6+, OpenCASCADE 7.x):
- Exact SubD limit surface evaluation (Stam eigenanalysis)
- NURBS operations and Boolean ops
- Mathematical analysis (curvature, spectral)
- GPU acceleration via Metal backend (macOS)

**Python Layer** (PyQt6 6.9.1, VTK 9.3.0):
- UI framework and user interaction
- State management and undo/redo
- Rhino communication (HTTP bridge)
- Workflow orchestration

**pybind11 Bindings**:
- Zero-copy numpy array sharing
- C++ module imported as `import cpp_core`

---

## UX Reference

See `docs/UX_GUIDE.md` for implementation details.

**Source of truth**: The React prototype in `docs/reference/UX/`

**Key concepts**:
- 4-sided layout (TOP/LEFT/RIGHT/BOTTOM)
- 6 workflow tabs (FILE/ANALYZE/EDIT/VALIDATE/FABRICATE/VIEW)
- Rhino-compatible viewport controls (LEFT=select, RIGHT=rotate)

---

## File Structure

```
Latent/
├── main.py                    # Application entry point
├── launch.py                  # Quick launcher
├── app/                       # Python application
│   ├── state/                 # ApplicationState, EditMode, ParametricRegion
│   ├── bridge/                # RhinoBridge, GeometryReceiver
│   ├── analysis/              # LensManager, DifferentialLens, SpectralLens
│   ├── ui/                    # Viewport3D, panels, toolbars
│   └── export/                # NURBS serialization
├── cpp_core/                  # C++ geometry kernel
│   ├── geometry/              # SubDEvaluator, NURBS (stubs)
│   ├── analysis/              # CurvatureAnalyzer
│   ├── constraints/           # DraftChecker, UndercutDetector
│   └── python_bindings/       # pybind11 bindings
├── rhino/                     # Grasshopper server components
├── tests/                     # Test suite
└── docs/
    ├── PROJECT_STATUS.md      # Single source of truth for status
    ├── UX_GUIDE.md            # UX implementation guide
    └── reference/             # Technical specs and UX prototype
```

---

## Development Best Practices

### Path Conventions

- ✅ `app/ui/viewport_3d.py`
- ❌ `ceramic_mold_analyzer/app/ui/viewport_3d.py`

### State Management

**Always go through ApplicationState**:
```python
# Correct
self.state.set_region_pinned(region_id, True)  # Emits signals, adds history

# Wrong
region.pinned = True  # Bypasses signals and history!
```

### Rhino Communication

**Control cage transfer** (correct, lossless):
```python
cage_data = {
    'vertices': [[x,y,z], ...],
    'faces': [[i,j,k,...], ...],
    'creases': [[i,j,sharpness], ...]
}
```

**Mesh transfer** (wrong, lossy):
```python
# ❌ DO NOT DO THIS
mesh = subd.ToMesh()  # Introduces approximation!
```

---

## Important Notes

### DO NOT:
- ❌ Convert SubD to mesh in data pipeline
- ❌ Create tracking/status .md files
- ❌ Modify state directly (use ApplicationState)
- ❌ Leave dead code or TODOs unaddressed

### DO:
- ✅ Transfer control cage (lossless)
- ✅ Define regions parametrically (face_id, u, v)
- ✅ Refactor as you go
- ✅ Update PROJECT_STATUS.md when status changes
- ✅ Delete temporary files when done

---

## Technical Philosophy

**Every form contains inherent mathematical coherences.** Different analytical lenses reveal different truths. The goal is eloquence over complexity - finding decompositions that create profound mathematical poetry written in light through translucent porcelain.

### Resonance Scores
- **0.8-1.0**: Excellent - form wants this decomposition
- **0.6-0.8**: Good - reveals important structure
- **0.4-0.6**: Moderate - usable but not ideal
- **0.0-0.4**: Poor - try different lens

---

## Archive Reference

Legacy implementations in `.Archive/` are **REFERENCE ONLY**:
- `.Archive/251013/` - Original Grasshopper implementation
- `.Archive/sprint_2025_11/` - Completed sprint artifacts

Study for concepts, do not copy code.
