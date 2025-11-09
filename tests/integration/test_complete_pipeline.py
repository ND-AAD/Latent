"""
Complete Pipeline Integration Tests

End-to-end integration tests validating the complete workflow:
- Simple geometry (cube) → Analysis → Constraints → NURBS → Export
- Complex geometry (torus) → Full pipeline
- Multiple lenses comparison
- Constraint validation
- NURBS export and serialization

All tests must complete in <2 seconds each.

Author: Agent 60, Ceramic Mold Analyzer
Date: November 2025
"""

import pytest
import numpy as np
import time
from typing import List, Dict
from dataclasses import dataclass

# Import core components
from app.analysis.lens_manager import LensManager, LensType, LensResult
from app.analysis.differential_lens import DifferentialLens
from app.state.parametric_region import ParametricRegion
from app.workflow.mold_generator import MoldWorkflow, MoldGenerationResult
from app.export.nurbs_serializer import NURBSSerializer, RhinoNURBSSurface
from app.ui.mold_params_dialog import MoldParameters

# Try to import cpp_core and check if fully functional
try:
    import cpp_core
    # Check if required classes are available (bindings must be built)
    CPP_CORE_AVAILABLE = (
        hasattr(cpp_core, 'SubDControlCage') and
        hasattr(cpp_core, 'SubDEvaluator') and
        hasattr(cpp_core, 'Point3D') and
        hasattr(cpp_core, 'Vector3') and
        hasattr(cpp_core, 'NURBSMoldGenerator') and
        hasattr(cpp_core, 'ConstraintValidator')
    )
    if not CPP_CORE_AVAILABLE:
        pytestmark = pytest.mark.skip("cpp_core bindings incomplete - skipping pipeline tests")
except ImportError:
    CPP_CORE_AVAILABLE = False
    pytestmark = pytest.mark.skip("cpp_core not available - skipping pipeline tests")


class TestCompletePipeline:
    """End-to-end integration tests for complete analysis and mold generation pipeline."""

    # ====================================================================
    # TEST 1: Simple Geometry (Cube) - Complete Pipeline
    # ====================================================================

    def test_cube_complete_pipeline(self):
        """
        Test complete pipeline with simple cube geometry.

        Pipeline: Control Cage → SubD Evaluation → Analysis → Regions →
                 Constraints → NURBS → Export

        Performance target: <2 seconds
        """
        start_time = time.time()

        # Step 1: Create simple cube control cage
        cage = self._create_cube_cage()

        # Step 2: Initialize SubD evaluator
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Verify initialization
        assert evaluator.is_initialized()
        num_faces = evaluator.get_num_faces()
        assert num_faces == 6, "Cube should have 6 faces"

        # Step 3: Run differential analysis
        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Verify regions discovered
        assert len(regions) > 0, "Should discover at least one region"
        assert len(regions) <= 6, "Cube shouldn't have more regions than faces"

        # Step 4: Validate constraints
        validator = cpp_core.ConstraintValidator(evaluator)
        demolding_dir = (0.0, 0.0, 1.0)  # Z-up
        wall_thickness = 5.0  # mm

        all_valid = True
        for region in regions:
            report = validator.validate_region(
                region.faces,
                cpp_core.Vector3(*demolding_dir),
                wall_thickness
            )
            if report.has_errors():
                all_valid = False
                print(f"Region {region.id} has constraint violations")

        # For a cube with Z-up demolding, should be valid
        assert all_valid, "Cube decomposition should pass constraints"

        # Step 5: Generate NURBS molds
        params = MoldParameters(
            draft_angle=2.0,
            wall_thickness=5.0,
            demolding_direction=demolding_dir
        )

        workflow = MoldWorkflow(evaluator)
        result = workflow.generate_molds(regions, params)

        # Verify mold generation success
        assert result.success, f"Mold generation failed: {result.error_message}"
        assert len(result.nurbs_surfaces) == len(regions)

        # Step 6: Verify export data
        assert 'molds' in result.export_data
        assert len(result.export_data['molds']) == len(regions)

        # Check performance
        elapsed = time.time() - start_time
        print(f"\nCube pipeline completed in {elapsed:.3f}s")
        assert elapsed < 2.0, f"Pipeline took {elapsed:.3f}s, should be <2s"

        # Verify data structure
        for mold_data in result.export_data['molds']:
            assert 'degree_u' in mold_data
            assert 'degree_v' in mold_data
            assert 'control_points' in mold_data
            assert 'knots_u' in mold_data
            assert 'knots_v' in mold_data
            assert len(mold_data['control_points']) > 0

    # ====================================================================
    # TEST 2: Complex Geometry (Torus) - Complete Pipeline
    # ====================================================================

    def test_torus_complete_pipeline(self):
        """
        Test complete pipeline with complex torus geometry.

        Torus has varying curvature → should produce interesting decomposition.

        Performance target: <2 seconds
        """
        start_time = time.time()

        # Step 1: Create torus control cage
        cage = self._create_torus_cage()

        # Step 2: Initialize evaluator
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)
        assert evaluator.is_initialized()

        # Step 3: Analyze with differential lens
        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Torus should produce multiple regions due to curvature variation
        assert len(regions) >= 2, "Torus should have multiple curvature regions"
        print(f"\nTorus decomposition: {len(regions)} regions")

        # Check region properties
        for region in regions:
            assert len(region.faces) > 0
            assert region.unity_strength >= 0.0
            assert region.unity_principle != ""
            assert 'lens' in region.metadata

        # Step 4: Test constraint validation on complex geometry
        validator = cpp_core.ConstraintValidator(evaluator)
        demolding_dir = (0.0, 0.0, 1.0)

        validation_results = []
        for region in regions:
            report = validator.validate_region(
                region.faces,
                cpp_core.Vector3(*demolding_dir),
                5.0  # wall_thickness
            )
            validation_results.append({
                'region_id': region.id,
                'has_errors': report.has_errors(),
                'has_warnings': report.has_warnings()
            })

        # Some regions may have issues due to torus geometry
        print(f"Validation results: {validation_results}")

        # Step 5: Generate molds for valid regions only
        valid_regions = [
            r for i, r in enumerate(regions)
            if not validation_results[i]['has_errors']
        ]

        if len(valid_regions) > 0:
            params = MoldParameters(
                draft_angle=2.0,
                wall_thickness=5.0,
                demolding_direction=demolding_dir
            )

            workflow = MoldWorkflow(evaluator)
            result = workflow.generate_molds(valid_regions, params)

            # Should succeed for valid regions
            assert result.success or len(valid_regions) == 0

        # Check performance
        elapsed = time.time() - start_time
        print(f"Torus pipeline completed in {elapsed:.3f}s")
        assert elapsed < 2.0, f"Pipeline took {elapsed:.3f}s, should be <2s"

    # ====================================================================
    # TEST 3: Multiple Lenses Comparison
    # ====================================================================

    def test_multiple_lenses_comparison(self):
        """
        Test comparing multiple analysis lenses on same geometry.

        Compare differential vs spectral (when available).
        Performance target: <2 seconds
        """
        start_time = time.time()

        # Create test geometry (sphere - good for both lenses)
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze with differential lens
        diff_regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)
        diff_result = manager.get_result(LensType.DIFFERENTIAL)

        assert len(diff_regions) > 0
        assert diff_result.resonance_score >= 0.0

        # Try spectral lens (may not be implemented yet)
        spectral_available = False
        try:
            spectral_regions = manager.analyze_with_lens(LensType.SPECTRAL)
            spectral_result = manager.get_result(LensType.SPECTRAL)
            spectral_available = True

            assert len(spectral_regions) > 0
            assert spectral_result.resonance_score >= 0.0

            # Compare scores
            print(f"\nDifferential resonance: {diff_result.resonance_score:.3f}")
            print(f"Spectral resonance: {spectral_result.resonance_score:.3f}")

        except NotImplementedError:
            print("\nSpectral lens not yet implemented - testing differential only")

        # Test comparison functionality
        scores = manager.compare_lenses([LensType.DIFFERENTIAL])
        assert LensType.DIFFERENTIAL in scores

        # Get best lens
        best = manager.get_best_lens()
        assert best == LensType.DIFFERENTIAL or (spectral_available and best == LensType.SPECTRAL)

        # Check analysis summary
        summary = manager.get_analysis_summary()
        assert 'num_lenses_analyzed' in summary
        assert summary['num_lenses_analyzed'] >= 1
        assert 'best_lens' in summary

        elapsed = time.time() - start_time
        print(f"Lens comparison completed in {elapsed:.3f}s")
        assert elapsed < 2.0

    # ====================================================================
    # TEST 4: Constraint Validation Comprehensive
    # ====================================================================

    def test_constraint_validation_comprehensive(self):
        """
        Test comprehensive constraint validation.

        Test:
        - Draft angle checking
        - Undercut detection
        - Wall thickness validation
        - Multiple demolding directions

        Performance target: <2 seconds
        """
        start_time = time.time()

        # Create geometry
        cage = self._create_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Get a region
        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)
        assert len(regions) > 0

        test_region = regions[0]
        validator = cpp_core.ConstraintValidator(evaluator)

        # Test 1: Valid demolding direction (Z-up)
        report_z = validator.validate_region(
            test_region.faces,
            cpp_core.Vector3(0.0, 0.0, 1.0),
            5.0
        )

        # Test 2: Different demolding direction (Y-up)
        report_y = validator.validate_region(
            test_region.faces,
            cpp_core.Vector3(0.0, 1.0, 0.0),
            5.0
        )

        # Test 3: Very thin wall (should warn)
        report_thin = validator.validate_region(
            test_region.faces,
            cpp_core.Vector3(0.0, 0.0, 1.0),
            1.0  # Very thin
        )

        # Test 4: Very thick wall
        report_thick = validator.validate_region(
            test_region.faces,
            cpp_core.Vector3(0.0, 0.0, 1.0),
            20.0  # Very thick
        )

        # Verify reports have expected structure
        for report in [report_z, report_y, report_thin, report_thick]:
            assert hasattr(report, 'has_errors')
            assert hasattr(report, 'has_warnings')

        # At least one should be valid for a simple cube
        valid_count = sum(1 for r in [report_z, report_y] if not r.has_errors())
        assert valid_count > 0, "At least one demolding direction should be valid"

        elapsed = time.time() - start_time
        print(f"Constraint validation completed in {elapsed:.3f}s")
        assert elapsed < 2.0

    # ====================================================================
    # TEST 5: NURBS Export and Serialization
    # ====================================================================

    def test_nurbs_export_serialization(self):
        """
        Test NURBS surface export and serialization.

        Verify:
        - NURBS fitting quality
        - Serialization format
        - Rhino compatibility
        - Data integrity

        Performance target: <2 seconds
        """
        start_time = time.time()

        # Create geometry and analyze
        cage = self._create_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Generate NURBS
        nurbs_gen = cpp_core.NURBSMoldGenerator(evaluator)

        nurbs_surfaces = []
        for region in regions:
            surface = nurbs_gen.fit_nurbs_surface(
                region.faces,
                sample_density=50
            )

            # Check fitting quality
            quality = nurbs_gen.check_fitting_quality(surface, region.faces)
            assert quality.max_deviation < 1.0, "Fitting should be accurate (<1mm)"

            nurbs_surfaces.append((surface, region.id))

        # Test serialization
        serializer = NURBSSerializer()

        # Serialize individual surface
        test_surface, test_id = nurbs_surfaces[0]
        rhino_surf = serializer.serialize_surface(
            test_surface,
            name=f"test_mold_{test_id}",
            region_id=test_id
        )

        # Verify structure
        assert isinstance(rhino_surf, RhinoNURBSSurface)
        assert rhino_surf.degree_u > 0
        assert rhino_surf.degree_v > 0
        assert len(rhino_surf.control_points) > 0
        assert len(rhino_surf.weights) == len(rhino_surf.control_points)
        assert len(rhino_surf.knots_u) > 0
        assert len(rhino_surf.knots_v) > 0
        assert rhino_surf.count_u * rhino_surf.count_v == len(rhino_surf.control_points)

        # Serialize complete mold set
        export_data = serializer.serialize_mold_set(
            nurbs_surfaces,
            metadata={
                'draft_angle': 2.0,
                'wall_thickness': 5.0,
                'demolding_direction': (0.0, 0.0, 1.0)
            }
        )

        # Verify export data structure
        assert export_data['type'] == 'ceramic_mold_set'
        assert 'version' in export_data
        assert 'molds' in export_data
        assert len(export_data['molds']) == len(nurbs_surfaces)
        assert 'metadata' in export_data
        assert export_data['metadata']['draft_angle'] == 2.0

        # Verify each mold is JSON-serializable
        import json
        json_str = json.dumps(export_data)
        assert len(json_str) > 0

        # Verify round-trip
        recovered = json.loads(json_str)
        assert recovered['type'] == 'ceramic_mold_set'
        assert len(recovered['molds']) == len(nurbs_surfaces)

        elapsed = time.time() - start_time
        print(f"NURBS export completed in {elapsed:.3f}s")
        assert elapsed < 2.0

    # ====================================================================
    # TEST 6: Performance Under Load
    # ====================================================================

    def test_pipeline_performance_multiple_geometries(self):
        """
        Test pipeline performance with multiple geometries.

        Run analysis on 3 different geometries sequentially.
        Total time should still be reasonable (<6 seconds = 3x2s).
        """
        start_time = time.time()

        geometries = [
            ('cube', self._create_cube_cage()),
            ('sphere', self._create_sphere_cage()),
            ('cylinder', self._create_cylinder_cage())
        ]

        results = {}

        for name, cage in geometries:
            geo_start = time.time()

            # Initialize
            evaluator = cpp_core.SubDEvaluator()
            evaluator.initialize(cage)

            # Analyze
            manager = LensManager(evaluator)
            regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

            # Validate
            validator = cpp_core.ConstraintValidator(evaluator)
            valid_count = 0
            for region in regions:
                report = validator.validate_region(
                    region.faces,
                    cpp_core.Vector3(0.0, 0.0, 1.0),
                    5.0
                )
                if not report.has_errors():
                    valid_count += 1

            geo_elapsed = time.time() - geo_start

            results[name] = {
                'num_regions': len(regions),
                'valid_regions': valid_count,
                'time': geo_elapsed
            }

            print(f"\n{name}: {len(regions)} regions, {geo_elapsed:.3f}s")

        # All geometries should produce results
        for name, result in results.items():
            assert result['num_regions'] > 0, f"{name} should produce regions"
            assert result['time'] < 2.0, f"{name} took too long"

        total_elapsed = time.time() - start_time
        print(f"\nTotal time for 3 geometries: {total_elapsed:.3f}s")
        assert total_elapsed < 6.0, "Should handle 3 geometries in <6s"

    # ====================================================================
    # TEST 7: Error Handling and Edge Cases
    # ====================================================================

    def test_error_handling(self):
        """
        Test error handling in pipeline.

        Test:
        - Invalid region data
        - Failed constraint validation
        - Empty region lists
        - Invalid parameters
        """
        # Create valid geometry
        cage = self._create_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Test 1: Empty region list
        workflow = MoldWorkflow(evaluator)
        params = MoldParameters(
            draft_angle=2.0,
            wall_thickness=5.0,
            demolding_direction=(0.0, 0.0, 1.0)
        )

        result = workflow.generate_molds([], params)
        # Should handle gracefully (may succeed with empty output or fail gracefully)
        assert isinstance(result, MoldGenerationResult)

        # Test 2: Invalid demolding direction (zero vector)
        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        if len(regions) > 0:
            validator = cpp_core.ConstraintValidator(evaluator)

            # This should either handle gracefully or raise appropriate error
            try:
                report = validator.validate_region(
                    regions[0].faces,
                    cpp_core.Vector3(0.0, 0.0, 0.0),  # Invalid!
                    5.0
                )
                # If it doesn't raise, it should mark as error
                assert report.has_errors() or report.has_warnings()
            except (ValueError, RuntimeError):
                # Expected behavior - invalid direction rejected
                pass

        # Test 3: Negative wall thickness
        invalid_params = MoldParameters(
            draft_angle=2.0,
            wall_thickness=-1.0,  # Invalid!
            demolding_direction=(0.0, 0.0, 1.0)
        )

        # Should handle gracefully
        result = workflow.generate_molds(regions, invalid_params)
        assert isinstance(result, MoldGenerationResult)

    # ====================================================================
    # Helper Methods - Geometry Creation
    # ====================================================================

    def _create_cube_cage(self):
        """Create cube SubD control cage (8 vertices, 6 quad faces)."""
        cage = cpp_core.SubDControlCage()

        # 8 vertices of unit cube
        vertices = [
            (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),  # Bottom
            (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)   # Top
        ]

        for x, y, z in vertices:
            cage.vertices.append(cpp_core.Point3D(x, y, z))

        # 6 quad faces
        cage.faces = [
            [0, 1, 2, 3],  # Bottom
            [4, 5, 6, 7],  # Top
            [0, 1, 5, 4],  # Front
            [2, 3, 7, 6],  # Back
            [0, 3, 7, 4],  # Left
            [1, 2, 6, 5]   # Right
        ]

        return cage

    def _create_sphere_cage(self):
        """Create sphere-like SubD control cage (octahedron base)."""
        cage = cpp_core.SubDControlCage()

        # 6 vertices (octahedron)
        r = 1.0
        vertices = [
            (r, 0, 0), (-r, 0, 0),    # X axis
            (0, r, 0), (0, -r, 0),    # Y axis
            (0, 0, r), (0, 0, -r)     # Z axis
        ]

        for x, y, z in vertices:
            cage.vertices.append(cpp_core.Point3D(x, y, z))

        # 8 triangular faces (octahedron)
        cage.faces = [
            [0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2],  # Right hemisphere
            [1, 4, 2], [1, 3, 4], [1, 5, 3], [1, 2, 5]   # Left hemisphere
        ]

        return cage

    def _create_cylinder_cage(self):
        """Create cylinder-like SubD control cage."""
        cage = cpp_core.SubDControlCage()

        # 8 vertices (4 bottom, 4 top)
        r = 1.0
        h = 2.0
        angles = [0, np.pi/2, np.pi, 3*np.pi/2]

        for z in [-h/2, h/2]:
            for angle in angles:
                x = r * np.cos(angle)
                y = r * np.sin(angle)
                cage.vertices.append(cpp_core.Point3D(x, y, z))

        # 4 side faces + 2 caps
        cage.faces = [
            [0, 1, 5, 4],  # Side 1
            [1, 2, 6, 5],  # Side 2
            [2, 3, 7, 6],  # Side 3
            [3, 0, 4, 7],  # Side 4
            [0, 1, 2, 3],  # Bottom cap
            [4, 5, 6, 7]   # Top cap
        ]

        return cage

    def _create_torus_cage(self):
        """Create torus-like SubD control cage."""
        cage = cpp_core.SubDControlCage()

        # Simplified torus: 16 vertices (4x4 grid wrapped)
        R = 2.0  # Major radius
        r = 0.5  # Minor radius

        # Create vertices
        for i in range(4):
            angle_major = i * np.pi / 2
            cx = R * np.cos(angle_major)
            cy = R * np.sin(angle_major)

            for j in range(4):
                angle_minor = j * np.pi / 2
                dx = r * np.cos(angle_minor) * np.cos(angle_major)
                dy = r * np.cos(angle_minor) * np.sin(angle_major)
                dz = r * np.sin(angle_minor)

                cage.vertices.append(cpp_core.Point3D(cx + dx, cy + dy, dz))

        # Create faces (4x4 quad grid, wrapped)
        faces = []
        for i in range(4):
            for j in range(4):
                v0 = i * 4 + j
                v1 = i * 4 + ((j + 1) % 4)
                v2 = ((i + 1) % 4) * 4 + ((j + 1) % 4)
                v3 = ((i + 1) % 4) * 4 + j
                faces.append([v0, v1, v2, v3])

        cage.faces = faces

        return cage


# ====================================================================
# Additional Integration Test Suite
# ====================================================================

class TestWorkflowIntegration:
    """Test workflow-level integration and orchestration."""

    def test_workflow_state_management(self):
        """Test that workflow properly manages state through pipeline."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Create workflow
        workflow = MoldWorkflow(evaluator)

        # Verify components initialized
        assert workflow.evaluator is evaluator
        assert workflow.nurbs_gen is not None
        assert workflow.constraint_val is not None
        assert workflow.serializer is not None

    def test_lens_result_caching(self):
        """Test that lens results are properly cached across workflow."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # First analysis
        start1 = time.time()
        regions1 = manager.analyze_with_lens(LensType.DIFFERENTIAL)
        time1 = time.time() - start1

        # Second analysis (cached)
        start2 = time.time()
        regions2 = manager.analyze_with_lens(LensType.DIFFERENTIAL)
        time2 = time.time() - start2

        # Should be same regions
        assert len(regions1) == len(regions2)

        # Cached should be much faster
        assert time2 < time1 * 0.5, "Cached access should be faster"

    def test_parametric_region_consistency(self):
        """Test that ParametricRegion data remains consistent through pipeline."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Store original data
        original_data = [
            {
                'id': r.id,
                'faces': r.faces.copy(),
                'unity_strength': r.unity_strength,
                'metadata': r.metadata.copy()
            }
            for r in regions
        ]

        # Pass through validation
        validator = cpp_core.ConstraintValidator(evaluator)
        for region in regions:
            validator.validate_region(
                region.faces,
                cpp_core.Vector3(0.0, 0.0, 1.0),
                5.0
            )

        # Verify data unchanged
        for i, region in enumerate(regions):
            orig = original_data[i]
            assert region.id == orig['id']
            assert region.faces == orig['faces']
            assert region.unity_strength == orig['unity_strength']
            # Metadata may have additions but original keys should remain
            for key in orig['metadata']:
                assert key in region.metadata

    def _create_simple_cage(self):
        """Create simple test cage."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-s'])
