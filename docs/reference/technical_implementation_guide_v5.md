# Technical Implementation Guide
## SubD Ceramic Mold Generation System v5.0
### C++ Performance Core & Parametric Region Architecture

---

## 1. C++ PERFORMANCE CORE ARCHITECTURE

### 1.1 Module Structure

```
cpp_core/
├── CMakeLists.txt
├── python_bindings/
│   └── py_subd_evaluator.cpp      # pybind11 bindings
├── geometry/
│   ├── subd_evaluator.h/cpp       # OpenSubdiv integration
│   ├── parametric_region.h/cpp    # Region definitions
│   └── nurbs_converter.h/cpp      # OpenCASCADE integration
├── analysis/
│   ├── spectral_analyzer.h/cpp    # Eigenfunction analysis
│   ├── flow_analyzer.h/cpp        # Geodesic/flow computation
│   ├── thermal_analyzer.h/cpp     # Heat equation solver
│   └── curvature_analyzer.h/cpp   # Differential geometry
└── utils/
    ├── mesh_mapping.h/cpp         # Triangle→Face mapping
    └── math_utils.h/cpp           # Linear algebra helpers
```

### 1.2 OpenSubdiv Integration

```cpp
// subd_evaluator.h
#pragma once
#include <opensubdiv/far/topologyRefiner.h>
#include <opensubdiv/far/primvarRefiner.h>
#include <opensubdiv/osd/cpuEvaluator.h>
#include <opensubdiv/osd/cpuVertexBuffer.h>

class SubDEvaluator {
private:
    using namespace OpenSubdiv;
    std::unique_ptr<Far::TopologyRefiner> refiner_;
    std::unique_ptr<Osd::CpuVertexBuffer> vertex_buffer_;
    
    // Maintain tessellation genealogy
    std::vector<int> triangle_to_face_map_;
    std::vector<int> vertex_to_control_map_;
    
public:
    struct TessellationResult {
        std::vector<float> vertices;      // 3D positions
        std::vector<float> normals;       // Limit surface normals
        std::vector<int> triangles;       // Triangle indices
        std::vector<int> face_parents;    // Which SubD face each tri came from
    };
    
    // Main tessellation function
    TessellationResult tessellate(const SubDSurface& surface, 
                                  int uniform_level = 3,
                                  bool adaptive = false);
    
    // Exact limit surface evaluation
    Point3D evaluate_limit_point(int face_index, float u, float v) const;
    
    // Evaluate exact boundary curve on limit surface
    std::vector<Point3D> evaluate_limit_curve(
        const ParametricCurve& curve, 
        int samples = 128) const;
    
    // Get parent face for any tessellated triangle
    int get_parent_face(int triangle_index) const {
        return triangle_to_face_map_[triangle_index];
    }
};
```

### 1.3 Python Bindings

```cpp
// py_subd_evaluator.cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "geometry/subd_evaluator.h"

namespace py = pybind11;

PYBIND11_MODULE(cpp_core, m) {
    m.doc() = "C++ performance core for SubD mold generation";
    
    py::class_<SubDEvaluator>(m, "SubDEvaluator")
        .def(py::init<>())
        .def("tessellate", [](SubDEvaluator& self, 
                             const SubDSurface& surface,
                             int level,
                             bool adaptive) {
            auto result = self.tessellate(surface, level, adaptive);
            
            // Convert to numpy arrays for Python
            py::array_t<float> vertices({result.vertices.size() / 3, 3}, 
                                       result.vertices.data());
            py::array_t<float> normals({result.normals.size() / 3, 3},
                                      result.normals.data());
            py::array_t<int> triangles({result.triangles.size() / 3, 3},
                                      result.triangles.data());
            py::array_t<int> face_map(result.face_parents.size(),
                                     result.face_parents.data());
            
            return py::make_tuple(vertices, normals, triangles, face_map);
        }, py::arg("surface"), py::arg("level") = 3, py::arg("adaptive") = false,
        "Tessellate SubD surface and return numpy arrays")
        
        .def("evaluate_limit_point", &SubDEvaluator::evaluate_limit_point,
             "Evaluate exact point on limit surface")
        
        .def("evaluate_limit_curve", &SubDEvaluator::evaluate_limit_curve,
             "Evaluate exact curve on limit surface");
    
    // Parametric region bindings
    py::class_<ParametricRegion>(m, "ParametricRegion")
        .def(py::init<>())
        .def_readwrite("face_indices", &ParametricRegion::face_indices)
        .def_readwrite("boundary_curves", &ParametricRegion::boundary_curves)
        .def("compute_area", &ParametricRegion::compute_area)
        .def("check_convexity", &ParametricRegion::check_convexity);
}
```

---

## 2. PARAMETRIC REGION IMPLEMENTATION

### 2.1 Core Data Structure

```python
# parametric_region.py
from dataclasses import dataclass, field
from typing import Set, List, Dict, Optional, Tuple
import numpy as np

@dataclass
class ParametricCurve:
    """
    A curve defined in the surface's parameter space,
    not in 3D coordinates.
    """
    # List of (face_index, u, v) tuples
    points: List[Tuple[int, float, float]]
    
    # Is this curve closed?
    is_closed: bool = False
    
    # Curve metadata
    length_parameter: Optional[float] = None
    curvature_integral: Optional[float] = None
    
    def evaluate(self, t: float) -> Tuple[int, float, float]:
        """Evaluate curve at parameter t ∈ [0,1]"""
        # Interpolate between points
        segment_count = len(self.points) - (0 if self.is_closed else 1)
        segment = int(t * segment_count)
        local_t = (t * segment_count) - segment
        
        p1 = self.points[segment % len(self.points)]
        p2 = self.points[(segment + 1) % len(self.points)]
        
        # Handle crossing face boundaries
        if p1[0] == p2[0]:  # Same face
            u = p1[1] * (1 - local_t) + p2[1] * local_t
            v = p1[2] * (1 - local_t) + p2[2] * local_t
            return (p1[0], u, v)
        else:  # Face boundary crossing
            # This requires topological information
            return self._handle_face_crossing(p1, p2, local_t)
    
    def split_at_parameter(self, t: float) -> Tuple['ParametricCurve', 'ParametricCurve']:
        """Split curve into two curves at parameter t"""
        split_point = self.evaluate(t)
        # Implementation details...
        pass

@dataclass
class ParametricRegion:
    """
    A region defined by its topological and parametric properties,
    not by explicit geometry.
    """
    # Topological definition
    face_indices: Set[int] = field(default_factory=set)
    
    # Boundary definition in parameter space
    boundary_curves: List[ParametricCurve] = field(default_factory=list)
    
    # How was this region generated?
    generation_method: Optional[str] = None
    generation_parameters: Dict = field(default_factory=dict)
    resonance_score: float = 0.0
    
    # Physical parameters
    draft_angle: float = 5.0  # degrees
    min_thickness: float = 3.0  # mm
    demolding_vector: Optional[np.ndarray] = None
    
    # State
    is_pinned: bool = False
    pin_timestamp: Optional[float] = None
    
    # Cached geometric realizations (invalidated on change)
    _cached_nurbs: Optional['NurbsSurface'] = None
    _cached_mesh: Optional['Mesh'] = None
    _cache_subdivision_level: Optional[int] = None
    
    def add_face(self, face_index: int):
        """Add a face to this region"""
        self.face_indices.add(face_index)
        self._invalidate_cache()
    
    def remove_face(self, face_index: int):
        """Remove a face from this region"""
        self.face_indices.discard(face_index)
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        """Clear cached geometric realizations"""
        self._cached_nurbs = None
        self._cached_mesh = None
    
    def to_nurbs(self, subd_surface: 'SubDSurface', 
                 evaluator: 'SubDEvaluator') -> 'NurbsSurface':
        """Generate NURBS representation on demand"""
        if self._cached_nurbs is None:
            # Use C++ evaluator for exact limit surface
            limit_points = []
            for face_idx in self.face_indices:
                # Sample face at regular intervals
                for u in np.linspace(0, 1, 10):
                    for v in np.linspace(0, 1, 10):
                        pt = evaluator.evaluate_limit_point(face_idx, u, v)
                        limit_points.append(pt)
            
            # Fit NURBS to limit surface points
            self._cached_nurbs = fit_nurbs_to_points(limit_points)
        
        return self._cached_nurbs
    
    def to_mesh(self, subd_surface: 'SubDSurface',
                evaluator: 'SubDEvaluator',
                subdivision_level: int = 3) -> 'Mesh':
        """Generate mesh representation at specified detail level"""
        if (self._cached_mesh is None or 
            self._cache_subdivision_level != subdivision_level):
            
            # Get full tessellation from C++
            verts, norms, tris, face_map = evaluator.tessellate(
                subd_surface, subdivision_level
            )
            
            # Filter to only triangles in this region
            region_tris = []
            for i, tri in enumerate(tris):
                parent_face = face_map[i]
                if parent_face in self.face_indices:
                    region_tris.append(tri)
            
            self._cached_mesh = Mesh(verts, norms, region_tris)
            self._cache_subdivision_level = subdivision_level
        
        return self._cached_mesh
```

### 2.2 Region Manipulation

```python
class RegionManipulator:
    """
    Operations on parametric regions maintaining mathematical consistency.
    """
    
    def __init__(self, evaluator: SubDEvaluator):
        self.evaluator = evaluator
    
    def split_region(self, 
                    region: ParametricRegion, 
                    split_curve: ParametricCurve) -> Tuple[ParametricRegion, ParametricRegion]:
        """
        Split a region along a parametric curve.
        Works in parameter space, not 3D.
        """
        # Classify faces as left/right of split curve
        left_faces = set()
        right_faces = set()
        
        for face_idx in region.face_indices:
            # Determine which side of split curve
            side = self._classify_face_side(face_idx, split_curve)
            if side < 0:
                left_faces.add(face_idx)
            else:
                right_faces.add(face_idx)
        
        # Create new regions
        left_region = ParametricRegion(
            face_indices=left_faces,
            generation_method=f"split_from_{region.generation_method}"
        )
        right_region = ParametricRegion(
            face_indices=right_faces,
            generation_method=f"split_from_{region.generation_method}"
        )
        
        # Update boundaries
        self._compute_region_boundaries(left_region)
        self._compute_region_boundaries(right_region)
        
        return left_region, right_region
    
    def merge_regions(self,
                     region1: ParametricRegion,
                     region2: ParametricRegion) -> ParametricRegion:
        """
        Merge two adjacent regions.
        """
        merged = ParametricRegion(
            face_indices=region1.face_indices.union(region2.face_indices),
            generation_method="merged"
        )
        
        # Inherit physical properties from larger region
        if len(region1.face_indices) > len(region2.face_indices):
            merged.draft_angle = region1.draft_angle
            merged.min_thickness = region1.min_thickness
        else:
            merged.draft_angle = region2.draft_angle
            merged.min_thickness = region2.min_thickness
        
        self._compute_region_boundaries(merged)
        return merged
    
    def adjust_boundary(self,
                       region: ParametricRegion,
                       boundary_index: int,
                       adjustment: ParametricCurve):
        """
        Modify a region boundary in parameter space.
        """
        if region.is_pinned:
            raise ValueError("Cannot adjust boundary of pinned region")
        
        # Replace old boundary with adjusted one
        region.boundary_curves[boundary_index] = adjustment
        
        # Update affected faces
        self._update_faces_from_boundaries(region)
        
        # Invalidate cache
        region._invalidate_cache()
```

---

## 3. RENDERING PIPELINE INTEGRATION

### 3.1 Display Manager

```python
class DisplayManager:
    """
    Manages the tessellation→display pipeline.
    Mathematical operations stay exact, display is adaptive.
    """
    
    def __init__(self, cpp_evaluator: SubDEvaluator):
        self.evaluator = cpp_evaluator
        self.renderer = None  # VTK, Qt3D, or OpenGL
        
        # Display state
        self.current_subdivision_level = 3
        self.show_boundaries = True
        self.show_regions = True
        self.boundary_samples = 32
        
        # Caches
        self.display_mesh = None
        self.boundary_curves_3d = []
        self.selection_map = SelectionMapper()
    
    def update_display(self, 
                      subd_surface: SubDSurface,
                      regions: List[ParametricRegion]):
        """
        Convert mathematical definitions to visual representation.
        """
        # Step 1: Get tessellated mesh from C++
        verts, norms, tris, face_map = self.evaluator.tessellate(
            subd_surface,
            self.current_subdivision_level,
            adaptive=True  # More detail at silhouettes
        )
        
        # Step 2: Build selection mapping
        self.selection_map.update_triangle_to_face(tris, face_map)
        self.selection_map.update_face_to_region(regions)
        
        # Step 3: Generate exact boundary curves
        if self.show_boundaries:
            self.boundary_curves_3d = []
            for region in regions:
                for boundary in region.boundary_curves:
                    # Evaluate on exact limit surface
                    curve_3d = self.evaluator.evaluate_limit_curve(
                        boundary, 
                        samples=self.boundary_samples
                    )
                    self.boundary_curves_3d.append({
                        'points': curve_3d,
                        'is_pinned': region.is_pinned,
                        'region_id': id(region)
                    })
        
        # Step 4: Color regions for visualization
        region_colors = self._generate_region_colors(regions, face_map)
        
        # Step 5: Send to renderer
        self.renderer.update_mesh(verts, norms, tris, region_colors)
        self.renderer.update_curves(self.boundary_curves_3d)
    
    def adjust_quality(self, camera_distance: float, fps: float):
        """
        Dynamic level-of-detail based on performance.
        """
        target_fps = 30
        
        if fps < target_fps - 5:
            # Reduce quality to maintain interactivity
            self.current_subdivision_level = max(2, 
                self.current_subdivision_level - 1)
        elif fps > target_fps + 10 and camera_distance < 10:
            # Can afford more detail
            self.current_subdivision_level = min(5,
                self.current_subdivision_level + 1)
        
        # Boundaries always stay smooth
        if camera_distance < 5:
            self.boundary_samples = 64
        else:
            self.boundary_samples = 32
```

### 3.2 Selection System

```python
class SelectionMapper:
    """
    Maps display geometry to mathematical entities.
    Critical for maintaining the mathematical→display separation.
    """
    
    def __init__(self):
        self.triangle_to_face = {}
        self.face_to_region = {}
        self.triangle_to_region = {}
    
    def update_triangle_to_face(self, triangles, face_map):
        """Build mapping from display triangles to SubD faces"""
        self.triangle_to_face.clear()
        for tri_idx, parent_face in enumerate(face_map):
            self.triangle_to_face[tri_idx] = parent_face
    
    def update_face_to_region(self, regions: List[ParametricRegion]):
        """Build mapping from SubD faces to regions"""
        self.face_to_region.clear()
        self.triangle_to_region.clear()
        
        for region_idx, region in enumerate(regions):
            for face_idx in region.face_indices:
                self.face_to_region[face_idx] = region_idx
        
        # Cascade to triangles
        for tri_idx, face_idx in self.triangle_to_face.items():
            if face_idx in self.face_to_region:
                region_idx = self.face_to_region[face_idx]
                self.triangle_to_region[tri_idx] = region_idx
    
    def select_at_screen_point(self, x: int, y: int, 
                              regions: List[ParametricRegion]) -> ParametricRegion:
        """
        User clicks display, selects mathematical region.
        """
        # Ray cast to display mesh
        hit_triangle = self.ray_cast(x, y)
        
        if hit_triangle in self.triangle_to_region:
            region_idx = self.triangle_to_region[hit_triangle]
            return regions[region_idx]
        
        return None
```

---

## 4. BUILD SYSTEM

### 4.1 CMake Configuration

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(subd_ceramic_molds)

set(CMAKE_CXX_STANDARD 17)

# Find dependencies
find_package(OpenSubdiv REQUIRED)
find_package(OpenCASCADE REQUIRED)
find_package(pybind11 REQUIRED)

# Build C++ core library
add_library(cpp_core SHARED
    geometry/subd_evaluator.cpp
    geometry/parametric_region.cpp
    geometry/nurbs_converter.cpp
    analysis/spectral_analyzer.cpp
    analysis/flow_analyzer.cpp
    analysis/thermal_analyzer.cpp
)

target_link_libraries(cpp_core
    OpenSubdiv::osd
    ${OpenCASCADE_LIBRARIES}
)

# Python bindings
pybind11_add_module(py_cpp_core 
    python_bindings/py_subd_evaluator.cpp
)

target_link_libraries(py_cpp_core PRIVATE cpp_core)

# Enable GPU acceleration on macOS
if(APPLE)
    target_compile_definitions(cpp_core PRIVATE OPENSUBDIV_HAS_METAL)
endif()
```

### 4.2 Python Setup

```python
# setup.py
from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "cpp_core",
        ["python_bindings/py_subd_evaluator.cpp"],
        include_dirs=[
            "/usr/local/include",
            "/usr/local/include/opensubdiv",
        ],
        libraries=["osd", "OpenCASCADE"],
        library_dirs=["/usr/local/lib"],
        cxx_std=17,
    ),
]

setup(
    name="subd_ceramic_molds",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    python_requires=">=3.9",
)
```

---

## 5. PERFORMANCE OPTIMIZATION STRATEGIES

### 5.1 Critical Path Optimizations

```cpp
// Parallel tessellation using OpenMP
TessellationResult SubDEvaluator::tessellate_parallel(
    const SubDSurface& surface,
    int level) {
    
    // OpenSubdiv supports OMP parallelization
    #pragma omp parallel for
    for (int face = 0; face < surface.num_faces(); ++face) {
        // Tessellate each face independently
        tessellate_face(face, level);
    }
    
    // Merge results
    return merge_face_tessellations();
}
```

### 5.2 GPU Acceleration (Metal on macOS)

```cpp
// Use OpenSubdiv's Metal backend
#ifdef OPENSUBDIV_HAS_METAL
    #include <opensubdiv/osd/metalComputeEvaluator.h>
    
    class MetalAcceleratedEvaluator : public SubDEvaluator {
        Osd::MetalComputeEvaluator* metal_evaluator;
        
        TessellationResult tessellate(const SubDSurface& surface, int level) {
            // Evaluation happens on GPU
            metal_evaluator->EvalStencils(...);
            // Results come back to CPU for display
        }
    };
#endif
```

---

This implementation guide provides the concrete technical foundation for building the system. The key insights:

1. **C++ does the heavy lifting** (SubD evaluation, mathematical analysis)
2. **Python manages interaction** (UI, state, orchestration)
3. **Parametric regions are lightweight** (just topology + parameters)
4. **Display is generated on-demand** from mathematical truth
5. **Selection always maps back** to mathematical entities

Ready to start implementation with Phase 0?
