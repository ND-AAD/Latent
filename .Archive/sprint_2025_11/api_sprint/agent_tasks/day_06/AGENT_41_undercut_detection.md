# Agent 41: Undercut Detection Implementation

**Day**: 6
**Duration**: 5-6 hours
**Cost**: $6-10 (100K tokens)

---

## Mission

Implement ray-casting undercut detection for rigid plaster molds.

---

## Context

**CRITICAL**: Rigid plaster cannot tolerate ANY negative draft. Even 0.1° negative requires additional mold piece.

**Algorithm**: Ray-cast from each face along demolding direction. Any intersection = undercut.

**Dependencies**: Agent 40 (validator.h), SubDEvaluator

---

## Deliverables

**File**: `cpp_core/constraints/undercut_detector.cpp`

---

## Requirements

```cpp
// cpp_core/constraints/undercut_detector.cpp

#include "validator.h"
#include <cmath>

namespace latent {

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

    // Sample face center
    Point3D center, normal;
    evaluator_.evaluate_limit(face_id, 0.5f, 0.5f, center, normal);

    // Cast ray from face center along demolding direction
    // Check if ray hits any other face (occlusion = undercut)

    // [IMPLEMENT RAY-CASTING LOGIC]

    // Severity = how deep the undercut (distance ratio)
    return 0.0f;  // Placeholder
}

bool UndercutDetector::ray_intersects_face(
    const Point3D& origin,
    const Vector3& direction,
    int face_id) {

    // Ray-triangle intersection test
    // [IMPLEMENT MOLLER-TRUMBORE ALGORITHM]

    return false;
}

} // namespace latent
```

---

## Success Criteria

- [ ] Ray-casting implementation complete
- [ ] Intersection detection accurate
- [ ] Severity measurement correct
- [ ] Tests pass (cube, sphere)

---

**Ready to begin!**
