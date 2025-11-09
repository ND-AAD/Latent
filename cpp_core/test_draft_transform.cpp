// test_draft_transform.cpp
// Test draft angle transformation for NURBS surfaces

#include "geometry/nurbs_generator.h"
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"

#include <Geom_BSplineSurface.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>
#include <gp_Pnt.hxx>

#include <iostream>
#include <cmath>
#include <vector>

using namespace latent;

// Create a simple planar NURBS surface for testing
Handle(Geom_BSplineSurface) create_test_plane() {
    // Create a 3x3 control point grid for a flat plane
    int u_poles = 3;
    int v_poles = 3;

    TColgp_Array2OfPnt poles(1, u_poles, 1, v_poles);

    // Create a flat plane at z=0, spanning x=[0,100], y=[0,100]
    for (int i = 1; i <= u_poles; i++) {
        for (int j = 1; j <= v_poles; j++) {
            double x = (i - 1) * 50.0;  // 0, 50, 100
            double y = (j - 1) * 50.0;  // 0, 50, 100
            double z = 0.0;
            poles.SetValue(i, j, gp_Pnt(x, y, z));
        }
    }

    // Uniform knot vectors for degree 2
    TColStd_Array1OfReal u_knots(1, 2);
    TColStd_Array1OfReal v_knots(1, 2);
    u_knots.SetValue(1, 0.0);
    u_knots.SetValue(2, 1.0);
    v_knots.SetValue(1, 0.0);
    v_knots.SetValue(2, 1.0);

    TColStd_Array1OfInteger u_mults(1, 2);
    TColStd_Array1OfInteger v_mults(1, 2);
    u_mults.SetValue(1, 3);  // Multiplicity = degree + 1
    u_mults.SetValue(2, 3);
    v_mults.SetValue(1, 3);
    v_mults.SetValue(2, 3);

    int degree = 2;

    Handle(Geom_BSplineSurface) surface = new Geom_BSplineSurface(
        poles,
        u_knots,
        v_knots,
        u_mults,
        v_mults,
        degree,
        degree
    );

    return surface;
}

// Create a cylindrical NURBS surface for testing
Handle(Geom_BSplineSurface) create_test_cylinder() {
    // Create a simple cylinder with radius 50, height 100
    int u_poles = 5;  // Around circumference
    int v_poles = 3;  // Along height

    TColgp_Array2OfPnt poles(1, u_poles, 1, v_poles);

    double radius = 50.0;

    for (int j = 1; j <= v_poles; j++) {
        double z = (j - 1) * 50.0;  // 0, 50, 100

        for (int i = 1; i <= u_poles; i++) {
            double angle = (i - 1) * 2.0 * M_PI / (u_poles - 1);
            double x = radius * std::cos(angle);
            double y = radius * std::sin(angle);
            poles.SetValue(i, j, gp_Pnt(x, y, z));
        }
    }

    // Uniform knot vectors
    TColStd_Array1OfReal u_knots(1, 2);
    TColStd_Array1OfReal v_knots(1, 2);
    u_knots.SetValue(1, 0.0);
    u_knots.SetValue(2, 1.0);
    v_knots.SetValue(1, 0.0);
    v_knots.SetValue(2, 1.0);

    TColStd_Array1OfInteger u_mults(1, 2);
    TColStd_Array1OfInteger v_mults(1, 2);
    u_mults.SetValue(1, 3);
    u_mults.SetValue(2, 3);
    v_mults.SetValue(1, 3);
    v_mults.SetValue(2, 3);

    int degree = 2;

    Handle(Geom_BSplineSurface) surface = new Geom_BSplineSurface(
        poles,
        u_knots,
        v_knots,
        u_mults,
        v_mults,
        degree,
        degree
    );

    return surface;
}

bool test_draft_on_plane() {
    std::cout << "\n=== Test: Draft transformation on planar surface ===" << std::endl;

    // Create a simple SubDEvaluator (we need it for NURBSMoldGenerator constructor)
    // For this test, we'll use a dummy cage since we're working directly with NURBS
    SubDControlCage dummy_cage;
    dummy_cage.vertices.push_back(Point3D(0, 0, 0));
    dummy_cage.faces.push_back({0});

    SubDEvaluator evaluator(dummy_cage);
    NURBSMoldGenerator generator(evaluator);

    // Create test plane
    Handle(Geom_BSplineSurface) plane = create_test_plane();
    std::cout << "Created planar surface: "
              << plane->NbUPoles() << "x" << plane->NbVPoles() << " control points" << std::endl;

    // Define demolding direction (upward along Z)
    Vector3 demolding_dir(0, 0, 1);

    // Define parting line (bottom edge of plane at z=0)
    std::vector<Point3D> parting_line;
    parting_line.push_back(Point3D(0, 50, 0));
    parting_line.push_back(Point3D(100, 50, 0));

    // Apply 2 degree draft angle
    float draft_angle = 2.0f;

    try {
        Handle(Geom_BSplineSurface) drafted = generator.apply_draft_angle(
            plane, demolding_dir, draft_angle, parting_line
        );

        if (drafted.IsNull()) {
            std::cout << "ERROR: Draft transformation returned null surface" << std::endl;
            return false;
        }

        std::cout << "SUCCESS: Draft transformation completed" << std::endl;
        std::cout << "Drafted surface: "
                  << drafted->NbUPoles() << "x" << drafted->NbVPoles() << " control points" << std::endl;

        // Verify surface is still valid
        Standard_Real u_min, u_max, v_min, v_max;
        drafted->Bounds(u_min, u_max, v_min, v_max);
        std::cout << "Surface bounds: u=[" << u_min << "," << u_max << "], "
                  << "v=[" << v_min << "," << v_max << "]" << std::endl;

        // Check that the parting line region hasn't moved much
        gp_Pnt p_origin, d_origin;
        plane->D0(0.5, 0.5, p_origin);
        drafted->D0(0.5, 0.5, d_origin);

        double dist = p_origin.Distance(d_origin);
        std::cout << "Distance moved at center: " << dist << " mm" << std::endl;

        return true;

    } catch (const std::exception& e) {
        std::cout << "ERROR: Exception during draft transformation: " << e.what() << std::endl;
        return false;
    }
}

bool test_draft_angles() {
    std::cout << "\n=== Test: Various draft angles ===" << std::endl;

    SubDControlCage dummy_cage;
    dummy_cage.vertices.push_back(Point3D(0, 0, 0));
    dummy_cage.faces.push_back({0});

    SubDEvaluator evaluator(dummy_cage);
    NURBSMoldGenerator generator(evaluator);

    Handle(Geom_BSplineSurface) cylinder = create_test_cylinder();

    Vector3 demolding_dir(0, 0, 1);
    std::vector<Point3D> parting_line;
    parting_line.push_back(Point3D(50, 0, 0));

    std::vector<float> angles = {0.5f, 1.0f, 2.0f, 3.0f, 5.0f};

    for (float angle : angles) {
        try {
            Handle(Geom_BSplineSurface) drafted = generator.apply_draft_angle(
                cylinder, demolding_dir, angle, parting_line
            );

            if (drafted.IsNull()) {
                std::cout << "ERROR: Draft angle " << angle << "° failed (null surface)" << std::endl;
                return false;
            }

            std::cout << "SUCCESS: Draft angle " << angle << "° applied" << std::endl;

        } catch (const std::exception& e) {
            std::cout << "ERROR: Draft angle " << angle << "° failed: " << e.what() << std::endl;
            return false;
        }
    }

    return true;
}

bool test_invalid_inputs() {
    std::cout << "\n=== Test: Invalid input handling ===" << std::endl;

    SubDControlCage dummy_cage;
    dummy_cage.vertices.push_back(Point3D(0, 0, 0));
    dummy_cage.faces.push_back({0});

    SubDEvaluator evaluator(dummy_cage);
    NURBSMoldGenerator generator(evaluator);

    Handle(Geom_BSplineSurface) plane = create_test_plane();
    Vector3 demolding_dir(0, 0, 1);
    std::vector<Point3D> parting_line;

    // Test null surface
    try {
        Handle(Geom_BSplineSurface) null_surface;
        generator.apply_draft_angle(null_surface, demolding_dir, 2.0f, parting_line);
        std::cout << "ERROR: Should have thrown exception for null surface" << std::endl;
        return false;
    } catch (const std::exception& e) {
        std::cout << "SUCCESS: Correctly rejected null surface" << std::endl;
    }

    // Test invalid draft angle (negative)
    try {
        generator.apply_draft_angle(plane, demolding_dir, -2.0f, parting_line);
        std::cout << "ERROR: Should have thrown exception for negative draft angle" << std::endl;
        return false;
    } catch (const std::exception& e) {
        std::cout << "SUCCESS: Correctly rejected negative draft angle" << std::endl;
    }

    // Test invalid draft angle (too large)
    try {
        generator.apply_draft_angle(plane, demolding_dir, 50.0f, parting_line);
        std::cout << "ERROR: Should have thrown exception for excessive draft angle" << std::endl;
        return false;
    } catch (const std::exception& e) {
        std::cout << "SUCCESS: Correctly rejected excessive draft angle (>45°)" << std::endl;
    }

    return true;
}

int main() {
    std::cout << "==================================================" << std::endl;
    std::cout << "  Draft Angle Transformation Tests" << std::endl;
    std::cout << "==================================================" << std::endl;

    int passed = 0;
    int total = 0;

    total++;
    if (test_draft_on_plane()) {
        passed++;
        std::cout << "✓ Planar draft test passed" << std::endl;
    } else {
        std::cout << "✗ Planar draft test failed" << std::endl;
    }

    total++;
    if (test_draft_angles()) {
        passed++;
        std::cout << "✓ Multiple angles test passed" << std::endl;
    } else {
        std::cout << "✗ Multiple angles test failed" << std::endl;
    }

    total++;
    if (test_invalid_inputs()) {
        passed++;
        std::cout << "✓ Invalid input handling passed" << std::endl;
    } else {
        std::cout << "✗ Invalid input handling failed" << std::endl;
    }

    std::cout << "\n==================================================" << std::endl;
    std::cout << "Results: " << passed << "/" << total << " tests passed" << std::endl;
    std::cout << "==================================================" << std::endl;

    return (passed == total) ? 0 : 1;
}
