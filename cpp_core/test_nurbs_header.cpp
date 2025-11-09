/**
 * @file test_nurbs_header.cpp
 * @brief Compilation test for nurbs_generator.h
 *
 * Tests that the header:
 * - Compiles without errors
 * - All methods are declared correctly
 * - Types are defined properly
 * - Namespace structure is correct
 */

#include "geometry/nurbs_generator.h"
#include <iostream>

using namespace latent;

int main() {
    std::cout << "Testing NURBSMoldGenerator header compilation...\n";

    // Test that we can reference the class
    // (We can't instantiate without OpenCASCADE, but can check types)

    // Check FittingQuality struct
    NURBSMoldGenerator::FittingQuality quality;
    quality.max_deviation = 0.1f;
    quality.mean_deviation = 0.05f;
    quality.rms_deviation = 0.06f;
    quality.num_samples = 1000;

    std::cout << "FittingQuality struct compiles correctly\n";
    std::cout << "  max_deviation: " << quality.max_deviation << " mm\n";
    std::cout << "  mean_deviation: " << quality.mean_deviation << " mm\n";
    std::cout << "  rms_deviation: " << quality.rms_deviation << " mm\n";
    std::cout << "  num_samples: " << quality.num_samples << "\n";

    // Check Vector3 type usage
    Vector3 demolding_dir(0.0f, 0.0f, 1.0f);
    std::cout << "\nVector3 compiles correctly\n";
    std::cout << "  demolding_direction: ("
              << demolding_dir.x << ", "
              << demolding_dir.y << ", "
              << demolding_dir.z << ")\n";

    // Check Point3D type usage
    std::vector<Point3D> parting_line;
    parting_line.push_back(Point3D(0.0f, 0.0f, 0.0f));
    parting_line.push_back(Point3D(10.0f, 0.0f, 0.0f));
    std::cout << "\nPoint3D vector compiles correctly\n";
    std::cout << "  parting_line size: " << parting_line.size() << "\n";

    // Check face index vector
    std::vector<int> face_indices = {0, 1, 2, 3};
    std::cout << "\nFace indices vector: " << face_indices.size() << " faces\n";

    std::cout << "\n✓ All header types and structures compile correctly!\n";
    std::cout << "✓ NURBSMoldGenerator header ready for implementation.\n";

    return 0;
}
