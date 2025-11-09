# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **Ceramic Mold Analyzer** is a desktop application for discovering mathematical decompositions of SubD surfaces to create slip-casting ceramic molds. The project combines computational geometry, multiple mathematical analysis engines, and translucent porcelain artistry where "seams are not flaws to hide but truths to celebrate."

## ⚠️ CRITICAL ARCHITECTURAL PRINCIPLE: LOSSLESS UNTIL FABRICATION

**THIS IS THE MOST IMPORTANT PRINCIPLE OF THE ENTIRE PROJECT.**

The system maintains **exact mathematical representation** from input SubD through all analysis and region discovery. Approximation occurs **ONLY ONCE** at the final fabrication export (G-code/STL).

### What This Means:

**NEVER convert SubD → mesh in the data pipeline**. This would introduce approximation at the first step and violate the core lossless principle.

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

**Display meshes** are generated on-demand for VTK viewport visualization ONLY. They do NOT replace the exact SubD model used for all analysis and region definitions.

### Why This Matters:

- **Mathematical Truth**: Regions represent genuine mathematical boundaries, not discretization artifacts
- **Infinite Resolution**: Can evaluate at any density without re-fetching from Rhino
- **Zero Accumulated Error**: No compounding approximations through the pipeline
- **Philosophical Alignment**: Seams inscribe true mathematical structure, not mesh artifacts

**If you find yourself converting SubD to mesh anywhere before final export, STOP and reconsider the architecture.**

---

## ⚡ 10-DAY API SPRINT (CURRENT MODE)

**Status**: Day 0 preparation, ready to launch Day 1
**Timeline**: 10 days with maximum parallelization
**Strategy**: 6-8 agents working in parallel per day (67 agents total)
**Budget**: $1000 API credits ($242-412 expected, $588-758 reserve)
**Start Date**: November 2025

### Why Hybrid C++/Python Architecture is REQUIRED

**Critical Discovery**: The v5.0 specification requires capabilities that pure Python cannot provide:

1. **OpenSubdiv** (C++) - Exact SubD limit surface evaluation via Stam eigenanalysis
2. **OpenCASCADE** (C++) - NURBS operations and Boolean ops
3. **pybind11** - Zero-copy bindings for C++↔Python integration
4. **Performance** - 10-100x faster than pure Python for geometry operations

This is NOT an optimization - it's a **fundamental requirement** for the lossless architecture.

### Sprint Documentation

**All sprint docs located in**: `docs/reference/api_sprint/`

**Quick Reference**:
- **QUICK_START.md** - Daily launch commands ⭐ **START HERE**
- **MASTER_ORCHESTRATION.md** - Agent-by-agent details
- **10_DAY_SPRINT_STRATEGY.md** - Complete 10-day breakdown
- **IMPLEMENTATION_ROADMAP.md** - Technical roadmap
- **agent_tasks/day_XX/** - 67 individual agent task files

### Custom Slash Commands

**Available commands** (in `.claude/commands/`):

```bash
# Launch full day batches
/launch-day1-morning    # Agents 1-6 in parallel
/launch-day1-evening    # Agents 7-9 in parallel

# Integration and build
/integrate-day1         # Run all Day 1 integration tests
/build-cpp             # Build C++ core and run tests
```

**Usage**:
```
You: /launch-day1-morning
Claude: [Launches 6 agents in parallel, each reading their task file]
```

### Sprint Best Practices (From Comprehensive Review)

**Agent Execution**:
1. ✅ Each agent reads entire task file autonomously
2. ✅ Implements ALL deliverables before reporting complete
3. ✅ Runs all tests and verifies success criteria
4. ✅ Provides integration notes for subsequent agents
5. ✅ Reports actual completion (not partial)

**Path Conventions**:
- **Python modules**: `app/` (NOT `ceramic_mold_analyzer/app/`)
- **C++ source**: `cpp_core/geometry/`, `cpp_core/analysis/`, etc.
- **Tests**: `tests/`
- **Python imports**: `from app.bridge import RhinoBridge` (simple, direct)
- **Always use relative paths** in scripts and commands

**Critical Distinctions**:
- **Control cage transfer** = Exact, lossless ✅ (vertices, faces, creases)
- **Mesh transfer** = Approximation, lossy ❌ (Week 3 workaround - being replaced)

**Module Naming**:
- C++ Python extension: `cpp_core` (imported as `import cpp_core`)
- NOT `latent_core` (outdated naming)

---

## UI/UX Reference

The application follows **Rhino 8 standard viewport navigation** for continuity with the user's existing Rhino workflow.

### **Rhino-Compatible Controls (DO NOT DEVIATE)**

**Mouse Navigation (Perspective Viewport)**:
- **LEFT click/drag** = Select objects (window/crossing selection)
- **RIGHT drag** = Rotate/orbit view
- **Shift + RIGHT drag** = Pan view
- **Ctrl + RIGHT drag** or **Mouse wheel** = Zoom in/out

**Object Selection**:
- **Left-click** = Select object (yellow highlighting)
- **Shift + Left-click** = Add to selection
- **Ctrl + Left-click** = Remove from selection
- **Esc key** = Deselect all

**Sub-object Selection**:
- **Ctrl + Shift + Left-click** = Select face/edge/vertex

**Implementation**: Custom interactor in `app/ui/viewport_3d.py` extending base `vtkInteractorStyle` with manual camera control implementation to ensure LEFT click does NOT move camera.

**Reference Documents**:
- `docs/reference/RhinoUI/Rhino User's Guide - Navigating Viewports.pdf`
- `docs/reference/RhinoUI/Rhino User's Guide - Selecting Objects.pdf`

---

## Quick Start Commands

### Running the Application
```bash
# Quick launch (recommended - auto-configures Qt plugins)
python3 launch.py

# Or directly (requires manual Qt plugin path setup)
python3 main.py
```

### Testing the Application
```bash
# Launch the app
python3 launch.py

# Test VTK visualization:
# - View → Show Test Cube
# - View → Show Test SubD Sphere
# - View → Show Test SubD Torus
# - View → Show Colored Cube (6-region demo)

# Test region workflow:
# - Click "Analyze" for simulated regions
# - Pin/unpin regions
# - Use Cmd+Z/Cmd+Shift+Z for undo/redo
```

---

## Sprint Architecture (Hybrid C++/Python)

**Technology Stack**:

**C++ Core** (OpenSubdiv 3.6+, OpenCASCADE 7.x):
- Exact SubD limit surface evaluation (Stam eigenanalysis)
- NURBS operations and Boolean ops
- Mathematical analysis (curvature, spectral, etc.)
- GPU acceleration via Metal backend (macOS)

**Python Layer** (PyQt6 6.9.1, VTK 9.3.0):
- UI framework and user interaction
- State management and undo/redo
- Rhino communication (HTTP bridge)
- Workflow orchestration
- File I/O

**pybind11 Bindings**:
- Zero-copy numpy array sharing
- Seamless C++↔Python integration
- All C++ classes exposed to Python

---

## Data Flow (LOSSLESS)

**1. Rhino → Desktop**:
- SubD control cage extracted in Grasshopper
- Transferred as JSON: `{vertices: [[x,y,z],...], faces: [[i,j,k,...],...], creases: [[i,j,sharpness],...]}`
- NO mesh conversion - preserves exact topology

**2. C++ OpenSubdiv**:
- Build TopologyRefiner from control cage
- Exact limit surface evaluation at any (u,v) parameter
- Tessellation for display only (VTK viewport)

**3. Analysis**:
- Mathematical lenses query exact limit surface
- Regions defined in parametric space (face_id, u, v)
- Curvature from exact surface derivatives
- All analysis on true limit surface, not mesh

**4. Mold Generation**:
- Evaluate exact limit surface at high resolution
- Fit analytical NURBS through sampled points
- Apply draft transformation (exact vector math)
- Create mold solids with Boolean ops (exact)

**5. Export**:
- Send NURBS molds to Rhino (exact)
- **ONLY at STL/G-code export: single approximation**

---

## Current Implementation Status

**Phase 0 (Weeks 1-4)**: Desktop UI Foundation - **COMPLETE** ✅
- PyQt6 application with multi-viewport system
- VTK 3D visualization with Rhino-compatible controls
- Edit mode system (Solid/Panel/Edge/Vertex)
- Selection/picking system with unified yellow highlighting
- Undo/redo with history management
- HTTP bridge to Grasshopper (mesh transfer - temporary)

**Next: 10-Day Sprint** (Phase 0 + Phase 1 MVP)
- Day 1-2: C++ core with OpenSubdiv integration
- Day 3-5: Mathematical lenses (Differential, Spectral)
- Day 6: Constraint validation (undercuts, draft angles)
- Day 7-8: NURBS mold generation with OpenCASCADE
- Day 9-10: Testing, polish, documentation

---

## File Structure

```
Latent/                         # Project root
├── main.py                     # Application entry point
├── launch.py                   # Quick launcher (Qt config)
├── requirements.txt            # Python dependencies
├── app/                        # Python application modules
│   ├── state/
│   │   ├── app_state.py       # Centralized state management
│   │   └── edit_mode.py       # Edit mode state
│   ├── bridge/
│   │   └── rhino_bridge.py    # HTTP communication (stub)
│   ├── geometry/
│   │   └── subd_display.py    # VTK visualization helpers
│   └── ui/
│       ├── viewport_3d.py     # 3D viewport with Rhino controls
│       ├── viewport_layout.py # Multi-viewport manager
│       ├── region_list.py     # Region list widget
│       └── edit_mode_toolbar.py # Edit mode selector
├── cpp_core/                   # C++ geometry kernel (Sprint Day 1+)
│   ├── geometry/
│   │   ├── types.h            # Point3D, SubDControlCage, etc.
│   │   ├── subd_evaluator.h/cpp # OpenSubdiv wrapper
│   │   └── ...
│   ├── analysis/              # Mathematical analysis (Day 4+)
│   ├── constraints/           # Validation (Day 6+)
│   ├── python_bindings/       # pybind11 bindings
│   │   └── py_bindings.cpp
│   └── CMakeLists.txt         # Build configuration
├── rhino/                      # Grasshopper components
│   ├── grasshopper_server_control.py        # Current (mesh transfer)
│   └── grasshopper_http_server_control_cage.py # Sprint Day 1 (control cage)
├── tests/                      # Test suite
└── docs/reference/             # Technical specifications
    ├── api_sprint/            # Sprint documentation
    ├── subdivision_surface_ceramic_mold_generation_v5.md
    ├── technical_implementation_guide_v5.md
    └── SlipCasting_Ceramics_Technical_Reference.md
```

---

## Development Best Practices

### Path Conventions

**CRITICAL**: Always use correct paths
- ✅ `app/ui/viewport_3d.py`
- ❌ `ceramic_mold_analyzer/app/ui/viewport_3d.py`

**Imports**:
```python
from app.state.app_state import ApplicationState
from app.bridge.rhino_bridge import RhinoBridge
```

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
# Grasshopper extracts control cage
cage_data = {
    'vertices': [[x,y,z], ...],  # Control vertices
    'faces': [[i,j,k,...], ...], # Face topology
    'creases': [[i,j,s], ...]    # Edge sharpness
}

# Desktop converts to C++ SubDControlCage
cage = cpp_core.SubDControlCage()
for v in cage_data['vertices']:
    cage.vertices.append(cpp_core.Point3D(v[0], v[1], v[2]))
cage.faces = cage_data['faces']
```

**Mesh transfer** (wrong, lossy):
```python
# ❌ DO NOT DO THIS
mesh = subd.ToMesh()  # Introduces approximation!
```

### Testing Requirements

When implementing features:
1. Write tests BEFORE marking complete
2. Test C++ code compiles and links
3. Test Python imports work
4. Test integration with existing code
5. Verify success criteria met

### Clean Code

- Remove temporary files after issues resolved
- Delete obsolete code and commented sections
- Consolidate related functionality
- Update docs instead of creating tracking files
- Keep only essential files

---

## Sprint Agent Workflow

**When launched as an agent** (reading task file):

1. ✅ **Read entire task file** - All context provided
2. ✅ **Work autonomously** - Don't ask for clarification
3. ✅ **Implement ALL deliverables** - Files, tests, docs
4. ✅ **Run tests before completing** - Verify success
5. ✅ **Provide integration notes** - Help next agents
6. ✅ **Mark success criteria** - Confirm checkboxes

**Testing is non-negotiable**:
- C++ code must compile
- Python imports must work
- Tests must pass
- Success criteria verified

---

## Alignment with v5.0 Specification

**✅ Parametric Region Architecture** (v5.0 §3.1):
- Regions in (face_id, u, v) parameter space
- All analysis queries exact limit surface

**✅ Lossless Until Fabrication** (v5.0 §2.2):
- Control cage → OpenSubdiv → Exact evaluation
- Single approximation at G-code export

**✅ Mathematical Lenses** (v5.0 §4):
- Differential (curvature-based)
- Spectral (Laplace-Beltrami eigenfunctions)
- Flow, Morse, Thermal, Slip (future)

**✅ OpenSubdiv Integration** (Tech Guide §2.1):
- Stam eigenanalysis for exact evaluation
- Metal backend (GPU acceleration)
- Catmull-Clark subdivision

**✅ OpenCASCADE Integration** (Tech Guide §3.1):
- NURBS surface fitting from limit points
- Draft angle transformation
- Boolean operations for solids

---

## Technical Philosophy

**Every form contains inherent mathematical coherences.** Different analytical lenses reveal different truths. The goal is eloquence over complexity - finding decompositions that create profound mathematical poetry written in light through translucent porcelain.

### Constraint Hierarchy
1. **Mathematical** - High resonance score (form "wants" this)
2. **Physical** - Ceramic properties (wall thickness, draft)
3. **Manufacturing** - 3D printing and demolding feasibility

### Resonance Scores
- **0.8-1.0**: Excellent - form wants this decomposition
- **0.6-0.8**: Good - reveals important structure
- **0.4-0.6**: Moderate - usable but not ideal
- **0.0-0.4**: Poor - try different lens

---

## Important Notes

### DO NOT:
- ❌ **Convert SubD to mesh in data pipeline** - #1 violation
- ❌ Use absolute paths - always relative
- ❌ Modify state directly - use ApplicationState
- ❌ Port from Archive - different tech stack
- ❌ Use `ceramic_mold_analyzer/` path prefix

### DO:
- ✅ Transfer control cage (lossless)
- ✅ Define regions parametrically
- ✅ Evaluate limit surface on-demand
- ✅ Generate display meshes separately
- ✅ Use `app/` for Python modules
- ✅ Keep approximation to final export only

### Architecture Decisions:
- **Lossless until fabrication** - Core principle
- **Hybrid C++/Python** - Required for performance
- **OpenSubdiv + OpenCASCADE** - Exact geometry
- **PyQt6 + VTK** - Professional UI/3D
- **pybind11** - Zero-copy C++↔Python
- **HTTP bridge** - Simple, sufficient
- **Parametric regions** - Mathematical truth

---

## Archive Reference

Legacy Grasshopper implementation in `.Archive/251013/` is **REFERENCE ONLY**:

**Study for concepts**:
- Mathematical decomposition approaches
- Resonance scoring methods
- Multi-lens analysis patterns

**Do NOT**:
- Copy or import code
- Use RhinoCommon API
- Port directly to standalone

**Instead**:
- Implement fresh using numpy/scipy/VTK
- Query C++ limit surface (not mesh)
- Build on OpenSubdiv foundation

---

**Sprint Status**: Ready to launch Day 1 after completing Day 0 preparation (OpenSubdiv installation).

**Next Step**: Complete Day 0 checklist, then `/launch-day1-morning`
