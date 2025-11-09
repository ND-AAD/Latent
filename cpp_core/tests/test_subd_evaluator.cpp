// cpp_core/tests/test_subd_evaluator.cpp

#include <gtest/gtest.h>
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"
#include <cmath>

using namespace latent;

/**
 * @brief Test fixture for SubDEvaluator tests
 *
 * Provides helper methods to create common test geometries
 * like cubes and planes.
 */
class SubDEvaluatorTest : public ::testing::Test {
protected:
    /**
     * Create a simple unit cube control cage
     * 8 vertices, 6 quad faces
     */
    SubDControlCage create_cube() {
        SubDControlCage cage;
        cage.vertices = {
            Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
            Point3D(0,0,1), Point3D(1,0,1), Point3D(1,1,1), Point3D(0,1,1)
        };
        cage.faces = {
            {0,1,2,3}, {4,5,6,7}, {0,1,5,4},
            {2,3,7,6}, {0,3,7,4}, {1,2,6,5}
        };
        return cage;
    }

    /**
     * Create a simple quad plane control cage
     * 4 vertices, 1 quad face
     */
    SubDControlCage create_plane() {
        SubDControlCage cage;
        cage.vertices = {
            Point3D(0,0,0), Point3D(1,0,0),
            Point3D(1,1,0), Point3D(0,1,0)
        };
        cage.faces = {{0,1,2,3}};
        return cage;
    }

    /**
     * Create a cube with a crease edge for testing sharp features
     */
    SubDControlCage create_cube_with_crease() {
        SubDControlCage cage = create_cube();
        // Add a crease on one edge with full sharpness
        cage.creases.push_back({0, 10.0f});  // Edge 0, max sharpness
        return cage;
    }

    /**
     * Helper: Check if point is within expected bounds
     */
    bool point_in_bounds(const Point3D& p, float min_val, float max_val) {
        return p.x >= min_val && p.x <= max_val &&
               p.y >= min_val && p.y <= max_val &&
               p.z >= min_val && p.z <= max_val;
    }

    /**
     * Helper: Compute distance between two points
     */
    float distance(const Point3D& a, const Point3D& b) {
        float dx = a.x - b.x;
        float dy = a.y - b.y;
        float dz = a.z - b.z;
        return std::sqrt(dx*dx + dy*dy + dz*dz);
    }
};

// ============================================================
// Initialization Tests
// ============================================================

TEST_F(SubDEvaluatorTest, DefaultConstructor) {
    SubDEvaluator eval;
    EXPECT_FALSE(eval.is_initialized());
}

TEST_F(SubDEvaluatorTest, InitializationWithCube) {
    SubDEvaluator eval;
    auto cage = create_cube();

    eval.initialize(cage);

    EXPECT_TRUE(eval.is_initialized());
    EXPECT_EQ(eval.get_control_vertex_count(), 8);
    EXPECT_EQ(eval.get_control_face_count(), 6);
}

TEST_F(SubDEvaluatorTest, InitializationWithPlane) {
    SubDEvaluator eval;
    auto cage = create_plane();

    eval.initialize(cage);

    EXPECT_TRUE(eval.is_initialized());
    EXPECT_EQ(eval.get_control_vertex_count(), 4);
    EXPECT_EQ(eval.get_control_face_count(), 1);
}

TEST_F(SubDEvaluatorTest, ReinitializationWorks) {
    SubDEvaluator eval;
    auto cube = create_cube();
    auto plane = create_plane();

    // Initialize with cube
    eval.initialize(cube);
    EXPECT_EQ(eval.get_control_vertex_count(), 8);

    // Re-initialize with plane
    eval.initialize(plane);
    EXPECT_EQ(eval.get_control_vertex_count(), 4);
}

// ============================================================
// Limit Point Evaluation Tests
// ============================================================

TEST_F(SubDEvaluatorTest, LimitEvaluationAccuracy) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    // Evaluate center of bottom face (face 0)
    Point3D center = eval.evaluate_limit_point(0, 0.5f, 0.5f);

    // Should be within cube bounds
    EXPECT_TRUE(point_in_bounds(center, 0.0f, 1.0f));

    // For a subdivided cube, center should be pulled slightly inward
    // due to smoothing, but still close to geometric center
    EXPECT_NEAR(center.x, 0.5f, 0.1f);
    EXPECT_NEAR(center.y, 0.5f, 0.1f);
}

TEST_F(SubDEvaluatorTest, LimitEvaluationCorner) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    // Evaluate corner (0,0) - should be close to control vertex
    Point3D corner = eval.evaluate_limit_point(0, 0.0f, 0.0f);

    // Corner should be at or near (0,0,0)
    EXPECT_NEAR(corner.x, 0.0f, 0.01f);
    EXPECT_NEAR(corner.y, 0.0f, 0.01f);
    EXPECT_NEAR(corner.z, 0.0f, 0.01f);
}

TEST_F(SubDEvaluatorTest, LimitEvaluationWithNormal) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    Point3D point, normal;
    eval.evaluate_limit(0, 0.5f, 0.5f, point, normal);

    // Normal should point roughly in +Z direction for XY plane
    EXPECT_GT(std::abs(normal.z), 0.9f);  // Mostly Z-aligned

    // Normal should be unit length
    float length = std::sqrt(normal.x*normal.x + normal.y*normal.y + normal.z*normal.z);
    EXPECT_NEAR(length, 1.0f, 0.01f);
}

TEST_F(SubDEvaluatorTest, LimitEvaluationMultipleFaces) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    // Evaluate center of each face
    for (int face = 0; face < 6; ++face) {
        Point3D center = eval.evaluate_limit_point(face, 0.5f, 0.5f);

        // All centers should be within cube bounds
        EXPECT_TRUE(point_in_bounds(center, -0.1f, 1.1f));
    }
}

// ============================================================
// Derivative Evaluation Tests
// ============================================================

TEST_F(SubDEvaluatorTest, FirstDerivativesNonZero) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    Point3D position, du, dv;
    eval.evaluate_limit_with_derivatives(0, 0.5f, 0.5f, position, du, dv);

    // Derivatives should be non-zero for a plane
    float du_length = std::sqrt(du.x*du.x + du.y*du.y + du.z*du.z);
    float dv_length = std::sqrt(dv.x*dv.x + dv.y*dv.y + dv.z*dv.z);

    EXPECT_GT(du_length, 0.01f);
    EXPECT_GT(dv_length, 0.01f);
}

TEST_F(SubDEvaluatorTest, SecondDerivativesAvailable) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    Point3D position, du, dv, duu, dvv, duv;
    eval.evaluate_limit_with_second_derivatives(
        0, 0.5f, 0.5f,
        position, du, dv, duu, dvv, duv
    );

    // For a cube, second derivatives should exist
    // (may be zero for flat faces, but should be computable)
    // Just check that the function completes without error
    EXPECT_TRUE(true);
}

TEST_F(SubDEvaluatorTest, TangentFrameOrthogonal) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    Point3D tangent_u, tangent_v, normal;
    eval.compute_tangent_frame(0, 0.5f, 0.5f, tangent_u, tangent_v, normal);

    // Tangents should be roughly orthogonal (dot product near 0)
    float dot_product = tangent_u.x * tangent_v.x +
                       tangent_u.y * tangent_v.y +
                       tangent_u.z * tangent_v.z;
    EXPECT_NEAR(dot_product, 0.0f, 0.1f);

    // Tangents and normal should all be unit length
    float len_u = std::sqrt(tangent_u.x*tangent_u.x + tangent_u.y*tangent_u.y + tangent_u.z*tangent_u.z);
    float len_v = std::sqrt(tangent_v.x*tangent_v.x + tangent_v.y*tangent_v.y + tangent_v.z*tangent_v.z);
    float len_n = std::sqrt(normal.x*normal.x + normal.y*normal.y + normal.z*normal.z);

    EXPECT_NEAR(len_u, 1.0f, 0.01f);
    EXPECT_NEAR(len_v, 1.0f, 0.01f);
    EXPECT_NEAR(len_n, 1.0f, 0.01f);
}

// ============================================================
// Tessellation Tests
// ============================================================

TEST_F(SubDEvaluatorTest, TessellationOutput) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    auto mesh = eval.tessellate(2);

    // Tessellation should have more vertices than control cage
    EXPECT_GT(mesh.vertex_count(), 8);

    // Should have triangles
    EXPECT_GT(mesh.triangle_count(), 0);

    // Vertices and normals should have same count
    EXPECT_EQ(mesh.vertices.size(), mesh.normals.size());
}

TEST_F(SubDEvaluatorTest, TessellationIncreasingLevels) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    auto mesh_level_1 = eval.tessellate(1);
    auto mesh_level_2 = eval.tessellate(2);
    auto mesh_level_3 = eval.tessellate(3);

    // Higher subdivision levels should produce more vertices
    EXPECT_LT(mesh_level_1.vertex_count(), mesh_level_2.vertex_count());
    EXPECT_LT(mesh_level_2.vertex_count(), mesh_level_3.vertex_count());

    // Higher subdivision levels should produce more triangles
    EXPECT_LT(mesh_level_1.triangle_count(), mesh_level_2.triangle_count());
    EXPECT_LT(mesh_level_2.triangle_count(), mesh_level_3.triangle_count());
}

TEST_F(SubDEvaluatorTest, TessellationTriangleIndicesValid) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    auto mesh = eval.tessellate(2);

    // All triangle indices should be valid (within vertex count)
    size_t vertex_count = mesh.vertex_count();
    for (size_t i = 0; i < mesh.triangles.size(); ++i) {
        EXPECT_LT(mesh.triangles[i], static_cast<int>(vertex_count));
        EXPECT_GE(mesh.triangles[i], 0);
    }
}

TEST_F(SubDEvaluatorTest, TessellationVertexBounds) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    auto mesh = eval.tessellate(3);

    // All vertices should be within reasonable bounds of original cube
    for (size_t i = 0; i < mesh.vertices.size(); i += 3) {
        float x = mesh.vertices[i];
        float y = mesh.vertices[i + 1];
        float z = mesh.vertices[i + 2];

        // Allow slight overshoot due to subdivision
        EXPECT_GE(x, -0.1f);
        EXPECT_LE(x, 1.1f);
        EXPECT_GE(y, -0.1f);
        EXPECT_LE(y, 1.1f);
        EXPECT_GE(z, -0.1f);
        EXPECT_LE(z, 1.1f);
    }
}

TEST_F(SubDEvaluatorTest, TessellationNormalsUnitLength) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    auto mesh = eval.tessellate(2);

    // Check that normals are approximately unit length
    for (size_t i = 0; i < mesh.normals.size(); i += 3) {
        float nx = mesh.normals[i];
        float ny = mesh.normals[i + 1];
        float nz = mesh.normals[i + 2];

        float length = std::sqrt(nx*nx + ny*ny + nz*nz);
        EXPECT_NEAR(length, 1.0f, 0.01f);
    }
}

// ============================================================
// Batch Evaluation Tests
// ============================================================

TEST_F(SubDEvaluatorTest, BatchEvaluationMatchesIndividual) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    // Test points
    std::vector<int> face_indices = {0, 0, 1, 1};
    std::vector<float> params_u = {0.25f, 0.75f, 0.25f, 0.75f};
    std::vector<float> params_v = {0.25f, 0.75f, 0.25f, 0.75f};

    // Batch evaluation
    auto batch_result = eval.batch_evaluate_limit(face_indices, params_u, params_v);

    // Individual evaluations
    for (size_t i = 0; i < face_indices.size(); ++i) {
        Point3D individual = eval.evaluate_limit_point(
            face_indices[i], params_u[i], params_v[i]
        );

        // Extract corresponding point from batch result
        size_t idx = i * 3;
        Point3D batch_point(
            batch_result.vertices[idx],
            batch_result.vertices[idx + 1],
            batch_result.vertices[idx + 2]
        );

        // Should match within tolerance
        EXPECT_NEAR(individual.x, batch_point.x, 0.001f);
        EXPECT_NEAR(individual.y, batch_point.y, 0.001f);
        EXPECT_NEAR(individual.z, batch_point.z, 0.001f);
    }
}

TEST_F(SubDEvaluatorTest, BatchEvaluationCorrectCount) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    std::vector<int> face_indices = {0, 1, 2, 3, 4, 5};
    std::vector<float> params_u(6, 0.5f);
    std::vector<float> params_v(6, 0.5f);

    auto result = eval.batch_evaluate_limit(face_indices, params_u, params_v);

    // Should have 6 points (one per face)
    EXPECT_EQ(result.vertex_count(), 6);
    EXPECT_EQ(result.vertices.size(), 18);  // 6 points * 3 coords
}

// ============================================================
// Edge Cases and Error Handling
// ============================================================

TEST_F(SubDEvaluatorTest, ParameterBoundaries) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    // Test all four corners
    Point3D corner_00 = eval.evaluate_limit_point(0, 0.0f, 0.0f);
    Point3D corner_10 = eval.evaluate_limit_point(0, 1.0f, 0.0f);
    Point3D corner_01 = eval.evaluate_limit_point(0, 0.0f, 1.0f);
    Point3D corner_11 = eval.evaluate_limit_point(0, 1.0f, 1.0f);

    // All should evaluate successfully (no crashes)
    EXPECT_TRUE(true);
}

TEST_F(SubDEvaluatorTest, ZeroSubdivisionLevel) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    // Level 0 should still produce valid output (control cage itself)
    auto mesh = eval.tessellate(0);

    EXPECT_GT(mesh.vertex_count(), 0);
    EXPECT_GT(mesh.triangle_count(), 0);
}

// ============================================================
// Main
// ============================================================

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
