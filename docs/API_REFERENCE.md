# API Reference

**Ceramic Mold Analyzer - Complete API Documentation**

Version: 1.0
Last Updated: November 2025
Corresponds to: 10-Day API Sprint Completion

---

## Table of Contents

1. [C++ Core API](#c-core-api)
   - [Geometry Types](#geometry-types)
   - [SubD Evaluation](#subd-evaluation)
   - [Curvature Analysis](#curvature-analysis)
   - [NURBS Generation](#nurbs-generation)
   - [Constraint Validation](#constraint-validation)
2. [Python API](#python-api)
   - [State Management](#state-management)
   - [Analysis Lenses](#analysis-lenses)
   - [Export](#export)
   - [Workflow](#workflow)
   - [UI Components](#ui-components)
3. [Usage Examples](#usage-examples)
4. [Cross-References](#cross-references)

---

# C++ Core API

All C++ classes are exposed to Python via the `cpp_core` module using pybind11 bindings with zero-copy numpy integration.

## Geometry Types

### Point3D

3D point with float precision.

**Constructor:**
```python
Point3D()                    # Default: (0, 0, 0)
Point3D(x: float, y: float, z: float)
```

**Attributes:**
- `x: float` - X coordinate
- `y: float` - Y coordinate
- `z: float` - Z coordinate

**Example:**
```python
import cpp_core
p = cpp_core.Point3D(1.0, 2.0, 3.0)
print(p.x, p.y, p.z)  # 1.0 2.0 3.0
```

---

### Vector3

3D vector with float precision and vector operations.

**Constructor:**
```python
Vector3()                    # Default: (0, 0, 0)
Vector3(x: float, y: float, z: float)
Vector3(p: Point3D)         # From Point3D
```

**Methods:**
- `dot(other: Vector3) -> float` - Dot product
- `length() -> float` - Vector magnitude
- `normalized() -> Vector3` - Unit vector in same direction
- `cross(other: Vector3) -> Vector3` - Cross product

**Example:**
```python
v1 = cpp_core.Vector3(1.0, 0.0, 0.0)
v2 = cpp_core.Vector3(0.0, 1.0, 0.0)
cross = v1.cross(v2)  # Vector3(0, 0, 1)
```

---

### SubDControlCage

Subdivision surface control cage representation.

**Constructor:**
```python
SubDControlCage()
```

**Attributes:**
- `vertices: List[Point3D]` - Control vertices
- `faces: List[List[int]]` - Face topology (vertex indices)
- `creases: List[Tuple[int, float]]` - Edge creases (edge_id, sharpness)

**Methods:**
- `vertex_count() -> int` - Number of vertices
- `face_count() -> int` - Number of faces

**Example:**
```python
cage = cpp_core.SubDControlCage()
cage.vertices = [
    cpp_core.Point3D(0, 0, 0),
    cpp_core.Point3D(1, 0, 0),
    cpp_core.Point3D(1, 1, 0),
    cpp_core.Point3D(0, 1, 0)
]
cage.faces = [[0, 1, 2, 3]]  # Single quad face
print(f"Cage: {cage.vertex_count()} vertices, {cage.face_count()} faces")
```

**Related:** [SubDEvaluator](#subdevaluator)

---

### TessellationResult

Result of subdivision surface tessellation for display.

**Constructor:**
```python
TessellationResult()
```

**Properties:**
- `vertices: numpy.ndarray` - Vertex positions (N, 3) zero-copy numpy array
- `normals: numpy.ndarray` - Vertex normals (N, 3) zero-copy numpy array
- `triangles: numpy.ndarray` - Triangle indices (M, 3) zero-copy numpy array
- `face_parents: List[int]` - Parent control face for each triangle

**Methods:**
- `vertex_count() -> int` - Number of vertices
- `triangle_count() -> int` - Number of triangles

**Example:**
```python
mesh = evaluator.tessellate(subdivision_level=3)
import numpy as np
vertices = np.array(mesh.vertices)  # Zero-copy view
print(f"Mesh: {mesh.vertex_count()} vertices, {mesh.triangle_count()} triangles")
```

**Related:** [SubDEvaluator.tessellate()](#tessellate)

---

## SubD Evaluation

### SubDEvaluator

Evaluates exact limit surface of SubD control cage using OpenSubdiv.

**Purpose:** Provides exact limit surface evaluation using Stam's eigenanalysis. Supports both tessellation for display and parametric point evaluation for analysis.

**Constructor:**
```python
SubDEvaluator()
```

**Initialization:**

#### initialize()

Build subdivision topology from control cage.

```python
initialize(cage: SubDControlCage) -> None
```

**Parameters:**
- `cage: SubDControlCage` - Control cage with vertices, faces, and creases

**Raises:**
- `ValueError` - If cage is invalid or empty
- `RuntimeError` - If initialization fails

**Example:**
```python
evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)
assert evaluator.is_initialized()
```

---

#### is_initialized()

Check if evaluator has been initialized.

```python
is_initialized() -> bool
```

**Returns:** `True` if initialized with a control cage

---

### Surface Tessellation

#### tessellate()

Tessellate subdivided surface into triangles for display.

```python
tessellate(subdivision_level: int = 3, adaptive: bool = False) -> TessellationResult
```

**Parameters:**
- `subdivision_level: int` - Number of subdivision iterations (0-6, default 3)
- `adaptive: bool` - Use adaptive subdivision (default False)

**Returns:** `TessellationResult` with triangulated mesh

**Example:**
```python
mesh = evaluator.tessellate(subdivision_level=4)
vertices = mesh.vertices  # numpy array (N, 3)
triangles = mesh.triangles  # numpy array (M, 3)
```

**Related:** [TessellationResult](#tessellationresult)

---

### Point Evaluation

#### evaluate_limit_point()

Evaluate exact point on limit surface.

```python
evaluate_limit_point(face_index: int, u: float, v: float) -> Point3D
```

**Parameters:**
- `face_index: int` - Control face index
- `u: float` - Parametric coordinate (0-1)
- `v: float` - Parametric coordinate (0-1)

**Returns:** `Point3D` on limit surface

**Raises:**
- `RuntimeError` - If evaluator not initialized
- `ValueError` - If parameters out of range [0,1]

**Example:**
```python
pt = evaluator.evaluate_limit_point(face_index=0, u=0.5, v=0.5)
print(f"Limit point: ({pt.x}, {pt.y}, {pt.z})")
```

---

#### evaluate_limit()

Evaluate point and normal on limit surface.

```python
evaluate_limit(face_index: int, u: float, v: float) -> Tuple[Point3D, Point3D]
```

**Parameters:**
- `face_index: int` - Control face index
- `u: float` - Parametric coordinate (0-1)
- `v: float` - Parametric coordinate (0-1)

**Returns:** `(point, normal)` - Point and unit normal at that point

**Example:**
```python
point, normal = evaluator.evaluate_limit(0, 0.5, 0.5)
```

---

### Derivative Evaluation

#### evaluate_limit_with_derivatives()

Evaluate limit position and first derivatives.

```python
evaluate_limit_with_derivatives(face_index: int, u: float, v: float)
    -> Tuple[Point3D, Point3D, Point3D]
```

**Parameters:**
- `face_index: int` - Control face index
- `u: float` - Parameter u in [0,1]
- `v: float` - Parameter v in [0,1]

**Returns:** `(position, du, dv)` - Position and first derivatives

**Example:**
```python
pos, du, dv = evaluator.evaluate_limit_with_derivatives(0, 0.5, 0.5)
# du, dv are tangent vectors in u and v directions
```

**Related:** [CurvatureAnalyzer](#curvatureanalyzer)

---

#### evaluate_limit_with_second_derivatives()

Evaluate limit position with first and second derivatives.

```python
evaluate_limit_with_second_derivatives(face_index: int, u: float, v: float)
    -> Tuple[Point3D, Point3D, Point3D, Point3D, Point3D, Point3D]
```

**Parameters:**
- `face_index: int` - Control face index
- `u: float` - Parameter u in [0,1]
- `v: float` - Parameter v in [0,1]

**Returns:** `(pos, du, dv, duu, dvv, duv)` - Position and all derivatives

**Example:**
```python
pos, du, dv, duu, dvv, duv = evaluator.evaluate_limit_with_second_derivatives(0, 0.5, 0.5)
# Second derivatives enable curvature computation
```

**Related:** [CurvatureAnalyzer.compute_curvature()](#compute_curvature)

---

#### compute_tangent_frame()

Compute tangent frame (tangent_u, tangent_v, normal).

```python
compute_tangent_frame(face_index: int, u: float, v: float)
    -> Tuple[Point3D, Point3D, Point3D]
```

**Parameters:**
- `face_index: int` - Control face index
- `u: float` - Parametric coordinate (0-1)
- `v: float` - Parametric coordinate (0-1)

**Returns:** `(tangent_u, tangent_v, normal)` - Normalized vectors forming orthogonal frame

**Example:**
```python
tu, tv, n = evaluator.compute_tangent_frame(0, 0.5, 0.5)
# Forms right-handed coordinate system
```

---

### Batch Evaluation

#### batch_evaluate_limit()

Batch evaluate multiple points on limit surface.

```python
batch_evaluate_limit(face_indices: List[int],
                    params_u: List[float],
                    params_v: List[float]) -> TessellationResult
```

**Parameters:**
- `face_indices: List[int]` - Face index for each point
- `params_u: List[float]` - U parameters for each point
- `params_v: List[float]` - V parameters for each point

**Returns:** `TessellationResult` with evaluated points and normals

**Note:** More efficient than individual calls for large point sets.

**Example:**
```python
faces = [0, 0, 0, 1, 1, 1]
u_vals = [0.0, 0.5, 1.0, 0.0, 0.5, 1.0]
v_vals = [0.0, 0.5, 1.0, 0.0, 0.5, 1.0]
result = evaluator.batch_evaluate_limit(faces, u_vals, v_vals)
```

---

### Topology Queries

#### get_parent_face()

Get parent control face for a tessellated triangle.

```python
get_parent_face(triangle_index: int) -> int
```

**Parameters:**
- `triangle_index: int` - Index into tessellation result triangles

**Returns:** Index of parent control face, or -1 if invalid

---

#### get_control_vertex_count()

Get number of vertices in control cage.

```python
get_control_vertex_count() -> int
```

**Returns:** Vertex count

---

#### get_control_face_count()

Get number of faces in control cage.

```python
get_control_face_count() -> int
```

**Returns:** Face count

---

## Curvature Analysis

### CurvatureResult

Result of curvature analysis at a point on the surface.

**Constructor:**
```python
CurvatureResult()
```

**Principal Curvatures:**
- `kappa1: float` - Maximum principal curvature
- `kappa2: float` - Minimum principal curvature

**Principal Directions:**
- `dir1: Point3D` - Direction of maximum curvature
- `dir2: Point3D` - Direction of minimum curvature

**Derived Curvatures:**
- `gaussian_curvature: float` - Gaussian curvature (K = κ₁ × κ₂)
- `mean_curvature: float` - Mean curvature (H = (κ₁ + κ₂) / 2)
- `abs_mean_curvature: float` - Absolute mean curvature |H|
- `rms_curvature: float` - RMS curvature √((κ₁² + κ₂²) / 2)

**Fundamental Forms:**
- `E, F, G: float` - First fundamental form coefficients
- `L, M, N: float` - Second fundamental form coefficients

**Surface Normal:**
- `normal: Point3D` - Unit surface normal at evaluation point

**Example:**
```python
result = curvature_analyzer.compute_curvature(evaluator, face_id=0, u=0.5, v=0.5)
print(f"Gaussian: {result.gaussian_curvature}")
print(f"Mean: {result.mean_curvature}")
print(f"Principal: k1={result.kappa1}, k2={result.kappa2}")
```

**Related:** [CurvatureAnalyzer](#curvatureanalyzer)

---

### CurvatureAnalyzer

Curvature analyzer for SubD limit surfaces.

**Purpose:** Computes differential geometry quantities using exact second derivatives from SubD limit surface evaluation. Implements standard differential geometry formulas based on first and second fundamental forms.

**Mathematical Reference:** do Carmo, "Differential Geometry of Curves and Surfaces"

**Constructor:**
```python
CurvatureAnalyzer()
```

---

#### compute_curvature()

Compute all curvature quantities at a point on the surface.

```python
compute_curvature(evaluator: SubDEvaluator,
                 face_index: int,
                 u: float,
                 v: float) -> CurvatureResult
```

**Parameters:**
- `evaluator: SubDEvaluator` - Initialized SubD evaluator
- `face_index: int` - Control face index
- `u: float` - Parametric coordinate in [0,1]
- `v: float` - Parametric coordinate in [0,1]

**Returns:** `CurvatureResult` with all curvature data

**Computes:**
- First and second fundamental forms
- Shape operator and its eigendecomposition
- Principal curvatures and directions
- Gaussian and mean curvatures

**Example:**
```python
evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

analyzer = cpp_core.CurvatureAnalyzer()
result = analyzer.compute_curvature(evaluator, face_index=0, u=0.5, v=0.5)

print(f"Gaussian curvature: {result.gaussian_curvature}")
print(f"Mean curvature: {result.mean_curvature}")
print(f"Principal curvatures: k1={result.kappa1}, k2={result.kappa2}")
```

**Related:** [SubDEvaluator.evaluate_limit_with_second_derivatives()](#evaluate_limit_with_second_derivatives)

---

#### batch_compute_curvature()

Batch compute curvature at multiple points.

```python
batch_compute_curvature(evaluator: SubDEvaluator,
                       face_indices: List[int],
                       params_u: List[float],
                       params_v: List[float]) -> List[CurvatureResult]
```

**Parameters:**
- `evaluator: SubDEvaluator` - Initialized SubD evaluator
- `face_indices: List[int]` - Face index for each point
- `params_u: List[float]` - U parameters for each point
- `params_v: List[float]` - V parameters for each point

**Returns:** List of `CurvatureResult` for each point

**Note:** More efficient than individual calls for large numbers of points.

**Example:**
```python
analyzer = cpp_core.CurvatureAnalyzer()
results = analyzer.batch_compute_curvature(
    evaluator,
    face_indices=[0, 0, 0],
    params_u=[0.25, 0.5, 0.75],
    params_v=[0.5, 0.5, 0.5]
)
```

---

## NURBS Generation

### NURBSMoldGenerator

NURBS mold generator from exact SubD limit surface.

**Purpose:** Samples exact limit surface and fits NURBS, applies draft transformation, creates solid mold cavities.

**Constructor:**
```python
NURBSMoldGenerator(evaluator: SubDEvaluator)
```

**Parameters:**
- `evaluator: SubDEvaluator` - Initialized SubD evaluator

---

#### fit_nurbs_surface()

Sample exact limit surface and fit NURBS.

```python
fit_nurbs_surface(face_indices: List[int],
                 sample_density: int = 50) -> Handle(Geom_BSplineSurface)
```

**Parameters:**
- `face_indices: List[int]` - SubD faces to sample
- `sample_density: int` - Samples per face dimension (default 50)

**Returns:** OpenCASCADE B-spline surface handle

**Example:**
```python
gen = cpp_core.NURBSMoldGenerator(evaluator)
nurbs = gen.fit_nurbs_surface(face_indices=[0, 1, 2], sample_density=50)
```

**Related:** [check_fitting_quality()](#check_fitting_quality)

---

#### apply_draft_angle()

Apply draft angle transformation to NURBS surface.

```python
apply_draft_angle(surface: Handle(Geom_BSplineSurface),
                 demolding_direction: Vector3,
                 draft_angle_degrees: float,
                 parting_line: List[Point3D]) -> Handle(Geom_BSplineSurface)
```

**Parameters:**
- `surface` - Input NURBS surface
- `demolding_direction: Vector3` - Direction of mold removal
- `draft_angle_degrees: float` - Draft angle in degrees (typically 0.5-5°)
- `parting_line: List[Point3D]` - Fixed base curve (no transformation)

**Returns:** Transformed NURBS surface with draft applied

**Example:**
```python
demold_dir = cpp_core.Vector3(0, 0, 1)  # Pull upward
draft_nurbs = gen.apply_draft_angle(
    nurbs,
    demolding_direction=demold_dir,
    draft_angle_degrees=2.0,
    parting_line=parting_curve_points
)
```

---

#### create_mold_solid()

Create solid mold cavity from NURBS surface.

```python
create_mold_solid(surface: Handle(Geom_BSplineSurface),
                 wall_thickness: float = 40.0) -> TopoDS_Shape
```

**Parameters:**
- `surface` - NURBS surface
- `wall_thickness: float` - Wall thickness in mm (default 40.0)

**Returns:** OpenCASCADE solid shape

---

#### add_registration_keys()

Add registration features (keys/notches) to mold.

```python
add_registration_keys(mold: TopoDS_Shape,
                     key_positions: List[Point3D]) -> TopoDS_Shape
```

**Parameters:**
- `mold: TopoDS_Shape` - Input mold solid
- `key_positions: List[Point3D]` - Positions for registration keys

**Returns:** Mold with registration features

---

### FittingQuality

Quality control for NURBS fitting.

**Structure:**
```python
class FittingQuality:
    max_deviation: float      # Maximum deviation in mm
    mean_deviation: float     # Mean deviation in mm
    rms_deviation: float      # RMS deviation in mm
    num_samples: int          # Number of sample points
    passes_tolerance: bool    # True if max_deviation < 0.1mm
```

---

#### check_fitting_quality()

Check NURBS fitting quality against original limit surface.

```python
check_fitting_quality(nurbs: Handle(Geom_BSplineSurface),
                     face_indices: List[int]) -> FittingQuality
```

**Parameters:**
- `nurbs` - Fitted NURBS surface
- `face_indices: List[int]` - Original SubD faces

**Returns:** `FittingQuality` with deviation statistics

**Example:**
```python
quality = gen.check_fitting_quality(nurbs, face_indices=[0, 1, 2])
if quality.passes_tolerance:
    print(f"Excellent fit: max deviation {quality.max_deviation:.3f}mm")
else:
    print(f"Warning: max deviation {quality.max_deviation:.3f}mm exceeds 0.1mm")
```

---

## Constraint Validation

### ConstraintLevel

Constraint severity levels.

```python
class ConstraintLevel(Enum):
    ERROR    # Physical impossibility - must fix
    WARNING  # Manufacturing challenge - negotiable
    FEATURE  # Mathematical tension - aesthetic feature
```

---

### ConstraintViolation

Single constraint violation report.

**Structure:**
```python
class ConstraintViolation:
    level: ConstraintLevel
    description: str
    face_id: int              # Which face violates
    severity: float           # 0.0-1.0 magnitude
    suggestion: str           # How to fix
```

---

### ConstraintReport

Complete constraint report for a region.

**Methods:**

```python
add_error(description: str, face_id: int, severity: float) -> None
add_warning(description: str, face_id: int, severity: float) -> None
add_feature(description: str, face_id: int) -> None

has_errors() -> bool
has_warnings() -> bool
error_count() -> int
warning_count() -> int
```

**Attributes:**
- `violations: List[ConstraintViolation]` - All violations

**Example:**
```python
report = validator.validate_region(face_indices, demold_dir)
if report.has_errors():
    for v in report.violations:
        if v.level == cpp_core.ConstraintLevel.ERROR:
            print(f"ERROR on face {v.face_id}: {v.description}")
```

---

### UndercutDetector

Detect undercuts along demolding direction.

**Constructor:**
```python
UndercutDetector(evaluator: SubDEvaluator)
```

---

#### detect_undercuts()

Detect undercuts for all faces in region.

```python
detect_undercuts(face_indices: List[int],
                demolding_direction: Vector3) -> Dict[int, float]
```

**Parameters:**
- `face_indices: List[int]` - Faces to check
- `demolding_direction: Vector3` - Direction of mold removal

**Returns:** Dictionary mapping face_id to undercut severity (0.0-1.0)

---

#### check_face_undercut()

Check single face for undercut.

```python
check_face_undercut(face_id: int,
                   demolding_direction: Vector3) -> float
```

**Returns:** Undercut severity (0.0 = none, 1.0 = severe)

---

### DraftChecker

Draft angle checker for manufacturability.

**Constructor:**
```python
DraftChecker(evaluator: SubDEvaluator)
```

**Constants:**
- `MIN_DRAFT_ANGLE = 0.5` degrees (absolute minimum)
- `RECOMMENDED_DRAFT_ANGLE = 2.0` degrees (recommended)

---

#### compute_draft_angles()

Compute draft angles for all faces.

```python
compute_draft_angles(face_indices: List[int],
                    demolding_direction: Vector3) -> Dict[int, float]
```

**Parameters:**
- `face_indices: List[int]` - Faces to check
- `demolding_direction: Vector3` - Direction of mold removal

**Returns:** Dictionary mapping face_id to draft angle in degrees

---

#### check_face_draft()

Check single face draft angle.

```python
check_face_draft(face_id: int,
                demolding_direction: Vector3) -> float
```

**Returns:** Draft angle in degrees

**Example:**
```python
checker = cpp_core.DraftChecker(evaluator)
draft = checker.check_face_draft(0, cpp_core.Vector3(0, 0, 1))
if draft < cpp_core.DraftChecker.MIN_DRAFT_ANGLE:
    print(f"Insufficient draft: {draft:.2f}° < {cpp_core.DraftChecker.MIN_DRAFT_ANGLE}°")
```

---

### ConstraintValidator

Complete constraint validator for regions.

**Constructor:**
```python
ConstraintValidator(evaluator: SubDEvaluator)
```

---

#### validate_region()

Validate complete region against all constraints.

```python
validate_region(face_indices: List[int],
               demolding_direction: Vector3,
               min_wall_thickness: float = 3.0) -> ConstraintReport
```

**Parameters:**
- `face_indices: List[int]` - Faces in region
- `demolding_direction: Vector3` - Direction of mold removal
- `min_wall_thickness: float` - Minimum wall thickness in mm (default 3.0)

**Returns:** `ConstraintReport` with all violations

**Example:**
```python
validator = cpp_core.ConstraintValidator(evaluator)
demold_dir = cpp_core.Vector3(0, 0, 1)
report = validator.validate_region(
    face_indices=[0, 1, 2, 3],
    demolding_direction=demold_dir,
    min_wall_thickness=3.0
)

print(f"Errors: {report.error_count()}, Warnings: {report.warning_count()}")
for violation in report.violations:
    print(f"{violation.level}: {violation.description}")
```

---

# Python API

## State Management

### ApplicationState

Central state manager for the application.

**Purpose:** Manages all application state including SubD geometry, regions, edit mode, selection, and undo/redo history.

**Signals:**
- `state_changed` - Emitted when any state changes
- `regions_updated(list)` - Emitted when regions change
- `region_pinned(str, bool)` - Emitted when region pin state changes
- `history_changed` - Emitted when undo/redo history changes
- `edit_mode_changed(object)` - Emitted when edit mode changes
- `selection_changed(object)` - Emitted when selection changes
- `iteration_changed(str)` - Emitted when iteration changes

**Constructor:**
```python
ApplicationState()
```

**Attributes:**
- `subd_geometry` - Current SubD geometry
- `regions: List[ParametricRegion]` - Discovered regions
- `selected_region_id: Optional[str]` - Currently selected region
- `current_lens: str` - Active mathematical lens
- `edit_mode_manager: EditModeManager` - Edit mode state
- `iteration_manager: IterationManager` - Iteration state
- `history: List[HistoryItem]` - Undo/redo history

---

#### set_subd_geometry()

Set the SubD geometry from Rhino.

```python
set_subd_geometry(geometry) -> None
```

**Example:**
```python
state = ApplicationState()
state.set_subd_geometry(geometry)
```

---

#### get_current_geometry()

Get the current SubD geometry.

```python
get_current_geometry() -> Any
```

---

#### add_region()

Add a discovered region.

```python
add_region(region: ParametricRegion) -> None
```

---

#### set_regions()

Set all regions at once (typically after lens analysis).

```python
set_regions(regions: List[ParametricRegion]) -> None
```

**Example:**
```python
regions = lens.discover_regions()
state.set_regions(regions)
```

---

#### get_region()

Get a region by ID.

```python
get_region(region_id: str) -> Optional[ParametricRegion]
```

---

#### set_region_pinned()

Set the pinned state of a region.

```python
set_region_pinned(region_id: str, pinned: bool) -> None
```

**Note:** Automatically adds to undo/redo history and emits signals.

**Example:**
```python
state.set_region_pinned("region_0", True)  # Pin region
```

---

#### get_pinned_regions()

Get all pinned regions.

```python
get_pinned_regions() -> List[ParametricRegion]
```

---

#### get_unpinned_regions()

Get all unpinned regions.

```python
get_unpinned_regions() -> List[ParametricRegion]
```

---

#### get_unpinned_faces()

Get all face indices not in pinned regions.

```python
get_unpinned_faces() -> List[int]
```

---

#### get_pinned_face_indices()

Get all face indices in pinned regions.

```python
get_pinned_face_indices() -> List[int]
```

---

#### undo() / redo()

Undo or redo last action.

```python
undo() -> None
redo() -> None
can_undo() -> bool
can_redo() -> bool
```

**Example:**
```python
state.set_region_pinned("region_0", True)
state.undo()  # Unpins the region
state.redo()  # Re-pins the region
```

---

### ParametricRegion

A region defined in parameter space (face_id, u, v).

**Purpose:** Represents a collection of SubD faces that form a coherent region based on mathematical analysis. Maintains exact mathematical representation until fabrication.

**Constructor:**
```python
ParametricRegion(
    id: str,
    faces: List[int],
    boundary: List[ParametricCurve] = [],
    unity_principle: str = "",
    unity_strength: float = 0.0,
    pinned: bool = False,
    metadata: Dict[str, Any] = {}
)
```

**Attributes:**
- `id: str` - Unique identifier
- `faces: List[int]` - SubD face indices
- `boundary: List[ParametricCurve]` - Boundary curves in (face_id, u, v) space
- `unity_principle: str` - What unifies this region (mathematical lens)
- `unity_strength: float` - Resonance score [0.0, 1.0]
- `pinned: bool` - Preserved across re-analysis
- `metadata: Dict[str, Any]` - Lens-specific data

**Methods:**

```python
to_dict() -> Dict[str, Any]  # Serialize to dict
to_json() -> str              # Serialize to JSON string

@classmethod
from_dict(data: Dict) -> ParametricRegion
from_json(json_str: str) -> ParametricRegion
```

**Example:**
```python
from app.state.parametric_region import ParametricRegion

region = ParametricRegion(
    id="region_0",
    faces=[0, 1, 2, 3],
    unity_principle="Curvature coherence",
    unity_strength=0.87,
    pinned=True
)
```

---

### ParametricCurve

A curve defined in surface parameter space (face_id, u, v).

**Purpose:** Maintains exact mathematical representation of region boundaries. NOT in 3D coordinates.

**Constructor:**
```python
ParametricCurve(
    points: List[Tuple[int, float, float]] = [],
    is_closed: bool = False
)
```

**Attributes:**
- `points: List[Tuple[int, float, float]]` - Points as (face_id, u, v)
- `is_closed: bool` - Whether curve forms a closed loop
- `length_parameter: Optional[float]` - Parametric length
- `curvature_integral: Optional[float]` - Integrated curvature

**Methods:**

```python
evaluate(t: float) -> Tuple[int, float, float]  # Evaluate at parameter t ∈ [0,1]
to_json() -> Dict[str, Any]
from_json(data: Dict) -> ParametricCurve
```

**Example:**
```python
from app.state.parametric_region import ParametricCurve

curve = ParametricCurve(
    points=[(0, 0.0, 0.5), (0, 0.5, 0.5), (0, 1.0, 0.5)],
    is_closed=False
)
face_id, u, v = curve.evaluate(0.5)  # Midpoint
```

---

### IterationManager

Manages design iterations with snapshots.

**Purpose:** Tracks different design iterations, allowing comparison and rollback.

**Constructor:**
```python
IterationManager()
```

**Methods:**

```python
create_iteration(name: str, regions: List[ParametricRegion]) -> str
get_iteration(iteration_id: str) -> Optional[Iteration]
get_all_iterations() -> List[Iteration]
set_current_iteration(iteration_id: str) -> None
get_current_iteration() -> Optional[Iteration]
```

**Example:**
```python
iter_mgr = state.iteration_manager
iter_id = iter_mgr.create_iteration("Differential Analysis v1", regions)
iter_mgr.set_current_iteration(iter_id)
```

---

## Analysis Lenses

### LensManager

Unified interface for all mathematical lenses.

**Purpose:** Manages lens selection, analysis, and result comparison. Coordinates multiple mathematical analysis approaches.

**Constructor:**
```python
LensManager(evaluator: cpp_core.SubDEvaluator)
```

**Attributes:**
- `evaluator: SubDEvaluator` - SubD evaluator
- `lenses: Dict[LensType, Lens]` - Available lenses
- `current_lens: Optional[LensType]` - Currently selected lens
- `analysis_results: Dict[LensType, List[ParametricRegion]]` - Cached results

---

#### analyze_with_lens()

Analyze surface using specified lens.

```python
analyze_with_lens(
    lens_type: LensType,
    params: Optional[Dict[str, Any]] = None,
    force_recompute: bool = False
) -> List[ParametricRegion]
```

**Parameters:**
- `lens_type: LensType` - Which lens to use (DIFFERENTIAL, SPECTRAL, etc.)
- `params: Dict` - Lens-specific parameters
- `force_recompute: bool` - Ignore cached results

**Returns:** List of discovered `ParametricRegion` objects

**Example:**
```python
from app.analysis.lens_manager import LensManager, LensType

lens_mgr = LensManager(evaluator)

# Differential analysis
diff_regions = lens_mgr.analyze_with_lens(
    LensType.DIFFERENTIAL,
    params={'curvature_tolerance': 0.3}
)

# Spectral analysis
spec_regions = lens_mgr.analyze_with_lens(
    LensType.SPECTRAL,
    params={'num_modes': 10}
)
```

**Related:** [DifferentialLens](#differentiallens), [SpectralLens](#spectrallens)

---

#### get_available_lenses()

Get list of available lenses.

```python
get_available_lenses() -> List[LensType]
```

---

#### compare_results()

Compare results from different lenses.

```python
compare_results() -> Dict[LensType, float]
```

**Returns:** Dictionary mapping lens type to resonance score

---

### LensType

Available mathematical lenses.

```python
class LensType(Enum):
    DIFFERENTIAL = "differential"  # Curvature-based
    SPECTRAL = "spectral"          # Eigenfunction-based
    FLOW = "flow"                  # Future
    MORSE = "morse"                # Future
    THERMAL = "thermal"            # Future
```

---

### DifferentialLens

First mathematical lens: Differential Geometry decomposition.

**Purpose:** Discovers regions by analyzing curvature coherence on the exact SubD limit surface using C++ CurvatureAnalyzer with exact second derivatives.

**Mathematical Basis:**
- Principal curvatures κ₁, κ₂ from exact second derivatives
- Ridge lines: local maxima of |κ₁|
- Valley lines: local minima of |κ₁|
- Region classification: sign of mean curvature H (convex/concave)
- Region boundaries: thresholds on |H|

**Constructor:**
```python
DifferentialLens(
    evaluator: cpp_core.SubDEvaluator,
    params: Optional[DifferentialLensParams] = None
)
```

---

#### discover_regions()

Discover regions based on curvature coherence.

```python
discover_regions() -> List[ParametricRegion]
```

**Returns:** List of regions with curvature-based unity

**Example:**
```python
from app.analysis.differential_lens import DifferentialLens, DifferentialLensParams

params = DifferentialLensParams(
    samples_per_face=9,
    mean_curvature_threshold=0.01,
    curvature_tolerance=0.3,
    min_region_size=3
)

lens = DifferentialLens(evaluator, params)
regions = lens.discover_regions()

for r in regions:
    print(f"Region {r.id}: {len(r.faces)} faces, strength={r.unity_strength:.2f}")
```

**Related:** [CurvatureAnalyzer](#curvatureanalyzer)

---

### DifferentialLensParams

Parameters for differential geometry lens.

```python
class DifferentialLensParams:
    samples_per_face: int = 9          # Sample 3x3 grid per face
    mean_curvature_threshold: float = 0.01
    gaussian_threshold: float = 0.01
    curvature_tolerance: float = 0.3    # Relative tolerance
    min_region_size: int = 3            # Minimum faces per region
    detect_ridges: bool = True
    detect_valleys: bool = True
    ridge_percentile: float = 90.0      # Top 10% of |κ₁|
    valley_percentile: float = 10.0     # Bottom 10% of |κ₁|
```

---

### SpectralLens

Mathematical lens using spectral (eigenfunction) analysis.

**Purpose:** Reveals the surface's natural vibration modes through eigenfunction analysis of the Laplace-Beltrami operator.

**Mathematical Basis:**
- Eigenfunctions of Laplace-Beltrami operator
- Zero-crossings (nodal lines) create natural boundaries
- Different eigenmodes reveal different structural patterns
- Forms orthogonal basis for analyzing surface geometry

**Constructor:**
```python
SpectralLens(evaluator: cpp_core.SubDEvaluator)
```

---

#### analyze()

Discover regions using spectral analysis.

```python
analyze(
    num_modes: int = 10,
    mode_indices: List[int] = None
) -> List[ParametricRegion]
```

**Parameters:**
- `num_modes: int` - Number of eigenmodes to compute (default 10)
- `mode_indices: List[int]` - Which modes to use (default [1,2,3])

**Returns:** List of discovered `ParametricRegion` objects

**Example:**
```python
from app.analysis.spectral_lens import SpectralLens

lens = SpectralLens(evaluator)
regions = lens.analyze(num_modes=10, mode_indices=[1, 2, 3])
```

**Related:** [SpectralDecomposer](#spectraldecomposer)

---

#### get_eigenmode()

Get specific eigenmode for visualization.

```python
get_eigenmode(index: int) -> EigenMode
```

**Raises:** `ValueError` if `analyze()` not called first

---

### SpectralDecomposer

Discover regions using Laplace-Beltrami eigenfunction analysis.

**Constructor:**
```python
SpectralDecomposer(evaluator: cpp_core.SubDEvaluator)
```

---

#### compute_eigenmodes()

Compute first k eigenmodes of Laplace-Beltrami operator.

```python
compute_eigenmodes(
    num_modes: int = 10,
    tessellation_level: int = 3
) -> List[EigenMode]
```

**Parameters:**
- `num_modes: int` - Number of eigenmodes to compute
- `tessellation_level: int` - Subdivision level for sampling

**Returns:** List of `EigenMode` objects sorted by eigenvalue

**Example:**
```python
from app.analysis.spectral_decomposition import SpectralDecomposer

decomposer = SpectralDecomposer(evaluator)
modes = decomposer.compute_eigenmodes(num_modes=10)

for mode in modes:
    print(f"Mode {mode.index}: λ={mode.eigenvalue:.4f}")
```

---

#### extract_nodal_domains()

Extract regions from eigenmode zero-crossings.

```python
extract_nodal_domains(
    mode_index: int,
    positive_only: bool = False
) -> List[ParametricRegion]
```

**Parameters:**
- `mode_index: int` - Which eigenmode to analyze
- `positive_only: bool` - Only return positive nodal domains

**Returns:** List of regions defined by nodal lines

---

#### compute_resonance_score()

Compute resonance score for region set.

```python
compute_resonance_score(regions: List[ParametricRegion]) -> float
```

**Returns:** Resonance score [0.0, 1.0] indicating decomposition quality

---

### EigenMode

Single eigenmode of the Laplacian.

```python
class EigenMode:
    eigenvalue: float
    eigenfunction: np.ndarray  # Per-vertex values
    index: int                 # Mode number (0-indexed)
    multiplicity: int = 1      # Eigenvalue multiplicity
```

---

## Export

### NURBSSerializer

Extract NURBS data from OpenCASCADE and serialize for Rhino.

**Purpose:** Maintains exact mathematical representation during transfer to Rhino.

**Constructor:**
```python
NURBSSerializer()
```

---

#### serialize_surface()

Extract NURBS data from OpenCASCADE surface.

```python
serialize_surface(
    occt_surface,  # Handle(Geom_BSplineSurface)
    name: str = "mold",
    region_id: int = -1
) -> RhinoNURBSSurface
```

**Parameters:**
- `occt_surface` - OpenCASCADE B-spline surface handle
- `name: str` - Surface identifier
- `region_id: int` - Associated region ID

**Returns:** `RhinoNURBSSurface` ready for JSON export

**Example:**
```python
from app.export.nurbs_serializer import NURBSSerializer

serializer = NURBSSerializer()
nurbs_data = serializer.serialize_surface(
    occt_surface,
    name="mold_piece_0",
    region_id=0
)
json_data = nurbs_data.to_dict()
```

---

### RhinoNURBSSurface

Rhino-compatible NURBS surface representation.

**Structure:**
```python
class RhinoNURBSSurface:
    degree_u: int
    degree_v: int
    control_points: List[Tuple[float, float, float]]
    weights: List[float]
    count_u: int
    count_v: int
    knots_u: List[float]
    knots_v: List[float]
    name: str = ""
    region_id: int = -1
    draft_angle: float = 0.0
```

**Methods:**
```python
to_dict() -> Dict  # Convert to JSON-serializable dict
```

---

## Workflow

### MoldWorkflow

Orchestrate end-to-end mold generation workflow.

**Purpose:** Complete workflow from region analysis through NURBS generation to Rhino export.

**Steps:**
1. Validate regions (constraints)
2. Generate NURBS from exact limit surface
3. Apply draft transformation
4. Create solid mold cavities
5. Serialize for Rhino export

**Constructor:**
```python
MoldWorkflow(evaluator: cpp_core.SubDEvaluator)
```

**Raises:**
- `RuntimeError` - If cpp_core not available or evaluator not initialized

---

#### generate_molds()

Generate complete mold set from regions.

```python
generate_molds(
    regions: List[ParametricRegion],
    params: MoldParameters
) -> MoldGenerationResult
```

**Parameters:**
- `regions: List[ParametricRegion]` - Regions to convert to molds
- `params: MoldParameters` - Mold generation parameters

**Returns:** `MoldGenerationResult` with NURBS surfaces and export data

**Example:**
```python
from app.workflow.mold_generator import MoldWorkflow
from app.ui.mold_params_dialog import MoldParameters

workflow = MoldWorkflow(evaluator)

params = MoldParameters(
    draft_angle=2.0,
    wall_thickness=40.0,
    demolding_direction=(0, 0, 1)
)

result = workflow.generate_molds(pinned_regions, params)

if result.success:
    print(f"Generated {len(result.nurbs_surfaces)} molds")
    # Export to Rhino
    export_json = result.export_data
else:
    print(f"Failed: {result.error_message}")
```

**Related:** [NURBSMoldGenerator](#nurbsmoldgenerator), [ConstraintValidator](#constraintvalidator)

---

### MoldGenerationResult

Complete mold generation result.

```python
class MoldGenerationResult:
    success: bool
    nurbs_surfaces: List              # OpenCASCADE surfaces
    constraint_reports: List          # Validation results
    export_data: Dict                 # Serialized for Rhino
    error_message: str = ""
```

---

### MoldParameters

Mold generation parameters.

```python
class MoldParameters:
    draft_angle: float = 2.0                  # Degrees
    wall_thickness: float = 40.0              # mm
    demolding_direction: Tuple[float, float, float] = (0, 0, 1)
    min_wall_thickness: float = 3.0           # mm
    add_registration_keys: bool = True
    registration_key_size: float = 10.0       # mm
```

---

## UI Components

### SubDViewport

Specialized viewport for SubD visualization with VTK.

**Purpose:** 3D viewport with Rhino-compatible camera controls, multiple display modes, and selection highlighting.

**Features:**
- Rhino-compatible camera controls
- Multiple display modes (solid/wireframe/shaded_wireframe/points)
- Selection highlighting
- Performance optimization

**Constructor:**
```python
SubDViewport(view_name: str = "Perspective")
```

**Signals:**
- `element_selected(int)` - Emitted when face/edge/vertex selected
- `view_changed(str)` - Emitted when view changes

**Methods:**

```python
set_geometry(evaluator: SubDEvaluator) -> None
set_display_mode(mode: str) -> None  # "solid", "wireframe", "points"
show_control_cage(show: bool) -> None
reset_camera() -> None
```

**Example:**
```python
from app.ui.subd_viewport import SubDViewport

viewport = SubDViewport("Perspective")
viewport.set_geometry(evaluator)
viewport.set_display_mode("solid")
```

---

### AnalysisPanel

Panel for mathematical lens analysis controls.

**Constructor:**
```python
AnalysisPanel(state: ApplicationState)
```

**Signals:**
- `analyze_requested(str)` - Emitted when user requests analysis with lens name

**Methods:**

```python
set_lens_manager(lens_mgr: LensManager) -> None
update_results(regions: List[ParametricRegion]) -> None
```

---

### RegionListWidget

Widget displaying discovered regions with pin controls.

**Constructor:**
```python
RegionListWidget(state: ApplicationState)
```

**Methods:**

```python
update_regions(regions: List[ParametricRegion]) -> None
set_selected_region(region_id: str) -> None
```

---

### ProgressDialog

Progress dialog for long-running operations.

**Constructor:**
```python
ProgressDialog(title: str, parent: QWidget = None)
```

**Methods:**

```python
set_progress(value: int, message: str = "") -> None
set_max(max_value: int) -> None
is_cancelled() -> bool
```

**Example:**
```python
from app.ui.progress_dialog import ProgressDialog

progress = ProgressDialog("Generating molds...")
progress.set_max(len(regions))

for i, region in enumerate(regions):
    if progress.is_cancelled():
        break
    # Generate mold...
    progress.set_progress(i + 1, f"Processing region {i+1}")
```

---

# Usage Examples

## Complete Workflow Example

```python
import cpp_core
from app.state.app_state import ApplicationState
from app.analysis.lens_manager import LensManager, LensType
from app.workflow.mold_generator import MoldWorkflow
from app.ui.mold_params_dialog import MoldParameters

# 1. Load SubD control cage
cage = cpp_core.SubDControlCage()
# ... populate cage from Rhino ...

# 2. Initialize evaluator
evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

# 3. Set up application state
state = ApplicationState()
state.set_subd_geometry(cage)

# 4. Analyze with differential lens
lens_mgr = LensManager(evaluator)
regions = lens_mgr.analyze_with_lens(LensType.DIFFERENTIAL)
state.set_regions(regions)

# 5. Pin desired regions
for i, region in enumerate(regions):
    if region.unity_strength > 0.7:  # High quality regions
        state.set_region_pinned(region.id, True)

# 6. Generate molds
workflow = MoldWorkflow(evaluator)
params = MoldParameters(
    draft_angle=2.0,
    wall_thickness=40.0,
    demolding_direction=(0, 0, 1)
)

result = workflow.generate_molds(state.get_pinned_regions(), params)

if result.success:
    # 7. Export to Rhino
    export_json = result.export_data
    # ... send to Rhino via HTTP bridge ...
else:
    print(f"Generation failed: {result.error_message}")
```

## Curvature Analysis Example

```python
import cpp_core
import numpy as np

# Initialize
evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

analyzer = cpp_core.CurvatureAnalyzer()

# Analyze curvature at specific point
result = analyzer.compute_curvature(evaluator, face_index=0, u=0.5, v=0.5)

print(f"Gaussian curvature: {result.gaussian_curvature:.4f}")
print(f"Mean curvature: {result.mean_curvature:.4f}")
print(f"Principal curvatures: k1={result.kappa1:.4f}, k2={result.kappa2:.4f}")

# Batch analysis for heatmap
faces = []
u_vals = []
v_vals = []

for face_id in range(evaluator.get_control_face_count()):
    for u in np.linspace(0, 1, 5):
        for v in np.linspace(0, 1, 5):
            faces.append(face_id)
            u_vals.append(u)
            v_vals.append(v)

results = analyzer.batch_compute_curvature(evaluator, faces, u_vals, v_vals)

# Extract mean curvature for visualization
mean_curvatures = [r.mean_curvature for r in results]
```

## Spectral Analysis Example

```python
from app.analysis.spectral_lens import SpectralLens

# Initialize spectral lens
lens = SpectralLens(evaluator)

# Compute eigenmodes and extract regions
regions = lens.analyze(num_modes=10, mode_indices=[1, 2, 3])

# Visualize specific eigenmode
mode = lens.get_eigenmode(1)  # First non-trivial mode
eigenfunction = mode.eigenfunction  # Per-vertex values
eigenvalue = mode.eigenvalue

print(f"Mode 1: λ={eigenvalue:.4f}")

# Regions from this mode
for region in regions:
    if region.metadata.get('mode_index') == 1:
        print(f"  Region {region.id}: {len(region.faces)} faces")
```

## NURBS Export Example

```python
from app.export.nurbs_serializer import NURBSSerializer
import json

# Generate NURBS from region
gen = cpp_core.NURBSMoldGenerator(evaluator)
nurbs = gen.fit_nurbs_surface(region.faces, sample_density=50)

# Check fitting quality
quality = gen.check_fitting_quality(nurbs, region.faces)
print(f"Max deviation: {quality.max_deviation:.3f}mm")

# Apply draft
demold_dir = cpp_core.Vector3(0, 0, 1)
draft_nurbs = gen.apply_draft_angle(
    nurbs,
    demolding_direction=demold_dir,
    draft_angle_degrees=2.0,
    parting_line=[]
)

# Serialize for Rhino
serializer = NURBSSerializer()
nurbs_data = serializer.serialize_surface(draft_nurbs, name=f"mold_{region.id}")

# Export as JSON
json_str = json.dumps(nurbs_data.to_dict(), indent=2)
```

## Constraint Validation Example

```python
# Validate region manufacturability
validator = cpp_core.ConstraintValidator(evaluator)
demold_dir = cpp_core.Vector3(0, 0, 1)

report = validator.validate_region(
    face_indices=region.faces,
    demolding_direction=demold_dir,
    min_wall_thickness=3.0
)

print(f"Validation: {report.error_count()} errors, {report.warning_count()} warnings")

for violation in report.violations:
    level_str = {
        cpp_core.ConstraintLevel.ERROR: "ERROR",
        cpp_core.ConstraintLevel.WARNING: "WARNING",
        cpp_core.ConstraintLevel.FEATURE: "FEATURE"
    }[violation.level]

    print(f"{level_str}: {violation.description}")
    print(f"  Face {violation.face_id}, severity={violation.severity:.2f}")
    print(f"  Suggestion: {violation.suggestion}")

if not report.has_errors():
    print("Region is manufacturable!")
```

---

# Cross-References

## Workflow Dependencies

```
SubDControlCage → SubDEvaluator → Analysis Lenses → ParametricRegion
                                ↓
                         CurvatureAnalyzer
                         SpectralDecomposer
                                ↓
                         LensManager → ApplicationState
                                ↓
                    ConstraintValidator → MoldWorkflow
                                ↓
                    NURBSMoldGenerator → NURBSSerializer
                                ↓
                         Export to Rhino
```

## Common Usage Patterns

### Pattern 1: SubD Load → Analysis → Regions
1. [SubDControlCage](#subdcontrolcage)
2. [SubDEvaluator.initialize()](#initialize)
3. [LensManager.analyze_with_lens()](#analyze_with_lens)
4. [ApplicationState.set_regions()](#set_regions)

### Pattern 2: Region → Curvature Analysis
1. [ParametricRegion](#parametricregion)
2. [CurvatureAnalyzer.compute_curvature()](#compute_curvature)
3. [CurvatureResult](#curvatureresult)

### Pattern 3: Region → NURBS → Export
1. [NURBSMoldGenerator.fit_nurbs_surface()](#fit_nurbs_surface)
2. [NURBSMoldGenerator.check_fitting_quality()](#check_fitting_quality)
3. [NURBSMoldGenerator.apply_draft_angle()](#apply_draft_angle)
4. [NURBSSerializer.serialize_surface()](#serialize_surface)

### Pattern 4: Complete Mold Generation
1. [ConstraintValidator.validate_region()](#validate_region)
2. [MoldWorkflow.generate_molds()](#generate_molds)
3. [MoldGenerationResult](#moldgenerationresult)

## Mathematical Relationships

### Curvature Relationships
- **Gaussian curvature**: K = κ₁ × κ₂
- **Mean curvature**: H = (κ₁ + κ₂) / 2
- **RMS curvature**: √((κ₁² + κ₂²) / 2)
- **Principal curvatures**: κ₁ (max), κ₂ (min)

### First Fundamental Form (Metric)
```
I = E du² + 2F du dv + G dv²
E = ⟨du, du⟩
F = ⟨du, dv⟩
G = ⟨dv, dv⟩
```

### Second Fundamental Form (Curvature)
```
II = L du² + 2M du dv + N dv²
L = ⟨duu, n⟩
M = ⟨duv, n⟩
N = ⟨dvv, n⟩
```

### Shape Operator
```
S = I⁻¹ × II
Principal curvatures = eigenvalues of S
Principal directions = eigenvectors of S
```

---

## Related Documentation

- **Technical Implementation Guide**: `/docs/reference/technical_implementation_guide_v5.md`
- **v5.0 Specification**: `/docs/reference/subdivision_surface_ceramic_mold_generation_v5.md`
- **Sprint Overview**: `/docs/reference/api_sprint/10_DAY_SPRINT_STRATEGY.md`
- **CLAUDE.md**: Project overview and conventions

---

**End of API Reference**
