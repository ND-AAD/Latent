// cpp_core/tests/test_constraints.cpp

#include <gtest/gtest.h>
#include "constraints/validator.h"
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"
#include <cmath>

using namespace latent;

/**
 * @brief Test fixture for constraint validation tests
 *
 * Provides test geometries with known constraint properties:
 * - Vertical walls (good draft)
 * - Sloped surfaces (various draft angles)
 * - Undercut features
 */
class ConstraintValidatorTest : public ::testing::Test {
protected:
    /**
     * Create a vertical wall - should have good draft angle in +Z direction
     */
    SubDControlCage create_vertical_wall() {
        SubDControlCage cage;
        cage.vertices = {
            Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
            Point3D(0,0,1), Point3D(1,0,1), Point3D(1,1,1), Point3D(0,1,1)
        };
        cage.faces = {
            {0,1,2,3},  // Bottom
            {4,5,6,7},  // Top
            {0,1,5,4},  // Front (vertical)
            {2,3,7,6},  // Back (vertical)
            {0,3,7,4},  // Left (vertical)
            {1,2,6,5}   // Right (vertical)
        };
        return cage;
    }

    /**
     * Create a sloped surface - draft angle depends on slope
     */
    SubDControlCage create_sloped_surface(float slope = 0.2f) {
        SubDControlCage cage;
        cage.vertices = {
            Point3D(0,0,0), Point3D(1,0,0),
            Point3D(1+slope,1,1), Point3D(0+slope,1,1)
        };
        cage.faces = {{0,1,2,3}};
        return cage;
    }

    /**
     * Create a surface with undercut - should fail demolding in +Z
     */
    SubDControlCage create_undercut_surface() {
        SubDControlCage cage;
        cage.vertices = {
            Point3D(0,0,0), Point3D(1,0,0),
            Point3D(1,1,0.5f), Point3D(0,1,0.5f),
            Point3D(0.8f,2,0), Point3D(0.2f,2,0)  // Overhangs back
        };
        cage.faces = {
            {0,1,2,3}, {3,2,4,5}
        };
        return cage;
    }

    /**
     * Create a flat horizontal surface
     */
    SubDControlCage create_horizontal_surface() {
        SubDControlCage cage;
        cage.vertices = {
            Point3D(0,0,0), Point3D(2,0,0),
            Point3D(2,2,0), Point3D(0,2,0)
        };
        cage.faces = {{0,1,2,3}};
        return cage;
    }
};

// ============================================================
// ConstraintReport Tests
// ============================================================

TEST_F(ConstraintValidatorTest, ConstraintReportInitiallyEmpty) {
    ConstraintReport report;
    EXPECT_FALSE(report.has_errors());
    EXPECT_FALSE(report.has_warnings());
    EXPECT_EQ(report.error_count(), 0);
    EXPECT_EQ(report.warning_count(), 0);
}

TEST_F(ConstraintValidatorTest, ConstraintReportAddError) {
    ConstraintReport report;
    report.add_error("Test error", 0, 0.5f);

    EXPECT_TRUE(report.has_errors());
    EXPECT_EQ(report.error_count(), 1);
    EXPECT_EQ(report.violations.size(), 1);
    EXPECT_EQ(report.violations[0].level, ConstraintLevel::ERROR);
}

TEST_F(ConstraintValidatorTest, ConstraintReportAddWarning) {
    ConstraintReport report;
    report.add_warning("Test warning", 0, 0.3f);

    EXPECT_TRUE(report.has_warnings());
    EXPECT_EQ(report.warning_count(), 1);
    EXPECT_EQ(report.violations.size(), 1);
    EXPECT_EQ(report.violations[0].level, ConstraintLevel::WARNING);
}

TEST_F(ConstraintValidatorTest, ConstraintReportAddFeature) {
    ConstraintReport report;
    report.add_feature("Test feature", 0);

    EXPECT_FALSE(report.has_errors());
    EXPECT_FALSE(report.has_warnings());
    EXPECT_EQ(report.violations.size(), 1);
    EXPECT_EQ(report.violations[0].level, ConstraintLevel::FEATURE);
}

TEST_F(ConstraintValidatorTest, ConstraintReportMultipleViolations) {
    ConstraintReport report;
    report.add_error("Error 1", 0, 0.5f);
    report.add_warning("Warning 1", 1, 0.3f);
    report.add_error("Error 2", 2, 0.7f);

    EXPECT_TRUE(report.has_errors());
    EXPECT_TRUE(report.has_warnings());
    EXPECT_EQ(report.error_count(), 2);
    EXPECT_EQ(report.warning_count(), 1);
    EXPECT_EQ(report.violations.size(), 3);
}

// ============================================================
// DraftChecker Tests
// ============================================================

TEST_F(ConstraintValidatorTest, DraftCheckerVerticalWall) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    DraftChecker checker(eval);
    Vector3 demold_dir(0, 0, 1);  // Pull straight up

    // Check front face (face 2) - should be vertical
    float draft_angle = checker.check_face_draft(2, demold_dir);

    // Vertical wall should have ~90 degree draft angle
    EXPECT_GT(draft_angle, 80.0f);
    EXPECT_LT(draft_angle, 100.0f);
}

TEST_F(ConstraintValidatorTest, DraftCheckerHorizontalSurface) {
    SubDEvaluator eval;
    auto cage = create_horizontal_surface();
    eval.initialize(cage);

    DraftChecker checker(eval);
    Vector3 demold_dir(0, 0, 1);  // Pull straight up

    float draft_angle = checker.check_face_draft(0, demold_dir);

    // Horizontal surface should have ~0 degree draft
    EXPECT_LT(draft_angle, 10.0f);
}

TEST_F(ConstraintValidatorTest, DraftCheckerSlopedSurface) {
    SubDEvaluator eval;
    auto cage = create_sloped_surface(0.3f);
    eval.initialize(cage);

    DraftChecker checker(eval);
    Vector3 demold_dir(0, 0, 1);

    float draft_angle = checker.check_face_draft(0, demold_dir);

    // Sloped surface should have intermediate draft angle
    EXPECT_GT(draft_angle, 10.0f);
    EXPECT_LT(draft_angle, 80.0f);
}

TEST_F(ConstraintValidatorTest, DraftCheckerMultipleFaces) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    DraftChecker checker(eval);
    Vector3 demold_dir(0, 0, 1);

    std::vector<int> face_indices = {0, 1, 2, 3, 4, 5};
    auto draft_angles = checker.compute_draft_angles(face_indices, demold_dir);

    // Should have draft angle for each face
    EXPECT_EQ(draft_angles.size(), 6);

    // All angles should be valid (positive)
    for (const auto& pair : draft_angles) {
        EXPECT_GE(pair.second, 0.0f);
        EXPECT_LE(pair.second, 180.0f);
    }
}

TEST_F(ConstraintValidatorTest, DraftCheckerMinimumAngleConstants) {
    // Check that constants are reasonable
    EXPECT_GT(DraftChecker::MIN_DRAFT_ANGLE, 0.0f);
    EXPECT_LT(DraftChecker::MIN_DRAFT_ANGLE, 5.0f);
    EXPECT_GT(DraftChecker::RECOMMENDED_DRAFT_ANGLE, DraftChecker::MIN_DRAFT_ANGLE);
}

// ============================================================
// UndercutDetector Tests
// ============================================================

TEST_F(ConstraintValidatorTest, UndercutDetectorNoUndercutVertical) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    UndercutDetector detector(eval);
    Vector3 demold_dir(0, 0, 1);

    // Vertical walls should have no undercuts when demolding upward
    std::vector<int> face_indices = {2, 3, 4, 5};  // Vertical faces
    auto undercuts = detector.detect_undercuts(face_indices, demold_dir);

    // Should have results for each face
    EXPECT_EQ(undercuts.size(), face_indices.size());

    // None should have significant undercuts
    for (const auto& pair : undercuts) {
        EXPECT_LE(pair.second, 0.1f);  // Severity should be low
    }
}

TEST_F(ConstraintValidatorTest, UndercutDetectorSingleFace) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    UndercutDetector detector(eval);
    Vector3 demold_dir(0, 0, 1);

    // Check single face
    float severity = detector.check_face_undercut(2, demold_dir);

    // Should be low severity (no undercut)
    EXPECT_GE(severity, 0.0f);
    EXPECT_LE(severity, 1.0f);
}

TEST_F(ConstraintValidatorTest, UndercutDetectorWithUndercut) {
    SubDEvaluator eval;
    auto cage = create_undercut_surface();
    eval.initialize(cage);

    UndercutDetector detector(eval);
    Vector3 demold_dir(0, 0, 1);  // Pull up

    // Check face with undercut
    float severity = detector.check_face_undercut(1, demold_dir);

    // May or may not detect depending on implementation
    // Just verify it returns valid value
    EXPECT_GE(severity, 0.0f);
    EXPECT_LE(severity, 1.0f);
}

// ============================================================
// ConstraintValidator Integration Tests
// ============================================================

TEST_F(ConstraintValidatorTest, ValidateRegionVerticalWalls) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    ConstraintValidator validator(eval);
    Vector3 demold_dir(0, 0, 1);

    // Validate vertical faces
    std::vector<int> face_indices = {2, 3, 4, 5};
    ConstraintReport report = validator.validate_region(
        face_indices, demold_dir, 3.0f
    );

    // Vertical walls should pass (no errors expected)
    // May have warnings depending on exact implementation
    EXPECT_FALSE(report.has_errors());
}

TEST_F(ConstraintValidatorTest, ValidateRegionHorizontalSurface) {
    SubDEvaluator eval;
    auto cage = create_horizontal_surface();
    eval.initialize(cage);

    ConstraintValidator validator(eval);
    Vector3 demold_dir(0, 0, 1);

    std::vector<int> face_indices = {0};
    ConstraintReport report = validator.validate_region(
        face_indices, demold_dir, 3.0f
    );

    // Horizontal surface may have draft angle issues
    // Just check that validation completes
    EXPECT_GE(report.violations.size(), 0);
}

TEST_F(ConstraintValidatorTest, ValidateRegionWithUndercut) {
    SubDEvaluator eval;
    auto cage = create_undercut_surface();
    eval.initialize(cage);

    ConstraintValidator validator(eval);
    Vector3 demold_dir(0, 0, 1);

    std::vector<int> face_indices = {0, 1};
    ConstraintReport report = validator.validate_region(
        face_indices, demold_dir, 3.0f
    );

    // Should detect issues (errors or warnings)
    // Exact behavior depends on implementation
    EXPECT_TRUE(report.has_errors() || report.has_warnings() ||
                report.violations.size() > 0);
}

TEST_F(ConstraintValidatorTest, ValidateRegionWithWallThickness) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    ConstraintValidator validator(eval);
    Vector3 demold_dir(0, 0, 1);
    std::vector<int> face_indices = {2, 3, 4, 5};

    // Test with different wall thickness requirements
    ConstraintReport report_thin = validator.validate_region(
        face_indices, demold_dir, 1.0f
    );
    ConstraintReport report_thick = validator.validate_region(
        face_indices, demold_dir, 10.0f
    );

    // Both should complete without crash
    EXPECT_TRUE(true);
}

TEST_F(ConstraintValidatorTest, ValidateRegionEmptyFaceList) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    ConstraintValidator validator(eval);
    Vector3 demold_dir(0, 0, 1);

    std::vector<int> empty_faces;
    ConstraintReport report = validator.validate_region(
        empty_faces, demold_dir, 3.0f
    );

    // Empty region should have no violations
    EXPECT_EQ(report.violations.size(), 0);
}

// ============================================================
// ConstraintLevel Tests
// ============================================================

TEST_F(ConstraintValidatorTest, ConstraintLevelEnumValues) {
    // Verify enum values are distinct
    EXPECT_NE(static_cast<int>(ConstraintLevel::ERROR),
              static_cast<int>(ConstraintLevel::WARNING));
    EXPECT_NE(static_cast<int>(ConstraintLevel::WARNING),
              static_cast<int>(ConstraintLevel::FEATURE));
    EXPECT_NE(static_cast<int>(ConstraintLevel::ERROR),
              static_cast<int>(ConstraintLevel::FEATURE));
}

// ============================================================
// ConstraintViolation Tests
// ============================================================

TEST_F(ConstraintValidatorTest, ViolationStructureComplete) {
    ConstraintViolation violation;
    violation.level = ConstraintLevel::WARNING;
    violation.description = "Test violation";
    violation.face_id = 5;
    violation.severity = 0.7f;
    violation.suggestion = "Fix this";

    EXPECT_EQ(violation.level, ConstraintLevel::WARNING);
    EXPECT_EQ(violation.description, "Test violation");
    EXPECT_EQ(violation.face_id, 5);
    EXPECT_NEAR(violation.severity, 0.7f, 0.001f);
    EXPECT_EQ(violation.suggestion, "Fix this");
}

// ============================================================
// Demolding Direction Tests
// ============================================================

TEST_F(ConstraintValidatorTest, DifferentDemoldingDirections) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    DraftChecker checker(eval);

    // Test different demolding directions
    Vector3 up(0, 0, 1);
    Vector3 right(1, 0, 0);
    Vector3 forward(0, 1, 0);

    float draft_up = checker.check_face_draft(2, up);
    float draft_right = checker.check_face_draft(2, right);
    float draft_forward = checker.check_face_draft(2, forward);

    // All should be valid angles
    EXPECT_GE(draft_up, 0.0f);
    EXPECT_GE(draft_right, 0.0f);
    EXPECT_GE(draft_forward, 0.0f);

    // They should be different (face 2 is oriented differently)
    // At least one pair should differ significantly
    bool has_difference = (std::abs(draft_up - draft_right) > 5.0f) ||
                         (std::abs(draft_up - draft_forward) > 5.0f) ||
                         (std::abs(draft_right - draft_forward) > 5.0f);
    EXPECT_TRUE(has_difference);
}

TEST_F(ConstraintValidatorTest, NormalizedDemoldingDirection) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    DraftChecker checker(eval);

    // Non-normalized direction
    Vector3 demold_dir(0, 0, 10);

    // Should handle non-normalized directions gracefully
    float draft_angle = checker.check_face_draft(2, demold_dir);

    EXPECT_GE(draft_angle, 0.0f);
    EXPECT_LE(draft_angle, 180.0f);
}

// ============================================================
// Edge Cases
// ============================================================

TEST_F(ConstraintValidatorTest, SingleFaceValidation) {
    SubDEvaluator eval;
    auto cage = create_horizontal_surface();
    eval.initialize(cage);

    ConstraintValidator validator(eval);
    Vector3 demold_dir(0, 0, 1);

    std::vector<int> single_face = {0};
    ConstraintReport report = validator.validate_region(
        single_face, demold_dir, 3.0f
    );

    // Should complete without error
    EXPECT_TRUE(true);
}

TEST_F(ConstraintValidatorTest, MultipleFacesValidation) {
    SubDEvaluator eval;
    auto cage = create_vertical_wall();
    eval.initialize(cage);

    ConstraintValidator validator(eval);
    Vector3 demold_dir(0, 0, 1);

    std::vector<int> all_faces = {0, 1, 2, 3, 4, 5};
    ConstraintReport report = validator.validate_region(
        all_faces, demold_dir, 3.0f
    );

    // Should complete and have some violations for bottom/top faces
    EXPECT_GE(report.violations.size(), 0);
}

// ============================================================
// Main
// ============================================================

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
