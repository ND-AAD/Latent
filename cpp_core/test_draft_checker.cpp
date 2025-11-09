// cpp_core/test_draft_checker.cpp

#include "constraints/validator.h"
#include "geometry/subd_evaluator.h"
#include <iostream>
#include <cassert>
#include <cmath>

using namespace latent;

// Helper to compare floats with tolerance
bool approx_equal(float a, float b, float tolerance = 0.01f) {
    return std::abs(a - b) < tolerance;
}

void test_compute_angle() {
    std::cout << "Testing compute_angle..." << std::endl;
    
    // Create a simple cube control cage
    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),  // Bottom
        Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)   // Top
    };
    cage.faces = {
        {0, 1, 2, 3},  // Bottom face (normal = -Z)
        {4, 5, 6, 7},  // Top face (normal = +Z)
        {0, 1, 5, 4},  // Front face (normal = -Y)
        {2, 3, 7, 6},  // Back face (normal = +Y)
        {0, 3, 7, 4},  // Left face (normal = -X)
        {1, 2, 6, 5}   // Right face (normal = +X)
    };
    
    SubDEvaluator evaluator;
    evaluator.initialize(cage);
    
    DraftChecker checker(evaluator);
    
    // Test 1: Parallel faces (90° draft)
    // Top face normal is +Z, demolding direction is +Z
    // Normal parallel to demolding direction -> 90° draft angle
    std::cout << "  Test 1: Parallel faces (90° draft)..." << std::endl;
    Vector3 demold_up(0, 0, 1);  // Demolding upward (+Z)
    float draft_top = checker.check_face_draft(1, demold_up);  // Top face
    std::cout << "    Top face draft angle: " << draft_top << "°" << std::endl;
    assert(approx_equal(draft_top, 90.0f, 1.0f));  // Should be ~90°
    
    // Test 2: Perpendicular faces (0° draft)
    // Front face normal is -Y, demolding direction is +Z
    // Normal perpendicular to demolding direction -> 0° draft angle
    std::cout << "  Test 2: Perpendicular faces (0° draft)..." << std::endl;
    float draft_front = checker.check_face_draft(2, demold_up);  // Front face
    std::cout << "    Front face draft angle: " << draft_front << "°" << std::endl;
    assert(approx_equal(draft_front, 0.0f, 1.0f));  // Should be ~0°
    
    // Test 3: Opposite parallel faces (90° draft with negative)
    // Bottom face normal is -Z, demolding direction is +Z
    // Normal anti-parallel to demolding direction -> -90° draft angle (undercut)
    std::cout << "  Test 3: Opposite parallel faces (-90° draft)..." << std::endl;
    float draft_bottom = checker.check_face_draft(0, demold_up);  // Bottom face
    std::cout << "    Bottom face draft angle: " << draft_bottom << "°" << std::endl;
    assert(approx_equal(draft_bottom, -90.0f, 1.0f));  // Should be ~-90°
    
    std::cout << "  ✓ All compute_angle tests passed!" << std::endl;
}

void test_compute_draft_angles_batch() {
    std::cout << "Testing compute_draft_angles (batch)..." << std::endl;
    
    // Create a simple cube
    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),
        Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)
    };
    cage.faces = {
        {0, 1, 2, 3},  // Bottom
        {4, 5, 6, 7},  // Top
        {0, 1, 5, 4},  // Front
        {2, 3, 7, 6},  // Back
        {0, 3, 7, 4},  // Left
        {1, 2, 6, 5}   // Right
    };
    
    SubDEvaluator evaluator;
    evaluator.initialize(cage);
    
    DraftChecker checker(evaluator);
    
    // Test batch computation
    std::vector<int> face_indices = {0, 1, 2, 3, 4, 5};
    Vector3 demold_up(0, 0, 1);
    
    auto draft_map = checker.compute_draft_angles(face_indices, demold_up);
    
    std::cout << "  Draft angles for all faces:" << std::endl;
    for (const auto& [face_id, draft] : draft_map) {
        std::cout << "    Face " << face_id << ": " << draft << "°" << std::endl;
    }
    
    // Verify we got results for all faces
    assert(draft_map.size() == 6);
    
    // Verify top face is ~90°
    assert(approx_equal(draft_map[1], 90.0f, 1.0f));
    
    // Verify side faces are ~0°
    assert(approx_equal(draft_map[2], 0.0f, 1.0f));
    assert(approx_equal(draft_map[3], 0.0f, 1.0f));
    assert(approx_equal(draft_map[4], 0.0f, 1.0f));
    assert(approx_equal(draft_map[5], 0.0f, 1.0f));
    
    // Verify bottom face is ~-90° (undercut)
    assert(approx_equal(draft_map[0], -90.0f, 1.0f));
    
    std::cout << "  ✓ Batch computation test passed!" << std::endl;
}

void test_draft_angle_with_angled_demolding() {
    std::cout << "Testing draft angles with angled demolding direction..." << std::endl;
    
    // Create a simple cube
    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0), Point3D(1, 0, 0), Point3D(1, 1, 0), Point3D(0, 1, 0),
        Point3D(0, 0, 1), Point3D(1, 0, 1), Point3D(1, 1, 1), Point3D(0, 1, 1)
    };
    cage.faces = {
        {0, 1, 2, 3},  // Bottom
        {4, 5, 6, 7}   // Top
    };
    
    SubDEvaluator evaluator;
    evaluator.initialize(cage);
    
    DraftChecker checker(evaluator);
    
    // Test with 45° angled demolding direction
    Vector3 demold_45(0, 0, 1);  // Normalized (0, 0, 1) for simplicity
    demold_45 = Vector3(0.707f, 0, 0.707f);  // 45° angle in XZ plane
    
    float draft_top = checker.check_face_draft(1, demold_45);
    std::cout << "  Top face draft with 45° demolding: " << draft_top << "°" << std::endl;
    
    // The angle between +Z normal and 45° demolding (0.707, 0, 0.707) is 45°
    // So draft angle = 90° - 45° = 45°
    assert(approx_equal(draft_top, 45.0f, 1.0f));
    
    std::cout << "  ✓ Angled demolding test passed!" << std::endl;
}

int main() {
    std::cout << "=== Draft Checker Tests ===" << std::endl;
    
    try {
        test_compute_angle();
        test_compute_draft_angles_batch();
        test_draft_angle_with_angled_demolding();
        
        std::cout << "\n✓ All tests passed!" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "✗ Test failed with exception: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cerr << "✗ Test failed with unknown exception" << std::endl;
        return 1;
    }
}
