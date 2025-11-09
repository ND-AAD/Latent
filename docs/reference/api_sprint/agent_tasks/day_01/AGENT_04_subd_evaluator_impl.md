# Agent 4: SubDEvaluator Implementation

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 4-5 hours
**Estimated Cost**: $5-8 (60K tokens, Sonnet)

---

## Mission

Implement the SubDEvaluator class that wraps OpenSubdiv's TopologyRefiner for exact SubD limit surface evaluation.

---

## Context

You are implementing the core C++ class that provides exact subdivision surface evaluation using OpenSubdiv 3.6+. This class:
- Builds TopologyRefiner from control cage topology
- Performs uniform/adaptive subdivision
- Tessellates refined mesh for display (triangulation)
- Evaluates exact points on limit surface using Stam's eigenanalysis
- Tracks triangle→face mapping for selection

**Critical**: This class provides **exact limit surface evaluation**, not mesh approximation. Tessellation is for display only.

**Dependencies**:
- Agent 1's `types.h` (Point3D, SubDControlCage, TessellationResult)
- Agent 2's `subd_evaluator.h` (class interface)
- OpenSubdiv 3.6+ installed on system

---

## Deliverables

**File to Create**: `cpp_core/geometry/subd_evaluator.cpp`

---

## Requirements

### 1. Constructor/Destructor
```cpp
SubDEvaluator::SubDEvaluator() : initialized_(false) {}

SubDEvaluator::~SubDEvaluator() {
    // unique_ptr handles cleanup automatically
}
```

### 2. Initialize from Control Cage
```cpp
void SubDEvaluator::initialize(const SubDControlCage& cage) {
    using namespace OpenSubdiv;

    // Build TopologyDescriptor from cage
    Far::TopologyDescriptor desc;
    desc.numVertices = cage.vertex_count();
    desc.numFaces = cage.face_count();

    // Set face vertex counts and indices
    std::vector<int> num_verts_per_face;
    std::vector<int> face_vert_indices;

    for (const auto& face : cage.faces) {
        num_verts_per_face.push_back(face.size());
        face_vert_indices.insert(face_vert_indices.end(),
                                  face.begin(), face.end());
    }

    desc.numVertsPerFace = num_verts_per_face.data();
    desc.vertIndicesPerFace = face_vert_indices.data();

    // Handle creases if present
    // [IMPLEMENT CREASE HANDLING]

    // Create refiner
    Far::TopologyRefinerFactory<Far::TopologyDescriptor>::Options options;
    options.schemeType = Far::SCHEME_CATMARK;

    refiner_.reset(
        Far::TopologyRefinerFactory<Far::TopologyDescriptor>::Create(
            desc, options));

    initialized_ = true;
}
```

### 3. Tessellation for Display
```cpp
TessellationResult SubDEvaluator::tessellate(int subdivision_level,
                                             bool adaptive) {
    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    using namespace OpenSubdiv;

    // Refine topology
    Far::TopologyRefiner::UniformOptions refine_options(subdivision_level);
    refiner_->RefineUniform(refine_options);

    // Get refined level
    Far::TopologyLevel const& refined_level =
        refiner_->GetLevel(subdivision_level);

    // Allocate primvar buffer for positions
    std::vector<float> verts(refined_level.GetNumVertices() * 3);

    // Interpolate positions using PrimvarRefiner
    // [IMPLEMENT POSITION INTERPOLATION]

    // Triangulate quads
    TessellationResult result;
    // [IMPLEMENT TRIANGULATION WITH PARENT TRACKING]

    return result;
}
```

### 4. Exact Limit Surface Evaluation
```cpp
Point3D SubDEvaluator::evaluate_limit_point(int face_index,
                                            float u, float v) const {
    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    using namespace OpenSubdiv;

    // Get base level (control cage)
    Far::TopologyLevel const& base_level = refiner_->GetLevel(0);

    // Use PatchTable for limit evaluation
    // [IMPLEMENT STAM EVALUATION]

    Point3D result;
    return result;
}

void SubDEvaluator::evaluate_limit(int face_index, float u, float v,
                                   Point3D& point, Point3D& normal) const {
    // Evaluate both position and first derivatives
    // Normal = cross(du, dv)
    // [IMPLEMENT LIMIT EVALUATION WITH DERIVATIVES]
}
```

### 5. Selection Mapping
```cpp
int SubDEvaluator::get_parent_face(int triangle_index) const {
    if (triangle_index < 0 ||
        triangle_index >= triangle_to_face_map_.size()) {
        return -1;
    }
    return triangle_to_face_map_[triangle_index];
}
```

### 6. Statistics
```cpp
size_t SubDEvaluator::get_control_vertex_count() const {
    if (!initialized_) return 0;
    return refiner_->GetLevel(0).GetNumVertices();
}

size_t SubDEvaluator::get_control_face_count() const {
    if (!initialized_) return 0;
    return refiner_->GetLevel(0).GetNumFaces();
}
```

---

## OpenSubdiv Integration Details

### Key Classes to Use:
```cpp
#include <opensubdiv/far/topologyRefiner.h>
#include <opensubdiv/far/topologyRefinerFactory.h>
#include <opensubdiv/far/topologyDescriptor.h>
#include <opensubdiv/far/primvarRefiner.h>
#include <opensubdiv/far/patchTable.h>
#include <opensubdiv/far/patchTableFactory.h>
```

### Uniform Refinement Pattern:
```cpp
// Refine uniformly to specified level
Far::TopologyRefiner::UniformOptions options(level);
refiner_->RefineUniform(options);

// Access refined level
Far::TopologyLevel const& refined = refiner_->GetLevel(level);
```

### Primvar Interpolation Pattern:
```cpp
// Create primvar refiner
Far::PrimvarRefiner primvar_refiner(*refiner_);

// Interpolate from level 0 to level N
std::vector<float> src_data, dst_data;
for (int level = 1; level <= max_level; ++level) {
    primvar_refiner.Interpolate(level, src_data, dst_data);
    src_data = dst_data;
}
```

### Limit Evaluation Pattern:
```cpp
// Create patch table for limit evaluation
Far::PatchTableFactory::Options patch_options;
patch_options.endCapType =
    Far::PatchTableFactory::Options::ENDCAP_GREGORY_BASIS;

std::unique_ptr<Far::PatchTable const> patch_table(
    Far::PatchTableFactory::Create(*refiner_, patch_options));

// Evaluate at (u,v) on face
Far::PatchMap patch_map(*patch_table);
Far::PatchTable::PatchHandle const* handle =
    patch_map.FindPatch(face_index, u, v);

// Get stencils and evaluate
// [Use PatchTable::EvaluateBasis]
```

---

## Testing

**Test File**: `cpp_core/test_subd_evaluator.cpp`

```cpp
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"
#include <iostream>
#include <cassert>
#include <cmath>

using namespace latent;

// Helper to compare floats
bool approx_equal(float a, float b, float eps = 1e-5f) {
    return std::abs(a - b) < eps;
}

void test_cube_subdivision() {
    std::cout << "Test: Cube subdivision..." << std::endl;

    // Create unit cube control cage
    SubDControlCage cube;

    // 8 vertices
    cube.vertices = {
        Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
        Point3D(0,0,1), Point3D(1,0,1), Point3D(1,1,1), Point3D(0,1,1)
    };

    // 6 quad faces
    cube.faces = {
        {0,1,2,3}, {4,5,6,7}, {0,1,5,4},
        {2,3,7,6}, {0,3,7,4}, {1,2,6,5}
    };

    // Test initialization
    SubDEvaluator eval;
    assert(!eval.is_initialized());

    eval.initialize(cube);
    assert(eval.is_initialized());
    assert(eval.get_control_vertex_count() == 8);
    assert(eval.get_control_face_count() == 6);

    std::cout << "  ✅ Initialization successful" << std::endl;

    // Test tessellation
    TessellationResult mesh = eval.tessellate(2);  // Level 2

    assert(mesh.vertex_count() > 8);  // Should have more verts than cage
    assert(mesh.triangle_count() > 0);  // Should have triangles
    assert(mesh.vertices.size() == mesh.normals.size());  // Normals match

    std::cout << "  ✅ Tessellation produced " << mesh.vertex_count()
              << " vertices, " << mesh.triangle_count() << " triangles"
              << std::endl;

    // Test parent mapping
    for (size_t i = 0; i < mesh.triangle_count(); ++i) {
        int parent = eval.get_parent_face(i);
        assert(parent >= 0 && parent < 6);  // Valid parent face
    }

    std::cout << "  ✅ Parent face mapping valid" << std::endl;

    // Test limit evaluation at face center
    Point3D center = eval.evaluate_limit_point(0, 0.5f, 0.5f);

    // For a cube, face center should be between control points
    assert(center.x >= 0.0f && center.x <= 1.0f);
    assert(center.y >= 0.0f && center.y <= 1.0f);
    assert(center.z >= -0.1f && center.z <= 0.1f);  // Near z=0 plane

    std::cout << "  ✅ Limit evaluation at (" << center.x << ", "
              << center.y << ", " << center.z << ")" << std::endl;

    // Test limit with normal
    Point3D point, normal;
    eval.evaluate_limit(0, 0.5f, 0.5f, point, normal);

    // Normal should be unit length
    float length = std::sqrt(normal.x * normal.x +
                             normal.y * normal.y +
                             normal.z * normal.z);
    assert(approx_equal(length, 1.0f, 0.01f));

    std::cout << "  ✅ Normal evaluation: (" << normal.x << ", "
              << normal.y << ", " << normal.z << "), length="
              << length << std::endl;
}

void test_different_subdivision_levels() {
    std::cout << "\nTest: Different subdivision levels..." << std::endl;

    // Simple quad
    SubDControlCage quad;
    quad.vertices = {
        Point3D(0,0,0), Point3D(1,0,0),
        Point3D(1,1,0), Point3D(0,1,0)
    };
    quad.faces = {{0,1,2,3}};

    SubDEvaluator eval;
    eval.initialize(quad);

    for (int level = 1; level <= 4; ++level) {
        TessellationResult mesh = eval.tessellate(level);
        std::cout << "  Level " << level << ": "
                  << mesh.vertex_count() << " vertices, "
                  << mesh.triangle_count() << " triangles" << std::endl;

        // Higher levels should produce more triangles
        assert(mesh.triangle_count() > 0);
    }

    std::cout << "  ✅ All subdivision levels working" << std::endl;
}

int main() {
    try {
        test_cube_subdivision();
        test_different_subdivision_levels();

        std::cout << "\n✅ ALL TESTS PASSED!" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "\n❌ TEST FAILED: " << e.what() << std::endl;
        return 1;
    }
}
```

**Build and Run**:
```bash
cd cpp_core/build
cmake ..
make test_subd_evaluator
./test_subd_evaluator
```

---

## Success Criteria

- [ ] Implementation compiles without errors
- [ ] All methods from header implemented
- [ ] OpenSubdiv TopologyRefiner created successfully
- [ ] Tessellation produces valid triangle mesh
- [ ] Triangle→face parent mapping correct
- [ ] Limit evaluation returns valid points
- [ ] Normal computation produces unit vectors
- [ ] All tests pass
- [ ] No memory leaks (unique_ptr handles cleanup)

---

## Performance Notes

**Expected Performance**:
- Initialization: <10ms for typical control cage (100-500 vertices)
- Tessellation (level 3): <50ms for moderate complexity
- Single limit evaluation: <0.1ms (can evaluate millions of points/second)

**Memory Usage**:
- TopologyRefiner: ~100 bytes per control vertex
- Tessellation: ~50 bytes per output vertex
- Keep tessellation results temporary (generate on-demand)

---

## Integration Notes

**Used by**:
- Agent 5 will bind this class to Python
- Agent 7 will use tessellation for display
- Agent 10 will use limit evaluation for analysis
- Agent 27 will extend with curvature evaluation

**File Placement**:
```
cpp_core/
├── geometry/
│   ├── types.h              (Agent 1)
│   ├── subd_evaluator.h     (Agent 2)
│   └── subd_evaluator.cpp   (You create this) ← HERE
└── build/
```

**Next Steps** (other agents):
- Agent 3 will configure CMakeLists.txt to build this
- Agent 5 will expose to Python via pybind11

---

## Common Issues and Solutions

**Issue**: "TopologyRefiner creation failed"
- **Fix**: Check face winding order (CCW vs CW)
- **Fix**: Verify all face indices are valid (< vertex count)

**Issue**: "Tessellation produces degenerate triangles"
- **Fix**: Ensure control cage has valid topology (no duplicate vertices)

**Issue**: "Limit evaluation returns NaN"
- **Fix**: Check (u,v) parameters are in [0,1] range
- **Fix**: Verify face_index is valid

**Issue**: "Memory leak detected"
- **Fix**: Ensure unique_ptr is used for TopologyRefiner
- **Fix**: Don't call `new` directly - use `reset()`

---

## Output Format

Provide:
1. Complete `subd_evaluator.cpp` implementation
2. Test program output showing all tests passing
3. Brief explanation of OpenSubdiv integration approach
4. Any performance observations or optimizations made
5. Integration notes for other agents

---

**Ready to begin!**
