# Days 5-7 Agent Specifications Summary

**Created**: November 9, 2025
**Author**: Claude (Specification Agent)
**Status**: ✅ All 18 specifications complete and aligned

---

## Overview

This document summarizes the comprehensive agent specifications created for Days 5-7 of the 10-day sprint, covering:
- **Day 5**: Spectral Analysis + Integration (Agents 34-39)
- **Day 6**: Constraint Validation (Agents 40-45)
- **Day 7**: OpenCASCADE + NURBS Generation (Agents 46-51)

**Total**: 18 agent specifications ready for parallel execution

---

## Day 5: Spectral Analysis + Integration (Agents 34-39)

### Agent 34: Laplacian Matrix Builder
**Duration**: 4-5 hours | **Cost**: $4-7

**Key Deliverables**:
- `app/analysis/laplacian.py` - Cotangent-weight Laplace-Beltrami operator
- Exact limit surface geometry (not tessellated mesh approximation)
- Verification functions (symmetry, row sums)
- Comprehensive tests with analytical validation (sphere eigenvalues)

**Critical Alignment**:
- ✅ Uses exact limit evaluation for accurate cotangent weights
- ✅ Maintains lossless principle (geometry from limit surface)
- ✅ Proper sparse matrix handling (scipy.sparse)

---

### Agent 35: Spectral Decomposition
**Duration**: 5-6 hours | **Cost**: $5-9

**Key Deliverables**:
- `app/analysis/spectral_decomposition.py` - Eigenfunction analysis
- `app/analysis/spectral_lens.py` - Lens interface
- Nodal domain extraction via flood-fill
- Resonance scoring system

**Critical Alignment**:
- ✅ Regions defined parametrically (face sets + UV boundaries)
- ✅ From v5.0 §3.1.1: "Reveals natural vibration modes"
- ✅ Eigenfunction zero-crossings create natural boundaries
- ✅ Proper connected component analysis

**Mathematical Validation**:
- First eigenvalue ≈ 0 (constant function)
- Eigenvalue multiplicity detection (sphere symmetry)
- Nodal domain count matches theoretical predictions

---

### Agent 36: Spectral Visualization
**Duration**: 3-4 hours | **Cost**: $4-6

**Key Deliverables**:
- `app/geometry/spectral_renderer.py` - VTK eigenfunction rendering
- `app/ui/spectral_viz_widget.py` - Interactive controls
- Diverging colormap (blue-white-red)
- Nodal line extraction as zero-contours

**Features**:
- Mode selector (slider + combo box)
- Eigenvalue display
- Nodal line toggle
- Extract regions button

---

### Agent 37: Region Merge/Split Tools
**Duration**: 4-5 hours | **Cost**: $4-7

**Key Deliverables**:
- `app/operations/region_operations.py` - Merge/split logic
- `app/ui/region_editor_widget.py` - UI controls
- Parametric definition maintenance

**Critical Alignment**:
- ✅ Operations preserve parametric (face_id, u, v) representation
- ✅ Boundary curves updated correctly

---

### Agent 38: Lens Integration Manager
**Duration**: 3-4 hours | **Cost**: $4-6

**Key Deliverables**:
- `app/analysis/lens_manager.py` - Unified lens interface
- LensType enum (DIFFERENTIAL, SPECTRAL, FLOW, MORSE, THERMAL)
- Resonance score comparison
- Best lens selection

**Architecture**:
- Unified interface for all mathematical lenses
- Result caching by lens type
- Automatic best-lens recommendation

---

### Agent 39: Analysis Integration Tests
**Duration**: 3-4 hours | **Cost**: $2-4

**Key Deliverables**:
- `tests/integration/test_analysis_pipeline.py`
- `tests/integration/test_lens_comparison.py`
- End-to-end workflow validation

**Coverage**:
- Complete spectral pipeline
- Lens comparison
- Performance benchmarks (<2 seconds)

---

## Day 6: Constraint Validation (Agents 40-45)

### Agent 40: C++ Constraint Validator Header
**Duration**: 2-3 hours | **Cost**: $3-5

**Key Deliverables**:
- `cpp_core/constraints/validator.h`
- Three-tier hierarchy (ERROR/WARNING/FEATURE)
- UndercutDetector, DraftChecker interfaces
- ConstraintReport structure

**Critical Alignment**:
- ✅ From v5.0 §6.1: Three-tier constraint validation
- ✅ Physical (must fix), Manufacturing (negotiable), Mathematical tensions (features)

---

### Agent 41: Undercut Detection
**Duration**: 5-6 hours | **Cost**: $6-10

**Key Deliverables**:
- `cpp_core/constraints/undercut_detector.cpp`
- Ray-casting intersection detection
- Severity measurement

**From Slip-Casting Spec**:
- ✅ ZERO tolerance for rigid plaster molds
- ✅ ANY negative draft requires additional mold piece
- ✅ Even 0.1° negative is failure

---

### Agent 42: Draft Angle Checker
**Duration**: 4-5 hours | **Cost**: $5-8

**Key Deliverables**:
- `cpp_core/constraints/draft_checker.cpp`
- Per-face draft angle computation
- Angle = acos(normal · demolding_direction)

**From Slip-Casting Spec**:
- ✅ Minimum: 0.5° (absolute minimum)
- ✅ Recommended: 2.0° (reliable production)
- ✅ Depth-dependent: 1° per 1" cavity depth

---

### Agent 43: Constraint Python Bindings
**Duration**: 2-3 hours | **Cost**: $2-4

**Key Deliverables**:
- Updated `cpp_core/python_bindings/py_bindings.cpp`
- ConstraintLevel enum exposure
- ConstraintValidator binding
- NumPy array returns for face-wise data

---

### Agent 44: Constraint UI Panel
**Duration**: 4-5 hours | **Cost**: $4-7

**Key Deliverables**:
- `app/ui/constraint_panel.py`
- 3-tier tree widget (Errors/Warnings/Features)
- Color-coded display (red/yellow/blue)
- Click to highlight face in viewport

---

### Agent 45: Constraint Visualization
**Duration**: 3-4 hours | **Cost**: $4-6

**Key Deliverables**:
- `app/geometry/constraint_renderer.py`
- VTK rendering of violations
- Undercut highlighting (red)
- Draft angle gradient (red→yellow→green)
- Demolding vector arrow

---

## Day 7: OpenCASCADE + NURBS Generation (Agents 46-51)

### Agent 46: NURBS Generator Header
**Duration**: 2-3 hours | **Cost**: $3-5

**Key Deliverables**:
- `cpp_core/geometry/nurbs_generator.h`
- NURBSMoldGenerator class interface
- OpenCASCADE integration (Handle types)
- Quality validation structures

**Methods**:
- `fit_nurbs_surface()` - Sample and fit
- `apply_draft_angle()` - Transform for demolding
- `create_mold_solid()` - Generate solid Brep
- `add_registration_keys()` - Keys/notches for alignment

---

### Agent 47: NURBS Surface Fitting
**Duration**: 6-7 hours | **Cost**: $7-12

**Key Deliverables**:
- `cpp_core/geometry/nurbs_fitting.cpp`
- Exact limit surface sampling (high resolution grid)
- GeomAPI_PointsToBSplineSurface integration
- Quality validation (<0.1mm deviation)

**Critical Alignment**:
- ✅ **SAMPLES FROM EXACT LIMIT SURFACE** (not tessellation)
- ✅ Maintains lossless architecture until fabrication
- ✅ Deviation checking ensures quality

---

### Agent 48: Draft Transformation
**Duration**: 5-6 hours | **Cost**: $6-10

**Key Deliverables**:
- `cpp_core/geometry/draft_transform.cpp`
- Vector field-based transformation
- Parting line constraints (fixed base)
- BRepOffsetAPI_DraftAngle or custom implementation

**Algorithm**:
- Parting line remains fixed
- Surface tilted by draft angle
- Direction aligned with demolding vector

---

### Agent 49: Solid Brep Creation
**Duration**: 5-6 hours | **Cost**: $6-10

**Key Deliverables**:
- `cpp_core/geometry/mold_solid.cpp`
- Thicken NURBS to solid (BRepOffsetAPI_MakeThickSolid)
- Registration key/notch creation
- Boolean union operations

**From Slip-Casting Spec**:
- ✅ Wall thickness: 1.5-2" (40-50mm) standard
- ✅ Registration keys: 1/4" from model edge
- ✅ Tapered profile for easy mating

---

### Agent 50: NURBS Python Bindings
**Duration**: 2-3 hours | **Cost**: $3-5

**Key Deliverables**:
- Updated `cpp_core/python_bindings/py_bindings.cpp`
- NURBSMoldGenerator binding
- Handle type conversion (OpenCASCADE → Python)
- Serialization support for export

---

### Agent 51: NURBS Tests
**Duration**: 3-4 hours | **Cost**: $2-4

**Key Deliverables**:
- `tests/test_nurbs_generation.py`
- Fitting accuracy validation (<0.1mm)
- Draft angle verification
- Solid validity checking
- Round-trip tests

**Test Cases**:
- Sphere (analytical comparison)
- Planar surfaces (exact fit)
- Complex geometry (tolerance bounds)

---

## Architectural Compliance Summary

### Lossless Until Fabrication ✅

**Day 5 (Spectral)**:
- Laplacian built from exact limit geometry
- Eigenfunctions on true surface, not approximation
- Regions defined parametrically (face_id, u, v)

**Day 6 (Constraints)**:
- Draft angles from exact limit normals
- Undercut detection on exact surface
- No mesh-based approximations

**Day 7 (NURBS)**:
- **CRITICAL**: Samples from exact limit surface
- NURBS fit to exact geometry
- Single approximation at final export (acceptable per v5.0)

---

### V5.0 Specification Alignment ✅

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **§3.1.1 Spectral Lens** | ✅ | Agent 35: Eigenfunction nodal domains |
| **§6.1 3-Tier Constraints** | ✅ | Agent 40-45: ERROR/WARNING/FEATURE |
| **§2.2 Parametric Regions** | ✅ | All agents maintain (face_id, u, v) |
| **Slip-Casting Physics** | ✅ | Agent 41-42: 0.5-2.0° draft, no undercuts |
| **NURBS Mold Generation** | ✅ | Agent 46-51: Exact sampling → fitting |

---

### Slip-Casting Technical Reference Alignment ✅

| Constraint | Value | Source |
|------------|-------|--------|
| **Draft angle minimum** | 0.5° | Agent 42 constant |
| **Draft angle recommended** | 2.0° | Agent 42 constant |
| **Undercut tolerance** | 0.0° | Agent 41 (rigid plaster) |
| **Wall thickness** | 40mm (1.5-2") | Agent 49 default |
| **NURBS deviation** | <0.1mm | Agent 47 tolerance |
| **Registration key spacing** | 1/4" from edge | Agent 49 (from Pincus) |

---

## File Structure Summary

```
app/
├── analysis/
│   ├── laplacian.py                    ← Agent 34
│   ├── spectral_decomposition.py       ← Agent 35
│   ├── spectral_lens.py                ← Agent 35
│   └── lens_manager.py                 ← Agent 38
├── operations/
│   └── region_operations.py            ← Agent 37
├── geometry/
│   ├── spectral_renderer.py            ← Agent 36
│   └── constraint_renderer.py          ← Agent 45
└── ui/
    ├── spectral_viz_widget.py          ← Agent 36
    ├── region_editor_widget.py         ← Agent 37
    └── constraint_panel.py             ← Agent 44

cpp_core/
├── constraints/
│   ├── validator.h                     ← Agent 40
│   ├── undercut_detector.cpp           ← Agent 41
│   └── draft_checker.cpp               ← Agent 42
├── geometry/
│   ├── nurbs_generator.h               ← Agent 46
│   ├── nurbs_fitting.cpp               ← Agent 47
│   ├── draft_transform.cpp             ← Agent 48
│   └── mold_solid.cpp                  ← Agent 49
└── python_bindings/
    ├── py_constraints.cpp              ← Agent 43
    └── py_nurbs.cpp                    ← Agent 50

tests/
├── test_laplacian.py                   ← Agent 34
├── test_spectral_decomposition.py      ← Agent 35
├── test_spectral_viz.py                ← Agent 36
├── test_region_operations.py           ← Agent 37
├── test_lens_manager.py                ← Agent 38
├── test_nurbs_generation.py            ← Agent 51
└── integration/
    ├── test_analysis_pipeline.py       ← Agent 39
    └── test_lens_comparison.py         ← Agent 39
```

---

## Cost & Duration Summary

### Day 5: Spectral Analysis
| Agent | Duration | Cost | Deliverables |
|-------|----------|------|--------------|
| 34 | 4-5h | $4-7 | Laplacian builder |
| 35 | 5-6h | $5-9 | Spectral decomposition |
| 36 | 3-4h | $4-6 | Visualization |
| 37 | 4-5h | $4-7 | Region operations |
| 38 | 3-4h | $4-6 | Lens manager |
| 39 | 3-4h | $2-4 | Integration tests |
| **Total** | **22-28h** | **$23-39** | **6 agents** |

### Day 6: Constraint Validation
| Agent | Duration | Cost | Deliverables |
|-------|----------|------|--------------|
| 40 | 2-3h | $3-5 | Validator header |
| 41 | 5-6h | $6-10 | Undercut detection |
| 42 | 4-5h | $5-8 | Draft checker |
| 43 | 2-3h | $2-4 | Python bindings |
| 44 | 4-5h | $4-7 | UI panel |
| 45 | 3-4h | $4-6 | Visualization |
| **Total** | **20-26h** | **$24-40** | **6 agents** |

### Day 7: NURBS Generation
| Agent | Duration | Cost | Deliverables |
|-------|----------|------|--------------|
| 46 | 2-3h | $3-5 | NURBS header |
| 47 | 6-7h | $7-12 | Surface fitting |
| 48 | 5-6h | $6-10 | Draft transform |
| 49 | 5-6h | $6-10 | Solid creation |
| 50 | 2-3h | $3-5 | Python bindings |
| 51 | 3-4h | $2-4 | Tests |
| **Total** | **23-29h** | **$27-46** | **6 agents** |

### Grand Total (Days 5-7)
- **Agents**: 18
- **Duration**: 65-83 hours (agent work time)
- **Cost**: $74-125 (estimated)
- **Actual projected**: ~$50-80 (based on Day 1-3 savings)

---

## Critical Success Factors

### Technical Quality
1. ✅ **Lossless architecture maintained** throughout
2. ✅ **Exact limit surface evaluation** for all analysis
3. ✅ **Parametric region definitions** preserved
4. ✅ **OpenCASCADE integration** properly structured
5. ✅ **Slip-casting physics** accurately encoded

### Testing Coverage
1. ✅ **Unit tests** for each agent
2. ✅ **Integration tests** for complete pipelines
3. ✅ **Analytical validation** (sphere eigenvalues, etc.)
4. ✅ **Performance benchmarks** (<2 seconds analysis)
5. ✅ **Quality checks** (NURBS deviation <0.1mm)

### Documentation
1. ✅ **Comprehensive specifications** for all 18 agents
2. ✅ **Architecture alignment notes** in each spec
3. ✅ **Integration guidance** between agents
4. ✅ **Common issues** and solutions documented
5. ✅ **Success criteria** clearly defined

---

## Launch Readiness

All 18 specifications are:
- ✅ **Complete** with all required sections
- ✅ **Aligned** with v5.0 specification
- ✅ **Consistent** with slip-casting physics
- ✅ **Testable** with clear success criteria
- ✅ **Integrated** with dependency notes

**Status**: ✅ **READY TO LAUNCH**

---

## Next Steps

1. **Day 3 QA/QC** - Complete local integration testing
2. **Day 4 Launch** - If Day 3 tests pass, proceed to curvature analysis
3. **Days 5-7** - Use these specifications to launch agents in parallel

**Recommendation**: Launch Day 5 morning agents (34-39) in parallel after Day 4 evening completes.

---

**End of Specification Summary**
