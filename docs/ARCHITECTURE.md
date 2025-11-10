# Ceramic Mold Analyzer - Architecture

**Version**: 0.5.0 (Phase 0 Complete)
**Last Updated**: November 10, 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Architectural Principles](#core-architectural-principles)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Component Architecture](#component-architecture)
6. [Key Design Decisions](#key-design-decisions)
7. [Extension Points](#extension-points)
8. [Performance Characteristics](#performance-characteristics)
9. [Security and Reliability](#security-and-reliability)

---

## System Overview

The Ceramic Mold Analyzer is a desktop application for discovering mathematical decompositions of subdivision surfaces to create slip-casting ceramic molds. The system uses a **hybrid C++/Python architecture** where C++ provides exact geometry operations and Python provides UI and workflow orchestration.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Rhino + Grasshopper                      │
│              (SubD modeling environment)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/JSON (Control Cage)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  Desktop Application                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Python Layer (PyQt6 + VTK)                │   │
│  │  • User Interface                                   │   │
│  │  • State Management                                 │   │
│  │  • Workflow Orchestration                          │   │
│  │  • Analysis Coordination                            │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │ pybind11 (Zero-copy)              │
│  ┌──────────────────────↓──────────────────────────────┐   │
│  │        C++ Core (OpenSubdiv + OpenCASCADE)          │   │
│  │  • Exact SubD Evaluation                            │   │
│  │  • Mathematical Analysis                            │   │
│  │  • NURBS Operations                                 │   │
│  │  • Constraint Validation                            │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/JSON (NURBS Molds)
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    Rhino + Grasshopper                      │
│              (Mold export and fabrication)                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Characteristics

- **Hybrid Architecture**: C++ for geometry, Python for UI/workflow
- **Lossless Representation**: Exact mathematics until final G-code export
- **Parametric Regions**: All regions defined in (face_id, u, v) space
- **Multi-Lens Analysis**: Multiple mathematical perspectives on the same geometry
- **Real-time Visualization**: VTK-based 3D viewport with Rhino-compatible controls

---

## Core Architectural Principles

### 1. Lossless Until Fabrication

**This is the most important architectural principle.**

The system maintains **exact mathematical representation** from input SubD through all analysis and region discovery. Approximation occurs **ONLY ONCE** at the final fabrication export (G-code/STL).

#### Correct Data Pipeline

```
Rhino SubD (exact)
  ↓
HTTP Bridge
  → Control cage: {vertices, faces, creases} as JSON
  ↓
C++ OpenSubdiv
  → Exact limit surface evaluation (Stam eigenanalysis)
  → Infinite resolution evaluation at any (face_id, u, v)
  ↓
Parametric Regions
  → Defined in parameter space: (face_id, u, v)
  → No mesh artifacts or discretization errors
  ↓
Mathematical Analysis
  → Queries exact limit surface
  → Curvature from exact derivatives
  → Spectral analysis on continuous surface
  ↓
NURBS Surface Generation
  → Analytical fit to limit surface samples
  → Exact representation (not triangulated)
  ↓
Mold Solid Creation
  → Exact Brep operations (OpenCASCADE)
  → Boolean unions/intersections
  ↓
Export to Rhino
  → NURBS surfaces (exact)
  ↓
G-code Generation
  → SINGLE APPROXIMATION HAPPENS HERE
  → Tessellation for toolpaths only
```

#### Why This Matters

1. **Mathematical Truth**: Regions represent genuine mathematical boundaries, not mesh artifacts
2. **Infinite Resolution**: Can evaluate at any density without re-fetching from Rhino
3. **Zero Accumulated Error**: No compounding approximations through the pipeline
4. **Philosophical Alignment**: Seams inscribe true mathematical structure

#### Display Meshes

Display meshes are generated **separately** for VTK viewport visualization ONLY:

```cpp
// Display mesh - for visualization only
TessellationResult display_mesh = evaluator.tessellate(subdivision_level=4);
vtk_actor.SetPolyData(display_mesh);

// Analysis - uses exact limit surface
Point3D exact_point = evaluator.evaluateLimit(face_id, u, v);
Vector3 exact_normal = evaluator.evaluateNormal(face_id, u, v);
```

**Display meshes do NOT replace the exact SubD model** used for analysis.

### 2. Parametric Region Definition

All regions are defined in **parametric space**, not world space:

```python
class ParametricRegion:
    """Region defined by parametric coordinates"""
    parametric_coords: List[Tuple[int, float, float]]  # (face_id, u, v)
    boundary_curves: List[ParametricCurve]              # Curves in (u,v) space

    def evaluate_point(self, evaluator, index):
        """Evaluate world-space point from parametric coords"""
        face_id, u, v = self.parametric_coords[index]
        return evaluator.evaluateLimit(face_id, u, v)
```

**Benefits**:
- Resolution-independent (can evaluate at any density)
- No mesh topology dependence
- Exact boundary representation
- Stable under subdivision level changes

### 3. Separation of Concerns

Clean separation between computation and presentation:

```
┌────────────────────┐
│   C++ Core         │  Computation Layer
│  • Geometry        │  • Exact evaluation
│  • Analysis        │  • Mathematical analysis
│  • Validation      │  • Fast computation
└────────┬───────────┘
         │ pybind11 (Zero-copy NumPy arrays)
┌────────↓───────────┐
│   Python Layer     │  Orchestration Layer
│  • State           │  • User interaction
│  • UI              │  • Workflow logic
│  • Workflow        │  • Data management
└────────────────────┘
```

This allows:
- C++ optimization without UI concerns
- Python flexibility without performance penalties
- Independent testing of each layer
- Clear API boundaries

### 4. Reactive State Management

Centralized state with signal-based updates:

```python
class ApplicationState(QObject):
    # All state changes emit signals
    regions_updated = pyqtSignal(list)
    state_changed = pyqtSignal()

    def set_regions(self, regions):
        self.regions = regions
        self.regions_updated.emit(regions)  # Notify all observers
        self.state_changed.emit()
        self._add_history_item(...)  # Automatic undo/redo
```

**Benefits**:
- Single source of truth
- Automatic UI updates via signals
- Built-in undo/redo history
- Consistent state across components

---

## Data Flow

### Rhino → Desktop (Geometry Import)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Rhino/Grasshopper: Extract SubD Control Cage             │
│    • Vertices: [[x, y, z], ...]                              │
│    • Faces: [[i, j, k, l], ...] (quad or n-gon)             │
│    • Creases: [[edge_i, edge_j, sharpness], ...]            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP POST /api/control_cage
                     ↓ JSON
┌─────────────────────────────────────────────────────────────┐
│ 2. Desktop: Receive Control Cage                            │
│    bridge.py → ApplicationState                              │
└────────────────────┬────────────────────────────────────────┘
                     │ Convert to C++ types
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. C++ Core: Build OpenSubdiv Topology                      │
│    SubDControlCage → Far::TopologyRefiner                    │
│    • Construct topology descriptor                           │
│    • Build internal subdivision tables                       │
│    • Enable exact limit surface queries                      │
└─────────────────────────────────────────────────────────────┘
```

**Code Example**:

```python
# Grasshopper (Python component)
def export_control_cage(subd):
    """Extract control cage from SubD"""
    cage_data = {
        'vertices': [[v.X, v.Y, v.Z] for v in subd.Vertices],
        'faces': [list(face.GetVertexIndices()) for face in subd.Faces],
        'creases': extract_creases(subd)
    }

    # Send to desktop
    requests.post('http://localhost:8000/api/control_cage', json=cage_data)

# Desktop (Python)
def receive_control_cage(request):
    """Receive and build SubD evaluator"""
    data = request.json

    # Convert to C++ types
    cage = cpp_core.SubDControlCage()
    for v in data['vertices']:
        cage.vertices.append(cpp_core.Point3D(v[0], v[1], v[2]))
    cage.faces = data['faces']

    # Build topology
    evaluator = cpp_core.SubDEvaluator()
    evaluator.buildTopology(cage)

    # Store in state
    self.state.set_subd_geometry(evaluator)
```

### Desktop Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Selects Lens (Differential, Spectral, etc.)         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Python Decomposer: Sample Surface                        │
│    for face_id in range(face_count):                         │
│        for u, v in sample_grid:                              │
│            point = evaluator.evaluateLimit(face_id, u, v)    │
│            # Compute lens metrics...                         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. C++ Analysis: Mathematical Computation                    │
│    • Curvature analysis (principal curvatures K1, K2)        │
│    • Spectral analysis (Laplace-Beltrami eigenfunctions)     │
│    • Returns metrics to Python                               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Python Clustering: Region Discovery                       │
│    • k-means, spectral clustering, watershed, etc.           │
│    • Create ParametricRegion objects                         │
│    • Store in ApplicationState                               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. VTK Visualization: Display Regions                        │
│    • Generate display mesh (tessellation)                    │
│    • Color by region                                         │
│    • Highlight boundaries                                    │
└─────────────────────────────────────────────────────────────┘
```

### Desktop → Rhino (Mold Export)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Desktop: Generate NURBS Molds                             │
│    • Sample limit surface at high resolution                 │
│    • Fit NURBS surfaces (OpenCASCADE)                        │
│    • Apply draft angle transformation                        │
│    • Create solid Breps with Boolean operations              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Serialize NURBS Surfaces                                  │
│    nurbs_data = {                                            │
│        'degree_u': int,                                      │
│        'degree_v': int,                                      │
│        'knots_u': [...],                                     │
│        'knots_v': [...],                                     │
│        'control_points': [[[x,y,z,w], ...], ...],           │
│        'weights': [[...], ...]                               │
│    }                                                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP POST /api/import_nurbs
                     ↓ JSON
┌─────────────────────────────────────────────────────────────┐
│ 3. Grasshopper: Reconstruct NURBS Surfaces                   │
│    • Create Rhino NurbsSurface from data                     │
│    • Add to document                                         │
│    • Ready for fabrication export                            │
└─────────────────────────────────────────────────────────────┘
```

### State Management Flow

```
User Action
    ↓
UI Component
    ↓
ApplicationState.method()
    ├→ Modify internal state
    ├→ Emit signal(s)
    └→ Add to undo/redo history
         ↓
    Signals propagate to:
    ├→ UI Components (update display)
    ├→ VTK Viewports (refresh rendering)
    ├→ Analysis Panels (recompute if needed)
    └→ Region List (update list)
```

**Example**:

```python
# User pins a region
region_list.pin_button_clicked(region_id)
    ↓
self.state.set_region_pinned(region_id, True)
    ↓
    # Inside ApplicationState:
    region.pinned = True
    self.region_pinned.emit(region_id, True)  # Signal
    self._add_history_item(...)                # Undo/redo
    ↓
# All connected components auto-update:
viewport.on_region_pinned(region_id, True)    # Update visual
region_list.on_region_pinned(region_id, True) # Update icon
analysis_panel.on_state_changed()             # Recalculate stats
```

---

## Technology Stack

### C++ Core

| Component | Purpose | Version |
|-----------|---------|---------|
| **OpenSubdiv** | Exact SubD limit surface evaluation | 3.6+ |
| **OpenCASCADE** | NURBS operations, Boolean ops | 7.x |
| **pybind11** | Python bindings with zero-copy | 2.11+ |
| **CMake** | Build system configuration | 3.20+ |
| **Google Test** | Unit testing framework | 1.12+ |

**Why C++?**
- Performance: 10-100x faster than Python for geometry operations
- Libraries: OpenSubdiv and OpenCASCADE only available in C++
- Precision: Exact floating-point control
- Memory: Manual memory management for large datasets

### Python Layer

| Component | Purpose | Version |
|-----------|---------|---------|
| **PyQt6** | UI framework, widgets, layouts | 6.9.1 |
| **VTK** | 3D visualization, rendering | 9.3.0 |
| **NumPy** | Numerical arrays, linear algebra | 1.26+ |
| **SciPy** | Scientific computing, clustering | 1.11+ |
| **pytest** | Testing framework | 7.x+ |
| **requests** | HTTP communication with Rhino | 2.31+ |

**Why Python?**
- Rapid development: Fast iteration on UI and workflow
- Rich ecosystem: NumPy, SciPy for scientific computing
- Excellent UI libraries: PyQt6, VTK
- Easy testing: pytest and fixtures
- Dynamic: Hot-reload for development

### Integration Layer

**pybind11**: Zero-copy integration between C++ and Python

```cpp
// C++ side - return NumPy array (zero-copy)
py::array_t<float> getVertices() {
    return py::array_t<float>(
        {vertex_count, 3},               // Shape
        {3 * sizeof(float), sizeof(float)}, // Strides
        vertices.data(),                 // Data pointer
        py::cast(*this)                  // Owner (prevents deallocation)
    );
}
```

```python
# Python side - direct access to C++ memory
vertices = evaluator.getVertices()  # No copy!
vertices[0, 0] = 1.0  # Modifies C++ data directly
```

---

## Component Architecture

### C++ Core Components

```
cpp_core/
├── geometry/              # Core geometry operations
│   ├── types.h           # Point3D, Vector3, SubDControlCage
│   ├── subd_evaluator.*  # OpenSubdiv wrapper
│   ├── nurbs_generator.* # NURBS operations (OpenCASCADE)
│   ├── nurbs_fitting.*   # Surface fitting
│   ├── draft_transform.* # Draft angle transformation
│   └── mold_solid.*      # Solid creation
│
├── analysis/              # Mathematical analysis
│   ├── curvature_analyzer.* # Principal curvature computation
│   └── spectral_analyzer.*  # Laplace-Beltrami eigenanalysis
│
├── constraints/           # Validation and checking
│   ├── constraint_validator.*  # Base validator interface
│   ├── undercut_detector.*     # Undercut detection
│   └── draft_checker.*         # Draft angle verification
│
├── utils/                 # Utilities
│   └── mesh_mapping.*     # Display mesh generation
│
└── python_bindings/       # pybind11 bindings
    └── bindings.cpp       # Expose all C++ classes to Python
```

#### SubDEvaluator (Core Geometry)

```cpp
class SubDEvaluator {
public:
    // Build topology from control cage
    bool buildTopology(const SubDControlCage& cage);

    // Exact limit surface evaluation
    Point3D evaluateLimit(int face_index, float u, float v) const;
    Vector3 evaluateNormal(int face_index, float u, float v) const;
    void evaluateDerivatives(int face_index, float u, float v,
                             Vector3& du, Vector3& dv) const;

    // Tessellation for display (not used for analysis!)
    TessellationResult tessellate(int subdivision_level = 3) const;

    // Query methods
    int getFaceCount() const;
    int getVertexCount() const;
};
```

#### CurvatureAnalyzer (Mathematical Analysis)

```cpp
class CurvatureAnalyzer {
public:
    struct CurvatureResult {
        float k1, k2;           // Principal curvatures
        Vector3 dir1, dir2;     // Principal directions
        float mean_curvature;   // H = (k1 + k2) / 2
        float gaussian_curvature; // K = k1 * k2
    };

    CurvatureResult analyzeCurvature(
        const SubDEvaluator& evaluator,
        int face_index,
        float u, float v
    ) const;
};
```

#### ConstraintValidator (Validation)

```cpp
class ConstraintValidator {
public:
    struct ConstraintReport {
        bool valid;
        std::string message;
        std::vector<Point3D> violation_points;
        float severity;  // 0.0 = no violation, 1.0 = severe
    };

    // Check for undercuts (demolding issues)
    ConstraintReport checkUndercuts(
        const SubDEvaluator& evaluator,
        const ParametricRegion& region,
        const Vector3& parting_direction
    );

    // Check draft angles
    ConstraintReport checkDraftAngles(
        const SubDEvaluator& evaluator,
        const ParametricRegion& region,
        float min_draft_angle_degrees
    );
};
```

### Python Layer Components

```
app/
├── state/                 # State management
│   ├── app_state.py      # Central state manager (QObject)
│   ├── edit_mode.py      # Edit mode state machine
│   ├── parametric_region.py # Region data structure
│   └── iteration_manager.py # Iteration tracking
│
├── ui/                    # User interface
│   ├── viewport_3d.py    # 3D viewport with VTK
│   ├── viewport_layout.py # Multi-viewport manager
│   ├── region_list.py    # Region list widget
│   ├── analysis_panel.py # Analysis controls
│   └── pickers/          # Sub-object selection
│       ├── face_picker.py
│       ├── edge_picker.py
│       └── vertex_picker.py
│
├── analysis/              # Analysis modules
│   ├── differential_decomposer.py # Curvature-based analysis
│   └── spectral_decomposer.py     # Spectral analysis
│
├── constraints/           # Constraint checking
│   └── constraint_manager.py # Validation orchestration
│
├── workflow/              # High-level workflows
│   └── mold_workflow.py  # Mold generation workflow
│
├── bridge/                # Rhino communication
│   └── rhino_bridge.py   # HTTP client
│
└── export/                # Export functionality
    └── rhino_exporter.py # Send NURBS to Rhino
```

#### ApplicationState (State Management)

```python
class ApplicationState(QObject):
    """Central state manager - single source of truth"""

    # Signals (observers connect to these)
    regions_updated = pyqtSignal(list)
    region_pinned = pyqtSignal(str, bool)
    state_changed = pyqtSignal()

    # Core state
    subd_geometry: Optional[cpp_core.SubDEvaluator]
    regions: List[ParametricRegion]
    history: List[HistoryItem]

    # State modification methods (all emit signals)
    def set_regions(self, regions: List[ParametricRegion])
    def set_region_pinned(self, region_id: str, pinned: bool)
    def add_region(self, region: ParametricRegion)

    # Undo/redo
    def undo()
    def redo()
```

#### Viewport3D (3D Visualization)

```python
class Viewport3D(QWidget):
    """VTK-based 3D viewport with Rhino-compatible controls"""

    def __init__(self, state: ApplicationState):
        self.state = state
        self.vtk_widget = QVTKRenderWindowInteractor()
        self.renderer = vtkRenderer()

        # Connect to state updates
        self.state.regions_updated.connect(self._update_regions_display)

    def display_geometry(self, evaluator: cpp_core.SubDEvaluator):
        """Display SubD geometry"""
        # Generate display mesh (tessellation)
        display_mesh = evaluator.tessellate(subdivision_level=4)

        # Create VTK pipeline
        actor = self._create_mesh_actor(display_mesh)
        self.renderer.AddActor(actor)
```

---

## Key Design Decisions

### Why OpenSubdiv for Exact Limit Surface?

**Problem**: Subdivision surfaces are defined by an infinite refinement process. How do we evaluate the "limit surface" exactly?

**Solution**: OpenSubdiv implements **Stam's eigenanalysis** method, which evaluates the limit surface and its derivatives analytically without actually performing subdivision.

**Benefits**:
- **Exact evaluation**: No approximation at any step
- **Infinite resolution**: Can evaluate at any (u, v) coordinate
- **Derivatives**: Exact tangents and normals for curvature
- **Performance**: GPU acceleration via Metal/CUDA

**Alternative rejected**: Mesh conversion would introduce approximation immediately, violating the lossless principle.

### Why OpenCASCADE for NURBS Operations?

**Problem**: Need to create manufacturable mold surfaces from discovered regions.

**Solution**: OpenCASCADE provides industrial-strength NURBS operations:
- Surface fitting from point clouds
- Draft angle transformations
- Boolean operations for solid creation
- IGES/STEP export (future)

**Benefits**:
- **Exact NURBS**: Analytical surface representation
- **CAD interoperability**: Standard NURBS format
- **Robust geometry**: Handles complex topologies
- **Manufacturing ready**: Draft angles, undercuts, etc.

**Alternative rejected**: Custom NURBS implementation would take months and be less robust.

### Why VTK for Visualization?

**Problem**: Need professional 3D visualization with region coloring, selection, etc.

**Solution**: VTK provides scientific visualization toolkit:
- High-performance rendering
- PyQt6 integration
- Rich actor/property system
- Picking and selection

**Benefits**:
- **Professional quality**: Used in ParaView, Slicer, etc.
- **PyQt6 integration**: QVTKRenderWindowInteractor
- **Flexible rendering**: Region colors, boundaries, highlights
- **Proven**: Industry standard for scientific visualization

**Alternative rejected**: Raw OpenGL would require too much low-level code.

### Why Parametric Regions?

**Problem**: How to represent regions that are resolution-independent and exact?

**Solution**: Define regions in **parametric space** (face_id, u, v) rather than world space vertices.

**Benefits**:
- **Resolution independent**: Can evaluate at any density
- **Exact boundaries**: No mesh topology dependence
- **Stable**: Doesn't change with subdivision level
- **Analytical**: Can compute derivatives, curvature, etc.

**Example**:
```python
# Parametric region (resolution-independent)
region = ParametricRegion()
region.add_parametric_coords([
    (face_id=0, u=0.0, v=0.0),
    (face_id=0, u=0.5, v=0.0),
    (face_id=0, u=0.5, v=0.5),
    # ...
])

# Evaluate at any resolution
for u, v in high_res_grid:
    point = evaluator.evaluateLimit(region.face_id, u, v)
```

**Alternative rejected**: Storing world-space vertices would be resolution-dependent and introduce discretization errors.

### Why Hybrid C++/Python?

**Problem**: Need both performance and development velocity.

**Solution**: Hybrid architecture with clear boundaries:
- **C++**: Geometry operations, mathematical analysis
- **Python**: UI, workflow, state management

**Benefits**:
- **Performance where needed**: 10-100x speedup for geometry
- **Flexibility where needed**: Rapid UI development in Python
- **Best of both**: Zero-copy integration via pybind11
- **Testable**: Each layer independently testable

**Data transfer**:
```python
# Zero-copy NumPy array from C++
vertices = evaluator.getVertices()  # np.ndarray, no copy!
mean = np.mean(vertices, axis=0)    # Direct NumPy operations
```

---

## Extension Points

The architecture provides clear extension points for adding new functionality.

### 1. Mathematical Lenses Interface

To add a new mathematical lens for region discovery:

**C++ Analysis** (optional, for performance):
```cpp
// cpp_core/analysis/my_lens_analyzer.h
class MyLensAnalyzer {
public:
    struct Result {
        float metric;
        std::vector<int> regions;
    };

    Result analyze(const SubDEvaluator& evaluator,
                   int face_index, float u, float v);
};
```

**Python Decomposer** (required):
```python
# app/analysis/my_lens_decomposer.py
class MyLensDecomposer:
    """Custom mathematical lens for region discovery"""

    def decompose(self, evaluator: cpp_core.SubDEvaluator,
                  target_regions: int) -> List[ParametricRegion]:
        # 1. Sample surface and compute metrics
        # 2. Cluster into regions
        # 3. Return ParametricRegion objects
        pass
```

**Integration Point**: Register in `app/ui/analysis_panel.py`

### 2. Constraint Validators

To add a new constraint validator:

**C++ Validator**:
```cpp
// cpp_core/constraints/my_constraint.h
class MyConstraint {
public:
    ConstraintReport check(const SubDEvaluator& evaluator,
                          const ParametricRegion& region);
};
```

**Python Integration**:
```python
# app/constraints/constraint_manager.py
class ConstraintManager:
    def check_all(self, evaluator, regions):
        # Add your constraint
        for region in regions:
            result = self.my_constraint.check(evaluator, region)
            # Handle result
```

**Visualization**: Add to `app/ui/constraint_panel.py`

### 3. Export Formats

To add a new export format:

**Exporter Interface**:
```python
# app/export/base_exporter.py
class BaseExporter(ABC):
    @abstractmethod
    def export(self, molds: List[NURBSSurface], filepath: str):
        pass

# app/export/my_format_exporter.py
class MyFormatExporter(BaseExporter):
    def export(self, molds, filepath):
        # Export to your format
        pass
```

**Registration**:
```python
# app/export/exporter_registry.py
EXPORTERS = {
    'rhino': RhinoExporter(),
    'step': STEPExporter(),
    'myformat': MyFormatExporter(),  # Add here
}
```

### 4. UI Widgets

To add a new UI panel:

**Widget Class**:
```python
# app/ui/my_panel.py
class MyPanel(QWidget):
    def __init__(self, state: ApplicationState):
        self.state = state
        self._setup_ui()
        self._connect_signals()

    def _connect_signals(self):
        # Connect to state updates
        self.state.regions_updated.connect(self._on_regions_updated)
```

**Integration**: Add to `main.py` main window

### 5. Rhino Bridge Extensions

To add new Rhino communication endpoints:

**Grasshopper Server**:
```python
# rhino/grasshopper_http_server_control_cage.py
@app.route('/api/my_endpoint', methods=['POST'])
def handle_my_endpoint():
    data = request.json
    # Process in Rhino/Grasshopper
    return jsonify(result)
```

**Desktop Client**:
```python
# app/bridge/rhino_bridge.py
class RhinoBridge:
    def send_my_data(self, data):
        response = requests.post(
            f'{self.base_url}/api/my_endpoint',
            json=data
        )
        return response.json()
```

---

## Performance Characteristics

### Computation Times (Typical)

Based on medium complexity SubD (1000 faces):

| Operation | Time | Notes |
|-----------|------|-------|
| Build OpenSubdiv topology | 10-50ms | One-time cost |
| Evaluate single limit point | 0.001ms | Fast (cached topology) |
| Evaluate 100k limit points | 100ms | Fully parallelizable |
| Curvature analysis (full surface) | 200-500ms | C++ implementation |
| Spectral decomposition | 500-2000ms | Eigenvalue computation |
| NURBS surface fitting | 100-300ms | Per region |
| Draft angle transformation | 50-150ms | Per surface |
| Boolean solid operations | 200-1000ms | Depends on complexity |

### Memory Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| OpenSubdiv topology | 10-50 MB | Per SubD |
| Display mesh (VTK) | 5-20 MB | Per viewport |
| C++ working memory | 50-200 MB | Analysis buffers |
| Python UI | 100-300 MB | PyQt6 + VTK |
| **Total typical** | **200-600 MB** | For medium models |

### Optimization Strategies

1. **Batch evaluation**: Evaluate multiple points in single C++ call
2. **Caching**: Cache expensive computations (eigenvectors, etc.)
3. **Level-of-detail**: Use coarser tessellation for distant objects
4. **Lazy evaluation**: Compute on-demand, not preemptively
5. **Parallel processing**: Use OpenMP for independent computations

---

## Security and Reliability

### Data Validation

All external data is validated:

```python
def validate_control_cage(data: dict) -> bool:
    """Validate control cage data from Rhino"""
    # Check required fields
    if not all(k in data for k in ['vertices', 'faces']):
        return False

    # Validate vertices
    if not all(len(v) == 3 for v in data['vertices']):
        return False

    # Validate face indices
    max_index = len(data['vertices']) - 1
    for face in data['faces']:
        if not all(0 <= idx <= max_index for idx in face):
            return False

    return True
```

### Error Handling

Graceful degradation on errors:

```python
try:
    evaluator = cpp_core.SubDEvaluator()
    evaluator.buildTopology(cage)
except RuntimeError as e:
    # Fallback: show error, allow reload
    QMessageBox.critical(self, "Geometry Error", str(e))
    return
```

### State Recovery

Undo/redo history enables state recovery:

```python
# All state changes automatically tracked
self.state.set_regions(new_regions)  # Adds to history

# User can undo/redo
self.state.undo()  # Restore previous state
self.state.redo()  # Re-apply change
```

### Testing Strategy

Multi-layer testing approach:

1. **C++ Unit Tests** (Google Test): Test individual C++ classes
2. **Python Unit Tests** (pytest): Test Python modules
3. **Integration Tests**: Test C++↔Python interaction
4. **UI Tests** (pytest-qt): Test UI components
5. **End-to-End Tests**: Test complete workflows

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for testing details.

---

## Future Architecture Considerations

### Planned Extensions

1. **GPU Acceleration**: Move more analysis to GPU (CUDA/Metal)
2. **Distributed Computing**: Split analysis across multiple machines
3. **Cloud Integration**: Optional cloud-based heavy computation
4. **Plugin System**: Dynamic loading of analysis modules
5. **Scripting API**: Python API for automation

### Scalability

Current architecture scales to:
- **SubD complexity**: Up to 10,000 faces (limited by Rhino, not desktop)
- **Region count**: Up to 100 regions (UI/performance limit)
- **Display mesh**: Up to 1M triangles (VTK hardware limit)

For larger models, consider:
- Hierarchical region representation
- Spatial partitioning (octree, BVH)
- Out-of-core processing
- Progressive refinement

---

## Conclusion

The Ceramic Mold Analyzer architecture prioritizes:

1. **Mathematical Exactness**: Lossless representation until fabrication
2. **Performance**: C++ for heavy computation, Python for flexibility
3. **Extensibility**: Clear extension points for new features
4. **Maintainability**: Clean separation of concerns
5. **Reliability**: Comprehensive testing and error handling

This hybrid C++/Python architecture provides the best balance of performance, development velocity, and mathematical rigor for the ceramic mold generation problem.

---

**For implementation details, see**:
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development practices
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - Build setup

**Last Updated**: November 10, 2025
**Version**: 0.5.0
