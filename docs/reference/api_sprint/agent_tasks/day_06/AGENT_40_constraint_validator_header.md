# Agent 40: C++ Constraint Validator Header

**Day**: 6
**Phase**: Phase 1b - Constraints + Molds
**Duration**: 2-3 hours
**Estimated Cost**: $3-5 (50K tokens, Sonnet)

---

## Mission

Define C++ interfaces for constraint validation (undercut detection, draft angle checking).

---

## Context

**From v5.0 Specification (§6.1)**: Three-tier constraint hierarchy:
1. Physical (must fix) - undercuts, impossible geometry
2. Manufacturing (negotiable) - thin walls, tight draft
3. Mathematical tensions (aesthetic features) - symmetry breaks

**From Slip-Casting Reference**:
- Draft angle: 0.5-2.0° minimum (rigid plaster molds)
- Undercuts: ZERO tolerance (ANY negative draft requires additional mold piece)

**Dependencies**: SubDEvaluator (for limit surface queries)

---

## Deliverables

**File**: `cpp_core/constraints/validator.h`

---

## Requirements

```cpp
// cpp_core/constraints/validator.h

#pragma once

#include "geometry/types.h"
#include "geometry/subd_evaluator.h"
#include <vector>
#include <map>
#include <string>

namespace latent {

// Constraint severity levels
enum class ConstraintLevel {
    ERROR,      // Physical impossibility - must fix
    WARNING,    // Manufacturing challenge - negotiable
    FEATURE     // Mathematical tension - aesthetic feature
};

// Constraint report for a single constraint
struct ConstraintViolation {
    ConstraintLevel level;
    std::string description;
    int face_id;              // Which face violates
    float severity;           // 0.0-1.0 magnitude
    std::string suggestion;   // How to fix
};

// Complete constraint report for a region
class ConstraintReport {
public:
    std::vector<ConstraintViolation> violations;

    void add_error(const std::string& desc, int face_id, float severity);
    void add_warning(const std::string& desc, int face_id, float severity);
    void add_feature(const std::string& desc, int face_id);

    bool has_errors() const;
    bool has_warnings() const;
    int error_count() const;
    int warning_count() const;
};

// Undercut detector
class UndercutDetector {
public:
    UndercutDetector(const SubDEvaluator& evaluator);

    // Detect undercuts along demolding direction
    std::map<int, float> detect_undercuts(
        const std::vector<int>& face_indices,
        const Vector3& demolding_direction
    );

    // Check single face for undercut
    float check_face_undercut(
        int face_id,
        const Vector3& demolding_direction
    );

private:
    const SubDEvaluator& evaluator_;

    // Ray-cast to detect occlusions
    bool ray_intersects_face(
        const Point3D& origin,
        const Vector3& direction,
        int face_id
    );
};

// Draft angle checker
class DraftChecker {
public:
    DraftChecker(const SubDEvaluator& evaluator);

    // Compute draft angles for all faces
    std::map<int, float> compute_draft_angles(
        const std::vector<int>& face_indices,
        const Vector3& demolding_direction
    );

    // Check single face draft angle
    float check_face_draft(
        int face_id,
        const Vector3& demolding_direction
    );

    // Minimum acceptable draft angle (degrees)
    static constexpr float MIN_DRAFT_ANGLE = 0.5f;
    static constexpr float RECOMMENDED_DRAFT_ANGLE = 2.0f;

private:
    const SubDEvaluator& evaluator_;

    // Compute angle between face normal and demolding direction
    float compute_angle(const Vector3& normal, const Vector3& demold_dir);
};

// Complete constraint validator
class ConstraintValidator {
public:
    ConstraintValidator(const SubDEvaluator& evaluator);

    // Validate complete region
    ConstraintReport validate_region(
        const std::vector<int>& face_indices,
        const Vector3& demolding_direction,
        float min_wall_thickness = 3.0f  // mm
    );

private:
    const SubDEvaluator& evaluator_;
    UndercutDetector undercut_detector_;
    DraftChecker draft_checker_;
};

} // namespace latent
```

---

## Success Criteria

- [ ] Header defines all constraint classes
- [ ] Three-tier constraint levels (ERROR/WARNING/FEATURE)
- [ ] UndercutDetector interface complete
- [ ] DraftChecker with correct minimum angles
- [ ] ConstraintValidator coordinates all checks
- [ ] Compiles without errors

---

## Integration Notes

**Used by**:
- Agent 41: Undercut implementation
- Agent 42: Draft checker implementation
- Agent 43: Python bindings

**File Placement**:
```
cpp_core/
├── constraints/
│   └── validator.h    ← YOU CREATE THIS
```

---

**Ready to begin!**
