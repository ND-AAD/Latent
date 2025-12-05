# Agent 1A: Inverse Surface Evaluation

## Objective

Implement 3D point → (face_id, u, v) projection onto SubD limit surface using Newton-Raphson iteration.

## Working Directory

`/Users/NickDuch/.claude-worktrees/Latent/focused-robinson`

## Read First

- `cpp_core/geometry/subd_evaluator.h` - existing evaluator interface
- `cpp_core/geometry/subd_evaluator.cpp` - current implementation
- `CLAUDE.md` - lossless architecture principles

## Files to Modify

1. `cpp_core/geometry/subd_evaluator.h` - add method declarations
2. `cpp_core/geometry/subd_evaluator.cpp` - add implementations

## Files to Create

1. `cpp_core/tests/test_inverse_eval.cpp` - unit tests

## Tasks

### 1. Add Method Declarations to subd_evaluator.h

```cpp
/**
 * Project a 3D point onto the limit surface.
 *
 * Uses Newton-Raphson iteration to find the closest point on the surface.
 * Searches all faces and returns the one with minimum distance.
 *
 * @param point The 3D point to project
 * @param out_face_id Output: face index of closest point
 * @param out_u Output: u parameter [0,1]
 * @param out_v Output: v parameter [0,1]
 * @param tolerance Convergence tolerance (default 1e-6)
 * @return true if projection succeeded within tolerance
 */
bool project_point_onto_surface(
    const Point3D& point,
    int& out_face_id,
    float& out_u,
    float& out_v,
    float tolerance = 1e-6f
);

/**
 * Invert a point known to be on the surface.
 *
 * Faster than project_point_onto_surface when point is exact.
 *
 * @param surface_point Point that lies exactly on the surface
 * @param out_face_id Output: face index
 * @param out_u Output: u parameter
 * @param out_v Output: v parameter
 * @return true if inversion succeeded
 */
bool invert_surface_point(
    const Point3D& surface_point,
    int& out_face_id,
    float& out_u,
    float& out_v
);
```

### 2. Implement Newton-Raphson Projection

```cpp
bool SubDEvaluator::project_point_onto_surface(
    const Point3D& point,
    int& out_face_id,
    float& out_u,
    float& out_v,
    float tolerance)
{
    float min_distance_sq = std::numeric_limits<float>::max();
    int best_face = -1;
    float best_u = 0.0f, best_v = 0.0f;

    const int max_iterations = 20;

    for (int face = 0; face < get_control_face_count(); ++face) {
        // Start from face center
        float u = 0.5f, v = 0.5f;

        for (int iter = 0; iter < max_iterations; ++iter) {
            // Evaluate surface and derivatives
            Point3D S;
            Vector3 dS_du, dS_dv;
            evaluate_limit_with_derivatives(face, u, v, S, dS_du, dS_dv);

            // Residual vector: S(u,v) - point
            Vector3 r = S - point;
            float dist_sq = r.length_squared();

            // Check convergence
            if (dist_sq < tolerance * tolerance) {
                if (dist_sq < min_distance_sq) {
                    min_distance_sq = dist_sq;
                    best_face = face;
                    best_u = u;
                    best_v = v;
                }
                break;
            }

            // Build Jacobian: J = [dS_du · r, dS_dv · r]
            // Gauss-Newton: solve (J^T J) Δ = -J^T r
            float a11 = dS_du.dot(dS_du);
            float a12 = dS_du.dot(dS_dv);
            float a22 = dS_dv.dot(dS_dv);
            float b1 = -dS_du.dot(r);
            float b2 = -dS_dv.dot(r);

            // Solve 2x2 system
            float det = a11 * a22 - a12 * a12;
            if (std::abs(det) < 1e-10f) break;  // Singular

            float du = (a22 * b1 - a12 * b2) / det;
            float dv = (a11 * b2 - a12 * b1) / det;

            // Line search with damping if needed
            float alpha = 1.0f;
            u += alpha * du;
            v += alpha * dv;

            // Clamp to [0,1]
            u = std::clamp(u, 0.0f, 1.0f);
            v = std::clamp(v, 0.0f, 1.0f);
        }

        // Even if not converged, check if this face is closer
        Point3D S = evaluate_limit_point(face, u, v);
        float dist_sq = (S - point).length_squared();
        if (dist_sq < min_distance_sq) {
            min_distance_sq = dist_sq;
            best_face = face;
            best_u = u;
            best_v = v;
        }
    }

    if (best_face >= 0) {
        out_face_id = best_face;
        out_u = best_u;
        out_v = best_v;
        return min_distance_sq < tolerance * tolerance * 100;  // Allow some slack
    }

    return false;
}

bool SubDEvaluator::invert_surface_point(
    const Point3D& surface_point,
    int& out_face_id,
    float& out_u,
    float& out_v)
{
    // For exact surface points, use tighter tolerance
    return project_point_onto_surface(surface_point, out_face_id, out_u, out_v, 1e-8f);
}
```

### 3. Create Unit Tests

```cpp
// cpp_core/tests/test_inverse_eval.cpp
#include <gtest/gtest.h>
#include "geometry/subd_evaluator.h"

class InverseEvalTest : public ::testing::Test {
protected:
    SubDEvaluator evaluator;

    void SetUp() override {
        // Initialize with unit cube control cage
        std::vector<float> vertices = {
            // 8 vertices of a cube
            -1, -1, -1,  1, -1, -1,  1, 1, -1,  -1, 1, -1,
            -1, -1,  1,  1, -1,  1,  1, 1,  1,  -1, 1,  1
        };
        std::vector<int> faces = {
            0, 1, 2, 3,  // bottom
            4, 7, 6, 5,  // top
            0, 4, 5, 1,  // front
            2, 6, 7, 3,  // back
            0, 3, 7, 4,  // left
            1, 5, 6, 2   // right
        };
        std::vector<int> face_sizes = {4, 4, 4, 4, 4, 4};

        evaluator.initialize(vertices.data(), vertices.size() / 3,
                            faces.data(), face_sizes.data(), 6,
                            nullptr, nullptr, 0);
    }
};

TEST_F(InverseEvalTest, ProjectExactSurfacePoint) {
    // Evaluate a known point
    int face_id = 0;
    float u = 0.5f, v = 0.5f;
    Point3D point = evaluator.evaluate_limit_point(face_id, u, v);

    // Project it back
    int out_face;
    float out_u, out_v;
    bool success = evaluator.project_point_onto_surface(point, out_face, out_u, out_v);

    EXPECT_TRUE(success);
    EXPECT_EQ(out_face, face_id);
    EXPECT_NEAR(out_u, u, 1e-4);
    EXPECT_NEAR(out_v, v, 1e-4);
}

TEST_F(InverseEvalTest, ProjectMultiplePoints) {
    // Test projection at various positions on each face
    for (int face = 0; face < 6; ++face) {
        for (float u = 0.1f; u <= 0.9f; u += 0.2f) {
            for (float v = 0.1f; v <= 0.9f; v += 0.2f) {
                Point3D point = evaluator.evaluate_limit_point(face, u, v);

                int out_face;
                float out_u, out_v;
                bool success = evaluator.project_point_onto_surface(
                    point, out_face, out_u, out_v);

                EXPECT_TRUE(success) << "Failed at face=" << face
                                     << " u=" << u << " v=" << v;
            }
        }
    }
}

TEST_F(InverseEvalTest, ProjectOffSurfacePoint) {
    // Point not on surface - should project to closest
    Point3D off_surface(0, 0, 2);  // Above the cube

    int out_face;
    float out_u, out_v;
    bool success = evaluator.project_point_onto_surface(
        off_surface, out_face, out_u, out_v, 0.1f);  // Larger tolerance

    // Should find the top face
    EXPECT_TRUE(success);
    EXPECT_EQ(out_face, 1);  // top face
}

TEST_F(InverseEvalTest, InvertExactPoint) {
    // Test invert_surface_point for exact points
    int face_id = 2;
    float u = 0.3f, v = 0.7f;
    Point3D point = evaluator.evaluate_limit_point(face_id, u, v);

    int out_face;
    float out_u, out_v;
    bool success = evaluator.invert_surface_point(point, out_face, out_u, out_v);

    EXPECT_TRUE(success);
    EXPECT_NEAR(out_u, u, 1e-6);
    EXPECT_NEAR(out_v, v, 1e-6);
}
```

## Success Criteria

- [ ] `project_point_onto_surface()` converges for points on surface
- [ ] Projection accuracy < 1e-4 for exact surface points
- [ ] Handles all faces correctly (searches entire surface)
- [ ] `invert_surface_point()` works for exact points with tighter tolerance
- [ ] Off-surface points project to closest surface point
- [ ] All unit tests pass

## Verification Commands

```bash
cd cpp_core/build
cmake .. && make -j4
./test_inverse_eval
```

## Do Not Modify

- Files in `c_bindings/` (Agent 1C's domain)
- Files outside `geometry/` directory
- Existing test files (only add new ones)

## Skills to Use

- `superpowers:test-driven-development` - write tests first
- `superpowers:verification-before-completion` - run tests before reporting

## Report

When complete, provide:
1. Test output showing all tests pass
2. Performance note: average iterations to converge
3. Any edge cases discovered and handled
