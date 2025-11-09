# Agent 48: Draft Angle Transformation

**Day**: 7
**Duration**: 5-6 hours
**Cost**: $6-10 (100K tokens)

---

## Mission

Apply draft angle transformation to NURBS surface for mold demolding.

---

## Context

**Draft transformation**: Tilt surface relative to fixed parting line.
- Parting line remains fixed
- Surface tilted by draft angle
- Direction: along demolding vector

**Dependencies**: Agent 47, OpenCASCADE transformation APIs

---

## Deliverables

**File**: `cpp_core/geometry/draft_transform.cpp`

---

## Requirements

```cpp
// cpp_core/geometry/draft_transform.cpp

#include "nurbs_generator.h"
#include <BRepOffsetAPI_DraftAngle.hxx>
#include <gp_Pln.hxx>
#include <gp_Ax1.hxx>

namespace latent {

Handle(Geom_BSplineSurface) NURBSMoldGenerator::apply_draft_angle(
    Handle(Geom_BSplineSurface) surface,
    const Vector3& demolding_direction,
    float draft_angle_degrees,
    const std::vector<Point3D>& parting_line) {

    // Convert draft angle to radians
    float angle_rad = draft_angle_degrees * M_PI / 180.0f;

    // [IMPLEMENT DRAFT TRANSFORMATION]
    // Options:
    // 1. BRepOffsetAPI_DraftAngle (for solids)
    // 2. Custom control point transformation
    // 3. Normal-based vector field displacement

    // Placeholder: return input (implement transformation)
    return surface;
}

} // namespace latent
```

---

## Success Criteria

- [ ] Draft angle applied correctly
- [ ] Parting line remains fixed
- [ ] Draft angle validated (tests)
- [ ] Surface remains valid NURBS

---

**Ready to begin!**
