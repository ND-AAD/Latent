// cpp_core/tests/test_curvature.cpp

#include <gtest/gtest.h>
#include "analysis/curvature_analyzer.h"
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"
#include <cmath>

using namespace latent;

/**
 * @brief Test fixture for curvature analysis tests
 *
 * Provides test geometries with known curvature properties:
 * - Planes (zero curvature)
 * - Spheres (constant positive curvature)
 * - Cylinders (mixed curvature)
 */
class CurvatureAnalyzerTest : public ::testing::Test {
protected:
    /**
     * Create a flat plane - should have zero curvature everywhere
     */
    SubDControlCage create_plane() {
        SubDControlCage cage;
        cage.vertices = {
            Point3D(0,0,0), Point3D(2,0,0),
            Point3D(2,2,0), Point3D(0,2,0)
        };
        cage.faces = {{0,1,2,3}};
        return cage;
    }

    /**
     * Create a sphere approximation (subdivided cube)
     * Should have positive Gaussian curvature
     */
    SubDControlCage create_sphere() {
        SubDControlCage cage;
        // Unit sphere approximation using cube vertices
        float r = 1.0f / std::sqrt(3.0f);  // Normalize to unit sphere
        cage.vertices = {
            Point3D(-r,-r,-r), Point3D(r,-r,-r), Point3D(r,r,-r), Point3D(-r,r,-r),
            Point3D(-r,-r,r), Point3D(r,-r,r), Point3D(r,r,r), Point3D(-r,r,r)
        };
        cage.faces = {
            {0,1,2,3}, {4,5,6,7}, {0,1,5,4},
            {2,3,7,6}, {0,3,7,4}, {1,2,6,5}
        };
        return cage;
    }

    /**
     * Create a cylindrical surface
     * Should have one principal curvature zero, one non-zero
     */
    SubDControlCage create_cylinder() {
        SubDControlCage cage;
        // Cylinder along Z axis, radius 1
        float angle_step = 2.0f * M_PI / 4.0f;
        for (int i = 0; i < 4; ++i) {
            float angle = i * angle_step;
            cage.vertices.push_back(Point3D(std::cos(angle), std::sin(angle), 0.0f));
        }
        for (int i = 0; i < 4; ++i) {
            float angle = i * angle_step;
            cage.vertices.push_back(Point3D(std::cos(angle), std::sin(angle), 2.0f));
        }
        // Two quad rings
        cage.faces = {
            {0,1,2,3}, {4,5,6,7},
            {0,1,5,4}, {1,2,6,5}, {2,3,7,6}, {3,0,4,7}
        };
        return cage;
    }

    /**
     * Create a saddle surface (hyperbolic paraboloid approximation)
     * Should have negative Gaussian curvature
     */
    SubDControlCage create_saddle() {
        SubDControlCage cage;
        // z = x^2 - y^2 approximation
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                float x = (i - 1.0f);
                float y = (j - 1.0f);
                float z = x*x - y*y;
                cage.vertices.push_back(Point3D(x, y, z * 0.5f));
            }
        }
        // Create quad faces
        for (int i = 0; i < 2; ++i) {
            for (int j = 0; j < 2; ++j) {
                int v0 = i * 3 + j;
                int v1 = i * 3 + (j + 1);
                int v2 = (i + 1) * 3 + (j + 1);
                int v3 = (i + 1) * 3 + j;
                cage.faces.push_back({v0, v1, v2, v3});
            }
        }
        return cage;
    }

    /**
     * Helper: Check if value is close to zero
     */
    bool is_near_zero(float value, float tolerance = 0.1f) {
        return std::abs(value) < tolerance;
    }

    /**
     * Helper: Check if curvature result is valid
     */
    bool is_valid_curvature(const CurvatureResult& curv) {
        // Check fundamental forms are non-degenerate
        if (curv.E <= 0 || curv.G <= 0) return false;

        // Check normal is unit length
        float normal_len = std::sqrt(
            curv.normal.x * curv.normal.x +
            curv.normal.y * curv.normal.y +
            curv.normal.z * curv.normal.z
        );
        if (std::abs(normal_len - 1.0f) > 0.01f) return false;

        // Check Gaussian curvature formula: K = k1 * k2
        float expected_K = curv.kappa1 * curv.kappa2;
        if (std::abs(curv.gaussian_curvature - expected_K) > 0.01f) return false;

        // Check mean curvature formula: H = (k1 + k2) / 2
        float expected_H = (curv.kappa1 + curv.kappa2) / 2.0f;
        if (std::abs(curv.mean_curvature - expected_H) > 0.01f) return false;

        return true;
    }
};

// ============================================================
// Basic Curvature Computation Tests
// ============================================================

TEST_F(CurvatureAnalyzerTest, ComputeCurvatureOnPlane) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // Plane should have zero Gaussian curvature
    EXPECT_NEAR(curv.gaussian_curvature, 0.0f, 0.1f);

    // Both principal curvatures should be near zero
    EXPECT_NEAR(curv.kappa1, 0.0f, 0.1f);
    EXPECT_NEAR(curv.kappa2, 0.0f, 0.1f);

    // Mean curvature should also be zero
    EXPECT_NEAR(curv.mean_curvature, 0.0f, 0.1f);

    // Result should be mathematically valid
    EXPECT_TRUE(is_valid_curvature(curv));
}

TEST_F(CurvatureAnalyzerTest, ComputeCurvatureOnSphere) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // Sphere should have positive Gaussian curvature
    EXPECT_GT(curv.gaussian_curvature, 0.0f);

    // Both principal curvatures should be positive and similar
    EXPECT_GT(curv.kappa1, 0.0f);
    EXPECT_GT(curv.kappa2, 0.0f);

    // For sphere, k1 ≈ k2 (within tolerance due to approximation)
    float ratio = std::abs(curv.kappa1 / curv.kappa2);
    EXPECT_GT(ratio, 0.5f);
    EXPECT_LT(ratio, 2.0f);

    // Result should be valid
    EXPECT_TRUE(is_valid_curvature(curv));
}

TEST_F(CurvatureAnalyzerTest, ComputeCurvatureOnSaddle) {
    SubDEvaluator eval;
    auto cage = create_saddle();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 2, 0.5f, 0.5f);  // Center face

    // Saddle should have negative Gaussian curvature
    EXPECT_LT(curv.gaussian_curvature, 0.0f);

    // Principal curvatures should have opposite signs
    EXPECT_NE(curv.kappa1 * curv.kappa2 > 0, true);

    // Result should be valid
    EXPECT_TRUE(is_valid_curvature(curv));
}

// ============================================================
// Principal Curvature Tests
// ============================================================

TEST_F(CurvatureAnalyzerTest, PrincipalCurvaturesOrdered) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // kappa1 should be >= kappa2 (max >= min)
    EXPECT_GE(curv.kappa1, curv.kappa2);
}

TEST_F(CurvatureAnalyzerTest, PrincipalDirectionsOrthogonal) {
    SubDEvaluator eval;
    auto cage = create_cylinder();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // Principal directions should be orthogonal
    float dot = curv.dir1.x * curv.dir2.x +
                curv.dir1.y * curv.dir2.y +
                curv.dir1.z * curv.dir2.z;

    EXPECT_NEAR(dot, 0.0f, 0.15f);
}

TEST_F(CurvatureAnalyzerTest, PrincipalDirectionsUnitLength) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // Both principal directions should be unit vectors
    float len1 = std::sqrt(curv.dir1.x*curv.dir1.x +
                          curv.dir1.y*curv.dir1.y +
                          curv.dir1.z*curv.dir1.z);
    float len2 = std::sqrt(curv.dir2.x*curv.dir2.x +
                          curv.dir2.y*curv.dir2.y +
                          curv.dir2.z*curv.dir2.z);

    EXPECT_NEAR(len1, 1.0f, 0.01f);
    EXPECT_NEAR(len2, 1.0f, 0.01f);
}

// ============================================================
// Derived Curvature Tests
// ============================================================

TEST_F(CurvatureAnalyzerTest, MeanCurvatureFormula) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // H = (k1 + k2) / 2
    float expected_H = (curv.kappa1 + curv.kappa2) / 2.0f;
    EXPECT_NEAR(curv.mean_curvature, expected_H, 0.001f);
}

TEST_F(CurvatureAnalyzerTest, GaussianCurvatureFormula) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // K = k1 * k2
    float expected_K = curv.kappa1 * curv.kappa2;
    EXPECT_NEAR(curv.gaussian_curvature, expected_K, 0.001f);
}

TEST_F(CurvatureAnalyzerTest, AbsMeanCurvature) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // abs_mean should equal |mean|
    EXPECT_NEAR(curv.abs_mean_curvature, std::abs(curv.mean_curvature), 0.001f);
    EXPECT_GE(curv.abs_mean_curvature, 0.0f);
}

TEST_F(CurvatureAnalyzerTest, RMSCurvature) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // RMS = sqrt((k1^2 + k2^2) / 2)
    float expected_rms = std::sqrt(
        (curv.kappa1 * curv.kappa1 + curv.kappa2 * curv.kappa2) / 2.0f
    );
    EXPECT_NEAR(curv.rms_curvature, expected_rms, 0.001f);
    EXPECT_GE(curv.rms_curvature, 0.0f);
}

// ============================================================
// Fundamental Form Tests
// ============================================================

TEST_F(CurvatureAnalyzerTest, FirstFundamentalFormPositive) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // E and G must be positive (metric coefficients)
    EXPECT_GT(curv.E, 0.0f);
    EXPECT_GT(curv.G, 0.0f);

    // F can be any value, but E*G - F^2 > 0 (positive definite)
    float det = curv.E * curv.G - curv.F * curv.F;
    EXPECT_GT(det, 0.0f);
}

TEST_F(CurvatureAnalyzerTest, SecondFundamentalFormValid) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // For a sphere, L, M, N should all exist
    // The actual values depend on parametrization, but they should be finite
    EXPECT_TRUE(std::isfinite(curv.L));
    EXPECT_TRUE(std::isfinite(curv.M));
    EXPECT_TRUE(std::isfinite(curv.N));
}

// ============================================================
// Normal Vector Tests
// ============================================================

TEST_F(CurvatureAnalyzerTest, NormalUnitLength) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    float len = std::sqrt(curv.normal.x * curv.normal.x +
                         curv.normal.y * curv.normal.y +
                         curv.normal.z * curv.normal.z);
    EXPECT_NEAR(len, 1.0f, 0.01f);
}

TEST_F(CurvatureAnalyzerTest, NormalOrthogonalToPrincipalDirections) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;
    CurvatureResult curv = analyzer.compute_curvature(eval, 0, 0.5f, 0.5f);

    // Normal should be orthogonal to both principal directions
    float dot1 = curv.normal.x * curv.dir1.x +
                 curv.normal.y * curv.dir1.y +
                 curv.normal.z * curv.dir1.z;
    float dot2 = curv.normal.x * curv.dir2.x +
                 curv.normal.y * curv.dir2.y +
                 curv.normal.z * curv.dir2.z;

    EXPECT_NEAR(dot1, 0.0f, 0.15f);
    EXPECT_NEAR(dot2, 0.0f, 0.15f);
}

// ============================================================
// Batch Computation Tests
// ============================================================

TEST_F(CurvatureAnalyzerTest, BatchComputeMatchesIndividual) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;

    // Test points
    std::vector<int> face_indices = {0, 0, 1};
    std::vector<float> params_u = {0.25f, 0.75f, 0.5f};
    std::vector<float> params_v = {0.25f, 0.75f, 0.5f};

    // Batch computation
    auto batch_results = analyzer.batch_compute_curvature(
        eval, face_indices, params_u, params_v
    );

    // Individual computations
    for (size_t i = 0; i < face_indices.size(); ++i) {
        CurvatureResult individual = analyzer.compute_curvature(
            eval, face_indices[i], params_u[i], params_v[i]
        );

        // Compare with batch result
        EXPECT_NEAR(batch_results[i].gaussian_curvature,
                   individual.gaussian_curvature, 0.001f);
        EXPECT_NEAR(batch_results[i].mean_curvature,
                   individual.mean_curvature, 0.001f);
        EXPECT_NEAR(batch_results[i].kappa1, individual.kappa1, 0.001f);
        EXPECT_NEAR(batch_results[i].kappa2, individual.kappa2, 0.001f);
    }
}

TEST_F(CurvatureAnalyzerTest, BatchComputeCorrectCount) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;

    std::vector<int> face_indices = {0, 1, 2, 3, 4};
    std::vector<float> params_u(5, 0.5f);
    std::vector<float> params_v(5, 0.5f);

    auto results = analyzer.batch_compute_curvature(
        eval, face_indices, params_u, params_v
    );

    EXPECT_EQ(results.size(), 5);
}

// ============================================================
// Special Cases
// ============================================================

TEST_F(CurvatureAnalyzerTest, CurvatureAtDifferentParameters) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;

    // Test at multiple parameter values
    for (float u = 0.1f; u <= 0.9f; u += 0.2f) {
        for (float v = 0.1f; v <= 0.9f; v += 0.2f) {
            CurvatureResult curv = analyzer.compute_curvature(eval, 0, u, v);

            // Plane should have zero curvature everywhere
            EXPECT_NEAR(curv.gaussian_curvature, 0.0f, 0.1f);
            EXPECT_TRUE(is_valid_curvature(curv));
        }
    }
}

TEST_F(CurvatureAnalyzerTest, CurvatureAtCorners) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;

    // Test at corners (may have different behavior due to subdivision)
    CurvatureResult corner_00 = analyzer.compute_curvature(eval, 0, 0.0f, 0.0f);
    CurvatureResult corner_11 = analyzer.compute_curvature(eval, 0, 1.0f, 1.0f);

    // Should still produce valid results
    EXPECT_TRUE(is_valid_curvature(corner_00));
    EXPECT_TRUE(is_valid_curvature(corner_11));
}

TEST_F(CurvatureAnalyzerTest, CurvatureConsistentAcrossFaces) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    CurvatureAnalyzer analyzer;

    // Sample multiple faces - should have similar curvature magnitudes
    std::vector<float> gaussian_curvatures;
    for (int face = 0; face < 6; ++face) {
        CurvatureResult curv = analyzer.compute_curvature(eval, face, 0.5f, 0.5f);
        gaussian_curvatures.push_back(curv.gaussian_curvature);
    }

    // All should be positive (sphere)
    for (float K : gaussian_curvatures) {
        EXPECT_GT(K, 0.0f);
    }

    // Variance should be reasonable (not wildly different)
    float mean_K = 0.0f;
    for (float K : gaussian_curvatures) {
        mean_K += K;
    }
    mean_K /= gaussian_curvatures.size();

    for (float K : gaussian_curvatures) {
        // Each should be within 2x of mean
        EXPECT_LT(K, mean_K * 2.0f);
        EXPECT_GT(K, mean_K * 0.5f);
    }
}

// ============================================================
// Main
// ============================================================

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
