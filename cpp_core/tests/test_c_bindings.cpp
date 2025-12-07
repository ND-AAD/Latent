// cpp_core/tests/test_c_bindings.cpp
#include <gtest/gtest.h>
#include "c_bindings/latent_core.h"
#include "c_bindings/latent_curves.h"
#include "c_bindings/latent_analysis.h"
#include <cmath>

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

TEST_F(CBindingsTest, EvaluatorDestroyNull) {
    // Should not crash
    latent_evaluator_destroy(nullptr);
}

TEST_F(CBindingsTest, EvaluatorInitialization) {
    EXPECT_TRUE(latent_evaluator_is_initialized(evaluator));
    EXPECT_EQ(latent_evaluator_get_face_count(evaluator), 6);
}

TEST_F(CBindingsTest, EvaluatorUninitializedCheck) {
    auto h = latent_evaluator_create();
    EXPECT_FALSE(latent_evaluator_is_initialized(h));
    EXPECT_EQ(latent_evaluator_get_face_count(h), 0);
    latent_evaluator_destroy(h);
}

TEST_F(CBindingsTest, ForwardEvaluation) {
    float x, y, z;
    bool result = latent_evaluate_point(evaluator, 0, 0.5f, 0.5f, &x, &y, &z);

    EXPECT_TRUE(result);
    EXPECT_FALSE(std::isnan(x));
    EXPECT_FALSE(std::isnan(y));
    EXPECT_FALSE(std::isnan(z));
}

TEST_F(CBindingsTest, ForwardEvaluationCorners) {
    float x, y, z;

    // Test all four corners of face 0
    EXPECT_TRUE(latent_evaluate_point(evaluator, 0, 0.0f, 0.0f, &x, &y, &z));
    EXPECT_FALSE(std::isnan(x));

    EXPECT_TRUE(latent_evaluate_point(evaluator, 0, 1.0f, 0.0f, &x, &y, &z));
    EXPECT_FALSE(std::isnan(x));

    EXPECT_TRUE(latent_evaluate_point(evaluator, 0, 0.0f, 1.0f, &x, &y, &z));
    EXPECT_FALSE(std::isnan(x));

    EXPECT_TRUE(latent_evaluate_point(evaluator, 0, 1.0f, 1.0f, &x, &y, &z));
    EXPECT_FALSE(std::isnan(x));
}

TEST_F(CBindingsTest, NormalEvaluation) {
    float nx, ny, nz;
    bool result = latent_evaluate_normal(evaluator, 0, 0.5f, 0.5f, &nx, &ny, &nz);

    EXPECT_TRUE(result);

    // Normal should be unit length
    float length = std::sqrt(nx*nx + ny*ny + nz*nz);
    EXPECT_NEAR(length, 1.0f, 0.01f);
}

TEST_F(CBindingsTest, PointAndNormalEvaluation) {
    float x, y, z, nx, ny, nz;
    bool result = latent_evaluate_point_and_normal(
        evaluator, 0, 0.5f, 0.5f, &x, &y, &z, &nx, &ny, &nz
    );

    EXPECT_TRUE(result);
    EXPECT_FALSE(std::isnan(x));
    EXPECT_FALSE(std::isnan(nx));

    // Normal should be unit length
    float length = std::sqrt(nx*nx + ny*ny + nz*nz);
    EXPECT_NEAR(length, 1.0f, 0.01f);
}

TEST_F(CBindingsTest, ProjectionStub) {
    // Projection is not yet implemented (waiting for Agent 1A)
    int face_id;
    float u, v;
    bool result = latent_project_point(evaluator, 0, 0, 0, &face_id, &u, &v);

    // Should return false (not implemented)
    EXPECT_FALSE(result);
}

TEST_F(CBindingsTest, TessellationSizeQuery) {
    int vertex_count = 0;
    int triangle_count = 0;

    // Query sizes only
    bool result = latent_tessellate(
        evaluator, 2, nullptr, nullptr, nullptr,
        &vertex_count, &triangle_count
    );

    EXPECT_TRUE(result);
    EXPECT_GT(vertex_count, 0);
    EXPECT_GT(triangle_count, 0);
}

TEST_F(CBindingsTest, TessellationFullGeneration) {
    int vertex_count = 0;
    int triangle_count = 0;

    // Query sizes
    latent_tessellate(
        evaluator, 1, nullptr, nullptr, nullptr,
        &vertex_count, &triangle_count
    );

    // Allocate arrays
    std::vector<float> verts(vertex_count * 3);
    std::vector<float> normals(vertex_count * 3);
    std::vector<int> tris(triangle_count * 3);

    // Generate mesh
    bool result = latent_tessellate(
        evaluator, 1,
        verts.data(), normals.data(), tris.data(),
        &vertex_count, &triangle_count
    );

    EXPECT_TRUE(result);

    // Verify data is valid
    for (float v : verts) {
        EXPECT_FALSE(std::isnan(v));
    }
    for (float n : normals) {
        EXPECT_FALSE(std::isnan(n));
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
    EXPECT_EQ(latent_curve_get_degree(curve), 1);

    latent_curve_destroy(curve);
}

TEST_F(CBindingsTest, CurveDestroyNull) {
    // Should not crash
    latent_curve_destroy(nullptr);
}

TEST_F(CBindingsTest, CurveCreateInvalidInputs) {
    int face_ids[] = {0, 0};
    float us[] = {0.0f, 1.0f};
    float vs[] = {0.5f, 0.5f};

    // Null inputs
    EXPECT_EQ(latent_curve_create(nullptr, us, vs, 2, LATENT_CURVE_BEZIER, 1), nullptr);
    EXPECT_EQ(latent_curve_create(face_ids, nullptr, vs, 2, LATENT_CURVE_BEZIER, 1), nullptr);
    EXPECT_EQ(latent_curve_create(face_ids, us, nullptr, 2, LATENT_CURVE_BEZIER, 1), nullptr);

    // Zero count
    EXPECT_EQ(latent_curve_create(face_ids, us, vs, 0, LATENT_CURVE_BEZIER, 1), nullptr);
}

TEST_F(CBindingsTest, CurveEvaluation) {
    // Curve evaluation now works with Agent 1B's SurfaceCurve
    int face_ids[] = {0, 0};
    float us[] = {0.0f, 1.0f};
    float vs[] = {0.5f, 0.5f};

    auto curve = latent_curve_create(face_ids, us, vs, 2, LATENT_CURVE_LINEAR, 1);

    float x, y, z;
    bool result = latent_curve_evaluate(curve, evaluator, 0.5f, &x, &y, &z);

    EXPECT_TRUE(result);
    EXPECT_FALSE(std::isnan(x));
    EXPECT_FALSE(std::isnan(y));
    EXPECT_FALSE(std::isnan(z));

    latent_curve_destroy(curve);
}

TEST_F(CBindingsTest, CurveSampling) {
    // Curve sampling now works with Agent 1B's SurfaceCurve
    int face_ids[] = {0, 0, 0};
    float us[] = {0.0f, 0.5f, 1.0f};
    float vs[] = {0.0f, 0.8f, 1.0f};

    auto curve = latent_curve_create(face_ids, us, vs, 3, LATENT_CURVE_BEZIER, 2);

    float points[30];  // 10 samples * 3 coords
    bool result = latent_curve_sample(curve, evaluator, 10, points);

    EXPECT_TRUE(result);

    // Verify all points are valid
    for (int i = 0; i < 30; ++i) {
        EXPECT_FALSE(std::isnan(points[i]));
    }

    latent_curve_destroy(curve);
}

TEST_F(CBindingsTest, CurveParametricEvaluation) {
    int face_ids[] = {0, 0};
    float us[] = {0.2f, 0.8f};
    float vs[] = {0.3f, 0.7f};

    auto curve = latent_curve_create(face_ids, us, vs, 2, LATENT_CURVE_LINEAR, 1);

    int out_face_id;
    float out_u, out_v;
    bool result = latent_curve_evaluate_parametric(curve, 0.0f, &out_face_id, &out_u, &out_v);

    EXPECT_TRUE(result);
    EXPECT_EQ(out_face_id, 0);
    EXPECT_NEAR(out_u, 0.2f, 0.01f);
    EXPECT_NEAR(out_v, 0.3f, 0.01f);

    latent_curve_destroy(curve);
}

TEST_F(CBindingsTest, CurveArcLength) {
    int face_ids[] = {0, 0};
    float us[] = {0.0f, 1.0f};
    float vs[] = {0.0f, 1.0f};

    auto curve = latent_curve_create(face_ids, us, vs, 2, LATENT_CURVE_LINEAR, 1);

    float length;
    bool result = latent_curve_arc_length(curve, evaluator, &length);

    EXPECT_TRUE(result);
    EXPECT_GT(length, 0.0f);
    EXPECT_FALSE(std::isnan(length));

    latent_curve_destroy(curve);
}

TEST_F(CBindingsTest, CurveTypes) {
    int face_ids[] = {0, 0, 0};
    float us[] = {0.0f, 0.5f, 1.0f};
    float vs[] = {0.0f, 0.5f, 1.0f};

    // Test all curve types
    auto linear = latent_curve_create(face_ids, us, vs, 3, LATENT_CURVE_LINEAR, 1);
    EXPECT_EQ(latent_curve_get_type(linear), LATENT_CURVE_LINEAR);
    latent_curve_destroy(linear);

    auto bezier = latent_curve_create(face_ids, us, vs, 3, LATENT_CURVE_BEZIER, 2);
    EXPECT_EQ(latent_curve_get_type(bezier), LATENT_CURVE_BEZIER);
    EXPECT_EQ(latent_curve_get_degree(bezier), 2);
    latent_curve_destroy(bezier);

    auto bspline = latent_curve_create(face_ids, us, vs, 3, LATENT_CURVE_BSPLINE, 3);
    EXPECT_EQ(latent_curve_get_type(bspline), LATENT_CURVE_BSPLINE);
    EXPECT_EQ(latent_curve_get_degree(bspline), 3);
    latent_curve_destroy(bspline);
}

//=============================================================================
// Curvature Tests
//=============================================================================

TEST_F(CBindingsTest, CurvatureComputation) {
    float k1, k2, H, K;
    bool result = latent_compute_curvature(evaluator, 0, 0.5f, 0.5f, &k1, &k2, &H, &K);

    EXPECT_TRUE(result);

    // Verify values are finite
    EXPECT_FALSE(std::isnan(k1));
    EXPECT_FALSE(std::isnan(k2));
    EXPECT_FALSE(std::isnan(H));
    EXPECT_FALSE(std::isnan(K));

    // Verify relationships
    EXPECT_FLOAT_EQ(H, (k1 + k2) / 2.0f);
    EXPECT_FLOAT_EQ(K, k1 * k2);
}

TEST_F(CBindingsTest, CurvatureDirections) {
    float dir1[3], dir2[3];
    bool result = latent_compute_curvature_directions(evaluator, 0, 0.5f, 0.5f, dir1, dir2);

    EXPECT_TRUE(result);

    // Verify directions are valid
    for (int i = 0; i < 3; ++i) {
        EXPECT_FALSE(std::isnan(dir1[i]));
        EXPECT_FALSE(std::isnan(dir2[i]));
    }

    // Directions should be unit vectors
    float len1 = std::sqrt(dir1[0]*dir1[0] + dir1[1]*dir1[1] + dir1[2]*dir1[2]);
    float len2 = std::sqrt(dir2[0]*dir2[0] + dir2[1]*dir2[1] + dir2[2]*dir2[2]);
    EXPECT_NEAR(len1, 1.0f, 0.01f);
    EXPECT_NEAR(len2, 1.0f, 0.01f);

    // Directions should be orthogonal
    float dot = dir1[0]*dir2[0] + dir1[1]*dir2[1] + dir1[2]*dir2[2];
    EXPECT_NEAR(dot, 0.0f, 0.01f);
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

TEST_F(CBindingsTest, CurvatureGridDifferentResolutions) {
    for (int res = 2; res <= 10; res += 2) {
        std::vector<float> H(res * res);
        std::vector<float> K(res * res);

        bool result = latent_sample_curvature_grid(evaluator, 0, res, H.data(), K.data());
        EXPECT_TRUE(result);

        // Verify all values are finite
        for (int i = 0; i < res * res; ++i) {
            EXPECT_FALSE(std::isnan(H[i]));
            EXPECT_FALSE(std::isnan(K[i]));
        }
    }
}

//=============================================================================
// Error Handling Tests
//=============================================================================

TEST(CBindingsErrorTest, NullHandles) {
    float dummy;
    int idummy;

    // Evaluator operations
    EXPECT_FALSE(latent_evaluator_is_initialized(nullptr));
    EXPECT_EQ(latent_evaluator_get_face_count(nullptr), 0);
    EXPECT_FALSE(latent_evaluate_point(nullptr, 0, 0, 0, &dummy, &dummy, &dummy));
    EXPECT_FALSE(latent_evaluate_normal(nullptr, 0, 0, 0, &dummy, &dummy, &dummy));

    // Curve operations
    EXPECT_FALSE(latent_curve_evaluate(nullptr, nullptr, 0, &dummy, &dummy, &dummy));
    EXPECT_EQ(latent_curve_get_point_count(nullptr), 0);

    // Analysis operations
    EXPECT_FALSE(latent_compute_curvature(nullptr, 0, 0, 0, &dummy, &dummy, &dummy, &dummy));
}

TEST(CBindingsErrorTest, NullOutputPointers) {
    auto eval = latent_evaluator_create();
    ASSERT_NE(eval, nullptr);

    // Initialize with minimal data
    float verts[] = {0,0,0, 1,0,0, 1,1,0, 0,1,0};
    int faces[] = {0,1,2,3};
    int sizes[] = {4};
    latent_evaluator_initialize(eval, verts, 4, faces, sizes, 1, nullptr, nullptr, 0);

    float dummy;

    // Null output pointers should fail
    EXPECT_FALSE(latent_evaluate_point(eval, 0, 0, 0, nullptr, &dummy, &dummy));
    EXPECT_FALSE(latent_evaluate_point(eval, 0, 0, 0, &dummy, nullptr, &dummy));
    EXPECT_FALSE(latent_evaluate_point(eval, 0, 0, 0, &dummy, &dummy, nullptr));

    EXPECT_FALSE(latent_evaluate_normal(eval, 0, 0, 0, nullptr, &dummy, &dummy));

    EXPECT_FALSE(latent_compute_curvature(eval, 0, 0, 0, nullptr, &dummy, &dummy, &dummy));

    latent_evaluator_destroy(eval);
}

TEST(CBindingsErrorTest, InvalidParameters) {
    auto eval = latent_evaluator_create();

    // Initialize with null vertices should fail
    int faces[] = {0,1,2,3};
    int sizes[] = {4};
    EXPECT_FALSE(latent_evaluator_initialize(eval, nullptr, 4, faces, sizes, 1, nullptr, nullptr, 0));

    latent_evaluator_destroy(eval);
}

//=============================================================================
// Integration Tests
//=============================================================================

TEST_F(CBindingsTest, EvaluateAllFaces) {
    float x, y, z;

    // Should be able to evaluate center of every face
    for (int face = 0; face < 6; ++face) {
        bool result = latent_evaluate_point(evaluator, face, 0.5f, 0.5f, &x, &y, &z);
        EXPECT_TRUE(result) << "Failed on face " << face;
        EXPECT_FALSE(std::isnan(x)) << "NaN on face " << face;
    }
}

TEST_F(CBindingsTest, CurvatureOnAllFaces) {
    float k1, k2, H, K;

    // Should be able to compute curvature on every face
    for (int face = 0; face < 6; ++face) {
        bool result = latent_compute_curvature(evaluator, face, 0.5f, 0.5f, &k1, &k2, &H, &K);
        EXPECT_TRUE(result) << "Failed on face " << face;
        EXPECT_FALSE(std::isnan(H)) << "NaN on face " << face;
    }
}
