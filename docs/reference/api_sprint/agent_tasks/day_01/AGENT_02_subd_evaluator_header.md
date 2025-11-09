# Agent 2: SubDEvaluator Header

**Day**: 1
**Phase**: Phase 0 - C++ Core Foundation
**Duration**: 2 hours
**Estimated Cost**: $2-3 (30K tokens, Sonnet)

---

## Mission

Define the SubDEvaluator class interface that will wrap OpenSubdiv's TopologyRefiner for exact SubD limit surface evaluation.

---

## Context

You are creating the header file for the core SubD evaluation class. This class will:
- Initialize OpenSubdiv TopologyRefiner from control cage
- Perform uniform/adaptive subdivision
- Tessellate for display (triangulate refined mesh)
- Evaluate exact points on limit surface
- Track triangle→face mapping for selection

**Dependencies**: Requires `types.h` (provided by Agent 1)

---

## Deliverables

**File to Create**: `cpp_core/geometry/subd_evaluator.h`

---

## Requirements

### Class Interface

```cpp
class SubDEvaluator {
private:
    std::unique_ptr<OpenSubdiv::Far::TopologyRefiner> refiner_;
    std::vector<int> triangle_to_face_map_;
    bool initialized_;

public:
    SubDEvaluator();
    ~SubDEvaluator();

    // Build from control cage
    void initialize(const SubDControlCage& cage);

    // Check if initialized
    bool is_initialized() const { return initialized_; }

    // Tessellate for display
    TessellationResult tessellate(int subdivision_level = 3,
                                   bool adaptive = false);

    // Exact limit surface evaluation
    Point3D evaluate_limit_point(int face_index, float u, float v) const;

    // Evaluate with normal
    void evaluate_limit(int face_index, float u, float v,
                       Point3D& point, Point3D& normal) const;

    // Get parent face for tessellated triangle
    int get_parent_face(int triangle_index) const;

    // Get statistics
    size_t get_control_vertex_count() const;
    size_t get_control_face_count() const;
};
```

---

## Code Template

```cpp
#pragma once
#include "types.h"
#include <opensubdiv/far/topologyRefiner.h>
#include <memory>

namespace latent {

/**
 * SubDEvaluator: Wrapper for OpenSubdiv topology refinement
 *
 * Provides exact limit surface evaluation and tessellation
 * for Catmull-Clark subdivision surfaces.
 */
class SubDEvaluator {
private:
    // [PRIVATE MEMBERS]

public:
    // [PUBLIC INTERFACE]
};

}  // namespace latent
```

---

## Success Criteria

- [ ] Header compiles with OpenSubdiv includes
- [ ] All public methods declared
- [ ] Private members use smart pointers appropriately
- [ ] Well-documented with Doxygen-style comments
- [ ] No implementation details (header only)

---

## OpenSubdiv Integration Notes

**Include Path**:
```cpp
#include <opensubdiv/far/topologyRefiner.h>
#include <opensubdiv/far/topologyDescriptor.h>
#include <opensubdiv/far/primvarRefiner.h>
```

**TopologyRefiner**:
- Use `std::unique_ptr` for RAII
- Created via `Far::TopologyRefinerFactory`
- Stores subdivision topology

**Important**: This is HEADER ONLY. Implementation comes from Agent 4.

---

## Documentation Guidelines

Add class-level documentation:
```cpp
/**
 * @brief Evaluates exact limit surface of SubD control cage
 *
 * Uses OpenSubdiv to build TopologyRefiner and evaluate limit surface
 * using Stam's eigenanalysis. Provides both tessellation for display
 * and exact point evaluation for analysis.
 *
 * Example:
 * @code
 *   SubDControlCage cage = ...;
 *   SubDEvaluator eval;
 *   eval.initialize(cage);
 *   TessellationResult mesh = eval.tessellate(3);  // Level 3
 *   Point3D pt = eval.evaluate_limit_point(0, 0.5, 0.5);
 * @endcode
 */
```

---

## Integration Notes

**Used by**:
- Agent 4 will implement this interface
- Agent 5 will bind to Python
- Agent 27 will add curvature analysis methods

**Depends on**:
- Agent 1's `types.h`
- OpenSubdiv (installed on system)

---

## Output Format

Provide:
1. Complete `subd_evaluator.h` file
2. Brief explanation of design choices
3. Any questions or clarifications needed

---

**Ready to begin!**
