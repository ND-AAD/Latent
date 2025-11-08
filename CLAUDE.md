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
  → HTTP Bridge (exact rhino3dm serialization)
  → Desktop SubD Model (exact limit surface evaluation)
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

## UI/UX Reference

The application follows **Rhino 8 standard viewport navigation** for continuity with the user's existing Rhino workflow. All viewport controls are based on the official *Rhino 8 User's Guide - Navigating Viewports* and *Selecting Objects* documentation located in `reference/RhinoUI/`.

### **Rhino-Compatible Controls (DO NOT DEVIATE)**

**Mouse Navigation (Perspective Viewport):**
- **LEFT click/drag** = Select objects (window/crossing selection)
- **RIGHT drag** = Rotate/orbit view
- **Shift + RIGHT drag** = Pan view
- **Ctrl + RIGHT drag** or **Mouse wheel** = Zoom in/out

**Object Selection:**
- **Left-click** = Select object (changes to yellow/selected color)
- **Shift + Left-click** = Add to selection
- **Ctrl + Left-click** = Remove from selection
- **Left-drag-right** = Window selection (fully enclosed only)
- **Left-drag-left** = Crossing selection (touching or enclosed)
- **Esc key** = Deselect all

**Sub-object Selection:**
- **Ctrl + Shift + Left-click** = Select face/edge/vertex

**Viewport Keyboard Shortcuts:**
- **Home key** = Undo view change
- **End key** = Redo view change
- **Space key** = Reset camera to default view
- **Double-click viewport title** = Maximize/restore viewport

**Implementation**: The `RhinoInteractorStyle` class is implemented directly in [app/ui/viewport_3d.py](ceramic_mold_analyzer/app/ui/viewport_3d.py) (lines 30-162), extending VTK's `vtkInteractorStyleTrackballCamera` to match Rhino's behavior exactly with zero momentum/inertia. LEFT click is reserved for selection, RIGHT click handles all camera operations.

**Reference Documents**:
- `reference/RhinoUI/Rhino User's Guide - Navigating Viewports.pdf`
- `reference/RhinoUI/Rhino User's Guide - Selecting Objects.pdf`

## Quick Start Commands

### Running the Application
```bash
# Navigate to the application directory
cd ceramic_mold_analyzer

# Quick launch (with Qt plugin auto-configuration) - RECOMMENDED
python3 launch.py

# Or directly (requires manual Qt plugin path setup)
python3 main.py
```

**Important**: Use `launch.py` for automatic Qt plugin path configuration on macOS.

### Virtual Environment Setup (First Time)
```bash
cd ceramic_mold_analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Note**: All critical dependencies are in requirements.txt:
- PyQt6==6.9.1 (UI framework)
- vtk==9.3.0 (3D visualization)
- numpy==1.26.2, scipy==1.11.4 (numerical computing)
- requests==2.31.0 (HTTP communication)
- rhino3dm 8.17.0 (exact SubD representation - custom ARM64 build)

### Testing the Application (Week 1 Complete)
```bash
# Launch the app
python3 launch.py

# Test VTK visualization:
# - View → Show Test Cube (basic VTK rendering with camera controls)
# - View → Show Test SubD Sphere (SubD control net + limit surface evaluation)
# - View → Show Test SubD Torus (SubD geometry)
# - View → Show Colored Cube (6 regions demonstrated with per-face coloring)

# Test region workflow:
# - Click "Analyze" to generate simulated test regions
# - Pin/unpin regions to test state management
# - Use Cmd+Z/Cmd+Shift+Z to test undo/redo
# - Test menu items and keyboard shortcuts
```

## Architecture Overview

### Current Strategy: Pure Python (Weeks 1-7), Pivot to Hybrid if Needed (Week 8+)

**Technology Stack (Current)**:
- Python 3.12 for all code (UI, state, geometry, analysis)
- PyQt6 6.9.1 (UI framework)
- VTK 9.3.0 (3D visualization)
- NumPy 1.26.2 / SciPy 1.11.4 (numerical computing)
- rhino3dm 8.17.0 (exact SubD representation - custom ARM64 build)

**Why Pure Python Now:**
- ✅ Rapid development velocity (2-3 day feature cycles)
- ✅ Adequate performance for test geometry (<5K control points)
- ✅ All dependencies available in Python ecosystem
- ✅ Focus on algorithms and UX, not build complexity

**When to Pivot (Week 8+ Decision):**

Stay pure Python while:
- UI development remains rapid
- Working with test/prototype geometry
- Multi-viewport rendering >30 FPS
- Real-time operations feel responsive (<100ms)

Pivot to hybrid Python/C++ when measured performance shows:
- 🚨 SubD operations become sluggish (>100ms)
- 🚨 Multi-viewport <30 FPS on production models
- 🚨 Spectral analysis >5 seconds
- 🚨 Testing with actual light fixture designs (10K-50K control points) shows issues

**Hybrid Migration Path (If Needed):**
```
Python Layer (Keep)               C++ Layer (Add only if bottlenecks)
├─ All UI (PyQt6)                ├─ OpenSubdiv (exact SubD limit eval)
├─ State management              ├─ OpenCASCADE (NURBS operations)
├─ Workflow orchestration        └─ Geometry-heavy operations
└─ SciPy eigensolvers (adequate)
         ↕ pybind11 bindings
```

**This is data-driven optimization, not premature optimization.** Profile in Week 8-9, migrate only bottlenecks.

### Current Implementation (v0.4.0 - Desktop Application)
The project has transitioned from a Grasshopper-based implementation (archived in `.Archive/251013/`) to a professional PyQt6 desktop application.

**Core Components:**
- [main.py](ceramic_mold_analyzer/main.py) - PyQt6-based desktop UI with mathematical lens selection, 3D viewport, region management
- [app/state/app_state.py](ceramic_mold_analyzer/app/state/app_state.py) - Centralized state with undo/redo, region tracking, history management
- [app/bridge/rhino_bridge.py](ceramic_mold_analyzer/app/bridge/rhino_bridge.py) - HTTP communication framework for live Rhino sync (stub implementation)
- [app/ui/](ceramic_mold_analyzer/app/ui/) - Modular PyQt6 widgets for viewport, region lists, constraints
- [rhino/http_server.py](ceramic_mold_analyzer/rhino/http_server.py) - Grasshopper component for SubD serialization

**Mathematical Analysis Engines** (To be implemented):
- **Flow/Geodesic Decomposition** - Drainage basins via heat method for geodesic computation
- **Spectral Decomposition** - Vibration modes via Laplace-Beltrami eigenfunctions
- **Differential Decomposition** - Curvature-based analysis (ridges, valleys, principal curvatures)
- **Topological Decomposition** - Critical point and flow pattern analysis
- **Note**: Reference implementations exist in `.Archive/251013/decomposition_engines/` but use RhinoCommon API (incompatible with standalone). The standalone app will implement these algorithms fresh using numpy/scipy operating on **exact SubD limit surface evaluation**, NOT mesh approximations.

### Key Design Patterns

#### Signal/Slot Architecture (PyQt6)
All UI updates are driven by signals from the `ApplicationState`:
```python
# State emits signals automatically
self.state.set_regions(new_regions)  # Emits regions_updated signal

# UI components connect to signals
self.state.regions_updated.connect(self.on_regions_updated)
```

#### Centralized State Management
ALL state changes flow through `ApplicationState` - never modify data directly:
```python
# Correct - goes through state manager
self.state.set_region_pinned(region_id, True)

# Wrong - bypasses history and signals
region.pinned = True  # Don't do this!
```

#### Undo/Redo History System
The state manager automatically tracks changes via `_add_history_item()`:
- Each state-changing operation adds a history item
- Undo/redo operations restore previous states
- History is limited to 100 items (configurable)

#### Pin-Based Workflow
Users "pin" regions to preserve them across re-analysis:
- Pinned regions are excluded from new analysis
- Only unpinned faces are re-analyzed
- Allows incremental refinement of decompositions

### Data Flow (LOSSLESS)

1. **Rhino → Desktop**: **Exact SubD** serialized via HTTP bridge using `rhino3dm` (NOT mesh!)
   - Control mesh vertices and topology preserved
   - Vertex valences, edge creases, face adjacency maintained
   - Catmull-Clark subdivision structure intact
   - Display mesh generated separately for viewport only

2. **Analysis**: Mathematical lenses query **exact limit surface** to discover coherent regions
   - Curvature computed from exact surface derivatives
   - Geodesics calculated on continuous surface
   - Eigenfunctions evaluated on true geometry
   - Regions defined in parametric space (face_id, u, v)

3. **User Interaction**: Pin regions, adjust parametric boundaries, validate constraints
   - All edits maintain parametric definitions
   - Boundaries remain curves in parameter space
   - No mesh dependency for region definitions

4. **Generation**: Create **NURBS mold surfaces** from parametric regions (planned)
   - Evaluate exact limit surface at high resolution
   - Apply draft transformation (exact vector math)
   - Fit analytical NURBS through evaluated points
   - Mold solids constructed with exact Brep operations

5. **Export**: Send **exact mold geometry** back to Rhino, or export to fabrication
   - **ONLY at STL/G-code export does approximation occur**
   - All other operations maintain exact representation

## Development Status

### ✅ Completed Features (Weeks 1-3)

#### Week 1: VTK Visualization (COMPLETE)
- Desktop application launches with full UI
- **Qt plugin path auto-configuration** via launch.py
- Menu system (File, Edit, Analysis, View, Help) with keyboard shortcuts
- Mathematical lens selection (Flow, Spectral, Curvature, Topological)
- **VTK 3D visualization integrated with PyQt6**
  - Control net rendering of SubD geometry
  - Camera controls: orbit, pan, zoom, reset (Rhino-compatible)
  - Axes helper and grid plane for orientation
- **Test geometry visualization** - Cube, colored cube, SubD sphere/torus
- Simulated region discovery and management
- Pin/unpin workflow for region preservation
- Undo/redo system with complete history tracking
- Three-tier constraint validation framework (display only)

#### Week 2: Multi-Viewport System (COMPLETE)
- **ViewportLayoutManager** with 4 layout modes:
  - Single viewport
  - Two Horizontal (top/bottom split)
  - Two Vertical (left/right split)
  - Four Grid (2x2 layout)
- **Per-viewport features**:
  - Independent camera controls
  - View type labels (Perspective, Top, Front, etc.)
  - Active viewport indicators (green border)
  - Context menu for changing view types
- **Fixed all UI issues**: Proper labeling, active viewport system, view type setting

#### Week 3: HTTP Bridge (COMPLETE - WITH LIMITATIONS)
- **Grasshopper HTTP Server** on port 8888
  - Two versions: Full (with 3dm serialization) and Simplified (for testing)
  - Successfully transfers SubD metadata (vertex/face/edge counts)
  - Connection status monitoring
  - Update detection system
- **Desktop Client**:
  - RhinoBridge class with full HTTP communication
  - Automatic polling for geometry updates
  - Connection status indicator in UI
- **Current Limitation**: Using simplified transfer (metadata only) due to IronPython serialization issues
  - Placeholder visualization (parametric torus) based on complexity
  - Architecture ready for full geometry transfer when serialization fixed

#### Week 4: Edit Mode & Selection System (COMPLETE ✅)
- **Edit Mode Infrastructure** ✅
  - EditModeManager with 4 modes: Solid, Panel, Edge, Vertex
  - Mode selector toolbar with S/P/E/V buttons
  - Visual indicators for active mode
  - Proper initialization on viewport startup
- **VTK Picking System** ✅
  - SubDFacePicker, SubDEdgePicker, SubDVertexPicker classes fully implemented
  - Integration with CustomCameraInteractor via pick callbacks
  - LEFT click reserved for selection (no camera movement)
  - Shift key detection for multi-select
- **ALL Selection Modes Working** ✅
  - **Solid Mode (S)**: View-only, no selection (intentional design)
  - **Panel Mode (P)**: Face selection with yellow highlighting
  - **Edge Mode (E)**: Edge selection with yellow highlighting, cyan wireframe guide
  - **Vertex Mode (V)**: Vertex selection with yellow spheres
  - Multi-select with Shift+Click (add/remove from selection)
  - Selection toggle (Shift+Click on selected element deselects it)
- **Visual Feedback** ✅
  - Unified yellow highlighting for all selection types (1.0, 1.0, 0.0)
  - HighlightManager with proper VTK selection extraction
  - Thick, tubular edge rendering for visibility
  - Vertex spheres for point selection
- **Architecture** ✅
  - Pick callbacks properly connected to interactor style
  - Selection state tracked per viewport (selected_faces, selected_edges, selected_vertices)
  - Geometry actor pickability controlled per mode
  - Edge actor created on-demand with proper extraction
  - Ready for OpenSubdiv integration (future)

### ✅ Weeks 1-4 FULLY COMPLETE - Ready for Week 5

**Current Status (November 3, 2025)**:
- ✅ Core application fully functional with professional UI
- ✅ Multi-viewport system with independent camera controls
- ✅ **Geometry transfer from Rhino working** (mesh representation via HTTP on port 8800)
- ✅ **Edit mode system FULLY operational** - All 4 modes working (Solid/Panel/Edge/Vertex)
- ✅ **Selection/picking system COMPLETE** - All modes with multi-select functional
- ✅ **Unified yellow highlighting** for consistent visual feedback
- ✅ Face, edge, and vertex selection all working with Shift+Click multi-select
- ✅ ~40% of MVP complete (Weeks 1-4 of 10-week plan)

**Next Priority: Week 5 - Differential Decomposition (First Mathematical Lens)**

### 🚧 Priority Development Needed (Week 5+)
1. **Differential Decomposition** (Week 5) - First working mathematical lens ⬅️ NEXT
2. **Iteration Management** (Week 6) - Design snapshot system
3. **Constraint Validation** (Week 7) - Physical checks (undercuts, draft angles)
4. **NURBS Generation** (Week 8) - Create manufacturable mold surfaces
5. **Architecture Transition** (Future) - OpenCASCADE + OpenSubdiv integration
6. **Full Lossless Transfer** (Enhancement) - True SubD serialization (not mesh)
7. **Additional Mathematical Lenses** (Post-MVP) - Spectral, Flow, Topological
8. **File I/O** (Post-MVP) - Save/load session state

### 📁 Archive Structure
Legacy Grasshopper implementation in `.Archive/251013/` is **REFERENCE ONLY**:
- Contains mathematical decomposition engines (spectral, differential, morse) using RhinoCommon API
- Multi-basis analysis with resonance scoring concepts
- Extensive development history showing evolution of mathematical approaches
- **CRITICAL**: Do NOT copy, import, or link to Archive files
  - They use RhinoCommon/IronPython (incompatible with standalone Python)
  - They require Rhino.Geometry API (not available outside Rhino/GH)
  - Different technology stack entirely
- **DO**: Study the mathematical concepts and algorithms
- **THEN**: Implement fresh versions using numpy/scipy/VTK for standalone app
- Active codebase is in `ceramic_mold_analyzer/` only

## File Structure
```
ceramic_mold_analyzer/          # Main desktop application
├── main.py                     # Application entry point with MainWindow
├── launch.py                   # Quick launcher with Qt plugin auto-config
├── requirements.txt            # All dependencies (PyQt6, VTK, numpy, scipy, requests, rhino3dm)
├── app/
│   ├── state/
│   │   └── app_state.py        # ApplicationState, ParametricRegion, HistoryItem
│   ├── bridge/
│   │   └── rhino_bridge.py     # RhinoBridge, SubDGeometry (COMPLETE)
│   ├── geometry/
│   │   └── subd_display.py     # SubD visualization helpers (VTK actors)
│   └── ui/
│       ├── viewport_3d.py      # Viewport3D with VTK integration, Rhino controls
│       ├── viewport_layout.py  # ViewportLayoutManager for multi-viewport (COMPLETE)
│       ├── region_list.py      # RegionListWidget
│       └── constraint_panel.py # ConstraintPanel
├── rhino/
│   ├── grasshopper_http_server.py        # Full server with 3dm serialization (issues)
│   └── grasshopper_http_server_simple.py # Simplified server (WORKING)
├── test_rhino_connection.py   # Connection testing utility
├── tests/                      # Unit tests (to be created)
└── venv/                       # Virtual environment (not in version control)

.Archive/251013/                # Legacy Grasshopper implementation (REFERENCE ONLY)
├── decomposition_engines/      # Mathematical analysis algorithms
│   ├── spectral_decomposition_fixed.py    # Rhino 8 compatible
│   ├── differential_decomposition_fixed.py # Rhino 8 compatible
│   └── morse_decomposition_fixed.py       # Rhino 8 compatible
├── multibasis_*.py            # Multi-lens analysis tools
└── (various diagnostic tools)

reference/                      # Technical documentation
├── SubD_Ceramic_Mold_Generation_Specification_v4.md
├── SlipCasting_Ceramics_Technical_Reference.md
├── UX_UI_DESIGN_SPECIFICATION.md
└── UX/                         # React/TypeScript design prototype
    ├── src/App.tsx             # Shows critical features:
    │                             - Edit modes: solid/panel/edge/vertex
    │                             - Viewport layouts: 1/2H/2V/4-grid
    │                             - Iteration management system
    │                             - Multiple view types per viewport
    └── src/components/         # Full UI component library
```

## Development Workflow

### General Development Principles

**Refactor as You Go - Keep the Codebase Clean**:
- Remove temporary files (debug scripts, progress tracking docs, blocker files) once issues are resolved
- If you create temporary documentation for tracking issues, clean it up after completion
- Delete obsolete code and commented-out sections rather than leaving them around
- **Consolidate related functionality** - don't create separate utility files when code can live in the main file (example: `RhinoInteractorStyle` is now directly in `viewport_3d.py` instead of a separate file)
- Keep only the essential files: source code, tests, main documentation (CLAUDE.md, ROADMAP, STATUS, README)
- Update existing documentation rather than creating new tracking files
- The goal is a clean, professional codebase without stray artifacts

**Recent Updates (November 2025)**:

**Week 4 - Selection System Complete**:
- ✅ Fixed geometry transfer from Rhino (port 8800, mesh representation)
- ✅ Implemented complete picking system for all edit modes
- ✅ All selection modes working: Solid (view-only), Panel, Edge, Vertex
- ✅ Multi-select with Shift+Click for faces, edges, and vertices
- ✅ Unified yellow highlighting (1.0, 1.0, 0.0) for all selection types
- ✅ Edge highlighting fixed to show only selected edges (not all edges)
- ✅ Proper VTK selection extraction and visual feedback

**Week 1-3 Foundation**:
- ✅ Fixed viewport controls to match Rhino exactly: LEFT click for selection, RIGHT click for camera
- ✅ Implemented clean CustomCameraInteractor with proper event handling
- ✅ Multi-viewport system (4 layouts) with independent cameras
- ✅ HTTP bridge for Rhino geometry transfer (Grasshopper manual push)

### Implementing Mathematical Lenses

1. Study conceptual approach in `.Archive/251013/decomposition_engines/` (mathematical logic only)
2. Create NEW analysis module in `ceramic_mold_analyzer/app/analysis/` that follows this interface:
   ```python
   def analyze_geometry(subd_geometry: SubDGeometry,
                        pinned_faces: List[int] = []) -> List[ParametricRegion]:
       """
       Returns: List of ParametricRegion objects with:
       - id: Unique identifier
       - faces: Face indices in this region
       - unity_principle: Description of what unifies this region
       - unity_strength: 0.0-1.0 "resonance score"
       """
   ```
3. Add lens option to [main.py:126-129](ceramic_mold_analyzer/main.py#L126-L129) in the Analysis menu
4. Add corresponding radio button in [main.py:155-163](ceramic_mold_analyzer/main.py#L155-L163)
5. Update `run_analysis()` method to call your analysis function
6. Test with various SubD forms and document resonance patterns

### Extending the UI

- Follow PyQt6 signal/slot patterns established in existing components
- All state changes MUST go through `ApplicationState` to maintain history
- Use consistent styling (70/30 viewport/controls split via splitter)
- Maintain pin metaphor for user workflow
- Group related controls in `QGroupBox` widgets
- Use emojis sparingly in buttons (only where established: 🔨 📤)

### Implementing Analysis Engines (NOT Porting)

**DO NOT port from `.Archive/251013/decomposition_engines/`** - incompatible technology stack.

**Approach: Fresh implementation using numpy/scipy:**

1. **Study Archive for mathematical concepts** (not code):
   - Understand what the algorithm discovers (e.g., nodal lines, drainage basins)
   - Note the mathematical approach (e.g., Laplacian eigenvalues, curvature tensor)
   - See how resonance scores are computed

2. **Implement fresh in `ceramic_mold_analyzer/app/analysis/`:**
   ```python
   # NEW implementation for standalone app
   import numpy as np
   from scipy import sparse
   from scipy.sparse import linalg

   class SpectralDecomposition:
       def __init__(self, mesh_data: Dict):
           """
           mesh_data: {
               'vertices': np.array([[x,y,z], ...]),
               'faces': np.array([[i,j,k], ...]),
               'normals': np.array([[nx,ny,nz], ...])
           }
           """
           self.vertices = mesh_data['vertices']
           self.faces = mesh_data['faces']

       def compute(self, num_modes=5) -> List[ParametricRegion]:
           # Build Laplacian matrix using cotangent weights
           L = self._build_laplacian()

           # Solve eigenvalue problem
           eigenvalues, eigenvectors = sparse.linalg.eigsh(L, k=num_modes)

           # Extract regions from nodal domains
           regions = self._extract_nodal_regions(eigenvectors)

           return regions
   ```

3. **Geometry arrives from Rhino as mesh via HTTP**:
   - Grasshopper converts SubD → Mesh
   - HTTP bridge sends as JSON: vertices, faces, normals
   - Python app works with numpy arrays
   - No RhinoCommon dependencies

4. **Focus on mathematical correctness**:
   - Proper Laplacian construction (cotangent weights for spectral)
   - Accurate curvature estimation (finite differences for differential)
   - Correct geodesic distances (heat method for flow)

### Testing Different Forms

- Simple forms first: sphere, torus, saddle shapes
- Document which mathematical lenses work best for different geometries
- Pay attention to how extraordinary vertices affect decomposition quality
- Test with forms of different genus (0, 1, 2+)
- Forms with high resonance scores (>0.8) indicate ideal lens match

## Technical Philosophy

The application embodies the principle that **every form contains inherent mathematical coherences**. Different analytical lenses (spectral, differential, morse, topological) reveal different truths about a form's structure. The goal is eloquence over complexity - finding decompositions that create profound mathematical poetry written in light through translucent porcelain.

### Constraint Hierarchy
1. **Mathematical** - Respects the form's inherent structure (high resonance score)
2. **Physical** - Accounts for ceramic material properties (wall thickness, draft angles)
3. **Manufacturing** - Ensures molds can be 3D printed and demolded

### Resonance Scores
- **0.8-1.0**: Excellent fit - the form "wants" this decomposition
- **0.6-0.8**: Good fit - reveals important structure
- **0.4-0.6**: Moderate fit - usable but not ideal
- **0.0-0.4**: Poor fit - consider different lens

## Common Patterns

### State Updates
```python
# Always emit signals for UI reactivity
self.state.set_regions(new_regions)  # Automatically emits regions_updated signal
self.state.set_region_pinned(region_id, True)  # Emits region_pinned signal

# Connect to signals in UI components
self.state.regions_updated.connect(self.on_regions_updated)
```

### Adding History Items
```python
# Happens automatically in state methods, but if adding new state operations:
self.state._add_history_item(
    action="action_name",
    data={"key": value},
    description="Human-readable description for UI"
)
```

### Rhino Communication (LOSSLESS - when implemented)
```python
# Check connection before operations
if self.rhino_bridge.is_connected():
    # Fetch EXACT SubD (not mesh!)
    subd_model = self.rhino_bridge.fetch_subd()  # Returns SubDModel with exact evaluation

    # WRONG: Don't do this!
    # mesh = self.rhino_bridge.fetch_mesh()  # ❌ BREAKS LOSSLESS PRINCIPLE

# Send exact mold geometry back to Rhino
# Molds are NURBS Breps (exact), not meshes
self.rhino_bridge.send_molds(nurbs_mold_pieces)
```

**Critical**: The bridge must transfer `rhino3dm.SubD` objects, NOT meshes. Display meshes are generated on-demand in the desktop app for visualization only.

### Working with Regions
```python
# Get region from state
region = self.state.get_region(region_id)

# Get all pinned/unpinned regions
pinned = self.state.get_pinned_regions()
unpinned = self.state.get_unpinned_regions()

# Get faces that need re-analysis
available_faces = self.state.get_unpinned_faces()
```

## Important Notes

### Do NOT:
- **❌ CONVERT SubD TO MESH IN THE DATA PIPELINE** - This is the #1 architectural violation
- Modify region objects directly - always go through `ApplicationState`
- Use absolute file paths in code - paths should be relative to project root
- Commit test data or generated geometry files
- Include the `venv/` directory or `__pycache__/` in version control
- Store mesh representations as primary geometry - only for display

### DO:
- ✅ Maintain exact SubD representation using `rhino3dm`
- ✅ Define regions in parametric space (face_id, u, v)
- ✅ Evaluate limit surface on-demand for analysis
- ✅ Generate display meshes separately for viewport only
- ✅ Keep approximation confined to final fabrication export

### Architecture Decisions Made:
- **Lossless until fabrication** - Mathematical exactness preserved throughout pipeline
- **PyQt6 over Tkinter** - More professional, better 3D integration via VTK
- **VTK for 3D** (when implemented) - Industry standard, powerful, well-documented
- **rhino3dm for SubD** - CRITICAL dependency for exact geometry representation
- **HTTP over WebSockets** - Simpler, sufficient for polling-based updates
- **Signal/slot pattern** - Clean event handling, decoupled components
- **Centralized state** - Single source of truth, automatic undo/redo
- **Parametric regions** - Defined in SubD parameter space, not mesh faces

The codebase is well-structured for incremental development, with clear separation between mathematical analysis, UI, and Rhino communication layers. The current implementation provides a solid foundation for adding real mathematical analysis engines and 3D visualization.

### Recent Updates (October 2025)

#### Week 2 - Multi-Viewport System ✅ COMPLETE
- **Implemented ViewportLayoutManager** (`app/ui/viewport_layout.py`) - Complete multi-viewport system
- **Four configurable layouts** - Single, Two Horizontal, Two Vertical, Four Grid (matching Rhino's standard layouts)
- **Independent cameras per viewport** - Each viewport maintains its own camera position and settings
- **Standard view presets** - Top, Front, Right, Back, Left, Bottom, Perspective, and Isometric views
- **Active viewport tracking** - Visual indicators (green border) show which viewport is active
- **Menu integration** - View → Viewport Layout submenu with keyboard shortcuts (Alt+1/2/3/4)
- **Updated main.py** - Replaced single viewport with ViewportLayoutManager, updated all test geometry methods
- **Professional CAD-like interface** - Now matches standard 3D modeling applications

#### Week 3 - HTTP Bridge ✅ COMPLETE
- **Python 3 Support** - Rhino 8 supports Python 3 natively (no IronPython issues)
- **Full Geometry Transfer** - Successfully transferring mesh representation of SubD from Rhino
- **Fixed Twitching Issue** - Resolved geometry re-rendering loop with smart change detection
- **Optimizations Applied**:
  - Added proper hash comparison to prevent duplicate updates
  - Viewport checks if geometry actually changed before re-rendering
  - Reduced polling frequency from 1s to 2s to minimize overhead
  - Initial geometry fetch doesn't trigger duplicate update
- **Current file**: `rhino/grasshopper_server_control.py` provides clean start/stop control

#### Week 4 - Edit Mode System ✅ COMPLETE
- **Edit Mode Infrastructure** - Solid/Panel/Edge/Vertex selection modes implemented
- **EditModeManager** - Centralized state tracking for selections and mode changes
- **Toolbar Integration** - Professional mode selector with visual indicators (S/P/E/V buttons)
- **VTK Picking System** - Face, edge, and vertex picking with visual highlighting
- **Architecture Ready for OpenSubdiv** - Designed with future Tier 1 hybrid architecture in mind
- **Files Created**:
  - `app/state/edit_mode.py` - Mode and selection state management
  - `app/ui/picker.py` - VTK-based element picking
  - `app/ui/edit_mode_toolbar.py` - Mode selector UI
- **Next Phase**: Will integrate with OpenCASCADE + OpenSubdiv for exact limit surface editing

#### Mouse Control Fixes ✅ FULLY RESOLVED (November 2025)
- **Critical UX Issue**: LEFT click was rotating camera instead of selecting elements
- **Root Cause**: Inheriting from `vtkInteractorStyleTrackballCamera` had deep internal state that couldn't be fully overridden
- **Complete Solution**: Created `app/ui/rhino_interactor.py` inheriting from base `vtkInteractorStyle`
  - Full manual implementation of Rotate, Pan, and Dolly camera methods
  - Complete control over event handling - no hidden parent behaviors
  - LEFT click/drag does NOTHING to camera (reserved for selection)
- **Final Control Mapping**:
  - LEFT click: Selection/picking only (no camera movement!)
  - RIGHT drag or MIDDLE drag: Rotate camera
  - Shift + RIGHT: Pan camera
  - Mouse wheel: Zoom
- **Files**: `app/ui/rhino_interactor.py`, `MOUSE_CONTROLS_SOLUTION.md`
- **Result**: Selection system now fully functional, matches Rhino/CAD standards
