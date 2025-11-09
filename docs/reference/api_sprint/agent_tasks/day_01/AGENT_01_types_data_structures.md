# Agent 1: Types & Data Structures

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 2 hours
**Estimated Cost**: $2-3 (30K tokens, Sonnet)

---

## Mission

Create foundational C++ data structures for SubD control cage and tessellation results.

---

## Context

You are implementing the foundational types for a SubD (subdivision surface) evaluation system using OpenSubdiv. These types will be used throughout the C++ core and exposed to Python via pybind11.

**Project**: Ceramic mold generation system using exact SubD limit surfaces
**Architecture**: Hybrid C++/Python (C++ for geometry, Python for UI)

---

## Deliverables

**File to Create**: `cpp_core/geometry/types.h`

---

## Requirements

### 1. Point3D Struct
```cpp
struct Point3D {
    float x, y, z;
    Point3D();
    Point3D(float _x, float _y, float _z);
};
```

### 2. SubDControlCage Struct
```cpp
struct SubDControlCage {
    std::vector<Point3D> vertices;
    std::vector<std::vector<int>> faces;  // Quad/n-gon faces
    std::vector<std::pair<int, float>> creases;  // Edge ID, sharpness

    size_t vertex_count() const;
    size_t face_count() const;
};
```

### 3. TessellationResult Struct
```cpp
struct TessellationResult {
    std::vector<float> vertices;      // Flattened [x,y,z, x,y,z, ...]
    std::vector<float> normals;       // Flattened normals
    std::vector<int> triangles;       // Flattened triangle indices [i,j,k, ...]
    std::vector<int> face_parents;    // Which SubD face each tri came from

    size_t vertex_count() const;      // Return vertices.size() / 3
    size_t triangle_count() const;    // Return triangles.size() / 3
};
```

---

## Code Template

```cpp
#pragma once
#include <vector>
#include <array>
#include <cstdint>

namespace latent {

// [IMPLEMENT STRUCTS HERE]

}  // namespace latent
```

---

## Success Criteria

- [ ] File compiles without errors
- [ ] All structs have proper constructors
- [ ] Helper methods (vertex_count, face_count, etc.) implemented
- [ ] Code is well-commented
- [ ] Follows namespace convention (latent::)

---

## Testing

Create a simple test program to verify:
```cpp
#include "types.h"
#include <iostream>

int main() {
    using namespace latent;

    // Test Point3D
    Point3D p(1.0f, 2.0f, 3.0f);
    assert(p.x == 1.0f && p.y == 2.0f && p.z == 3.0f);

    // Test SubDControlCage
    SubDControlCage cage;
    cage.vertices.push_back(Point3D(0,0,0));
    cage.vertices.push_back(Point3D(1,0,0));
    cage.faces.push_back({0, 1});
    assert(cage.vertex_count() == 2);
    assert(cage.face_count() == 1);

    // Test TessellationResult
    TessellationResult result;
    result.vertices = {0,0,0, 1,0,0, 0,1,0};  // 3 vertices
    result.triangles = {0,1,2};               // 1 triangle
    assert(result.vertex_count() == 3);
    assert(result.triangle_count() == 1);

    std::cout << "✅ All type tests passed!" << std::endl;
    return 0;
}
```

---

## Integration Notes

**Next Steps** (handled by other agents):
- Agent 2 will use these types in SubDEvaluator header
- Agent 5 will bind these to Python via pybind11

**No dependencies** - this agent can run completely independently.

---

## Output Format

Provide:
1. Complete `types.h` file
2. Brief explanation of design decisions
3. Any notes for integration

---

**Ready to begin!**
