# Agent 47: NURBS Surface Fitting

**Day**: 7
**Duration**: 6-7 hours
**Cost**: $7-12 (120K tokens)

---

## Mission

Sample exact SubD limit surface and fit NURBS using OpenCASCADE GeomAPI.

---

## Context

**CRITICAL**: Sample from EXACT limit surface, not tessellated mesh.

**Algorithm**:
1. Sample each SubD face at regular (u,v) grid using exact evaluation
2. Use GeomAPI_PointsToBSplineSurface to fit NURBS
3. Validate deviation < tolerance (0.1mm)

**Dependencies**: Agent 46, SubDEvaluator, OpenCASCADE

---

## Deliverables

**File**: `cpp_core/geometry/nurbs_fitting.cpp`

---

## Requirements

```cpp
// cpp_core/geometry/nurbs_fitting.cpp

#include "nurbs_generator.h"
#include <GeomAPI_PointsToBSplineSurface.hxx>
#include <TColgp_Array2OfPnt.hxx>

namespace latent {

Handle(Geom_BSplineSurface) NURBSMoldGenerator::fit_nurbs_surface(
    const std::vector<int>& face_indices,
    int sample_density) {

    // Sample exact limit surface
    std::vector<Point3D> samples = sample_limit_surface(face_indices, sample_density);

    // Convert to OpenCASCADE points
    int n = sample_density;
    TColgp_Array2OfPnt points(1, n, 1, n);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            int idx = i * n + j;
            points.SetValue(i+1, j+1,
                gp_Pnt(samples[idx].x, samples[idx].y, samples[idx].z));
        }
    }

    // Fit B-spline surface
    GeomAPI_PointsToBSplineSurface fitter(points);

    if (!fitter.IsDone()) {
        throw std::runtime_error("NURBS fitting failed");
    }

    return fitter.Surface();
}

std::vector<Point3D> NURBSMoldGenerator::sample_limit_surface(
    const std::vector<int>& face_indices,
    int density) {

    std::vector<Point3D> samples;

    for (int face_id : face_indices) {
        // Sample face at regular grid
        for (int i = 0; i < density; ++i) {
            for (int j = 0; j < density; ++j) {
                float u = static_cast<float>(i) / (density - 1);
                float v = static_cast<float>(j) / (density - 1);

                // EXACT limit evaluation
                Point3D pt = evaluator_.evaluate_limit_point(face_id, u, v);
                samples.push_back(pt);
            }
        }
    }

    return samples;
}

} // namespace latent
```

---

## Success Criteria

- [ ] Samples from exact limit surface
- [ ] NURBS fitting succeeds
- [ ] Deviation < 0.1mm
- [ ] Quality check passes
- [ ] Tests pass (sphere: analytical comparison)

---

**Ready to begin!**
