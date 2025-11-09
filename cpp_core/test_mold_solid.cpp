// cpp_core/test_mold_solid.cpp

#include "geometry/nurbs_generator.h"
#include "geometry/subd_evaluator.h"
#include "geometry/types.h"

#include <BRepCheck_Analyzer.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <Geom_BSplineSurface.hxx>
#include <GeomAPI_PointsToBSplineSurface.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <gp_Pnt.hxx>
#include <TopoDS_Shape.hxx>

#include <iostream>
#include <vector>
#include <cmath>
#include <cassert>

using namespace latent;

// Helper function to create a simple test NURBS surface (flat plane)
Handle(Geom_BSplineSurface) create_test_plane_surface() {
    const int n = 3;  // 3x3 control points for simple plane
    TColgp_Array2OfPnt points(1, n, 1, n);

    // Create a simple plane at z=0
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            double x = 100.0 * i / (n - 1);
            double y = 100.0 * j / (n - 1);
            points.SetValue(i + 1, j + 1, gp_Pnt(x, y, 0.0));
        }
    }

    GeomAPI_PointsToBSplineSurface fitter(points);
    if (!fitter.IsDone()) {
        std::cerr << "Failed to create test plane surface" << std::endl;
        return nullptr;
    }

    return fitter.Surface();
}

// Helper function to create a curved test NURBS surface (hemisphere-like)
Handle(Geom_BSplineSurface) create_test_curved_surface() {
    const int n = 5;  // 5x5 control points
    TColgp_Array2OfPnt points(1, n, 1, n);

    const double radius = 50.0;

    // Create a curved surface (partial hemisphere)
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            double u = static_cast<double>(i) / (n - 1);
            double v = static_cast<double>(j) / (n - 1);
            
            // Parametric surface with curvature
            double x = 100.0 * u;
            double y = 100.0 * v;
            double z = radius * (1.0 - std::sqrt(u*u + v*v) / std::sqrt(2.0));
            
            if (z < 0) z = 0;
            
            points.SetValue(i + 1, j + 1, gp_Pnt(x, y, z));
        }
    }

    GeomAPI_PointsToBSplineSurface fitter(points);
    if (!fitter.IsDone()) {
        std::cerr << "Failed to create test curved surface" << std::endl;
        return nullptr;
    }

    return fitter.Surface();
}

// Test 1: Create solid from flat plane
void test_create_mold_solid_from_plane() {
    std::cout << "Test 1: Create mold solid from plane..." << std::endl;

    // Create a simple SubD cage for testing (we'll use a minimal setup)
    SubDControlCage cage;
    
    // Add vertices for a simple quad
    cage.vertices.push_back(Point3D(0, 0, 0));
    cage.vertices.push_back(Point3D(100, 0, 0));
    cage.vertices.push_back(Point3D(100, 100, 0));
    cage.vertices.push_back(Point3D(0, 100, 0));
    
    cage.faces.push_back({0, 1, 2, 3});

    SubDEvaluator evaluator(cage);
    NURBSMoldGenerator generator(evaluator);

    // Create test plane surface
    Handle(Geom_BSplineSurface) surface = create_test_plane_surface();
    assert(!surface.IsNull() && "Failed to create test surface");

    // Create mold solid with 10mm wall thickness
    float wall_thickness = 10.0f;
    
    try {
        TopoDS_Shape mold = generator.create_mold_solid(surface, wall_thickness);
        
        // Validate the solid
        BRepCheck_Analyzer analyzer(mold);
        if (analyzer.IsValid()) {
            std::cout << "  ✓ Solid created successfully and is valid" << std::endl;
        } else {
            std::cerr << "  ✗ Created solid is not valid" << std::endl;
            assert(false);
        }
        
    } catch (const std::exception& e) {
        std::cerr << "  ✗ Exception: " << e.what() << std::endl;
        assert(false);
    }
}

// Test 2: Create solid from curved surface
void test_create_mold_solid_from_curved_surface() {
    std::cout << "Test 2: Create mold solid from curved surface..." << std::endl;

    SubDControlCage cage;
    cage.vertices.push_back(Point3D(0, 0, 0));
    cage.vertices.push_back(Point3D(100, 0, 0));
    cage.vertices.push_back(Point3D(100, 100, 0));
    cage.vertices.push_back(Point3D(0, 100, 0));
    cage.faces.push_back({0, 1, 2, 3});

    SubDEvaluator evaluator(cage);
    NURBSMoldGenerator generator(evaluator);

    Handle(Geom_BSplineSurface) surface = create_test_curved_surface();
    assert(!surface.IsNull() && "Failed to create curved test surface");

    float wall_thickness = 15.0f;
    
    try {
        TopoDS_Shape mold = generator.create_mold_solid(surface, wall_thickness);
        
        BRepCheck_Analyzer analyzer(mold);
        if (analyzer.IsValid()) {
            std::cout << "  ✓ Curved solid created successfully and is valid" << std::endl;
        } else {
            std::cerr << "  ✗ Curved solid is not valid" << std::endl;
            assert(false);
        }
        
    } catch (const std::exception& e) {
        std::cerr << "  ✗ Exception: " << e.what() << std::endl;
        assert(false);
    }
}

// Test 3: Add registration keys to mold
void test_add_registration_keys() {
    std::cout << "Test 3: Add registration keys to mold..." << std::endl;

    SubDControlCage cage;
    cage.vertices.push_back(Point3D(0, 0, 0));
    cage.vertices.push_back(Point3D(100, 0, 0));
    cage.vertices.push_back(Point3D(100, 100, 0));
    cage.vertices.push_back(Point3D(0, 100, 0));
    cage.faces.push_back({0, 1, 2, 3});

    SubDEvaluator evaluator(cage);
    NURBSMoldGenerator generator(evaluator);

    Handle(Geom_BSplineSurface) surface = create_test_plane_surface();
    assert(!surface.IsNull());

    TopoDS_Shape mold = generator.create_mold_solid(surface, 10.0f);

    // Add registration keys at specific positions
    std::vector<Point3D> key_positions = {
        Point3D(20, 20, 0),
        Point3D(80, 20, 0),
        Point3D(80, 80, 0),
        Point3D(20, 80, 0)
    };

    try {
        TopoDS_Shape mold_with_keys = generator.add_registration_keys(mold, key_positions);
        
        BRepCheck_Analyzer analyzer(mold_with_keys);
        if (analyzer.IsValid()) {
            std::cout << "  ✓ Registration keys added successfully, solid is valid" << std::endl;
        } else {
            std::cerr << "  ✗ Solid with keys is not valid" << std::endl;
            assert(false);
        }
        
    } catch (const std::exception& e) {
        std::cerr << "  ✗ Exception: " << e.what() << std::endl;
        assert(false);
    }
}

// Test 4: Test with zero thickness (should fail)
void test_invalid_wall_thickness() {
    std::cout << "Test 4: Test invalid wall thickness (should fail gracefully)..." << std::endl;

    SubDControlCage cage;
    cage.vertices.push_back(Point3D(0, 0, 0));
    cage.vertices.push_back(Point3D(100, 0, 0));
    cage.vertices.push_back(Point3D(100, 100, 0));
    cage.vertices.push_back(Point3D(0, 100, 0));
    cage.faces.push_back({0, 1, 2, 3});

    SubDEvaluator evaluator(cage);
    NURBSMoldGenerator generator(evaluator);

    Handle(Geom_BSplineSurface) surface = create_test_plane_surface();
    
    try {
        TopoDS_Shape mold = generator.create_mold_solid(surface, 0.0f);
        std::cerr << "  ✗ Should have thrown exception for zero thickness" << std::endl;
        assert(false);
    } catch (const std::runtime_error& e) {
        std::cout << "  ✓ Correctly rejected zero wall thickness: " << e.what() << std::endl;
    }
}

// Test 5: Test with null surface (should fail)
void test_null_surface() {
    std::cout << "Test 5: Test null surface (should fail gracefully)..." << std::endl;

    SubDControlCage cage;
    cage.vertices.push_back(Point3D(0, 0, 0));
    cage.vertices.push_back(Point3D(100, 0, 0));
    cage.vertices.push_back(Point3D(100, 100, 0));
    cage.vertices.push_back(Point3D(0, 100, 0));
    cage.faces.push_back({0, 1, 2, 3});

    SubDEvaluator evaluator(cage);
    NURBSMoldGenerator generator(evaluator);

    Handle(Geom_BSplineSurface) null_surface;
    
    try {
        TopoDS_Shape mold = generator.create_mold_solid(null_surface, 10.0f);
        std::cerr << "  ✗ Should have thrown exception for null surface" << std::endl;
        assert(false);
    } catch (const std::runtime_error& e) {
        std::cout << "  ✓ Correctly rejected null surface: " << e.what() << std::endl;
    }
}

int main() {
    std::cout << "=== Mold Solid Creation Tests ===" << std::endl << std::endl;

    try {
        test_create_mold_solid_from_plane();
        test_create_mold_solid_from_curved_surface();
        test_add_registration_keys();
        test_invalid_wall_thickness();
        test_null_surface();

        std::cout << std::endl << "=== All Tests Passed ===" << std::endl;
        return 0;

    } catch (const std::exception& e) {
        std::cerr << std::endl << "=== Test Suite Failed ===" << std::endl;
        std::cerr << "Exception: " << e.what() << std::endl;
        return 1;
    }
}
