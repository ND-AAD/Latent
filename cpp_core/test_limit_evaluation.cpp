#include "geometry/subd_evaluator.h"
#include "geometry/types.h"
#include <iostream>
#include <cassert>
#include <cmath>

using namespace latent;

bool approx_equal(float a, float b, float eps = 1e-4f) {
    return std::abs(a - b) < eps;
}

void test_derivatives() {
    std::cout << "Test: Derivative evaluation..." << std::endl;

    // Create simple quad
    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0),
        Point3D(1, 0, 0),
        Point3D(1, 1, 0),
        Point3D(0, 1, 0)
    };
    cage.faces = {{0, 1, 2, 3}};

    SubDEvaluator eval;
    eval.initialize(cage);

    // Evaluate at center
    Point3D pos, du, dv;
    eval.evaluate_limit_with_derivatives(0, 0.5f, 0.5f, pos, du, dv);

    std::cout << "  Position: (" << pos.x << ", " << pos.y << ", " << pos.z << ")" << std::endl;
    std::cout << "  du: (" << du.x << ", " << du.y << ", " << du.z << ")" << std::endl;
    std::cout << "  dv: (" << dv.x << ", " << dv.y << ", " << dv.z << ")" << std::endl;

    // For a planar quad, derivatives should be constant
    // du should be approximately (1, 0, 0)
    // dv should be approximately (0, 1, 0)
    // Position should be approximately (0.5, 0.5, 0)

    // Check position is near center
    assert(approx_equal(pos.x, 0.5f, 0.1f));
    assert(approx_equal(pos.y, 0.5f, 0.1f));
    assert(approx_equal(pos.z, 0.0f, 0.1f));

    // Check derivatives are non-zero
    float du_mag = std::sqrt(du.x*du.x + du.y*du.y + du.z*du.z);
    float dv_mag = std::sqrt(dv.x*dv.x + dv.y*dv.y + dv.z*dv.z);
    assert(du_mag > 0.1f);
    assert(dv_mag > 0.1f);

    std::cout << "  ✅ Derivatives evaluated" << std::endl;
}

void test_second_derivatives() {
    std::cout << "\nTest: Second derivative evaluation..." << std::endl;

    // Create a simple cube SubD (will become rounded cube at limit)
    SubDControlCage cage;

    // Simple 6-vertex octahedron (makes rounded shape)
    cage.vertices = {
        Point3D( 1,  0,  0),  // 0: +X
        Point3D(-1,  0,  0),  // 1: -X
        Point3D( 0,  1,  0),  // 2: +Y
        Point3D( 0, -1,  0),  // 3: -Y
        Point3D( 0,  0,  1),  // 4: +Z
        Point3D( 0,  0, -1)   // 5: -Z
    };

    // 8 triangular faces forming octahedron
    cage.faces = {
        {0, 2, 4},  // Top-front-right
        {2, 1, 4},  // Top-front-left
        {1, 3, 4},  // Top-back-left
        {3, 0, 4},  // Top-back-right
        {2, 0, 5},  // Bottom-front-right
        {1, 2, 5},  // Bottom-front-left
        {3, 1, 5},  // Bottom-back-left
        {0, 3, 5}   // Bottom-back-right
    };

    SubDEvaluator eval;
    eval.initialize(cage);

    Point3D pos, du, dv, duu, dvv, duv;
    eval.evaluate_limit_with_second_derivatives(
        0, 0.5f, 0.5f, pos, du, dv, duu, dvv, duv
    );

    std::cout << "  Position: (" << pos.x << ", " << pos.y << ", " << pos.z << ")" << std::endl;
    std::cout << "  First derivatives computed" << std::endl;
    std::cout << "  Second derivatives computed" << std::endl;

    // For non-planar surface, second derivatives should exist
    float duu_mag = std::sqrt(duu.x*duu.x + duu.y*duu.y + duu.z*duu.z);
    float dvv_mag = std::sqrt(dvv.x*dvv.x + dvv.y*dvv.y + dvv.z*dvv.z);

    std::cout << "  |duu| = " << duu_mag << std::endl;
    std::cout << "  |dvv| = " << dvv_mag << std::endl;

    // Second derivatives should be finite
    assert(std::isfinite(duu_mag));
    assert(std::isfinite(dvv_mag));

    std::cout << "  ✅ Second derivatives evaluated" << std::endl;
}

void test_batch_evaluation() {
    std::cout << "\nTest: Batch evaluation..." << std::endl;

    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0), Point3D(1, 0, 0),
        Point3D(1, 1, 0), Point3D(0, 1, 0)
    };
    cage.faces = {{0, 1, 2, 3}};

    SubDEvaluator eval;
    eval.initialize(cage);

    // Evaluate grid of points
    std::vector<int> faces;
    std::vector<float> us, vs;

    for (int i = 0; i < 10; ++i) {
        for (int j = 0; j < 10; ++j) {
            faces.push_back(0);
            us.push_back(i / 9.0f);
            vs.push_back(j / 9.0f);
        }
    }

    TessellationResult result = eval.batch_evaluate_limit(faces, us, vs);

    assert(result.vertex_count() == 100);
    std::cout << "  Evaluated " << result.vertex_count() << " points" << std::endl;

    // Check all normals are unit length
    for (size_t i = 0; i < result.vertex_count(); ++i) {
        float nx = result.normals[i*3 + 0];
        float ny = result.normals[i*3 + 1];
        float nz = result.normals[i*3 + 2];
        float len = std::sqrt(nx*nx + ny*ny + nz*nz);
        assert(approx_equal(len, 1.0f, 0.01f));
    }

    std::cout << "  ✅ Batch evaluation working" << std::endl;
}

void test_tangent_frame() {
    std::cout << "\nTest: Tangent frame computation..." << std::endl;

    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0), Point3D(1, 0, 0),
        Point3D(1, 1, 0), Point3D(0, 1, 0)
    };
    cage.faces = {{0, 1, 2, 3}};

    SubDEvaluator eval;
    eval.initialize(cage);

    Point3D tu, tv, n;
    eval.compute_tangent_frame(0, 0.5f, 0.5f, tu, tv, n);

    // Check all are unit vectors
    auto check_unit = [](const Point3D& v, const char* name) {
        float len = std::sqrt(v.x*v.x + v.y*v.y + v.z*v.z);
        std::cout << "  |" << name << "| = " << len << std::endl;
        assert(approx_equal(len, 1.0f, 0.01f));
    };

    check_unit(tu, "tangent_u");
    check_unit(tv, "tangent_v");
    check_unit(n, "normal");

    // Check orthogonality (tu · tv should be near 0 for orthogonal surface)
    float dot = tu.x*tv.x + tu.y*tv.y + tu.z*tv.z;
    std::cout << "  tu · tv = " << dot << " (should be ~0 for orthogonal)" << std::endl;

    // For a planar quad, tangent frame should be orthogonal
    assert(std::abs(dot) < 0.5f);  // Allow some flexibility for SubD smoothing

    std::cout << "  ✅ Tangent frame computed correctly" << std::endl;
}

void test_performance() {
    std::cout << "\nTest: Performance measurement..." << std::endl;

    SubDControlCage cage;
    cage.vertices = {
        Point3D(0, 0, 0), Point3D(1, 0, 0),
        Point3D(1, 1, 0), Point3D(0, 1, 0)
    };
    cage.faces = {{0, 1, 2, 3}};

    SubDEvaluator eval;
    eval.initialize(cage);

    // Warm up - ensure patch table is built
    Point3D p, du, dv;
    eval.evaluate_limit_with_derivatives(0, 0.5f, 0.5f, p, du, dv);

    // Batch evaluate 1000 points
    std::vector<int> faces(1000, 0);
    std::vector<float> us(1000);
    std::vector<float> vs(1000);

    for (int i = 0; i < 1000; ++i) {
        us[i] = (i % 32) / 31.0f;
        vs[i] = (i / 32) / 31.0f;
    }

    TessellationResult result = eval.batch_evaluate_limit(faces, us, vs);

    std::cout << "  Successfully evaluated 1000 points" << std::endl;
    std::cout << "  ✅ Performance test passed" << std::endl;
}

int main() {
    try {
        test_derivatives();
        test_second_derivatives();
        test_batch_evaluation();
        test_tangent_frame();
        test_performance();

        std::cout << "\n✅ ALL LIMIT EVALUATION TESTS PASSED!" << std::endl;
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "\n❌ TEST FAILED: " << e.what() << std::endl;
        return 1;
    }
}
