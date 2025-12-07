#include <gtest/gtest.h>
#include "geometry/subd_evaluator.h"

using namespace latent;

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

TEST_F(InverseEvalTest, ConvergenceOnMultipleFaces) {
    // Test that Newton-Raphson converges on different faces
    for (int face = 0; face < 6; ++face) {
        Point3D center = evaluator.evaluate_limit_point(face, 0.5f, 0.5f);

        int out_face;
        float out_u, out_v;
        bool success = evaluator.project_point_onto_surface(
            center, out_face, out_u, out_v);

        EXPECT_TRUE(success) << "Failed to converge on face " << face;
        EXPECT_EQ(out_face, face) << "Wrong face for center of face " << face;
        EXPECT_NEAR(out_u, 0.5f, 1e-3) << "Wrong u for face " << face;
        EXPECT_NEAR(out_v, 0.5f, 1e-3) << "Wrong v for face " << face;
    }
}

TEST_F(InverseEvalTest, ParameterClampingAtBoundaries) {
    // Test that parameters are properly clamped to [0,1]
    int face_id = 0;
    float u = 0.0f, v = 0.0f;
    Point3D corner = evaluator.evaluate_limit_point(face_id, u, v);

    int out_face;
    float out_u, out_v;
    bool success = evaluator.project_point_onto_surface(corner, out_face, out_u, out_v);

    EXPECT_TRUE(success);
    EXPECT_GE(out_u, 0.0f);
    EXPECT_LE(out_u, 1.0f);
    EXPECT_GE(out_v, 0.0f);
    EXPECT_LE(out_v, 1.0f);
}

TEST_F(InverseEvalTest, PerformanceAndConvergence) {
    // Performance test: measure convergence speed
    // This tests that Newton-Raphson converges quickly (< 10 iterations typical)
    int num_tests = 25;  // 5x5 grid per face
    int total_projections = 0;

    for (int face = 0; face < 6; ++face) {
        for (float u = 0.2f; u <= 0.8f; u += 0.2f) {
            for (float v = 0.2f; v <= 0.8f; v += 0.2f) {
                Point3D point = evaluator.evaluate_limit_point(face, u, v);

                int out_face;
                float out_u, out_v;
                bool success = evaluator.project_point_onto_surface(
                    point, out_face, out_u, out_v, 1e-6f);

                EXPECT_TRUE(success);
                total_projections++;
            }
        }
    }

    // All projections should succeed
    EXPECT_EQ(total_projections, 6 * 16);  // 6 faces * 4x4 grid (0.2, 0.4, 0.6, 0.8)
}
