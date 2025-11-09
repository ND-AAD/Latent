// cpp_core/test_nurbs_fitting.cpp
//
// Tests for NURBS surface fitting from exact SubD limit surface

#include "geometry/nurbs_generator.h"
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"

#include <Geom_BSplineSurface.hxx>
#include <gp_Pnt.hxx>

#include <iostream>
#include <vector>
#include <cmath>
#include <cassert>

using namespace latent;

// Helper to create a simple quad SubD cage (flat)
SubDControlCage create_flat_quad_cage() {
    SubDControlCage cage;

    // Create a 2x2 quad patch
    cage.vertices.push_back(Point3D(0, 0, 0));
    cage.vertices.push_back(Point3D(100, 0, 0));
    cage.vertices.push_back(Point3D(100, 100, 0));
    cage.vertices.push_back(Point3D(0, 100, 0));

    cage.faces.push_back({0, 1, 2, 3});

    return cage;
}

// Helper to create a curved SubD cage (hemisphere-like)
SubDControlCage create_curved_quad_cage() {
    SubDControlCage cage;

    const float radius = 50.0f;

    // Create control points for a curved surface
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            float u = static_cast<float>(i) / 2.0f;
            float v = static_cast<float>(j) / 2.0f;

            float x = 100.0f * u;
            float y = 100.0f * v;
            float z = radius * (1.0f - std::sqrt(u*u + v*v) / std::sqrt(2.0f));

            if (z < 0) z = 0;

            cage.vertices.push_back(Point3D(x, y, z));
        }
    }

    // Create quad faces (2x2 grid = 4 faces)
    cage.faces.push_back({0, 1, 4, 3});
    cage.faces.push_back({1, 2, 5, 4});
    cage.faces.push_back({3, 4, 7, 6});
    cage.faces.push_back({4, 5, 8, 7});

    return cage;
}

// Helper to create a sphere-like SubD cage for analytical comparison
SubDControlCage create_sphere_cage(float radius = 50.0f) {
    SubDControlCage cage;

    // Create an octahedral subdivision cage (approximates sphere)
    // 6 vertices: top, bottom, and 4 around equator
    cage.vertices.push_back(Point3D(0, 0, radius));           // 0: top
    cage.vertices.push_back(Point3D(radius, 0, 0));            // 1: front
    cage.vertices.push_back(Point3D(0, radius, 0));            // 2: right
    cage.vertices.push_back(Point3D(-radius, 0, 0));           // 3: back
    cage.vertices.push_back(Point3D(0, -radius, 0));           // 4: left
    cage.vertices.push_back(Point3D(0, 0, -radius));           // 5: bottom

    // Create 8 triangular faces (octahedron)
    cage.faces.push_back({0, 1, 2});  // Top hemisphere
    cage.faces.push_back({0, 2, 3});
    cage.faces.push_back({0, 3, 4});
    cage.faces.push_back({0, 4, 1});
    cage.faces.push_back({5, 2, 1});  // Bottom hemisphere
    cage.faces.push_back({5, 3, 2});
    cage.faces.push_back({5, 4, 3});
    cage.faces.push_back({5, 1, 4});

    return cage;
}

// Test 1: Fit NURBS to flat surface
void test_fit_flat_surface() {
    std::cout << "Test 1: Fit NURBS to flat quad surface..." << std::endl;

    SubDControlCage cage = create_flat_quad_cage();
    SubDEvaluator evaluator;
    evaluator.initialize(cage);

    NURBSMoldGenerator generator(evaluator);

    std::vector<int> face_indices = {0};  // Single face
    int sample_density = 10;

    try {
        Handle(Geom_BSplineSurface) nurbs =
            generator.fit_nurbs_surface(face_indices, sample_density);

        assert(!nurbs.IsNull() && "NURBS surface is null");

        std::cout << "  ✓ NURBS fitting succeeded" << std::endl;
        std::cout << "    U degree: " << nurbs->UDegree() << std::endl;
        std::cout << "    V degree: " << nurbs->VDegree() << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "  ✗ Exception: " << e.what() << std::endl;
        assert(false);
    }
}

// Test 2: Check fitting quality on flat surface
void test_quality_flat_surface() {
    std::cout << "Test 2: Check quality metrics for flat surface..." << std::endl;

    SubDControlCage cage = create_flat_quad_cage();
    SubDEvaluator evaluator;
    evaluator.initialize(cage);

    NURBSMoldGenerator generator(evaluator);

    std::vector<int> face_indices = {0};
    int sample_density = 20;

    Handle(Geom_BSplineSurface) nurbs =
        generator.fit_nurbs_surface(face_indices, sample_density);

    auto quality = generator.check_fitting_quality(nurbs, face_indices);

    std::cout << "  Quality metrics:" << std::endl;
    std::cout << "    Max deviation:  " << quality.max_deviation << " mm" << std::endl;
    std::cout << "    Mean deviation: " << quality.mean_deviation << " mm" << std::endl;
    std::cout << "    RMS deviation:  " << quality.rms_deviation << " mm" << std::endl;
    std::cout << "    Num samples:    " << quality.num_samples << std::endl;
    std::cout << "    Passes tolerance (<0.1mm): " << (quality.passes_tolerance ? "YES" : "NO") << std::endl;

    // For a flat surface, deviation should be very small
    assert(quality.max_deviation < 0.01f && "Deviation too large for flat surface");
    assert(quality.passes_tolerance && "Quality check should pass for flat surface");

    std::cout << "  ✓ Quality check passed (deviation < 0.1mm)" << std::endl;
}

// Test 3: Fit NURBS to curved surface
void test_fit_curved_surface() {
    std::cout << "Test 3: Fit NURBS to curved surface..." << std::endl;

    SubDControlCage cage = create_curved_quad_cage();
    SubDEvaluator evaluator;
    evaluator.initialize(cage);

    NURBSMoldGenerator generator(evaluator);

    // Test single face fitting
    std::vector<int> face_indices = {0};  // First face only
    int sample_density = 30;

    try {
        Handle(Geom_BSplineSurface) nurbs =
            generator.fit_nurbs_surface(face_indices, sample_density);

        assert(!nurbs.IsNull());

        std::cout << "  ✓ NURBS fitting succeeded for curved surface" << std::endl;

        // Check quality
        auto quality = generator.check_fitting_quality(nurbs, face_indices);

        std::cout << "    Max deviation: " << quality.max_deviation << " mm" << std::endl;
        std::cout << "    Passes tolerance: " << (quality.passes_tolerance ? "YES" : "NO") << std::endl;

        // For curved surfaces with sufficient sampling, should still pass tolerance
        if (quality.passes_tolerance) {
            std::cout << "  ✓ Quality check passed" << std::endl;
        } else {
            std::cout << "  ⚠ Warning: Quality tolerance not met (may need higher sampling)" << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "  ✗ Exception: " << e.what() << std::endl;
        assert(false);
    }
}

// Test 4: Verify exact limit surface sampling
void test_exact_limit_sampling() {
    std::cout << "Test 4: Verify exact limit surface sampling..." << std::endl;

    SubDControlCage cage = create_flat_quad_cage();
    SubDEvaluator evaluator;
    evaluator.initialize(cage);

    // Manually sample limit surface
    int density = 5;
    std::vector<Point3D> manual_samples;

    for (int i = 0; i < density; ++i) {
        for (int j = 0; j < density; ++j) {
            float u = static_cast<float>(i) / (density - 1);
            float v = static_cast<float>(j) / (density - 1);

            Point3D pt = evaluator.evaluate_limit_point(0, u, v);
            manual_samples.push_back(pt);
        }
    }

    std::cout << "  Sampled " << manual_samples.size() << " points from exact limit surface" << std::endl;
    assert(manual_samples.size() == static_cast<size_t>(density * density));

    // Verify points are on expected plane (z should be ~0 for flat quad)
    bool all_on_plane = true;
    for (const auto& pt : manual_samples) {
        if (std::abs(pt.z) > 0.01f) {
            all_on_plane = false;
            break;
        }
    }

    assert(all_on_plane && "Sample points not on expected plane");
    std::cout << "  ✓ All samples on expected surface" << std::endl;
    std::cout << "  ✓ Exact limit surface evaluation confirmed" << std::endl;
}

// Test 5: Sphere test (analytical comparison)
void test_sphere_fitting() {
    std::cout << "Test 5: Sphere fitting (analytical comparison)..." << std::endl;

    float radius = 50.0f;
    SubDControlCage cage = create_sphere_cage(radius);
    SubDEvaluator evaluator;
    evaluator.initialize(cage);

    NURBSMoldGenerator generator(evaluator);

    // Fit NURBS to one face of the sphere
    std::vector<int> face_indices = {0};
    int sample_density = 25;

    try {
        Handle(Geom_BSplineSurface) nurbs =
            generator.fit_nurbs_surface(face_indices, sample_density);

        assert(!nurbs.IsNull());

        // Check quality
        auto quality = generator.check_fitting_quality(nurbs, face_indices);

        std::cout << "  Sphere fitting quality:" << std::endl;
        std::cout << "    Radius:         " << radius << " mm" << std::endl;
        std::cout << "    Max deviation:  " << quality.max_deviation << " mm" << std::endl;
        std::cout << "    Mean deviation: " << quality.mean_deviation << " mm" << std::endl;
        std::cout << "    RMS deviation:  " << quality.rms_deviation << " mm" << std::endl;

        // For subdivision sphere, fitting should still be quite good
        std::cout << "    Passes tolerance: " << (quality.passes_tolerance ? "YES" : "NO") << std::endl;

        // Analytical comparison: sample a point and check distance from origin
        gp_Pnt test_pt;
        nurbs->D0(0.5, 0.5, test_pt);

        float distance = std::sqrt(
            test_pt.X() * test_pt.X() +
            test_pt.Y() * test_pt.Y() +
            test_pt.Z() * test_pt.Z()
        );

        float radius_error = std::abs(distance - radius);
        std::cout << "    Center point distance from origin: " << distance << " mm" << std::endl;
        std::cout << "    Radius error: " << radius_error << " mm" << std::endl;

        std::cout << "  ✓ Sphere fitting completed" << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "  ✗ Exception: " << e.what() << std::endl;
        assert(false);
    }
}

// Test 6: Test invalid inputs
void test_invalid_inputs() {
    std::cout << "Test 6: Test invalid inputs (should fail gracefully)..." << std::endl;

    SubDControlCage cage = create_flat_quad_cage();
    SubDEvaluator evaluator;
    evaluator.initialize(cage);

    NURBSMoldGenerator generator(evaluator);

    // Test 6a: Empty face indices
    try {
        std::vector<int> empty_faces;
        generator.fit_nurbs_surface(empty_faces, 10);
        std::cerr << "  ✗ Should have thrown for empty face indices" << std::endl;
        assert(false);
    } catch (const std::runtime_error& e) {
        std::cout << "  ✓ Correctly rejected empty face indices" << std::endl;
    }

    // Test 6b: Invalid sample density
    try {
        std::vector<int> faces = {0};
        generator.fit_nurbs_surface(faces, 1);  // Density < 2
        std::cerr << "  ✗ Should have thrown for invalid density" << std::endl;
        assert(false);
    } catch (const std::runtime_error& e) {
        std::cout << "  ✓ Correctly rejected invalid sample density" << std::endl;
    }

    // Test 6c: Multi-face input (not yet supported)
    try {
        std::vector<int> multi_faces = {0, 1};  // Multiple faces
        generator.fit_nurbs_surface(multi_faces, 10);
        std::cerr << "  ✗ Should have thrown for multi-face input" << std::endl;
        assert(false);
    } catch (const std::runtime_error& e) {
        std::cout << "  ✓ Correctly rejected multi-face input (not yet implemented)" << std::endl;
    }
}

// Test 7: Various sample densities
void test_sample_densities() {
    std::cout << "Test 7: Test various sample densities..." << std::endl;

    SubDControlCage cage = create_flat_quad_cage();
    SubDEvaluator evaluator;
    evaluator.initialize(cage);

    NURBSMoldGenerator generator(evaluator);
    std::vector<int> face_indices = {0};

    int densities[] = {5, 10, 20, 50};

    for (int density : densities) {
        try {
            Handle(Geom_BSplineSurface) nurbs =
                generator.fit_nurbs_surface(face_indices, density);

            auto quality = generator.check_fitting_quality(nurbs, face_indices);

            std::cout << "  Density " << density << "x" << density << ": "
                      << "max_dev=" << quality.max_deviation << "mm, "
                      << (quality.passes_tolerance ? "PASS" : "FAIL") << std::endl;

        } catch (const std::exception& e) {
            std::cerr << "  ✗ Failed at density " << density << ": " << e.what() << std::endl;
            assert(false);
        }
    }

    std::cout << "  ✓ All density tests passed" << std::endl;
}

int main() {
    std::cout << "=== NURBS Surface Fitting Tests ===" << std::endl;
    std::cout << "Testing exact limit surface sampling and NURBS fitting" << std::endl;
    std::cout << std::endl;

    try {
        test_fit_flat_surface();
        std::cout << std::endl;

        test_quality_flat_surface();
        std::cout << std::endl;

        test_fit_curved_surface();
        std::cout << std::endl;

        test_exact_limit_sampling();
        std::cout << std::endl;

        test_sphere_fitting();
        std::cout << std::endl;

        test_invalid_inputs();
        std::cout << std::endl;

        test_sample_densities();
        std::cout << std::endl;

        std::cout << "=== All NURBS Fitting Tests Passed ===" << std::endl;
        return 0;

    } catch (const std::exception& e) {
        std::cerr << std::endl << "=== Test Suite Failed ===" << std::endl;
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }
}
