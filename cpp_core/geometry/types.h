#pragma once
#include <vector>
#include <array>
#include <cstdint>
#include <cmath>

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
 * @brief 3D vector with float precision and vector operations
 */
struct Vector3 {
    float x, y, z;

    Vector3() : x(0.0f), y(0.0f), z(0.0f) {}
    Vector3(float _x, float _y, float _z) : x(_x), y(_y), z(_z) {}
    Vector3(const Point3D& p) : x(p.x), y(p.y), z(p.z) {}

    // Dot product
    float dot(const Vector3& other) const {
        return x * other.x + y * other.y + z * other.z;
    }

    // Length/magnitude
    float length() const {
        return std::sqrt(x * x + y * y + z * z);
    }

    // Normalize
    Vector3 normalized() const {
        float len = length();
        if (len > 0.0f) {
            return Vector3(x / len, y / len, z / len);
        }
        return Vector3(0.0f, 0.0f, 0.0f);
    }

    // Cross product
    Vector3 cross(const Vector3& other) const {
        return Vector3(
            y * other.z - z * other.y,
            z * other.x - x * other.z,
            x * other.y - y * other.x
        );
    }
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
