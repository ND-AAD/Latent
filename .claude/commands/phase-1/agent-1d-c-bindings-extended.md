# Agent 1D: C Bindings - Curve & Analysis Functions

## Objective

Create C-compatible wrappers for surface curves and curvature analysis, enabling P/Invoke from C#.

## Working Directory

`/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`

## Read First

- `cpp_core/c_bindings/latent_core.h` - existing C API (Agent 1C)
- `cpp_core/geometry/surface_curve.h` - curve class (Agent 1B)
- `cpp_core/analysis/curvature_analyzer.h` - curvature computation

## Dependencies

- **Agent 1B**: `SurfaceCurve` class must exist
- **Agent 1C**: Base C bindings must exist

If dependencies are not yet complete, create stubs with TODO comments.

## Files to Create

1. `cpp_core/c_bindings/latent_curves.h` - curve C API
2. `cpp_core/c_bindings/latent_curves.cpp` - curve implementation
3. `cpp_core/c_bindings/latent_analysis.h` - analysis C API
4. `cpp_core/c_bindings/latent_analysis.cpp` - analysis implementation
5. `cpp_core/tests/test_c_bindings.cpp` - comprehensive tests

## Files to Modify

1. `cpp_core/c_bindings/CMakeLists.txt` - add new sources

## Tasks

### 1. Create latent_curves.h

```cpp
// cpp_core/c_bindings/latent_curves.h
#ifndef LATENT_CURVES_H
#define LATENT_CURVES_H

#include "exports.h"
#include "latent_core.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// Handle Types
//=============================================================================

/** Opaque handle to surface curve */
typedef void* LatentCurveHandle;

//=============================================================================
// Curve Types
//=============================================================================

typedef enum {
    LATENT_CURVE_LINEAR = 0,
    LATENT_CURVE_BEZIER = 1,
    LATENT_CURVE_BSPLINE = 2
} LatentCurveType;

//=============================================================================
// Curve Lifecycle
//=============================================================================

/**
 * Create a surface curve from control points.
 *
 * @param face_ids Array of face indices for each control point
 * @param us Array of U parameters for each control point
 * @param vs Array of V parameters for each control point
 * @param point_count Number of control points
 * @param curve_type Type of curve interpolation
 * @param degree Curve degree (for Bezier/B-spline)
 * @return Handle to the curve, or NULL on failure
 */
LATENT_API LatentCurveHandle latent_curve_create(
    const int* face_ids,
    const float* us,
    const float* vs,
    int point_count,
    LatentCurveType curve_type,
    int degree
);

/**
 * Destroy a surface curve and free resources.
 * @param handle Curve handle (safe to call with NULL)
 */
LATENT_API void latent_curve_destroy(LatentCurveHandle handle);

//=============================================================================
// Curve Evaluation
//=============================================================================

/**
 * Evaluate a point on the curve.
 *
 * @param handle Curve handle
 * @param evaluator Evaluator handle for surface lookup
 * @param t Curve parameter [0, 1]
 * @param out_x Output X coordinate
 * @param out_y Output Y coordinate
 * @param out_z Output Z coordinate
 * @return true on success
 */
LATENT_API bool latent_curve_evaluate(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    float t,
    float* out_x, float* out_y, float* out_z
);

/**
 * Evaluate the parametric position on the curve.
 *
 * @param handle Curve handle
 * @param t Curve parameter [0, 1]
 * @param out_face_id Output face index
 * @param out_u Output U parameter
 * @param out_v Output V parameter
 * @return true on success
 */
LATENT_API bool latent_curve_evaluate_parametric(
    LatentCurveHandle handle,
    float t,
    int* out_face_id, float* out_u, float* out_v
);

/**
 * Sample the curve for display.
 *
 * @param handle Curve handle
 * @param evaluator Evaluator handle
 * @param num_samples Number of sample points
 * @param out_points Output array (must have space for num_samples * 3 floats)
 * @return true on success
 */
LATENT_API bool latent_curve_sample(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    int num_samples,
    float* out_points
);

/**
 * Get the arc length of the curve.
 *
 * @param handle Curve handle
 * @param evaluator Evaluator handle
 * @param out_length Output arc length
 * @return true on success
 */
LATENT_API bool latent_curve_arc_length(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    float* out_length
);

//=============================================================================
// Curve Properties
//=============================================================================

/**
 * Get the number of control points.
 * @param handle Curve handle
 * @return Number of control points
 */
LATENT_API int latent_curve_get_point_count(LatentCurveHandle handle);

/**
 * Get the curve type.
 * @param handle Curve handle
 * @return Curve type enum value
 */
LATENT_API LatentCurveType latent_curve_get_type(LatentCurveHandle handle);

/**
 * Get the curve degree.
 * @param handle Curve handle
 * @return Curve degree
 */
LATENT_API int latent_curve_get_degree(LatentCurveHandle handle);

#ifdef __cplusplus
}
#endif

#endif // LATENT_CURVES_H
```

### 2. Create latent_curves.cpp

```cpp
// cpp_core/c_bindings/latent_curves.cpp
#include "latent_curves.h"
#include "../geometry/surface_curve.h"
#include "../geometry/subd_evaluator.h"

using namespace latent;

//=============================================================================
// Curve Lifecycle
//=============================================================================

LATENT_API LatentCurveHandle latent_curve_create(
    const int* face_ids,
    const float* us,
    const float* vs,
    int point_count,
    LatentCurveType curve_type,
    int degree)
{
    if (!face_ids || !us || !vs || point_count <= 0) {
        return nullptr;
    }

    try {
        std::vector<ParametricPoint> points;
        points.reserve(point_count);

        for (int i = 0; i < point_count; ++i) {
            points.emplace_back(face_ids[i], us[i], vs[i]);
        }

        CurveType type;
        switch (curve_type) {
            case LATENT_CURVE_LINEAR:  type = CurveType::LINEAR; break;
            case LATENT_CURVE_BEZIER:  type = CurveType::BEZIER; break;
            case LATENT_CURVE_BSPLINE: type = CurveType::BSPLINE; break;
            default: type = CurveType::BEZIER;
        }

        return static_cast<LatentCurveHandle>(
            new SurfaceCurve(points, type, degree)
        );
    } catch (...) {
        return nullptr;
    }
}

LATENT_API void latent_curve_destroy(LatentCurveHandle handle) {
    if (handle) {
        delete static_cast<SurfaceCurve*>(handle);
    }
}

//=============================================================================
// Curve Evaluation
//=============================================================================

LATENT_API bool latent_curve_evaluate(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    float t,
    float* out_x, float* out_y, float* out_z)
{
    if (!handle || !evaluator || !out_x || !out_y || !out_z) {
        return false;
    }

    try {
        auto* curve = static_cast<SurfaceCurve*>(handle);
        auto* eval = static_cast<SubDEvaluator*>(evaluator);

        Point3D point = curve->evaluate(t, *eval);
        *out_x = point.x;
        *out_y = point.y;
        *out_z = point.z;
        return true;
    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_curve_evaluate_parametric(
    LatentCurveHandle handle,
    float t,
    int* out_face_id, float* out_u, float* out_v)
{
    if (!handle || !out_face_id || !out_u || !out_v) {
        return false;
    }

    try {
        auto* curve = static_cast<SurfaceCurve*>(handle);
        ParametricPoint p = curve->evaluate_parametric(t);

        *out_face_id = p.face_id;
        *out_u = p.u;
        *out_v = p.v;
        return p.is_valid();
    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_curve_sample(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    int num_samples,
    float* out_points)
{
    if (!handle || !evaluator || !out_points || num_samples <= 0) {
        return false;
    }

    try {
        auto* curve = static_cast<SurfaceCurve*>(handle);
        auto* eval = static_cast<SubDEvaluator*>(evaluator);

        std::vector<Point3D> samples = curve->sample(num_samples, *eval);

        for (size_t i = 0; i < samples.size(); ++i) {
            out_points[i * 3 + 0] = samples[i].x;
            out_points[i * 3 + 1] = samples[i].y;
            out_points[i * 3 + 2] = samples[i].z;
        }

        return true;
    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_curve_arc_length(
    LatentCurveHandle handle,
    LatentEvaluatorHandle evaluator,
    float* out_length)
{
    if (!handle || !evaluator || !out_length) {
        return false;
    }

    try {
        auto* curve = static_cast<SurfaceCurve*>(handle);
        auto* eval = static_cast<SubDEvaluator*>(evaluator);

        *out_length = curve->arc_length(*eval, 100);
        return true;
    } catch (...) {
        return false;
    }
}

//=============================================================================
// Curve Properties
//=============================================================================

LATENT_API int latent_curve_get_point_count(LatentCurveHandle handle) {
    if (!handle) return 0;
    auto* curve = static_cast<SurfaceCurve*>(handle);
    return static_cast<int>(curve->get_control_points().size());
}

LATENT_API LatentCurveType latent_curve_get_type(LatentCurveHandle handle) {
    if (!handle) return LATENT_CURVE_BEZIER;
    auto* curve = static_cast<SurfaceCurve*>(handle);

    switch (curve->get_type()) {
        case CurveType::LINEAR:  return LATENT_CURVE_LINEAR;
        case CurveType::BEZIER:  return LATENT_CURVE_BEZIER;
        case CurveType::BSPLINE: return LATENT_CURVE_BSPLINE;
        default: return LATENT_CURVE_BEZIER;
    }
}

LATENT_API int latent_curve_get_degree(LatentCurveHandle handle) {
    if (!handle) return 0;
    auto* curve = static_cast<SurfaceCurve*>(handle);
    return curve->get_degree();
}
```

### 3. Create latent_analysis.h

```cpp
// cpp_core/c_bindings/latent_analysis.h
#ifndef LATENT_ANALYSIS_H
#define LATENT_ANALYSIS_H

#include "exports.h"
#include "latent_core.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

//=============================================================================
// Curvature Analysis
//=============================================================================

/**
 * Compute principal curvatures at a surface point.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param u U parameter
 * @param v V parameter
 * @param out_k1 Output maximum principal curvature
 * @param out_k2 Output minimum principal curvature
 * @param out_H Output mean curvature (k1 + k2) / 2
 * @param out_K Output Gaussian curvature (k1 * k2)
 * @return true on success
 */
LATENT_API bool latent_compute_curvature(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_k1, float* out_k2,
    float* out_H, float* out_K
);

/**
 * Compute principal curvature directions at a surface point.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param u U parameter
 * @param v V parameter
 * @param out_dir1 Output direction of maximum curvature (3 floats)
 * @param out_dir2 Output direction of minimum curvature (3 floats)
 * @return true on success
 */
LATENT_API bool latent_compute_curvature_directions(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_dir1, float* out_dir2
);

/**
 * Sample curvature values across a grid on one face.
 *
 * @param handle Evaluator handle
 * @param face_id Face index
 * @param resolution Grid resolution (resolution x resolution samples)
 * @param out_H Output mean curvature values (resolution * resolution floats)
 * @param out_K Output Gaussian curvature values (resolution * resolution floats)
 * @return true on success
 */
LATENT_API bool latent_sample_curvature_grid(
    LatentEvaluatorHandle handle,
    int face_id,
    int resolution,
    float* out_H,
    float* out_K
);

#ifdef __cplusplus
}
#endif

#endif // LATENT_ANALYSIS_H
```

### 4. Create latent_analysis.cpp

```cpp
// cpp_core/c_bindings/latent_analysis.cpp
#include "latent_analysis.h"
#include "../geometry/subd_evaluator.h"
#include "../analysis/curvature_analyzer.h"

LATENT_API bool latent_compute_curvature(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_k1, float* out_k2,
    float* out_H, float* out_K)
{
    if (!handle || !out_k1 || !out_k2 || !out_H || !out_K) {
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);

        // Use CurvatureAnalyzer if available, otherwise compute directly
        CurvatureAnalyzer analyzer(*evaluator);
        float k1, k2;
        analyzer.compute_principal_curvatures(face_id, u, v, k1, k2);

        *out_k1 = k1;
        *out_k2 = k2;
        *out_H = (k1 + k2) / 2.0f;
        *out_K = k1 * k2;

        return true;
    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_compute_curvature_directions(
    LatentEvaluatorHandle handle,
    int face_id, float u, float v,
    float* out_dir1, float* out_dir2)
{
    if (!handle || !out_dir1 || !out_dir2) {
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);

        CurvatureAnalyzer analyzer(*evaluator);
        Vector3 dir1, dir2;
        analyzer.compute_principal_directions(face_id, u, v, dir1, dir2);

        out_dir1[0] = dir1.x;
        out_dir1[1] = dir1.y;
        out_dir1[2] = dir1.z;

        out_dir2[0] = dir2.x;
        out_dir2[1] = dir2.y;
        out_dir2[2] = dir2.z;

        return true;
    } catch (...) {
        return false;
    }
}

LATENT_API bool latent_sample_curvature_grid(
    LatentEvaluatorHandle handle,
    int face_id,
    int resolution,
    float* out_H,
    float* out_K)
{
    if (!handle || !out_H || !out_K || resolution <= 0) {
        return false;
    }

    try {
        auto* evaluator = static_cast<SubDEvaluator*>(handle);
        CurvatureAnalyzer analyzer(*evaluator);

        for (int j = 0; j < resolution; ++j) {
            for (int i = 0; i < resolution; ++i) {
                float u = static_cast<float>(i) / (resolution - 1);
                float v = static_cast<float>(j) / (resolution - 1);

                float k1, k2;
                analyzer.compute_principal_curvatures(face_id, u, v, k1, k2);

                int idx = j * resolution + i;
                out_H[idx] = (k1 + k2) / 2.0f;
                out_K[idx] = k1 * k2;
            }
        }

        return true;
    } catch (...) {
        return false;
    }
}
```

### 5. Create Comprehensive Tests

```cpp
// cpp_core/tests/test_c_bindings.cpp
#include <gtest/gtest.h>
#include "c_bindings/latent_core.h"
#include "c_bindings/latent_curves.h"
#include "c_bindings/latent_analysis.h"

class CBindingsTest : public ::testing::Test {
protected:
    LatentEvaluatorHandle evaluator = nullptr;

    // Unit cube vertices
    std::vector<float> vertices = {
        -1, -1, -1,  1, -1, -1,  1, 1, -1,  -1, 1, -1,
        -1, -1,  1,  1, -1,  1,  1, 1,  1,  -1, 1,  1
    };
    std::vector<int> faces = {
        0, 1, 2, 3,  4, 7, 6, 5,  0, 4, 5, 1,
        2, 6, 7, 3,  0, 3, 7, 4,  1, 5, 6, 2
    };
    std::vector<int> face_sizes = {4, 4, 4, 4, 4, 4};

    void SetUp() override {
        evaluator = latent_evaluator_create();
        ASSERT_NE(evaluator, nullptr);

        bool init = latent_evaluator_initialize(
            evaluator,
            vertices.data(), 8,
            faces.data(), face_sizes.data(), 6,
            nullptr, nullptr, 0
        );
        ASSERT_TRUE(init);
    }

    void TearDown() override {
        latent_evaluator_destroy(evaluator);
    }
};

//=============================================================================
// Evaluator Tests
//=============================================================================

TEST_F(CBindingsTest, EvaluatorLifecycle) {
    auto h = latent_evaluator_create();
    ASSERT_NE(h, nullptr);
    latent_evaluator_destroy(h);
    // No crash = success
}

TEST_F(CBindingsTest, EvaluatorInitialization) {
    EXPECT_TRUE(latent_evaluator_is_initialized(evaluator));
    EXPECT_EQ(latent_evaluator_get_face_count(evaluator), 6);
}

TEST_F(CBindingsTest, ForwardEvaluation) {
    float x, y, z;
    bool result = latent_evaluate_point(evaluator, 0, 0.5f, 0.5f, &x, &y, &z);

    EXPECT_TRUE(result);
    EXPECT_FALSE(std::isnan(x));
    EXPECT_FALSE(std::isnan(y));
    EXPECT_FALSE(std::isnan(z));
}

TEST_F(CBindingsTest, NormalEvaluation) {
    float nx, ny, nz;
    bool result = latent_evaluate_normal(evaluator, 0, 0.5f, 0.5f, &nx, &ny, &nz);

    EXPECT_TRUE(result);

    // Normal should be unit length
    float length = std::sqrt(nx*nx + ny*ny + nz*nz);
    EXPECT_NEAR(length, 1.0f, 0.01f);
}

TEST_F(CBindingsTest, ProjectionRoundTrip) {
    // Evaluate a known point
    float x, y, z;
    latent_evaluate_point(evaluator, 2, 0.3f, 0.7f, &x, &y, &z);

    // Project it back
    int face_id;
    float u, v;
    bool result = latent_project_point(evaluator, x, y, z, &face_id, &u, &v);

    if (result) {  // May fail if Agent 1A not complete
        EXPECT_NEAR(u, 0.3f, 0.01f);
        EXPECT_NEAR(v, 0.7f, 0.01f);
    }
}

//=============================================================================
// Curve Tests
//=============================================================================

TEST_F(CBindingsTest, CurveLifecycle) {
    int face_ids[] = {0, 0};
    float us[] = {0.0f, 1.0f};
    float vs[] = {0.5f, 0.5f};

    auto curve = latent_curve_create(face_ids, us, vs, 2, LATENT_CURVE_BEZIER, 1);
    ASSERT_NE(curve, nullptr);

    EXPECT_EQ(latent_curve_get_point_count(curve), 2);
    EXPECT_EQ(latent_curve_get_type(curve), LATENT_CURVE_BEZIER);

    latent_curve_destroy(curve);
}

TEST_F(CBindingsTest, CurveEvaluation) {
    int face_ids[] = {0, 0};
    float us[] = {0.0f, 1.0f};
    float vs[] = {0.5f, 0.5f};

    auto curve = latent_curve_create(face_ids, us, vs, 2, LATENT_CURVE_LINEAR, 1);

    float x, y, z;
    bool result = latent_curve_evaluate(curve, evaluator, 0.5f, &x, &y, &z);

    EXPECT_TRUE(result);
    EXPECT_FALSE(std::isnan(x));

    latent_curve_destroy(curve);
}

TEST_F(CBindingsTest, CurveSampling) {
    int face_ids[] = {0, 0, 0};
    float us[] = {0.0f, 0.5f, 1.0f};
    float vs[] = {0.0f, 0.8f, 1.0f};

    auto curve = latent_curve_create(face_ids, us, vs, 3, LATENT_CURVE_BEZIER, 2);

    float points[30];  // 10 samples * 3 coords
    bool result = latent_curve_sample(curve, evaluator, 10, points);

    EXPECT_TRUE(result);

    // All points should be valid
    for (int i = 0; i < 30; ++i) {
        EXPECT_FALSE(std::isnan(points[i]));
    }

    latent_curve_destroy(curve);
}

//=============================================================================
// Curvature Tests
//=============================================================================

TEST_F(CBindingsTest, CurvatureComputation) {
    float k1, k2, H, K;
    bool result = latent_compute_curvature(evaluator, 0, 0.5f, 0.5f, &k1, &k2, &H, &K);

    EXPECT_TRUE(result);
    EXPECT_FLOAT_EQ(H, (k1 + k2) / 2.0f);
    EXPECT_FLOAT_EQ(K, k1 * k2);
}

TEST_F(CBindingsTest, CurvatureGrid) {
    const int res = 5;
    float H[res * res];
    float K[res * res];

    bool result = latent_sample_curvature_grid(evaluator, 0, res, H, K);

    EXPECT_TRUE(result);

    // All values should be finite
    for (int i = 0; i < res * res; ++i) {
        EXPECT_FALSE(std::isnan(H[i]));
        EXPECT_FALSE(std::isnan(K[i]));
    }
}

//=============================================================================
// Error Handling Tests
//=============================================================================

TEST(CBindingsErrorTest, NullHandles) {
    float dummy;
    EXPECT_FALSE(latent_evaluate_point(nullptr, 0, 0, 0, &dummy, &dummy, &dummy));
    EXPECT_FALSE(latent_curve_evaluate(nullptr, nullptr, 0, &dummy, &dummy, &dummy));
    EXPECT_FALSE(latent_compute_curvature(nullptr, 0, 0, 0, &dummy, &dummy, &dummy, &dummy));
}

TEST(CBindingsErrorTest, NullOutputPointers) {
    auto eval = latent_evaluator_create();
    EXPECT_FALSE(latent_evaluate_point(eval, 0, 0, 0, nullptr, nullptr, nullptr));
    latent_evaluator_destroy(eval);
}
```

### 6. Update CMakeLists.txt

```cmake
# cpp_core/c_bindings/CMakeLists.txt

set(C_BINDINGS_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/latent_core.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/latent_curves.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/latent_analysis.cpp
)

target_sources(latent_core PRIVATE ${C_BINDINGS_SOURCES})

target_include_directories(latent_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

install(FILES
    exports.h
    latent_core.h
    latent_curves.h
    latent_analysis.h
    DESTINATION include/latent
)
```

## Success Criteria

- [ ] All curve functions compile and link
- [ ] All curvature functions compile and link
- [ ] Curve create/destroy works without memory leaks
- [ ] Curve sampling produces valid 3D points
- [ ] Curvature computation returns finite values
- [ ] All unit tests pass
- [ ] Error handling returns false for null pointers

## Verification Commands

```bash
cd cpp_core/build
cmake .. && make -j4
./test_c_bindings

# Check all exports
nm -gU liblatent_core.dylib | grep latent_
```

## Do Not Modify

- `latent_core.h/cpp` (Agent 1C's domain)
- Files in `geometry/` (Agent 1A/1B's domain)
- Files in `analysis/` (existing code)

## Skills to Use

- `superpowers:test-driven-development` - comprehensive test coverage
- `superpowers:verification-before-completion` - run all tests

## Report

When complete, provide:
1. Full list of exported symbols
2. Test output showing all tests pass
3. Memory check results (if valgrind available)
