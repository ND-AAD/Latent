# Agent 42: Draft Angle Checker

**Day**: 6
**Duration**: 4-5 hours
**Cost**: $5-8 (80K tokens)

---

## Mission

Implement draft angle computation per face against demolding direction.

---

## Context

**Draft angle** = angle between face normal and demolding direction.
- Minimum: 0.5° (absolute minimum)
- Recommended: 2.0° (reliable production)
- Formula: angle = acos(normal · demold_dir)

**Dependencies**: Agent 40, SubDEvaluator

---

## Deliverables

**File**: `cpp_core/constraints/draft_checker.cpp`

---

## Requirements

```cpp
// cpp_core/constraints/draft_checker.cpp

#include "validator.h"
#include <cmath>

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
    Point3D point, normal;
    evaluator_.evaluate_limit(face_id, 0.5f, 0.5f, point, normal);

    // Compute angle
    return compute_angle(normal, demolding_direction);
}

float DraftChecker::compute_angle(
    const Vector3& normal,
    const Vector3& demold_dir) {

    // Angle between normal and demolding direction
    float dot_product = normal.dot(demold_dir);
    float angle_rad = std::acos(std::clamp(dot_product, -1.0f, 1.0f));

    // Convert to degrees
    float angle_deg = angle_rad * 180.0f / M_PI;

    // Draft angle is 90° - angle to demolding direction
    return 90.0f - angle_deg;
}

} // namespace latent
```

---

## Success Criteria

- [ ] Draft angle computation accurate
- [ ] Handles parallel faces (90° draft)
- [ ] Handles perpendicular faces (0° draft)
- [ ] Tests pass

---

**Ready to begin!**
