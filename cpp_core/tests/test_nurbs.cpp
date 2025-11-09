// cpp_core/tests/test_nurbs.cpp

#include <gtest/gtest.h>

#ifdef HAVE_OPENCASCADE

#include "geometry/nurbs_generator.h"
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"
#include <cmath>

// OpenCASCADE includes
#include <TopoDS_Shape.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_BSplineSurface.hxx>
#include <BRep_Tool.hxx>
#include <TopExp_Explorer.hxx>

using namespace latent;

/**
 * @brief Test fixture for NURBS generation tests
 *
 * Tests the NURBS mold generation pipeline including:
 * - Surface fitting from SubD limit points
 * - Draft angle transformation
 * - Solid mold creation
 * - Quality validation
 */
class NURBSMoldGeneratorTest : public ::testing::Test {
protected:
    /**
     * Create a simple plane for basic fitting tests
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
     * Create a cube for testing multi-face fitting
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
     * Create a sphere approximation for testing curved surfaces
     */
    SubDControlCage create_sphere() {
        SubDControlCage cage;
        float r = 1.0f / std::sqrt(3.0f);
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
     * Helper: Check if NURBS surface is valid
     */
    bool is_valid_nurbs(Handle(Geom_BSplineSurface) surface) {
        if (surface.IsNull()) return false;
        if (surface->NbUPoles() < 2) return false;
        if (surface->NbVPoles() < 2) return false;
        if (surface->NbUKnots() < 2) return false;
        if (surface->NbVKnots() < 2) return false;
        return true;
    }

    /**
     * Helper: Get number of faces in a shape
     */
    int count_faces(const TopoDS_Shape& shape) {
        int count = 0;
        TopExp_Explorer exp(shape, TopAbs_FACE);
        for (; exp.More(); exp.Next()) {
            count++;
        }
        return count;
    }
};

// ============================================================
// NURBS Surface Fitting Tests
// ============================================================

TEST_F(NURBSMoldGeneratorTest, FitNURBSToPlane) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);

    std::vector<int> face_indices = {0};
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 20  // Low density for fast test
    );

    // Surface should be valid
    EXPECT_TRUE(is_valid_nurbs(surface));
    EXPECT_FALSE(surface.IsNull());

    // Should have reasonable number of control points
    EXPECT_GT(surface->NbUPoles(), 1);
    EXPECT_GT(surface->NbVPoles(), 1);
}

TEST_F(NURBSMoldGeneratorTest, FitNURBSToCube) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);

    // Fit single face
    std::vector<int> face_indices = {0};
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 15
    );

    EXPECT_TRUE(is_valid_nurbs(surface));
}

TEST_F(NURBSMoldGeneratorTest, FitNURBSToSphere) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);

    std::vector<int> face_indices = {0};
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 25
    );

    EXPECT_TRUE(is_valid_nurbs(surface));

    // Curved surface may need more control points
    EXPECT_GT(surface->NbUPoles(), 2);
    EXPECT_GT(surface->NbVPoles(), 2);
}

TEST_F(NURBSMoldGeneratorTest, FitNURBSMultipleFaces) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);

    // Try fitting multiple faces together
    std::vector<int> face_indices = {0, 1};
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 15
    );

    // Should still produce valid surface
    EXPECT_TRUE(is_valid_nurbs(surface));
}

TEST_F(NURBSMoldGeneratorTest, FitNURBSDifferentDensities) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    // Test different sample densities
    Handle(Geom_BSplineSurface) surface_low = generator.fit_nurbs_surface(
        face_indices, 10
    );
    Handle(Geom_BSplineSurface) surface_high = generator.fit_nurbs_surface(
        face_indices, 50
    );

    EXPECT_TRUE(is_valid_nurbs(surface_low));
    EXPECT_TRUE(is_valid_nurbs(surface_high));

    // Higher density might produce more control points (not guaranteed)
    // Just verify both are valid
}

// ============================================================
// Draft Angle Transformation Tests
// ============================================================

TEST_F(NURBSMoldGeneratorTest, ApplyDraftAngle) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) original = generator.fit_nurbs_surface(
        face_indices, 20
    );

    // Create parting line
    std::vector<Point3D> parting_line = {
        Point3D(0, 0, 0), Point3D(2, 0, 0)
    };

    Vector3 demold_dir(0, 0, 1);
    float draft_angle = 2.0f;  // degrees

    Handle(Geom_BSplineSurface) drafted = generator.apply_draft_angle(
        original, demold_dir, draft_angle, parting_line
    );

    // Drafted surface should be valid
    EXPECT_TRUE(is_valid_nurbs(drafted));
    EXPECT_FALSE(drafted.IsNull());
}

TEST_F(NURBSMoldGeneratorTest, ApplyDraftAngleZeroDraft) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) original = generator.fit_nurbs_surface(
        face_indices, 20
    );

    std::vector<Point3D> parting_line = {
        Point3D(0, 0, 0), Point3D(2, 0, 0)
    };

    Vector3 demold_dir(0, 0, 1);

    // Zero draft angle
    Handle(Geom_BSplineSurface) drafted = generator.apply_draft_angle(
        original, demold_dir, 0.0f, parting_line
    );

    // Should still produce valid surface
    EXPECT_TRUE(is_valid_nurbs(drafted));
}

TEST_F(NURBSMoldGeneratorTest, ApplyDraftAngleLargeAngle) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) original = generator.fit_nurbs_surface(
        face_indices, 20
    );

    std::vector<Point3D> parting_line = {
        Point3D(0, 0, 0), Point3D(2, 0, 0)
    };

    Vector3 demold_dir(0, 0, 1);

    // Large draft angle (5 degrees)
    Handle(Geom_BSplineSurface) drafted = generator.apply_draft_angle(
        original, demold_dir, 5.0f, parting_line
    );

    EXPECT_TRUE(is_valid_nurbs(drafted));
}

// ============================================================
// Mold Solid Creation Tests
// ============================================================

TEST_F(NURBSMoldGeneratorTest, CreateMoldSolid) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 20
    );

    TopoDS_Shape mold = generator.create_mold_solid(surface, 10.0f);

    // Mold should be a valid shape
    EXPECT_FALSE(mold.IsNull());

    // Should have at least one face
    EXPECT_GT(count_faces(mold), 0);
}

TEST_F(NURBSMoldGeneratorTest, CreateMoldSolidDifferentThickness) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 20
    );

    // Test different wall thicknesses
    TopoDS_Shape mold_thin = generator.create_mold_solid(surface, 5.0f);
    TopoDS_Shape mold_thick = generator.create_mold_solid(surface, 50.0f);

    EXPECT_FALSE(mold_thin.IsNull());
    EXPECT_FALSE(mold_thick.IsNull());
}

TEST_F(NURBSMoldGeneratorTest, CreateMoldSolidFromCurved) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 25
    );

    TopoDS_Shape mold = generator.create_mold_solid(surface, 15.0f);

    EXPECT_FALSE(mold.IsNull());
}

// ============================================================
// Registration Keys Tests
// ============================================================

TEST_F(NURBSMoldGeneratorTest, AddRegistrationKeys) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 20
    );
    TopoDS_Shape mold = generator.create_mold_solid(surface, 10.0f);

    // Add registration keys at corners
    std::vector<Point3D> key_positions = {
        Point3D(0.5f, 0.5f, 0.0f),
        Point3D(1.5f, 1.5f, 0.0f)
    };

    TopoDS_Shape mold_with_keys = generator.add_registration_keys(
        mold, key_positions
    );

    // Should produce valid shape
    EXPECT_FALSE(mold_with_keys.IsNull());
}

TEST_F(NURBSMoldGeneratorTest, AddRegistrationKeysNoKeys) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 20
    );
    TopoDS_Shape mold = generator.create_mold_solid(surface, 10.0f);

    // Empty key list
    std::vector<Point3D> no_keys;

    TopoDS_Shape mold_no_keys = generator.add_registration_keys(
        mold, no_keys
    );

    // Should still be valid
    EXPECT_FALSE(mold_no_keys.IsNull());
}

// ============================================================
// Fitting Quality Tests
// ============================================================

TEST_F(NURBSMoldGeneratorTest, CheckFittingQuality) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 30
    );

    auto quality = generator.check_fitting_quality(surface, face_indices);

    // Quality metrics should be non-negative
    EXPECT_GE(quality.max_deviation, 0.0f);
    EXPECT_GE(quality.mean_deviation, 0.0f);
    EXPECT_GE(quality.rms_deviation, 0.0f);
    EXPECT_GT(quality.num_samples, 0);

    // RMS should be between mean and max
    EXPECT_LE(quality.rms_deviation, quality.max_deviation);
    EXPECT_GE(quality.rms_deviation, quality.mean_deviation);
}

TEST_F(NURBSMoldGeneratorTest, FittingQualityPlaneSurface) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 40
    );

    auto quality = generator.check_fitting_quality(surface, face_indices);

    // Plane should fit very well (low deviation)
    EXPECT_LT(quality.max_deviation, 1.0f);  // Less than 1mm for a plane
}

TEST_F(NURBSMoldGeneratorTest, FittingQualityHighDensity) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    // High density should give better fit
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 60
    );

    auto quality = generator.check_fitting_quality(surface, face_indices);

    // Should have reasonable quality
    EXPECT_LT(quality.max_deviation, 2.0f);  // Within 2mm
}

TEST_F(NURBSMoldGeneratorTest, FittingQualityToleranceCheck) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 50
    );

    auto quality = generator.check_fitting_quality(surface, face_indices);

    // Simple plane should easily pass 0.1mm tolerance
    EXPECT_TRUE(quality.passes_tolerance);
}

// ============================================================
// Full Pipeline Integration Tests
// ============================================================

TEST_F(NURBSMoldGeneratorTest, FullPipelinePlane) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    // 1. Fit NURBS
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 30
    );
    EXPECT_TRUE(is_valid_nurbs(surface));

    // 2. Apply draft
    std::vector<Point3D> parting_line = {
        Point3D(0, 0, 0), Point3D(2, 0, 0)
    };
    Vector3 demold_dir(0, 0, 1);
    Handle(Geom_BSplineSurface) drafted = generator.apply_draft_angle(
        surface, demold_dir, 2.0f, parting_line
    );
    EXPECT_TRUE(is_valid_nurbs(drafted));

    // 3. Create solid
    TopoDS_Shape mold = generator.create_mold_solid(drafted, 20.0f);
    EXPECT_FALSE(mold.IsNull());

    // 4. Add keys
    std::vector<Point3D> keys = {Point3D(1, 1, 0)};
    TopoDS_Shape final_mold = generator.add_registration_keys(mold, keys);
    EXPECT_FALSE(final_mold.IsNull());

    // 5. Check quality
    auto quality = generator.check_fitting_quality(surface, face_indices);
    EXPECT_GE(quality.num_samples, 0);
}

TEST_F(NURBSMoldGeneratorTest, FullPipelineCurvedSurface) {
    SubDEvaluator eval;
    auto cage = create_sphere();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    // Complete pipeline for curved surface
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 40
    );
    EXPECT_TRUE(is_valid_nurbs(surface));

    std::vector<Point3D> parting_line = {
        Point3D(-0.5f, -0.5f, 0.0f), Point3D(0.5f, -0.5f, 0.0f)
    };
    Vector3 demold_dir(0, 0, 1);
    Handle(Geom_BSplineSurface) drafted = generator.apply_draft_angle(
        surface, demold_dir, 3.0f, parting_line
    );
    EXPECT_TRUE(is_valid_nurbs(drafted));

    TopoDS_Shape mold = generator.create_mold_solid(drafted, 25.0f);
    EXPECT_FALSE(mold.IsNull());
}

// ============================================================
// Edge Cases
// ============================================================

TEST_F(NURBSMoldGeneratorTest, SingleFaceRegion) {
    SubDEvaluator eval;
    auto cage = create_cube();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);

    std::vector<int> single_face = {0};
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        single_face, 20
    );

    EXPECT_TRUE(is_valid_nurbs(surface));
}

TEST_F(NURBSMoldGeneratorTest, MinimumSampleDensity) {
    SubDEvaluator eval;
    auto cage = create_plane();
    eval.initialize(cage);

    NURBSMoldGenerator generator(eval);
    std::vector<int> face_indices = {0};

    // Very low density (minimum viable)
    Handle(Geom_BSplineSurface) surface = generator.fit_nurbs_surface(
        face_indices, 3
    );

    // Should still produce valid surface (though quality may be poor)
    EXPECT_FALSE(surface.IsNull());
}

// ============================================================
// Main
// ============================================================

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

#else

// Fallback when OpenCASCADE is not available
#include <gtest/gtest.h>

TEST(NURBSMoldGeneratorTest, OpenCASCADENotAvailable) {
    GTEST_SKIP() << "OpenCASCADE not available, skipping NURBS tests";
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

#endif // HAVE_OPENCASCADE
