# Agent 49: Solid Brep Creation

**Day**: 7
**Duration**: 5-6 hours
**Cost**: $6-10 (100K tokens)

---

## Mission

Create solid mold cavity from NURBS surface using Boolean operations.

---

## Context

**Mold solid**: NURBS surface + wall thickness → solid Brep
- Offset surface outward (wall thickness)
- Close edges to create solid
- Add registration features (keys)

**Dependencies**: Agent 48, OpenCASCADE Boolean ops

---

## Deliverables

**File**: `cpp_core/geometry/mold_solid.cpp`

---

## Requirements

```cpp
// cpp_core/geometry/mold_solid.cpp

#include "nurbs_generator.h"
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepOffsetAPI_ThruSections.hxx>
#include <BRepOffsetAPI_MakeThickSolid.hxx>

namespace latent {

TopoDS_Shape NURBSMoldGenerator::create_mold_solid(
    Handle(Geom_BSplineSurface) surface,
    float wall_thickness) {

    // Create face from NURBS surface
    BRepBuilderAPI_MakeFace face_maker(surface, 1e-6);
    TopoDS_Face face = face_maker.Face();

    // Thicken to create solid
    TopTools_ListOfShape faces_to_remove;
    BRepOffsetAPI_MakeThickSolid solid_maker(
        face, faces_to_remove, wall_thickness, 1e-6
    );

    if (!solid_maker.IsDone()) {
        throw std::runtime_error("Solid creation failed");
    }

    return solid_maker.Shape();
}

TopoDS_Shape NURBSMoldGenerator::add_registration_keys(
    TopoDS_Shape mold,
    const std::vector<Point3D>& key_positions) {

    // [IMPLEMENT KEY/NOTCH CREATION]
    // Create cylindrical/conical keys at positions
    // Boolean union with mold

    return mold;
}

} // namespace latent
```

---

## Success Criteria

- [ ] Solid created from NURBS
- [ ] Wall thickness correct
- [ ] Solid is valid (IsValid check)
- [ ] Registration keys added
- [ ] Tests pass

---

**Ready to begin!**
