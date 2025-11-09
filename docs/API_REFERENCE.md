# Ceramic Mold Analyzer API Reference

**Version**: 0.5.0 (Phase 0 Complete)
**Date**: November 9, 2025
**Module**: `cpp_core` (C++ with Python bindings)

---

## Table of Contents

1. [Overview](#overview)
2. [C++ API](#cpp-api)
   - [Point3D](#point3d)
   - [SubDControlCage](#subdcontrolcage)
   - [TessellationResult](#tessellationresult)
   - [SubDEvaluator](#subdevaluator)
3. [Python API](#python-api)
   - [Importing the Module](#importing-the-module)
   - [Data Type Usage](#data-type-usage)
   - [Complete Examples](#complete-examples)
4. [Desktop Application API](#desktop-application-api)
   - [ApplicationState](#applicationstate)
   - [ParametricRegion](#parametricregion)
   - [SubDDisplayManager](#subddisplaymanager)
5. [Rhino Bridge API](#rhino-bridge-api)

---

## Overview

The `cpp_core` module provides exact subdivision surface evaluation using OpenSubdiv. All C++ classes are exposed to Python via pybind11 with zero-copy NumPy array integration.

**Key Principles**:
- **Exact Evaluation**: Limit surface evaluation uses Stam eigenanalysis, not mesh interpolation
- **Lossless Representation**: Control cage topology maintained exactly
- **Zero-Copy**: NumPy arrays share memory with C++ (no data copying)
- **Parametric Definition**: All evaluations use (face_index, u, v) coordinates

---

## C++ API

### Namespace

All C++ types are in the `latent` namespace:

```cpp
#include "geometry/types.h"
#include "geometry/subd_evaluator.h"

using namespace latent;
```

---

### Point3D

**Header**: `cpp_core/geometry/types.h`

**Description**: 3D point with float precision.

#### C++ Interface

```cpp
struct Point3D {
    float x, y, z;

    Point3D();                          // Default: (0, 0, 0)
    Point3D(float _x, float _y, float _z);
};
```

#### Examples

```cpp
// Construction
Point3D origin;                     // (0, 0, 0)
Point3D point(1.0f, 2.0f, 3.0f);   // (1, 2, 3)

// Member access
float x_coord = point.x;
point.y = 5.0f;
```

#### Python Interface

```python
import cpp_core

# Construction
origin = cpp_core.Point3D()              # (0, 0, 0)
point = cpp_core.Point3D(1.0, 2.0, 3.0)  # (1, 2, 3)

# Property access
x = point.x
point.y = 5.0

# String representation
print(point)  # "Point3D(1.000000, 2.000000, 3.000000)"
```

---

### SubDControlCage

**Header**: `cpp_core/geometry/types.h`

**Description**: Subdivision surface control cage with vertices, face topology, and edge creases.

#### C++ Interface

```cpp
struct SubDControlCage {
    std::vector<Point3D> vertices;           // Control vertices
    std::vector<std::vector<int>> faces;     // Face topology (quads/n-gons)
    std::vector<std::pair<int, float>> creases;  // (edge_id, sharpness)

    size_t vertex_count() const;
    size_t face_count() const;
};
```

#### Examples

```cpp
// Create cube control cage
SubDControlCage cage;

// Add vertices
cage.vertices.push_back(Point3D(-1, -1, -1));
cage.vertices.push_back(Point3D( 1, -1, -1));
cage.vertices.push_back(Point3D( 1,  1, -1));
cage.vertices.push_back(Point3D(-1,  1, -1));
cage.vertices.push_back(Point3D(-1, -1,  1));
cage.vertices.push_back(Point3D( 1, -1,  1));
cage.vertices.push_back(Point3D( 1,  1,  1));
cage.vertices.push_back(Point3D(-1,  1,  1));

// Add faces (quads)
cage.faces.push_back({0, 1, 2, 3});  // Bottom
cage.faces.push_back({4, 5, 6, 7});  // Top
cage.faces.push_back({0, 4, 7, 3});  // Left
cage.faces.push_back({1, 5, 6, 2});  // Right
cage.faces.push_back({0, 1, 5, 4});  // Front
cage.faces.push_back({3, 2, 6, 7});  // Back

// Add edge crease (sharp edge)
cage.creases.push_back({0, 1.0f});  // Edge 0, sharpness 1.0

// Query
size_t num_verts = cage.vertex_count();  // 8
size_t num_faces = cage.face_count();    // 6
```

#### Python Interface

```python
import cpp_core
import numpy as np

# Create cage
cage = cpp_core.SubDControlCage()

# Add vertices (list of Point3D)
cage.vertices = [
    cpp_core.Point3D(-1, -1, -1),
    cpp_core.Point3D( 1, -1, -1),
    cpp_core.Point3D( 1,  1, -1),
    cpp_core.Point3D(-1,  1, -1),
    cpp_core.Point3D(-1, -1,  1),
    cpp_core.Point3D( 1, -1,  1),
    cpp_core.Point3D( 1,  1,  1),
    cpp_core.Point3D(-1,  1,  1),
]

# Add faces (list of lists of ints)
cage.faces = [
    [0, 1, 2, 3],  # Bottom
    [4, 5, 6, 7],  # Top
    [0, 4, 7, 3],  # Left
    [1, 5, 6, 2],  # Right
    [0, 1, 5, 4],  # Front
    [3, 2, 6, 7],  # Back
]

# Add creases (list of tuples: (edge_id, sharpness))
cage.creases = [(0, 1.0)]

# Query counts
num_verts = cage.vertex_count()  # 8
num_faces = cage.face_count()    # 6

# String representation
print(cage)  # "SubDControlCage(8 vertices, 6 faces)"
```

#### Load from Rhino JSON

```python
import json
import cpp_core

# Load control cage from Grasshopper JSON
with open('control_cage.json', 'r') as f:
    data = json.load(f)

cage = cpp_core.SubDControlCage()

# Convert vertices
cage.vertices = [
    cpp_core.Point3D(v[0], v[1], v[2])
    for v in data['vertices']
]

# Faces are already lists of ints
cage.faces = data['faces']

# Creases: convert from [[edge_id, sharpness], ...] to [(id, sharp), ...]
cage.creases = [(c[0], c[1]) for c in data.get('creases', [])]
```

---

### TessellationResult

**Header**: `cpp_core/geometry/types.h`

**Description**: Triangulated mesh result from subdivision tessellation. Designed for efficient VTK rendering and NumPy integration.

#### C++ Interface

```cpp
struct TessellationResult {
    std::vector<float> vertices;      // Flattened [x,y,z, x,y,z, ...]
    std::vector<float> normals;       // Flattened normals [nx,ny,nz, ...]
    std::vector<int> triangles;       // Flattened indices [i,j,k, i,j,k, ...]
    std::vector<int> face_parents;    // Parent face ID for each triangle

    size_t vertex_count() const;      // = vertices.size() / 3
    size_t triangle_count() const;    // = triangles.size() / 3
};
```

#### Memory Layout

```
vertices:  [x0, y0, z0,  x1, y1, z1,  x2, y2, z2, ...]
normals:   [nx0,ny0,nz0, nx1,ny1,nz1, nx2,ny2,nz2, ...]
triangles: [i0, j0, k0,  i1, j1, k1,  i2, j2, k2, ...]
face_parents: [face_id_0, face_id_1, face_id_2, ...]
```

#### Python Interface (Zero-Copy NumPy)

```python
import cpp_core
import numpy as np

# Get tessellation result from evaluator
result = evaluator.tessellate(subdivision_level=3)

# Access as NumPy arrays (zero-copy!)
vertices = result.vertices    # shape (N, 3), dtype=float32
normals = result.normals      # shape (N, 3), dtype=float32
triangles = result.triangles  # shape (M, 3), dtype=int32
face_parents = result.face_parents  # shape (M,), dtype=int32

# Query counts
num_verts = result.vertex_count()     # Same as vertices.shape[0]
num_tris = result.triangle_count()    # Same as triangles.shape[0]

# Use in NumPy operations
centroid = np.mean(vertices, axis=0)
bounds_min = np.min(vertices, axis=0)
bounds_max = np.max(vertices, axis=0)

# Access individual vertices
first_vertex = vertices[0]  # [x, y, z]
x, y, z = vertices[0]

# Access individual triangles
first_tri = triangles[0]  # [i, j, k]
i, j, k = triangles[0]

# Get vertices of first triangle
tri_verts = vertices[triangles[0]]  # shape (3, 3)
```

---

### SubDEvaluator

**Header**: `cpp_core/geometry/subd_evaluator.h`

**Description**: Exact subdivision surface evaluator using OpenSubdiv. Provides both tessellation for display and exact limit surface evaluation for analysis.

#### C++ Interface

```cpp
class SubDEvaluator {
public:
    SubDEvaluator();
    ~SubDEvaluator();

    // ============================================================
    // Initialization
    // ============================================================

    /**
     * Build subdivision topology from control cage
     * Must be called before any evaluation
     */
    void initialize(const SubDControlCage& cage);

    /**
     * Check if evaluator is ready for use
     */
    bool is_initialized() const;

    // ============================================================
    // Display Tessellation
    // ============================================================

    /**
     * Generate triangulated mesh for rendering
     *
     * @param subdivision_level Number of subdivision iterations (1-5 typical)
     * @param adaptive Use adaptive tessellation (default false)
     * @return Triangulated mesh with vertices, normals, triangles
     */
    TessellationResult tessellate(int subdivision_level = 3,
                                   bool adaptive = false);

    // ============================================================
    // Exact Limit Surface Evaluation
    // ============================================================

    /**
     * Evaluate point on exact limit surface
     *
     * @param face_index Control face index [0, face_count)
     * @param u Parameter u in [0, 1]
     * @param v Parameter v in [0, 1]
     * @return Point on limit surface
     */
    Point3D evaluate_limit_point(int face_index, float u, float v) const;

    /**
     * Evaluate point and normal on limit surface
     *
     * @param face_index Control face index
     * @param u, v Parameters in [0, 1]
     * @param point Output: limit point
     * @param normal Output: unit normal
     */
    void evaluate_limit(int face_index, float u, float v,
                       Point3D& point, Point3D& normal) const;

    // ============================================================
    // Derivatives (for Curvature Analysis)
    // ============================================================

    /**
     * Evaluate limit point and first derivatives
     *
     * @param face_index Control face index
     * @param u, v Parameters in [0, 1]
     * @param position Output: limit position
     * @param du Output: ∂P/∂u (tangent in u direction)
     * @param dv Output: ∂P/∂v (tangent in v direction)
     */
    void evaluate_limit_with_derivatives(
        int face_index, float u, float v,
        Point3D& position,
        Point3D& du,
        Point3D& dv) const;

    /**
     * Evaluate limit point with first and second derivatives
     * Used for curvature computation
     *
     * @param face_index Control face index
     * @param u, v Parameters in [0, 1]
     * @param position Output: limit position
     * @param du, dv Output: first derivatives
     * @param duu Output: ∂²P/∂u²
     * @param dvv Output: ∂²P/∂v²
     * @param duv Output: ∂²P/∂u∂v
     */
    void evaluate_limit_with_second_derivatives(
        int face_index, float u, float v,
        Point3D& position,
        Point3D& du, Point3D& dv,
        Point3D& duu, Point3D& dvv, Point3D& duv) const;

    /**
     * Compute orthonormal tangent frame at limit point
     *
     * @param face_index Control face index
     * @param u, v Parameters in [0, 1]
     * @param tangent_u Output: normalized tangent in u direction
     * @param tangent_v Output: normalized tangent in v direction
     * @param normal Output: unit normal (tangent_u × tangent_v)
     */
    void compute_tangent_frame(
        int face_index, float u, float v,
        Point3D& tangent_u,
        Point3D& tangent_v,
        Point3D& normal) const;

    // ============================================================
    // Batch Operations
    // ============================================================

    /**
     * Batch evaluate multiple points (more efficient than loop)
     *
     * @param face_indices Face index for each point
     * @param params_u U parameters
     * @param params_v V parameters
     * @return TessellationResult with evaluated points and normals
     */
    TessellationResult batch_evaluate_limit(
        const std::vector<int>& face_indices,
        const std::vector<float>& params_u,
        const std::vector<float>& params_v) const;

    // ============================================================
    // Topology Queries
    // ============================================================

    /**
     * Get parent control face for a tessellated triangle
     */
    int get_parent_face(int triangle_index) const;

    /**
     * Get number of vertices in control cage
     */
    size_t get_control_vertex_count() const;

    /**
     * Get number of faces in control cage
     */
    size_t get_control_face_count() const;
};
```

---

## Python API

### Importing the Module

```python
import sys
import numpy as np

# Option 1: Development (local build)
sys.path.insert(0, 'cpp_core/build')
import cpp_core

# Option 2: Installed package
import cpp_core

# Check available classes
print(dir(cpp_core))
# ['Point3D', 'SubDControlCage', 'SubDEvaluator', 'TessellationResult']
```

---

### Complete Example: Load, Evaluate, Display

```python
import sys
sys.path.insert(0, 'cpp_core/build')
import cpp_core
import numpy as np
import json

# ============================================================
# 1. Load control cage from Rhino
# ============================================================

with open('subd_from_rhino.json', 'r') as f:
    data = json.load(f)

cage = cpp_core.SubDControlCage()
cage.vertices = [
    cpp_core.Point3D(v[0], v[1], v[2])
    for v in data['vertices']
]
cage.faces = data['faces']
cage.creases = [(c[0], c[1]) for c in data.get('creases', [])]

print(f"Loaded: {cage}")  # "SubDControlCage(N vertices, M faces)"

# ============================================================
# 2. Initialize evaluator
# ============================================================

evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

print(f"Initialized: {evaluator.is_initialized()}")  # True
print(f"Control vertices: {evaluator.get_control_vertex_count()}")
print(f"Control faces: {evaluator.get_control_face_count()}")

# ============================================================
# 3. Generate display mesh (for VTK)
# ============================================================

mesh = evaluator.tessellate(subdivision_level=3)

print(f"Tessellation:")
print(f"  Vertices: {mesh.vertex_count()}")
print(f"  Triangles: {mesh.triangle_count()}")

# Access as NumPy arrays (zero-copy!)
vertices = mesh.vertices    # shape (N, 3)
normals = mesh.normals      # shape (N, 3)
triangles = mesh.triangles  # shape (M, 3)

print(f"Vertex array shape: {vertices.shape}")
print(f"Triangle array shape: {triangles.shape}")

# ============================================================
# 4. Exact limit surface evaluation
# ============================================================

# Evaluate center point of first face
face_id = 0
u, v = 0.5, 0.5

point = evaluator.evaluate_limit_point(face_id, u, v)
print(f"Limit point at face {face_id}, ({u}, {v}): ({point.x}, {point.y}, {point.z})")

# Evaluate with normal
point = cpp_core.Point3D()
normal = cpp_core.Point3D()
evaluator.evaluate_limit(face_id, u, v, point, normal)
print(f"Normal: ({normal.x}, {normal.y}, {normal.z})")

# ============================================================
# 5. Compute curvature (requires derivatives)
# ============================================================

pos = cpp_core.Point3D()
du = cpp_core.Point3D()
dv = cpp_core.Point3D()
duu = cpp_core.Point3D()
dvv = cpp_core.Point3D()
duv = cpp_core.Point3D()

evaluator.evaluate_limit_with_second_derivatives(
    face_id, u, v, pos, du, dv, duu, dvv, duv
)

# Compute Gaussian curvature from derivatives
# K = (L*N - M²) / (E*G - F²)
# where E = du·du, F = du·dv, G = dv·dv
#       L = duu·n, M = duv·n, N = dvv·n

def dot(p1, p2):
    return p1.x*p2.x + p1.y*p2.y + p1.z*p2.z

def cross(p1, p2):
    return cpp_core.Point3D(
        p1.y*p2.z - p1.z*p2.y,
        p1.z*p2.x - p1.x*p2.z,
        p1.x*p2.y - p1.y*p2.x
    )

def normalize(p):
    length = np.sqrt(p.x**2 + p.y**2 + p.z**2)
    return cpp_core.Point3D(p.x/length, p.y/length, p.z/length)

# First fundamental form
E = dot(du, du)
F = dot(du, dv)
G = dot(dv, dv)

# Normal
n = normalize(cross(du, dv))

# Second fundamental form
L = dot(duu, n)
M = dot(duv, n)
N = dot(dvv, n)

# Gaussian curvature
K = (L*N - M*M) / (E*G - F*F)
print(f"Gaussian curvature: {K}")

# Mean curvature
H = (E*N - 2*F*M + G*L) / (2 * (E*G - F*F))
print(f"Mean curvature: {H}")

# ============================================================
# 6. Batch evaluation (efficient)
# ============================================================

# Sample 100 points on first face
face_indices = [0] * 100
params_u = np.linspace(0.1, 0.9, 10).repeat(10).tolist()
params_v = np.tile(np.linspace(0.1, 0.9, 10), 10).tolist()

sample_result = evaluator.batch_evaluate_limit(
    face_indices, params_u, params_v
)

sample_points = sample_result.vertices  # shape (100, 3)
sample_normals = sample_result.normals  # shape (100, 3)

print(f"Sampled {sample_points.shape[0]} points")
```

---

### Working with VTK

```python
import vtk
from vtk.util.numpy_support import numpy_to_vtk

def create_vtk_actor_from_tessellation(tessellation):
    """
    Convert TessellationResult to VTK actor for rendering
    """
    # Get arrays
    vertices = tessellation.vertices    # (N, 3)
    normals = tessellation.normals      # (N, 3)
    triangles = tessellation.triangles  # (M, 3)

    # Create VTK points
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(vertices, deep=False))  # Zero-copy!

    # Create VTK cells (triangles)
    vtk_cells = vtk.vtkCellArray()
    for tri in triangles:
        vtk_cells.InsertNextCell(3, tri.tolist())

    # Create polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)
    polydata.SetPolys(vtk_cells)

    # Add normals
    vtk_normals = vtk.vtkFloatArray()
    vtk_normals.SetNumberOfComponents(3)
    vtk_normals.SetName("Normals")
    for normal in normals:
        vtk_normals.InsertNextTuple(normal.tolist())
    polydata.GetPointData().SetNormals(vtk_normals)

    # Create mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.8, 0.8, 0.9)  # Light blue
    actor.GetProperty().SetSpecular(0.3)
    actor.GetProperty().SetSpecularPower(20)

    return actor
```

---

### Region-Based Coloring

```python
def create_colored_mesh_actor(tessellation, face_colors):
    """
    Create VTK actor with per-face colors

    Args:
        tessellation: TessellationResult
        face_colors: dict mapping face_id → (r, g, b) tuple

    Returns:
        vtk.vtkActor with per-face colors
    """
    vertices = tessellation.vertices
    normals = tessellation.normals
    triangles = tessellation.triangles
    face_parents = tessellation.face_parents

    # Create polydata (same as before)
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(vertices, deep=False))

    vtk_cells = vtk.vtkCellArray()
    for tri in triangles:
        vtk_cells.InsertNextCell(3, tri.tolist())

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)
    polydata.SetPolys(vtk_cells)

    # Add per-cell colors
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)
    colors.SetName("Colors")

    for face_id in face_parents:
        if face_id in face_colors:
            r, g, b = face_colors[face_id]
            colors.InsertNextTuple3(
                int(r * 255),
                int(g * 255),
                int(b * 255)
            )
        else:
            colors.InsertNextTuple3(200, 200, 200)  # Default gray

    polydata.GetCellData().SetScalars(colors)

    # Create actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarModeToUseCellData()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor

# Usage
region_colors = {
    0: (1.0, 0.0, 0.0),  # Red
    1: (0.0, 1.0, 0.0),  # Green
    2: (0.0, 0.0, 1.0),  # Blue
}

actor = create_colored_mesh_actor(mesh, region_colors)
```

---

## Desktop Application API

### ApplicationState

**File**: `app/state/app_state.py`

**Description**: Centralized state management with undo/redo, regions, edit modes, and signal/slot architecture.

```python
from app.state.app_state import ApplicationState
from app.state.parametric_region import ParametricRegion

# Create state (singleton pattern recommended)
state = ApplicationState()

# ============================================================
# Region Management
# ============================================================

# Add discovered region
region = ParametricRegion(
    id="region_0",
    faces=[0, 1, 2, 3],
    unity_principle="Differential",
    unity_strength=0.85,
    pinned=False
)
state.add_region(region)

# Pin/unpin region
state.set_region_pinned("region_0", True)

# Update region faces
state.update_region_faces("region_0", [0, 1, 2, 3, 4, 5])

# Get all regions
regions = state.get_regions()

# Get region by ID
region = state.get_region("region_0")

# Remove region
state.remove_region("region_0")

# ============================================================
# Undo/Redo
# ============================================================

# Most state changes automatically create undo commands
state.set_region_pinned("region_0", True)  # Creates undo entry
state.undo()  # Unpins region
state.redo()  # Re-pins region

# Check undo/redo availability
can_undo = state.can_undo()
can_redo = state.can_redo()

# ============================================================
# Edit Mode
# ============================================================

from app.state.edit_mode import EditMode

# Set edit mode
state.set_edit_mode(EditMode.PANEL)  # Face selection
state.set_edit_mode(EditMode.EDGE)   # Edge selection
state.set_edit_mode(EditMode.VERTEX) # Vertex selection
state.set_edit_mode(EditMode.SOLID)  # View-only

# Get current edit mode
mode = state.get_edit_mode()

# ============================================================
# Selection
# ============================================================

# Add to selection
state.add_to_selection([5, 10, 15])  # Face IDs

# Remove from selection
state.remove_from_selection([10])

# Clear selection
state.clear_selection()

# Get selection
selected = state.get_selection()  # List of IDs

# ============================================================
# Signals (Qt-style)
# ============================================================

# Connect to state changes
state.region_added.connect(on_region_added)
state.region_removed.connect(on_region_removed)
state.region_pinned_changed.connect(on_region_pinned_changed)
state.edit_mode_changed.connect(on_edit_mode_changed)
state.selection_changed.connect(on_selection_changed)

def on_region_added(region):
    print(f"Region added: {region.id}")

def on_region_pinned_changed(region_id, pinned):
    print(f"Region {region_id} pinned: {pinned}")
```

---

### ParametricRegion

**File**: `app/state/parametric_region.py`

**Description**: Parametric region definition (face_id, u, v) maintaining lossless representation.

```python
from app.state.parametric_region import ParametricRegion

# Create region
region = ParametricRegion(
    id="differential_0",
    faces=[0, 1, 2, 3, 4],
    boundary=None,  # Future: ParametricCurve
    unity_principle="Differential",
    unity_strength=0.87,
    pinned=False,
    modified=False,
    surface=None,  # Future: NURBS surface
    constraints_passed=True
)

# Query
num_faces = region.get_face_count()  # 5
contains = region.contains_face(2)   # True
info = region.get_info()  # Human-readable description

# Serialize
data = region.to_dict()
json.dump(data, open('region.json', 'w'))

# Deserialize
loaded = ParametricRegion.from_dict(json.load(open('region.json')))
```

---

### SubDDisplayManager

**File**: `app/geometry/subd_display.py`

**Description**: VTK visualization utilities for SubD surfaces.

```python
from app.geometry.subd_display import SubDDisplayManager
import cpp_core

display = SubDDisplayManager()

# ============================================================
# Create VTK Actors
# ============================================================

# Mesh actor from tessellation
mesh = evaluator.tessellate(3)
mesh_actor = display.create_mesh_actor(mesh)

# Control cage wireframe
cage_actor = display.create_control_cage_actor(cage)

# Colored mesh by region
face_colors = {
    0: (1.0, 0.0, 0.0),
    1: (0.0, 1.0, 0.0),
    2: (0.0, 0.0, 1.0),
}
colored_actor = display.create_colored_mesh_actor(mesh, face_colors)

# ============================================================
# Bounding Box
# ============================================================

bounds = display.compute_bounding_box(mesh)
# bounds = [xmin, xmax, ymin, ymax, zmin, zmax]

center = [
    (bounds[0] + bounds[1]) / 2,
    (bounds[2] + bounds[3]) / 2,
    (bounds[4] + bounds[5]) / 2,
]

size = [
    bounds[1] - bounds[0],
    bounds[3] - bounds[2],
    bounds[5] - bounds[4],
]
```

---

## Rhino Bridge API

### SubDFetcher

**File**: `app/bridge/subd_fetcher.py`

**Description**: Fetch control cage from Grasshopper HTTP server.

```python
from app.bridge.subd_fetcher import SubDFetcher
import cpp_core

fetcher = SubDFetcher(port=8888)

# ============================================================
# Server Status
# ============================================================

# Check if server is available
is_available = fetcher.is_server_available()

# Get connection status
status = fetcher.get_status()
# {'connected': True/False, 'url': 'http://localhost:8888'}

# ============================================================
# Fetch Control Cage
# ============================================================

# Fetch from Grasshopper
cage_data = fetcher.fetch_control_cage()

if cage_data is not None:
    # Convert to C++ SubDControlCage
    cage = cpp_core.SubDControlCage()
    cage.vertices = [
        cpp_core.Point3D(v[0], v[1], v[2])
        for v in cage_data['vertices']
    ]
    cage.faces = cage_data['faces']
    cage.creases = [(c[0], c[1]) for c in cage_data.get('creases', [])]

    # Initialize evaluator
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)

# ============================================================
# Change Detection
# ============================================================

# Check if geometry changed since last fetch
has_changed = fetcher.has_changed()  # Uses SHA hash
```

---

### LiveBridge

**File**: `app/bridge/live_bridge.py`

**Description**: Live sync with Grasshopper using polling.

```python
from app.bridge.live_bridge import LiveBridge

bridge = LiveBridge(port=8888, poll_interval=2.0)

# ============================================================
# Start/Stop Live Sync
# ============================================================

# Connect signals
bridge.geometry_updated.connect(on_geometry_updated)
bridge.connection_status_changed.connect(on_status_changed)

def on_geometry_updated(cage_data):
    print("New geometry received!")
    # Update evaluator, display, etc.

def on_status_changed(connected):
    print(f"Connection: {'Active' if connected else 'Lost'}")

# Start polling
bridge.start()

# Stop polling
bridge.stop()

# ============================================================
# Manual Fetch
# ============================================================

# Fetch once without polling
cage_data = bridge.fetch_once()

# ============================================================
# Status
# ============================================================

status = bridge.get_connection_status()
# {
#   'connected': True/False,
#   'active': True/False,  # Polling active
#   'last_update': datetime,
#   'update_count': int
# }
```

---

## Performance Tips

### 1. Reuse Evaluators When Possible

```python
# ❌ Slow: Create new evaluator every time
for level in [1, 2, 3]:
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)
    mesh = evaluator.tessellate(level)

# ✅ Fast: Reuse evaluator (but create new for different levels due to OpenSubdiv limitation)
# Best: Cache tessellation results
tessellation_cache = {}
for level in [1, 2, 3]:
    if level not in tessellation_cache:
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        tessellation_cache[level] = evaluator.tessellate(level)
```

### 2. Use Batch Evaluation

```python
# ❌ Slow: Loop with individual evaluations
points = []
for face_id, u, v in sample_params:
    point = evaluator.evaluate_limit_point(face_id, u, v)
    points.append([point.x, point.y, point.z])

# ✅ Fast: Batch evaluation (3-5x faster)
face_indices = [p[0] for p in sample_params]
params_u = [p[1] for p in sample_params]
params_v = [p[2] for p in sample_params]

result = evaluator.batch_evaluate_limit(face_indices, params_u, params_v)
points = result.vertices  # NumPy array (N, 3)
```

### 3. Zero-Copy NumPy Arrays

```python
# ✅ Zero-copy: Direct access to C++ memory
vertices = mesh.vertices  # No data copying!

# ✅ Fast NumPy operations
centroid = np.mean(vertices, axis=0)
distances = np.linalg.norm(vertices - centroid, axis=1)
```

### 4. Tessellation Level Selection

```python
# Level 1: ~4x faces (fast, low quality)
# Level 2: ~16x faces (moderate)
# Level 3: ~64x faces (good quality, recommended)
# Level 4: ~256x faces (high quality, slow)
# Level 5: ~1024x faces (very slow, rarely needed)

# For display: use level 3
display_mesh = evaluator.tessellate(3)

# For analysis: use exact evaluation (no tessellation needed)
point = evaluator.evaluate_limit_point(face_id, u, v)
```

---

## Error Handling

```python
import cpp_core

# ============================================================
# Handle uninitialized evaluator
# ============================================================

evaluator = cpp_core.SubDEvaluator()

# Check before using
if not evaluator.is_initialized():
    print("Error: Evaluator not initialized")
    evaluator.initialize(cage)

# ============================================================
# Handle invalid parameters
# ============================================================

try:
    # u, v must be in [0, 1]
    point = evaluator.evaluate_limit_point(face_id=0, u=1.5, v=0.5)
except RuntimeError as e:
    print(f"Invalid parameters: {e}")

try:
    # face_index must be valid
    point = evaluator.evaluate_limit_point(face_id=999, u=0.5, v=0.5)
except RuntimeError as e:
    print(f"Invalid face index: {e}")

# ============================================================
# Handle Grasshopper connection errors
# ============================================================

from app.bridge.subd_fetcher import SubDFetcher

fetcher = SubDFetcher()

if not fetcher.is_server_available():
    print("Grasshopper server not running")
    print("Start server in Grasshopper and try again")
else:
    cage_data = fetcher.fetch_control_cage()
    if cage_data is None:
        print("Failed to fetch geometry")
```

---

## Next Steps

For mathematical lens implementation (Day 4-5), see:
- **Curvature Analysis**: Use `evaluate_limit_with_second_derivatives()`
- **Spectral Decomposition**: Sample limit surface with `batch_evaluate_limit()`
- **Region Discovery**: Build parametric regions with `ParametricRegion`

For complete examples and integration patterns, see:
- `docs/PHASE_0_COMPLETE.md` - Integration guide
- `tests/test_day1_integration.py` - Working examples
- `cpp_core/INTEGRATION.md` - C++ integration details

---

*API Reference v0.5.0*
*Phase 0 Complete - November 9, 2025*
*Ceramic Mold Analyzer Project*
