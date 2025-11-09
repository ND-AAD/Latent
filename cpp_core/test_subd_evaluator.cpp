#include "geometry/subd_evaluator.h"
#include "geometry/types.h"
#include <iostream>
#include <cassert>
#include <cmath>

using namespace latent;

// Helper to compare floats
bool approx_equal(float a, float b, float eps = 1e-5f) {
    return std::abs(a - b) < eps;
}

void test_cube_subdivision() {
    std::cout << "Test: Cube subdivision..." << std::endl;

    // Create unit cube control cage
    SubDControlCage cube;

    // 8 vertices
    cube.vertices = {
        Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0),
        Point3D(0,0,1), Point3D(1,0,1), Point3D(1,1,1), Point3D(0,1,1)
    };

    // 6 quad faces
    cube.faces = {
        {0,1,2,3}, {4,5,6,7}, {0,1,5,4},
        {2,3,7,6}, {0,3,7,4}, {1,2,6,5}
    };

    // Test initialization
    SubDEvaluator eval;
    assert(!eval.is_initialized());

    eval.initialize(cube);
    assert(eval.is_initialized());
    assert(eval.get_control_vertex_count() == 8);
    assert(eval.get_control_face_count() == 6);

    std::cout << "  ✅ Initialization successful" << std::endl;

    // Test tessellation
    TessellationResult mesh = eval.tessellate(2);  // Level 2

    assert(mesh.vertex_count() > 8);  // Should have more verts than cage
    assert(mesh.triangle_count() > 0);  // Should have triangles
    assert(mesh.vertices.size() == mesh.normals.size());  // Normals match

    std::cout << "  ✅ Tessellation produced " << mesh.vertex_count()
              << " vertices, " << mesh.triangle_count() << " triangles"
              << std::endl;

    // Test parent mapping
    for (size_t i = 0; i < mesh.triangle_count(); ++i) {
        int parent = eval.get_parent_face(i);
        assert(parent >= 0);  // Valid parent face
    }

    std::cout << "  ✅ Parent face mapping valid" << std::endl;

    // Test limit evaluation at face center
    Point3D center = eval.evaluate_limit_point(0, 0.5f, 0.5f);

    // For a cube, face center should be between control points
    assert(center.x >= 0.0f && center.x <= 1.0f);
    assert(center.y >= 0.0f && center.y <= 1.0f);
    assert(center.z >= -0.1f && center.z <= 1.1f);

    std::cout << "  ✅ Limit evaluation at (" << center.x << ", "
              << center.y << ", " << center.z << ")" << std::endl;

    // Test limit with normal
    Point3D point, normal;
    eval.evaluate_limit(0, 0.5f, 0.5f, point, normal);

    // Normal should be unit length
    float length = std::sqrt(normal.x * normal.x +
                             normal.y * normal.y +
                             normal.z * normal.z);
    assert(approx_equal(length, 1.0f, 0.01f));

    std::cout << "  ✅ Normal evaluation: (" << normal.x << ", "
              << normal.y << ", " << normal.z << "), length="
              << length << std::endl;
}

void test_different_subdivision_levels() {
    std::cout << "\nTest: Different subdivision levels..." << std::endl;

    // Simple quad
    SubDControlCage quad;
    quad.vertices = {
        Point3D(0,0,0), Point3D(1,0,0),
        Point3D(1,1,0), Point3D(0,1,0)
    };
    quad.faces = {{0,1,2,3}};

    SubDEvaluator eval;
    eval.initialize(quad);

    int prev_tri_count = 0;
    for (int level = 1; level <= 4; ++level) {
        TessellationResult mesh = eval.tessellate(level);
        std::cout << "  Level " << level << ": "
                  << mesh.vertex_count() << " vertices, "
                  << mesh.triangle_count() << " triangles" << std::endl;

        // Higher levels should produce more triangles
        assert(mesh.triangle_count() > 0);
        assert(mesh.triangle_count() >= prev_tri_count);
        prev_tri_count = mesh.triangle_count();
    }

    std::cout << "  ✅ All subdivision levels working" << std::endl;
}

void test_triangle_face() {
    std::cout << "\nTest: Triangle face..." << std::endl;

    // Single triangle
    SubDControlCage tri;
    tri.vertices = {
        Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0)
    };
    tri.faces = {{0,1,2}};

    SubDEvaluator eval;
    eval.initialize(tri);

    assert(eval.get_control_vertex_count() == 3);
    assert(eval.get_control_face_count() == 1);

    TessellationResult mesh = eval.tessellate(2);
    assert(mesh.triangle_count() > 0);

    // Test limit evaluation
    Point3D center = eval.evaluate_limit_point(0, 0.33f, 0.33f);
    assert(center.x >= 0.0f && center.x <= 1.0f);
    assert(center.y >= 0.0f && center.y <= 1.0f);

    std::cout << "  ✅ Triangle face handled correctly" << std::endl;
}

void test_error_handling() {
    std::cout << "\nTest: Error handling..." << std::endl;

    SubDEvaluator eval;

    // Test uninitialized access
    try {
        eval.tessellate(2);
        assert(false);  // Should throw
    } catch (const std::runtime_error& e) {
        std::cout << "  ✅ Caught expected error: " << e.what() << std::endl;
    }

    // Test empty cage
    SubDControlCage empty;
    try {
        eval.initialize(empty);
        assert(false);  // Should throw
    } catch (const std::runtime_error& e) {
        std::cout << "  ✅ Caught expected error: " << e.what() << std::endl;
    }

    // Test invalid subdivision level
    SubDControlCage quad;
    quad.vertices = {Point3D(0,0,0), Point3D(1,0,0), Point3D(1,1,0), Point3D(0,1,0)};
    quad.faces = {{0,1,2,3}};
    eval.initialize(quad);

    try {
        eval.tessellate(100);  // Too high
        assert(false);  // Should throw
    } catch (const std::runtime_error& e) {
        std::cout << "  ✅ Caught expected error: " << e.what() << std::endl;
    }

    // Test invalid parametric coordinates
    try {
        eval.evaluate_limit_point(0, 1.5f, 0.5f);  // u > 1.0
        assert(false);  // Should throw
    } catch (const std::runtime_error& e) {
        std::cout << "  ✅ Caught expected error: " << e.what() << std::endl;
    }

    std::cout << "  ✅ All error handling tests passed" << std::endl;
}

int main() {
    try {
        test_cube_subdivision();
        test_different_subdivision_levels();
        test_triangle_face();
        test_error_handling();

        std::cout << "\n✅ ALL TESTS PASSED!" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "\n❌ TEST FAILED: " << e.what() << std::endl;
        return 1;
    }
}
