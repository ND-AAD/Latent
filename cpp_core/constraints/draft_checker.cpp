// cpp_core/constraints/draft_checker.cpp

#include "validator.h"
#include <cmath>
#include <algorithm>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace latent {

DraftChecker::DraftChecker(const SubDEvaluator& evaluator)
    : evaluator_(evaluator) {}

std::map<int, float> DraftChecker::compute_draft_angles(
    const std::vector<int>& face_indices,
    const Vector3& demolding_direction) {

    std::map<int, float> draft_map;

    for (int face_id : face_indices) {
        float draft_angle = check_face_draft(face_id, demolding_direction);
        draft_map[face_id] = draft_angle;
    }

    return draft_map;
}

float DraftChecker::check_face_draft(
    int face_id,
    const Vector3& demolding_direction) {

    // Evaluate face normal at center
    Point3D point, normal_pt;
    evaluator_.evaluate_limit(face_id, 0.5f, 0.5f, point, normal_pt);

    // Convert normal to Vector3
    Vector3 normal(normal_pt);

    // Compute angle
    return compute_angle(normal, demolding_direction);
}

float DraftChecker::compute_angle(
    const Vector3& normal,
    const Vector3& demold_dir) {

    // Normalize vectors
    float normal_len = std::sqrt(normal.x * normal.x + normal.y * normal.y + normal.z * normal.z);
    float demold_len = std::sqrt(demold_dir.x * demold_dir.x + demold_dir.y * demold_dir.y + demold_dir.z * demold_dir.z);
    
    if (normal_len < 1e-6f || demold_len < 1e-6f) {
        return 0.0f;  // Degenerate case
    }

    // Compute normalized dot product
    float dot_product = (normal.x * demold_dir.x + normal.y * demold_dir.y + normal.z * demold_dir.z) / (normal_len * demold_len);
    
    // Clamp to [-1, 1] to avoid numerical errors in acos
    dot_product = std::clamp(dot_product, -1.0f, 1.0f);
    
    // Angle between normal and demolding direction (radians)
    float angle_rad = std::acos(dot_product);

    // Convert to degrees
    float angle_deg = angle_rad * 180.0f / M_PI;

    // Draft angle is 90° - angle to demolding direction
    // When normal is parallel to demolding direction (angle_deg = 0), draft = 90°
    // When normal is perpendicular to demolding direction (angle_deg = 90), draft = 0°
    return 90.0f - angle_deg;
}

} // namespace latent
