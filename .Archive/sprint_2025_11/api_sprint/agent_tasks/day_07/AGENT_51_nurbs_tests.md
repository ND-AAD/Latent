# Agent 51: NURBS Tests

**Day**: 7
**Duration**: 3-4 hours
**Cost**: $2-4 (60K tokens)

---

## Mission

Comprehensive testing of NURBS mold generation pipeline.

---

## Deliverables

**File**: `tests/test_nurbs_generation.py`

---

## Requirements

```python
# tests/test_nurbs_generation.py

import pytest
import numpy as np
import cpp_core


class TestNURBSGeneration:
    """Test NURBS mold generation pipeline."""

    def test_nurbs_fitting_accuracy(self):
        """Test NURBS fitting deviation < 0.1mm."""
        # Create sphere SubD
        cage = self._create_sphere()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Fit NURBS
        face_indices = list(range(len(cage.faces)))
        nurbs = generator.fit_nurbs_surface(face_indices, sample_density=50)

        # Check quality
        quality = generator.check_fitting_quality(nurbs, face_indices)

        assert quality.max_deviation < 0.1  # mm
        assert quality.mean_deviation < 0.05

    def test_draft_angle_application(self):
        """Test draft angle transformation."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        nurbs = generator.fit_nurbs_surface([0], 20)

        # Apply 2° draft
        demolding_dir = cpp_core.Vector3(0, 0, 1)
        drafted = generator.apply_draft_angle(nurbs, demolding_dir, 2.0, [])

        # Verify draft applied (check surface normals)
        assert drafted is not None

    def test_solid_creation(self):
        """Test mold solid creation."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        nurbs = generator.fit_nurbs_surface([0], 20)
        solid = generator.create_mold_solid(nurbs, wall_thickness=40.0)

        # Check solid is valid
        # assert solid.IsValid()

    def _create_sphere(self):
        # [Icosahedron code]
        pass

    def _create_simple_cage(self):
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage
```

---

## Success Criteria

- [ ] Fitting accuracy test passes (<0.1mm)
- [ ] Draft transformation test passes
- [ ] Solid creation test passes
- [ ] All NURBS operations validated

---

**Ready to begin!**
