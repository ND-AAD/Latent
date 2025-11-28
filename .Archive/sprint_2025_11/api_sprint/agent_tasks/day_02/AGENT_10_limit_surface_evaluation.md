# Agent 10: Advanced Limit Surface Evaluation

**Day**: 2
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 5-6 hours
**Estimated Cost**: $6-10 (70K tokens, Sonnet)

---

## Mission

Extend SubDEvaluator with advanced limit surface evaluation methods needed for curvature analysis and region discovery.

---

## Context

You are enhancing the C++ SubDEvaluator class (from Day 1, Agent 4) with advanced evaluation capabilities:
- Evaluate derivatives (first and second) for curvature computation
- Batch evaluation of multiple points efficiently
- Derivative queries at arbitrary (u,v) parameters
- Normal and tangent frame computation
- Prepare foundation for curvature analysis (Day 4)

**Critical**: These methods provide **exact derivatives** from limit surface, not finite difference approximations.

**Dependencies**:
- Day 1 complete (SubDEvaluator base implementation)
- OpenSubdiv 3.6+ with patch table support

---

## Deliverables

**Files to Update/Create**:
1. Update `cpp_core/geometry/subd_evaluator.h` - Add new method declarations
2. Update `cpp_core/geometry/subd_evaluator.cpp` - Implement advanced evaluation
3. Update `cpp_core/python_bindings/bindings.cpp` - Expose new methods to Python
4. Create `cpp_core/test_limit_evaluation.cpp` - Test derivative accuracy

---

## Requirements

### 1. Update Header - New Method Declarations

**File**: `cpp_core/geometry/subd_evaluator.h`

Add to SubDEvaluator class:

```cpp
// Advanced limit surface evaluation

/**
 * Evaluate limit position and first derivatives
 *
 * @param face_index Control face index
 * @param u Parameter u in [0,1]
 * @param v Parameter v in [0,1]
 * @param position Output: limit position
 * @param du Output: first derivative wrt u
 * @param dv Output: first derivative wrt v
 */
void evaluate_limit_with_derivatives(
    int face_index, float u, float v,
    Point3D& position,
    Point3D& du,
    Point3D& dv) const;

/**
 * Evaluate limit position and first/second derivatives
 *
 * @param face_index Control face index
 * @param u Parameter u in [0,1]
 * @param v Parameter v in [0,1]
 * @param position Output: limit position
 * @param du, dv Output: first derivatives
 * @param duu, dvv, duv Output: second derivatives
 */
void evaluate_limit_with_second_derivatives(
    int face_index, float u, float v,
    Point3D& position,
    Point3D& du, Point3D& dv,
    Point3D& duu, Point3D& dvv, Point3D& duv) const;

/**
 * Batch evaluate multiple points on limit surface
 * More efficient than individual calls
 *
 * @param face_indices Face index for each point
 * @param params_u U parameters for each point
 * @param params_v V parameters for each point
 * @return TessellationResult with evaluated points
 */
TessellationResult batch_evaluate_limit(
    const std::vector<int>& face_indices,
    const std::vector<float>& params_u,
    const std::vector<float>& params_v) const;

/**
 * Compute tangent frame (tangent_u, tangent_v, normal)
 *
 * @param face_index Control face index
 * @param u Parameter u in [0,1]
 * @param v Parameter v in [0,1]
 * @param tangent_u Output: normalized tangent in u direction
 * @param tangent_v Output: normalized tangent in v direction
 * @param normal Output: unit normal (cross product of tangents)
 */
void compute_tangent_frame(
    int face_index, float u, float v,
    Point3D& tangent_u,
    Point3D& tangent_v,
    Point3D& normal) const;

private:
    // Helper for derivative evaluation
    std::unique_ptr<OpenSubdiv::Far::PatchTable const> patch_table_;

    // Build patch table on first use (lazy initialization)
    void ensure_patch_table() const;
```

### 2. Implementation

**File**: `cpp_core/geometry/subd_evaluator.cpp`

```cpp
#include <opensubdiv/far/patchTable.h>
#include <opensubdiv/far/patchTableFactory.h>
#include <opensubdiv/far/patchMap.h>

void SubDEvaluator::ensure_patch_table() const {
    if (patch_table_) return;  // Already built

    using namespace OpenSubdiv;

    // Create patch table for limit evaluation
    Far::PatchTableFactory::Options options;
    options.endCapType = Far::PatchTableFactory::Options::ENDCAP_GREGORY_BASIS;
    options.useInfSharpPatch = true;
    options.generateFVarTables = false;

    // Build patch table from refiner
    patch_table_.reset(
        Far::PatchTableFactory::Create(*refiner_, options)
    );
}

void SubDEvaluator::evaluate_limit_with_derivatives(
    int face_index, float u, float v,
    Point3D& position,
    Point3D& du,
    Point3D& dv) const {

    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    ensure_patch_table();

    using namespace OpenSubdiv;

    // Get control positions
    Far::TopologyLevel const& base_level = refiner_->GetLevel(0);
    int num_control_verts = base_level.GetNumVertices();

    // Get control positions (you'll need to store these during initialize)
    // For now, assume they're stored in control_positions_
    std::vector<float> control_positions(num_control_verts * 3);
    // [POPULATE control_positions from stored cage data]

    // Create patch map
    Far::PatchMap patch_map(*patch_table_);

    // Find patch handle for (face, u, v)
    Far::PatchTable::PatchHandle const* handle =
        patch_map.FindPatch(face_index, u, v);

    if (!handle) {
        throw std::runtime_error("Invalid face or parameters");
    }

    // Allocate output buffers
    float p[3], du_out[3], dv_out[3];

    // Evaluate position and derivatives
    patch_table_->Evaluate(*handle, u, v,
                           control_positions.data(),
                           p, du_out, dv_out);

    // Convert to Point3D
    position = Point3D(p[0], p[1], p[2]);
    du = Point3D(du_out[0], du_out[1], du_out[2]);
    dv = Point3D(dv_out[0], dv_out[1], dv_out[2]);
}

void SubDEvaluator::evaluate_limit_with_second_derivatives(
    int face_index, float u, float v,
    Point3D& position,
    Point3D& du, Point3D& dv,
    Point3D& duu, Point3D& dvv, Point3D& duv) const {

    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    ensure_patch_table();

    using namespace OpenSubdiv;

    // Get patch handle
    Far::PatchMap patch_map(*patch_table_);
    Far::PatchTable::PatchHandle const* handle =
        patch_map.FindPatch(face_index, u, v);

    if (!handle) {
        throw std::runtime_error("Invalid face or parameters");
    }

    // Output buffers
    float p[3];
    float d1[6];  // [du_x, du_y, du_z, dv_x, dv_y, dv_z]
    float d2[9];  // [duu_x, duu_y, duu_z, dvv_x, dvv_y, dvv_z, duv_x, duv_y, duv_z]

    // Evaluate with second derivatives
    patch_table_->EvaluateBasis(*handle, u, v,
                                control_positions_.data(),
                                p, d1, d2);

    // Convert outputs
    position = Point3D(p[0], p[1], p[2]);
    du = Point3D(d1[0], d1[1], d1[2]);
    dv = Point3D(d1[3], d1[4], d1[5]);
    duu = Point3D(d2[0], d2[1], d2[2]);
    dvv = Point3D(d2[3], d2[4], d2[5]);
    duv = Point3D(d2[6], d2[7], d2[8]);
}

TessellationResult SubDEvaluator::batch_evaluate_limit(
    const std::vector<int>& face_indices,
    const std::vector<float>& params_u,
    const std::vector<float>& params_v) const {

    if (!initialized_) {
        throw std::runtime_error("SubDEvaluator not initialized");
    }

    size_t num_points = face_indices.size();
    if (params_u.size() != num_points || params_v.size() != num_points) {
        throw std::runtime_error("Parameter array size mismatch");
    }

    TessellationResult result;
    result.vertices.reserve(num_points * 3);
    result.normals.reserve(num_points * 3);

    // Evaluate each point
    for (size_t i = 0; i < num_points; ++i) {
        Point3D pos, du, dv;
        evaluate_limit_with_derivatives(
            face_indices[i], params_u[i], params_v[i],
            pos, du, dv
        );

        // Add position
        result.vertices.push_back(pos.x);
        result.vertices.push_back(pos.y);
        result.vertices.push_back(pos.z);

        // Compute normal as cross(du, dv)
        Point3D normal;
        normal.x = du.y * dv.z - du.z * dv.y;
        normal.y = du.z * dv.x - du.x * dv.z;
        normal.z = du.x * dv.y - du.y * dv.x;

        // Normalize
        float length = std::sqrt(
            normal.x * normal.x +
            normal.y * normal.y +
            normal.z * normal.z
        );

        if (length > 1e-8f) {
            normal.x /= length;
            normal.y /= length;
            normal.z /= length;
        }

        result.normals.push_back(normal.x);
        result.normals.push_back(normal.y);
        result.normals.push_back(normal.z);

        // Store parent face
        result.face_parents.push_back(face_indices[i]);
    }

    return result;
}

void SubDEvaluator::compute_tangent_frame(
    int face_index, float u, float v,
    Point3D& tangent_u,
    Point3D& tangent_v,
    Point3D& normal) const {

    Point3D position;
    evaluate_limit_with_derivatives(face_index, u, v,
                                    position, tangent_u, tangent_v);

    // Normalize tangents
    auto normalize = [](Point3D& v) {
        float len = std::sqrt(v.x*v.x + v.y*v.y + v.z*v.z);
        if (len > 1e-8f) {
            v.x /= len; v.y /= len; v.z /= len;
        }
    };

    normalize(tangent_u);
    normalize(tangent_v);

    // Normal = cross(tangent_u, tangent_v)
    normal.x = tangent_u.y * tangent_v.z - tangent_u.z * tangent_v.y;
    normal.y = tangent_u.z * tangent_v.x - tangent_u.x * tangent_v.z;
    normal.z = tangent_u.x * tangent_v.y - tangent_u.y * tangent_v.x;

    normalize(normal);
}
```

### 3. Update Python Bindings

**File**: `cpp_core/python_bindings/bindings.cpp`

Add to SubDEvaluator binding:

```cpp
.def("evaluate_limit_with_derivatives",
     [](const SubDEvaluator& eval, int face_idx, float u, float v) {
         Point3D position, du, dv;
         eval.evaluate_limit_with_derivatives(face_idx, u, v,
                                             position, du, dv);
         return py::make_tuple(position, du, dv);
     },
     "Evaluate limit position and first derivatives",
     py::arg("face_index"), py::arg("u"), py::arg("v"))

.def("evaluate_limit_with_second_derivatives",
     [](const SubDEvaluator& eval, int face_idx, float u, float v) {
         Point3D pos, du, dv, duu, dvv, duv;
         eval.evaluate_limit_with_second_derivatives(
             face_idx, u, v, pos, du, dv, duu, dvv, duv
         );
         return py::make_tuple(pos, du, dv, duu, dvv, duv);
     },
     "Evaluate limit position with first and second derivatives",
     py::arg("face_index"), py::arg("u"), py::arg("v"))

.def("batch_evaluate_limit",
     &SubDEvaluator::batch_evaluate_limit,
     "Batch evaluate multiple points on limit surface",
     py::arg("face_indices"),
     py::arg("params_u"),
     py::arg("params_v"))

.def("compute_tangent_frame",
     [](const SubDEvaluator& eval, int face_idx, float u, float v) {
         Point3D tangent_u, tangent_v, normal;
         eval.compute_tangent_frame(face_idx, u, v,
                                   tangent_u, tangent_v, normal);
         return py::make_tuple(tangent_u, tangent_v, normal);
     },
     "Compute tangent frame (tangent_u, tangent_v, normal)",
     py::arg("face_index"), py::arg("u"), py::arg("v"));
```

---

## Testing

**Test File**: `cpp_core/test_limit_evaluation.cpp`

```cpp
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"
#include <iostream>
#include <cassert>
#include <cmath>

using namespace latent;

bool approx_equal(float a, float b, float eps = 1e-4f) {
    return std::abs(a - b) < eps;
}

void test_derivatives() {
    std::cout << "Test: Derivative evaluation..." << std::endl;

    // Create simple quad
    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(1, 1, 0),
        Point3D(0, 1, 0)
    };
    cage.faces = {{0, 1, 2, 3}};

    SubDEvaluator eval;
    eval.initialize(cage);

    // Evaluate at center
    Point3D pos, du, dv;
    eval.evaluate_limit_with_derivatives(0, 0.5f, 0.5f, pos, du, dv);

    std::cout << "  Position: (" << pos.x << ", " << pos.y << ", " << pos.z << ")" << std::endl;
    std::cout << "  du: (" << du.x << ", " << du.y << ", " << du.z << ")" << std::endl;
    std::cout << "  dv: (" << dv.x << ", " << dv.y << ", " << dv.z << ")" << std::endl;

    // For a planar quad, derivatives should be constant
    // du should be approximately (1, 0, 0)
    // dv should be approximately (0, 1, 0)

    std::cout << "  ✅ Derivatives evaluated" << std::endl;
}

void test_second_derivatives() {
    std::cout << "\nTest: Second derivative evaluation..." << std::endl;

    // Create sphere-like cage
    SubDControlCage cage;
    // [Create simple SubD sphere cage]

    SubDEvaluator eval;
    eval.initialize(cage);

    Point3D pos, du, dv, duu, dvv, duv;
    eval.evaluate_limit_with_second_derivatives(
        0, 0.5f, 0.5f, pos, du, dv, duu, dvv, duv
    );

    std::cout << "  Position: (" << pos.x << ", " << pos.y << ", " << pos.z << ")" << std::endl;
    std::cout << "  Second derivatives computed" << std::endl;

    // For non-planar surface, second derivatives should be non-zero
    float mag = std::sqrt(duu.x*duu.x + duu.y*duu.y + duu.z*duu.z);
    std::cout << "  |duu| = " << mag << std::endl;

    std::cout << "  ✅ Second derivatives evaluated" << std::endl;
}

void test_batch_evaluation() {
    std::cout << "\nTest: Batch evaluation..." << std::endl;

    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0), Point3D(1, 0, 0),
        Point3D(1, 1, 0), Point3D(0, 1, 0)
    };
    cage.faces = {{0, 1, 2, 3}};

    SubDEvaluator eval;
    eval.initialize(cage);

    // Evaluate grid of points
    std::vector<int> faces;
    std::vector<float> us, vs;

    for (int i = 0; i < 10; ++i) {
        for (int j = 0; j < 10; ++j) {
            faces.push_back(0);
            us.push_back(i / 9.0f);
            vs.push_back(j / 9.0f);
        }
    }

    TessellationResult result = eval.batch_evaluate_limit(faces, us, vs);

    assert(result.vertex_count() == 100);
    std::cout << "  Evaluated " << result.vertex_count() << " points" << std::endl;

    // Check all normals are unit length
    for (size_t i = 0; i < result.vertex_count(); ++i) {
        float nx = result.normals[i*3 + 0];
        float ny = result.normals[i*3 + 1];
        float nz = result.normals[i*3 + 2];
        float len = std::sqrt(nx*nx + ny*ny + nz*nz);
        assert(approx_equal(len, 1.0f, 0.01f));
    }

    std::cout << "  ✅ Batch evaluation working" << std::endl;
}

void test_tangent_frame() {
    std::cout << "\nTest: Tangent frame computation..." << std::endl;

    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0), Point3D(1, 0, 0),
        Point3D(1, 1, 0), Point3D(0, 1, 0)
    };
    cage.faces = {{0, 1, 2, 3}};

    SubDEvaluator eval;
    eval.initialize(cage);

    Point3D tu, tv, n;
    eval.compute_tangent_frame(0, 0.5f, 0.5f, tu, tv, n);

    // Check all are unit vectors
    auto check_unit = [](const Point3D& v, const char* name) {
        float len = std::sqrt(v.x*v.x + v.y*v.y + v.z*v.z);
        std::cout << "  |" << name << "| = " << len << std::endl;
        assert(approx_equal(len, 1.0f, 0.01f));
    };

    check_unit(tu, "tangent_u");
    check_unit(tv, "tangent_v");
    check_unit(n, "normal");

    // Check orthogonality (tu · tv ≈ 0 for orthogonal surface)
    float dot = tu.x*tv.x + tu.y*tv.y + tu.z*tv.z;
    std::cout << "  tu · tv = " << dot << " (should be ~0 for orthogonal)" << std::endl;

    std::cout << "  ✅ Tangent frame computed correctly" << std::endl;
}

int main() {
    try {
        test_derivatives();
        test_second_derivatives();
        test_batch_evaluation();
        test_tangent_frame();

        std::cout << "\n✅ ALL LIMIT EVALUATION TESTS PASSED!" << std::endl;
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "\n❌ TEST FAILED: " << e.what() << std::endl;
        return 1;
    }
}
```

**Build and run**:
```bash
cd cpp_core/build
cmake ..
make test_limit_evaluation
./test_limit_evaluation
```

---

## Success Criteria

- [ ] Header updated with new method declarations
- [ ] All methods implemented correctly
- [ ] PatchTable created and cached properly
- [ ] Derivatives computed accurately
- [ ] Second derivatives working
- [ ] Batch evaluation efficient (>10K points/sec)
- [ ] Tangent frames orthonormal
- [ ] Python bindings expose all new methods
- [ ] All tests pass
- [ ] No memory leaks

---

## Performance Notes

**Expected Performance**:
- Single derivative evaluation: <0.1ms
- Batch evaluation (1000 points): <10ms
- PatchTable creation (one-time): <50ms

**Memory**:
- PatchTable: ~500 bytes per control face
- Cached after first evaluation

---

## Integration Notes

**Used by**:
- Day 4: Curvature analysis will use second derivatives
- Day 5: Spectral decomposition will use batch evaluation
- Day 7: NURBS fitting will query limit points densely

**Depends on**:
- Day 1: SubDEvaluator base class
- OpenSubdiv PatchTable API

**File Updates**:
```
cpp_core/
├── geometry/
│   ├── subd_evaluator.h         (Update) ← HERE
│   └── subd_evaluator.cpp       (Update) ← HERE
├── python_bindings/
│   └── bindings.cpp             (Update) ← HERE
└── test_limit_evaluation.cpp    (Create) ← HERE
```

---

## Common Issues

**Issue**: "PatchTable creation failed"
- **Fix**: Ensure refiner was refined (call RefineUniform first)
- **Fix**: Check end cap type matches topology

**Issue**: "Invalid patch handle"
- **Fix**: Verify face_index < face_count
- **Fix**: Check u,v in [0,1] range

**Issue**: "Derivatives are zero"
- **Fix**: Ensure control positions are set correctly
- **Fix**: Check patch evaluation is using right basis

---

## Output Format

Provide:
1. Updated `subd_evaluator.h` with new declarations
2. Updated `subd_evaluator.cpp` with implementations
3. Updated `bindings.cpp` with Python exposure
4. Complete `test_limit_evaluation.cpp`
5. Test output showing all tests passing
6. Performance measurements
7. Integration notes

---

**Ready to begin!**
