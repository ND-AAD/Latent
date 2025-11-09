# NURBS Generator Integration Notes

## Overview

The `nurbs_generator.h` header defines the interface for NURBS-based mold generation, completing Day 7's morning agents for the 10-day sprint.

## Integration with Existing Components

### Dependency Graph
```
types.h (Point3D, Vector3)
    ↓
subd_evaluator.h (exact limit surface)
    ↓
nurbs_generator.h (NURBS mold generation) ← YOU ARE HERE
    ↓
[Agents 47-50: Implementation]
    ↓
Python bindings (Day 7-8)
    ↓
Desktop application
```

### Data Flow

#### 1. Input: SubD Control Cage
```cpp
SubDControlCage cage;
// Populated from Rhino via HTTP bridge
```

#### 2. Initialize Evaluator
```cpp
SubDEvaluator evaluator;
evaluator.initialize(cage);
```

#### 3. Create NURBS Generator
```cpp
NURBSMoldGenerator generator(evaluator);
// Generator now has access to exact limit surface
```

#### 4. Fit NURBS to Region
```cpp
std::vector<int> region_faces = {0, 1, 2, 3, 4};
auto nurbs = generator.fit_nurbs_surface(region_faces, 50);
// nurbs is exact B-spline fitted to limit surface
```

#### 5. Apply Draft Angle
```cpp
Vector3 demolding_dir(0.0f, 0.0f, 1.0f);  // +Z direction
std::vector<Point3D> parting_line = {...};
auto drafted = generator.apply_draft_angle(
    nurbs, demolding_dir, 3.0f, parting_line
);
```

#### 6. Create Solid Mold
```cpp
auto mold_solid = generator.create_mold_solid(drafted, 40.0f);
// 40mm wall thickness
```

#### 7. Add Registration Keys
```cpp
std::vector<Point3D> key_positions = {{10,0,0}, {-10,0,0}};
auto final_mold = generator.add_registration_keys(
    mold_solid, key_positions
);
```

#### 8. Quality Check
```cpp
auto quality = generator.check_fitting_quality(nurbs, region_faces);
if (quality.max_deviation < 0.01f) {
    // Excellent fit (< 0.01mm)
    std::cout << "High quality NURBS fit!\n";
}
```

## OpenCASCADE Integration

### Required OpenCASCADE Modules

**Geometry**:
- `Geom_BSplineSurface` - NURBS surface representation
- `GeomAPI_PointsToBSplineSurface` - Surface fitting
- `GeomAPI_ProjectPointOnSurf` - Distance computation

**Topology**:
- `TopoDS_Shape` - General shape container
- `TopoDS_Face` - Face representation
- `TopoDS_Solid` - Solid representation

**Modeling**:
- `BRepOffsetAPI_MakeThickSolid` - Create solid from surface
- `BRepAlgoAPI_Fuse` - Boolean union
- `BRepAlgoAPI_Cut` - Boolean subtraction
- `BRepPrimAPI_MakeBox` - Create primitive shapes

### CMake Configuration Example
```cmake
# Find OpenCASCADE
find_package(OpenCASCADE REQUIRED COMPONENTS
    TKernel
    TKMath
    TKG3d
    TKGeomBase
    TKGeomAlgo
    TKBRep
    TKTopAlgo
    TKPrim
    TKBO
)

# Link to library
target_link_libraries(cpp_core_static PUBLIC
    ${OpenCASCADE_LIBRARIES}
)
```

## Implementation Strategy for Agents 47-50

### Agent 47: Surface Sampling and NURBS Fitting
**Files**: `nurbs_generator.cpp` (partial)

Implement:
1. `sample_limit_surface()` - Regular grid sampling
2. `fit_nurbs_surface()` - NURBS fitting via OpenCASCADE

Key algorithm:
```cpp
std::vector<Point3D> NURBSMoldGenerator::sample_limit_surface(
    const std::vector<int>& face_indices, int density
) {
    std::vector<Point3D> samples;
    for (int face_id : face_indices) {
        for (int i = 0; i < density; ++i) {
            for (int j = 0; j < density; ++j) {
                float u = i / float(density - 1);
                float v = j / float(density - 1);
                Point3D pt = evaluator_.evaluate_limit_point(face_id, u, v);
                samples.push_back(pt);
            }
        }
    }
    return samples;
}
```

### Agent 48: Draft Angle Transformation
**Files**: `nurbs_generator.cpp` (continuation)

Implement:
- `apply_draft_angle()` - Transform control points

Algorithm:
1. Extract NURBS control points
2. Compute distance from parting line
3. Apply scaling transformation based on draft angle
4. Rebuild NURBS with transformed points

### Agent 49: Solid Creation
**Files**: `nurbs_generator.cpp` (continuation)

Implement:
- `create_mold_solid()` - Generate solid from surface

Algorithm:
1. Create face from NURBS surface
2. Offset surface outward by wall thickness
3. Create solid between inner and outer surfaces
4. Ensure watertight topology

### Agent 50: Quality Control and Registration
**Files**: `nurbs_generator.cpp` (complete)

Implement:
1. `check_fitting_quality()` - Compute deviation metrics
2. `add_registration_keys()` - Add alignment features

## Python Bindings Plan

### pybind11 Exposure
```cpp
// In python_bindings/bindings.cpp

py::class_<NURBSMoldGenerator>(m, "NURBSMoldGenerator")
    .def(py::init<const SubDEvaluator&>())
    .def("fit_nurbs_surface",
         &NURBSMoldGenerator::fit_nurbs_surface,
         py::arg("face_indices"),
         py::arg("sample_density") = 50)
    .def("apply_draft_angle",
         &NURBSMoldGenerator::apply_draft_angle,
         py::arg("surface"),
         py::arg("demolding_direction"),
         py::arg("draft_angle_degrees"),
         py::arg("parting_line"))
    .def("create_mold_solid",
         &NURBSMoldGenerator::create_mold_solid,
         py::arg("surface"),
         py::arg("wall_thickness") = 40.0f)
    .def("add_registration_keys",
         &NURBSMoldGenerator::add_registration_keys,
         py::arg("mold"),
         py::arg("key_positions"))
    .def("check_fitting_quality",
         &NURBSMoldGenerator::check_fitting_quality,
         py::arg("nurbs"),
         py::arg("face_indices"));

py::class_<NURBSMoldGenerator::FittingQuality>(m, "FittingQuality")
    .def_readonly("max_deviation", &NURBSMoldGenerator::FittingQuality::max_deviation)
    .def_readonly("mean_deviation", &NURBSMoldGenerator::FittingQuality::mean_deviation)
    .def_readonly("rms_deviation", &NURBSMoldGenerator::FittingQuality::rms_deviation)
    .def_readonly("num_samples", &NURBSMoldGenerator::FittingQuality::num_samples);
```

### Python Usage Example
```python
import cpp_core
import numpy as np

# Initialize evaluator with SubD cage
evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

# Create generator
generator = cpp_core.NURBSMoldGenerator(evaluator)

# Fit NURBS to region
face_indices = [0, 1, 2, 3, 4]
nurbs = generator.fit_nurbs_surface(face_indices, sample_density=50)

# Apply 3-degree draft in +Z direction
demolding_dir = cpp_core.Vector3(0, 0, 1)
parting_line = [cpp_core.Point3D(x, y, 0) for x, y in parting_points]
drafted_nurbs = generator.apply_draft_angle(
    nurbs, demolding_dir, 3.0, parting_line
)

# Create mold with 40mm walls
mold = generator.create_mold_solid(drafted_nurbs, wall_thickness=40.0)

# Check quality
quality = generator.check_fitting_quality(drafted_nurbs, face_indices)
print(f"NURBS fitting quality:")
print(f"  Max deviation: {quality.max_deviation:.4f} mm")
print(f"  Mean deviation: {quality.mean_deviation:.4f} mm")
print(f"  RMS deviation: {quality.rms_deviation:.4f} mm")
print(f"  Samples: {quality.num_samples}")
```

## Testing Requirements

### Unit Tests
```cpp
// Test 1: Sample limit surface
TEST(NURBSGenerator, SampleLimitSurface) {
    // Verify sampling produces correct point count
    // Verify points lie on limit surface
}

// Test 2: Fit NURBS
TEST(NURBSGenerator, FitNURBS) {
    // Verify NURBS degree and control point count
    // Verify deviation < tolerance
}

// Test 3: Draft angle
TEST(NURBSGenerator, DraftAngle) {
    // Verify parting line unchanged
    // Verify draft angle magnitude
}

// Test 4: Create solid
TEST(NURBSGenerator, CreateSolid) {
    // Verify solid is closed (watertight)
    // Verify wall thickness
}
```

### Integration Tests
```python
def test_nurbs_workflow():
    """Test complete NURBS generation pipeline"""
    # 1. Load SubD cage
    # 2. Create generator
    # 3. Fit NURBS
    # 4. Apply draft
    # 5. Create solid
    # 6. Verify quality
    assert quality.max_deviation < 0.01  # < 0.01mm
```

## Success Metrics

### Fitting Quality Targets
- **Max deviation**: < 0.01 mm (excellent), < 0.05 mm (acceptable)
- **Mean deviation**: < 0.005 mm
- **RMS deviation**: < 0.008 mm

### Performance Targets
- **Sampling**: < 1 second for 50×50 grid
- **NURBS fitting**: < 2 seconds per region
- **Draft application**: < 0.5 seconds
- **Solid creation**: < 1 second

## File Locations

```
cpp_core/
├── geometry/
│   ├── nurbs_generator.h          ← CREATED (Agent 46)
│   ├── nurbs_generator.cpp        ← TODO (Agents 47-50)
│   ├── types.h                    ← Existing
│   └── subd_evaluator.h/cpp       ← Existing
├── python_bindings/
│   └── bindings.cpp               ← TODO (Update Day 7-8)
├── test_nurbs_generator.cpp       ← TODO (Agents 47-50)
└── CMakeLists.txt                 ← TODO (Update for OpenCASCADE)
```

## Next Steps

1. **Agents 47-48**: Implement sampling and NURBS fitting
2. **Agent 49**: Implement draft and solid creation
3. **Agent 50**: Implement quality control and registration keys
4. **Day 7 Evening**: Update CMake, add OpenCASCADE, test compilation
5. **Day 8**: Python bindings and integration with desktop app

---

**Status**: Header complete, ready for implementation
**Agent 46**: ✅ COMPLETE
**Next Agent**: Agent 47 (NURBS fitting implementation)
