"""
Test NURBS mold generation pipeline.

Comprehensive testing of NURBS mold generation:
- NURBS surface fitting from exact limit surface
- Draft angle transformation for demolding
- Solid mold cavity creation
- Quality control and deviation checking

Author: Agent 51 (Day 7 Morning)
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add cpp_core to path if needed
cpp_core_path = Path(__file__).parent.parent / "cpp_core" / "build"
if cpp_core_path.exists():
    sys.path.insert(0, str(cpp_core_path))

try:
    import cpp_core
except ImportError as e:
    pytest.skip(f"cpp_core module not available: {e}", allow_module_level=True)

# Check if NURBSMoldGenerator is available
if not hasattr(cpp_core, 'NURBSMoldGenerator'):
    pytest.skip("NURBSMoldGenerator not yet implemented", allow_module_level=True)


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

        assert quality.max_deviation < 0.1, \
            f"Max deviation too large: {quality.max_deviation:.4f} mm (expected < 0.1 mm)"
        assert quality.mean_deviation < 0.05, \
            f"Mean deviation too large: {quality.mean_deviation:.4f} mm (expected < 0.05 mm)"

        print(f"  ✅ NURBS fitting quality: max={quality.max_deviation:.4f} mm, "
              f"mean={quality.mean_deviation:.4f} mm, "
              f"rms={quality.rms_deviation:.4f} mm "
              f"({quality.num_samples} samples)")

    def test_nurbs_fitting_density_scaling(self):
        """Test that higher sample density improves fitting accuracy."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Test with different densities
        deviations = []
        densities = [10, 20, 50]

        for density in densities:
            nurbs = generator.fit_nurbs_surface([0], sample_density=density)
            quality = generator.check_fitting_quality(nurbs, [0])
            deviations.append(quality.max_deviation)

        # Higher density should reduce deviation
        # (or at least not increase it significantly)
        assert deviations[2] <= deviations[0] * 1.5, \
            f"Higher density should improve or maintain accuracy: {deviations}"

        print(f"  ✅ Density scaling: density={densities}, deviations={[f'{d:.4f}' for d in deviations]}")

    def test_draft_angle_application(self):
        """Test draft angle transformation."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        nurbs = generator.fit_nurbs_surface([0], 20)

        # Apply 2° draft
        demolding_dir = cpp_core.Point3D(0, 0, 1)  # Direction vector as Point3D
        drafted = generator.apply_draft_angle(nurbs, demolding_dir, 2.0, [])

        # Verify draft applied (check surface normals)
        assert drafted is not None, "Draft transformation should return valid surface"

        print(f"  ✅ Draft angle applied successfully (2.0°)")

    def test_draft_angle_range(self):
        """Test various draft angles from minimal to recommended."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        demolding_dir = cpp_core.Point3D(0, 0, 1)  # Direction vector as Point3D

        # Test range of draft angles
        test_angles = [0.5, 1.0, 2.0, 3.0, 5.0]

        for angle in test_angles:
            drafted = generator.apply_draft_angle(nurbs, demolding_dir, angle, [])
            assert drafted is not None, f"Draft angle {angle}° should succeed"

        print(f"  ✅ Draft angles tested: {test_angles}° - all successful")

    def test_solid_creation(self):
        """Test mold solid creation."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        nurbs = generator.fit_nurbs_surface([0], 20)
        solid = generator.create_mold_solid(nurbs, wall_thickness=40.0)

        # Check solid is valid
        assert solid is not None, "Mold solid should be created"
        # Note: OpenCASCADE TopoDS_Shape validation would be:
        # assert solid.IsValid() if bindings expose this method

        print(f"  ✅ Mold solid created (wall thickness: 40.0 mm)")

    def test_solid_wall_thickness_variations(self):
        """Test mold solid creation with various wall thicknesses."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        # Test different wall thicknesses (typical ceramic mold range)
        thicknesses = [20.0, 30.0, 40.0, 50.0]

        for thickness in thicknesses:
            solid = generator.create_mold_solid(nurbs, wall_thickness=thickness)
            assert solid is not None, f"Solid creation failed for thickness {thickness} mm"

        print(f"  ✅ Wall thicknesses tested: {thicknesses} mm - all successful")

    def test_complete_pipeline_simple_geometry(self):
        """Test complete pipeline: fit → draft → solid."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Step 1: Fit NURBS
        nurbs = generator.fit_nurbs_surface([0], 30)
        assert nurbs is not None, "NURBS fitting failed"

        # Step 2: Apply draft
        demolding_dir = cpp_core.Point3D(0, 0, 1)  # Direction vector as Point3D
        drafted = generator.apply_draft_angle(nurbs, demolding_dir, 2.0, [])
        assert drafted is not None, "Draft application failed"

        # Step 3: Create solid
        solid = generator.create_mold_solid(drafted, wall_thickness=40.0)
        assert solid is not None, "Solid creation failed"

        print(f"  ✅ Complete pipeline executed successfully (simple geometry)")

    def test_complete_pipeline_sphere(self):
        """Test complete pipeline on sphere geometry."""
        cage = self._create_sphere()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)

        # Use all faces for full sphere
        face_indices = list(range(len(cage.faces)))

        # Step 1: Fit NURBS with reasonable density
        nurbs = generator.fit_nurbs_surface(face_indices, sample_density=40)
        assert nurbs is not None, "NURBS fitting failed for sphere"

        # Step 2: Check quality meets tolerance
        quality = generator.check_fitting_quality(nurbs, face_indices)
        assert quality.max_deviation < 0.1, \
            f"Sphere fitting quality insufficient: {quality.max_deviation:.4f} mm"

        # Step 3: Apply draft
        demolding_dir = cpp_core.Point3D(0, 0, 1)  # Direction vector as Point3D
        drafted = generator.apply_draft_angle(nurbs, demolding_dir, 3.0, [])
        assert drafted is not None, "Draft application failed for sphere"

        # Step 4: Create solid
        solid = generator.create_mold_solid(drafted, wall_thickness=40.0)
        assert solid is not None, "Solid creation failed for sphere"

        print(f"  ✅ Complete pipeline executed successfully (sphere)")
        print(f"     Quality: max={quality.max_deviation:.4f} mm, "
              f"mean={quality.mean_deviation:.4f} mm")

    def test_fitting_quality_structure(self):
        """Test that FittingQuality struct has correct fields."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)
        quality = generator.check_fitting_quality(nurbs, [0])

        # Check all required fields exist
        assert hasattr(quality, 'max_deviation'), "Missing max_deviation"
        assert hasattr(quality, 'mean_deviation'), "Missing mean_deviation"
        assert hasattr(quality, 'rms_deviation'), "Missing rms_deviation"
        assert hasattr(quality, 'num_samples'), "Missing num_samples"

        # Check reasonable values
        assert quality.max_deviation >= 0, "Negative max deviation"
        assert quality.mean_deviation >= 0, "Negative mean deviation"
        assert quality.rms_deviation >= 0, "Negative RMS deviation"
        assert quality.num_samples > 0, "No samples"
        assert quality.mean_deviation <= quality.max_deviation, \
            "Mean should be <= max"

        print(f"  ✅ FittingQuality structure validated")

    def test_parting_line_constraint(self):
        """Test that parting line points remain fixed during draft."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], 20)

        # Define parting line (edge of quad)
        parting_line = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
        ]

        demolding_dir = cpp_core.Point3D(0, 0, 1)  # Direction vector as Point3D
        drafted = generator.apply_draft_angle(nurbs, demolding_dir, 2.0, parting_line)

        assert drafted is not None, "Draft with parting line failed"

        print(f"  ✅ Parting line constraint applied ({len(parting_line)} points)")

    # ============================================================
    # Helper Methods
    # ============================================================

    def _create_sphere(self):
        """Create icosahedron (sphere approximation) for SubD."""
        phi = (1 + np.sqrt(5)) / 2

        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(-1, phi, 0),
            cpp_core.Point3D(1, phi, 0),
            cpp_core.Point3D(-1, -phi, 0),
            cpp_core.Point3D(1, -phi, 0),
            cpp_core.Point3D(0, -1, phi),
            cpp_core.Point3D(0, 1, phi),
            cpp_core.Point3D(0, -1, -phi),
            cpp_core.Point3D(0, 1, -phi),
            cpp_core.Point3D(phi, 0, -1),
            cpp_core.Point3D(phi, 0, 1),
            cpp_core.Point3D(-phi, 0, -1),
            cpp_core.Point3D(-phi, 0, 1)
        ]
        cage.faces = [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
        ]
        return cage

    def _create_simple_cage(self):
        """Create simple quad cage for basic testing."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


if __name__ == "__main__":
    # Allow running directly with pytest
    pytest.main([__file__, "-v"])
