// cpp_core/constraints/undercut_detector.cpp

#include "validator.h"
#include <cmath>
#include <algorithm>
#include <limits>

namespace latent {

// Helper function: Vector dot product
static float dot(const Vector3& a, const Vector3& b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

// Helper function: Vector cross product
static Vector3 cross(const Vector3& a, const Vector3& b) {
    return Vector3(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    );
}

// Helper function: Vector subtraction
static Vector3 subtract(const Point3D& a, const Point3D& b) {
    return Vector3(a.x - b.x, a.y - b.y, a.z - b.z);
}

// Helper function: Vector addition
static Point3D add(const Point3D& a, const Vector3& b) {
    return Point3D(a.x + b.x, a.y + b.y, a.z + b.z);
}

// Helper function: Vector scale
static Vector3 scale(const Vector3& v, float s) {
    return Vector3(v.x * s, v.y * s, v.z * s);
}

// Helper function: Vector length
static float length(const Vector3& v) {
    return std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

// Helper function: Normalize vector
static Vector3 normalize(const Vector3& v) {
    float len = length(v);
    if (len < 1e-6f) return Vector3(0, 0, 1);
    return Vector3(v.x / len, v.y / len, v.z / len);
}

UndercutDetector::UndercutDetector(const SubDEvaluator& evaluator)
    : evaluator_(evaluator) {}

std::map<int, float> UndercutDetector::detect_undercuts(
    const std::vector<int>& face_indices,
    const Vector3& demolding_direction) {

    std::map<int, float> undercut_map;

    for (int face_id : face_indices) {
        float undercut_severity = check_face_undercut(face_id, demolding_direction);
        if (undercut_severity > 0.0f) {
            undercut_map[face_id] = undercut_severity;
        }
    }

    return undercut_map;
}

float UndercutDetector::check_face_undercut(
    int face_id,
    const Vector3& demolding_direction) {

    // Normalize demolding direction
    Vector3 demold_dir = normalize(demolding_direction);

    // Sample multiple points on the face to detect undercuts
    const int samples = 5;
    std::vector<Point3D> sample_points;
    std::vector<Vector3> sample_normals;

    // Sample a grid on the face
    for (int i = 0; i < samples; ++i) {
        for (int j = 0; j < samples; ++j) {
            float u = (i + 0.5f) / samples;
            float v = (j + 0.5f) / samples;
            
            Point3D point, normal;
            evaluator_.evaluate_limit(face_id, u, v, point, normal);
            
            sample_points.push_back(point);
            sample_normals.push_back(normalize(normal));
        }
    }

    // Get tessellated mesh for ray-casting
    TessellationResult mesh = evaluator_.tessellate(3);

    // Track maximum undercut severity
    float max_severity = 0.0f;
    int undercut_count = 0;

    // Check each sample point
    for (size_t i = 0; i < sample_points.size(); ++i) {
        const Point3D& origin = sample_points[i];
        const Vector3& normal = sample_normals[i];

        // Check if face is facing away from demolding direction
        // (negative draft angle)
        float face_alignment = dot(normal, demold_dir);
        if (face_alignment < 0.0f) {
            // Face is already facing wrong direction - potential issue
            max_severity = std::max(max_severity, -face_alignment);
        }

        // Cast ray along demolding direction
        // Offset slightly to avoid self-intersection
        Point3D ray_origin = add(origin, scale(demold_dir, 0.001f));

        // Check intersection with all triangles in the mesh
        float min_distance = std::numeric_limits<float>::max();
        bool has_intersection = false;

        for (size_t tri_idx = 0; tri_idx < mesh.triangle_count(); ++tri_idx) {
            // Get parent face of this triangle
            int tri_face_id = mesh.face_parents[tri_idx];
            
            // Skip triangles from the same face
            if (tri_face_id == face_id) {
                continue;
            }

            // Get triangle vertices
            int idx0 = mesh.triangles[tri_idx * 3 + 0];
            int idx1 = mesh.triangles[tri_idx * 3 + 1];
            int idx2 = mesh.triangles[tri_idx * 3 + 2];

            Point3D v0(
                mesh.vertices[idx0 * 3 + 0],
                mesh.vertices[idx0 * 3 + 1],
                mesh.vertices[idx0 * 3 + 2]
            );
            Point3D v1(
                mesh.vertices[idx1 * 3 + 0],
                mesh.vertices[idx1 * 3 + 1],
                mesh.vertices[idx1 * 3 + 2]
            );
            Point3D v2(
                mesh.vertices[idx2 * 3 + 0],
                mesh.vertices[idx2 * 3 + 1],
                mesh.vertices[idx2 * 3 + 2]
            );

            // Moller-Trumbore ray-triangle intersection
            Vector3 edge1 = subtract(v1, v0);
            Vector3 edge2 = subtract(v2, v0);
            Vector3 h = cross(demold_dir, edge2);
            float a = dot(edge1, h);

            // Ray parallel to triangle
            if (std::abs(a) < 1e-6f) {
                continue;
            }

            float f = 1.0f / a;
            Vector3 s = subtract(ray_origin, v0);
            float u = f * dot(s, h);

            if (u < 0.0f || u > 1.0f) {
                continue;
            }

            Vector3 q = cross(s, edge1);
            float v = f * dot(demold_dir, q);

            if (v < 0.0f || u + v > 1.0f) {
                continue;
            }

            float t = f * dot(edge2, q);

            // Check if intersection is in front of ray (positive direction)
            if (t > 1e-6f) {
                has_intersection = true;
                min_distance = std::min(min_distance, t);
            }
        }

        if (has_intersection) {
            undercut_count++;
            // Severity based on how close the occlusion is
            // Closer occlusions are more severe
            float distance_severity = 1.0f / (1.0f + min_distance);
            max_severity = std::max(max_severity, distance_severity);
        }
    }

    // If more than a threshold of sample points have undercuts, report severity
    float undercut_ratio = static_cast<float>(undercut_count) / sample_points.size();
    if (undercut_ratio > 0.1f) {  // More than 10% of samples
        return max_severity * undercut_ratio;
    }

    return 0.0f;
}

bool UndercutDetector::ray_intersects_face(
    const Point3D& origin,
    const Vector3& direction,
    int face_id) {

    // Get tessellated mesh
    TessellationResult mesh = evaluator_.tessellate(3);

    // Check all triangles belonging to this face
    for (size_t tri_idx = 0; tri_idx < mesh.triangle_count(); ++tri_idx) {
        int tri_face_id = mesh.face_parents[tri_idx];
        
        if (tri_face_id != face_id) {
            continue;
        }

        // Get triangle vertices
        int idx0 = mesh.triangles[tri_idx * 3 + 0];
        int idx1 = mesh.triangles[tri_idx * 3 + 1];
        int idx2 = mesh.triangles[tri_idx * 3 + 2];

        Point3D v0(
            mesh.vertices[idx0 * 3 + 0],
            mesh.vertices[idx0 * 3 + 1],
            mesh.vertices[idx0 * 3 + 2]
        );
        Point3D v1(
            mesh.vertices[idx1 * 3 + 0],
            mesh.vertices[idx1 * 3 + 1],
            mesh.vertices[idx1 * 3 + 2]
        );
        Point3D v2(
            mesh.vertices[idx2 * 3 + 0],
            mesh.vertices[idx2 * 3 + 1],
            mesh.vertices[idx2 * 3 + 2]
        );

        // Moller-Trumbore ray-triangle intersection
        Vector3 edge1 = subtract(v1, v0);
        Vector3 edge2 = subtract(v2, v0);
        Vector3 h = cross(direction, edge2);
        float a = dot(edge1, h);

        if (std::abs(a) < 1e-6f) {
            continue;
        }

        float f = 1.0f / a;
        Vector3 s = subtract(origin, v0);
        float u = f * dot(s, h);

        if (u < 0.0f || u > 1.0f) {
            continue;
        }

        Vector3 q = cross(s, edge1);
        float v = f * dot(direction, q);

        if (v < 0.0f || u + v > 1.0f) {
            continue;
        }

        float t = f * dot(edge2, q);

        if (t > 1e-6f) {
            return true;
        }
    }

    return false;
}

} // namespace latent
