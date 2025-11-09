#pragma once
#include <vector>
#include <array>
#include <cstdint>

namespace latent {

/**
 * @brief 3D point with float precision
 */
struct Point3D {
    float x, y, z;

    Point3D() : x(0.0f), y(0.0f), z(0.0f) {}
    Point3D(float _x, float _y, float _z) : x(_x), y(_y), z(_z) {}
};

/**
 * @brief SubD control cage representation
 *
 * Contains vertices, face topology, and edge crease data
 * for subdivision surface evaluation.
 */
struct SubDControlCage {
    std::vector<Point3D> vertices;
    std::vector<std::vector<int>> faces;  // Quad/n-gon faces
    std::vector<std::pair<int, float>> creases;  // Edge ID, sharpness

    size_t vertex_count() const {
        return vertices.size();
    }

    size_t face_count() const {
        return faces.size();
    }
};

/**
 * @brief Result of subdivision surface tessellation
 *
 * Contains triangulated mesh data for display and rendering.
 * Arrays are flattened for efficient memory layout and numpy integration.
 */
struct TessellationResult {
    std::vector<float> vertices;      // Flattened [x,y,z, x,y,z, ...]
    std::vector<float> normals;       // Flattened normals
    std::vector<int> triangles;       // Flattened triangle indices [i,j,k, ...]
    std::vector<int> face_parents;    // Which SubD face each tri came from

    size_t vertex_count() const {
        return vertices.size() / 3;
    }

    size_t triangle_count() const {
        return triangles.size() / 3;
    }
};

}  // namespace latent
