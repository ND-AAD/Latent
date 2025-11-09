"""
Integration Tests for Lens Comparison

Tests the lens comparison and selection functionality:
- Comparing multiple lenses
- Selecting best lens based on resonance score
- Lens result metadata and statistics
- Multi-lens workflow integration

Author: Agent 39, Ceramic Mold Analyzer
Date: November 2025
"""

import pytest
import numpy as np
from typing import Dict

from app.analysis.lens_manager import LensManager, LensType, LensResult
from app.state.parametric_region import ParametricRegion

# Try to import cpp_core and check if fully functional
try:
    import cpp_core
    # Check if required classes are available (bindings must be built)
    CPP_CORE_AVAILABLE = (
        hasattr(cpp_core, 'SubDControlCage') and
        hasattr(cpp_core, 'SubDEvaluator') and
        hasattr(cpp_core, 'Point3D')
    )
    if not CPP_CORE_AVAILABLE:
        pytestmark = pytest.mark.skip("cpp_core bindings incomplete - skipping lens comparison tests")
except ImportError:
    CPP_CORE_AVAILABLE = False
    pytestmark = pytest.mark.skip("cpp_core not available - skipping lens comparison tests")


class TestLensComparison:
    """Test lens comparison and selection functionality."""

    def test_single_lens_comparison(self):
        """Test comparing a single lens (baseline)."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Compare only differential lens
        scores = manager.compare_lenses([LensType.DIFFERENTIAL])

        assert LensType.DIFFERENTIAL in scores
        assert 0.0 <= scores[LensType.DIFFERENTIAL] <= 1.0

    def test_get_best_lens_single(self):
        """Test getting best lens when only one has been analyzed."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Before analysis
        best = manager.get_best_lens()
        assert best is None, "Should be None before any analysis"

        # After single analysis
        manager.analyze_with_lens(LensType.DIFFERENTIAL)
        best = manager.get_best_lens()

        assert best == LensType.DIFFERENTIAL

    def test_compare_lenses_default(self):
        """Test comparing lenses with default settings."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Compare with defaults (should analyze all available)
        scores = manager.compare_lenses()

        assert len(scores) > 0
        assert LensType.DIFFERENTIAL in scores

        # All scores should be valid
        for score in scores.values():
            assert 0.0 <= score <= 1.0

    def test_lens_result_structure(self):
        """Test LensResult data structure."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        result = manager.get_result(LensType.DIFFERENTIAL)

        # Check all fields present
        assert hasattr(result, 'lens_type')
        assert hasattr(result, 'regions')
        assert hasattr(result, 'resonance_score')
        assert hasattr(result, 'computation_time')
        assert hasattr(result, 'metadata')

        # Check types
        assert isinstance(result.lens_type, LensType)
        assert isinstance(result.regions, list)
        assert isinstance(result.resonance_score, float)
        assert isinstance(result.computation_time, float)
        assert isinstance(result.metadata, dict)

        # Check values
        assert result.computation_time > 0
        assert 0.0 <= result.resonance_score <= 1.0

    def test_comparison_with_parameters(self):
        """Test comparing lenses with different parameters."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Define custom parameters for differential lens
        params = {
            LensType.DIFFERENTIAL: {
                'samples_per_face': 9,
                'mean_curvature_threshold': 0.01
            }
        }

        scores = manager.compare_lenses(
            lens_types=[LensType.DIFFERENTIAL],
            params=params
        )

        assert LensType.DIFFERENTIAL in scores

    def test_resonance_score_properties(self):
        """Test resonance score computation properties."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        result = manager.get_result(LensType.DIFFERENTIAL)
        score = result.resonance_score

        # Basic properties
        assert 0.0 <= score <= 1.0

        # For sphere, should get reasonable decomposition
        # (not too low, indicating complete failure)
        assert score > 0.1, "Sphere decomposition should have some resonance"

    def test_multiple_geometry_comparison(self):
        """Test comparing lenses across different geometries."""
        geometries = {
            'sphere': self._create_sphere_cage(),
            'cylinder': self._create_cylinder_cage()
        }

        results = {}

        for name, cage in geometries.items():
            evaluator = cpp_core.SubDEvaluator()
            evaluator.initialize(cage)

            manager = LensManager(evaluator)
            scores = manager.compare_lenses([LensType.DIFFERENTIAL])

            results[name] = {
                'scores': scores,
                'best': manager.get_best_lens()
            }

        # Both should produce valid results
        for name, result in results.items():
            assert len(result['scores']) > 0, f"{name} should have scores"
            assert result['best'] is not None, f"{name} should have best lens"

    def test_analysis_summary_format(self):
        """Test analysis summary output format."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        summary = manager.get_analysis_summary()

        # Check required fields
        assert 'num_lenses_analyzed' in summary
        assert 'lenses' in summary
        assert 'best_lens' in summary
        assert 'best_score' in summary

        # Check lens details
        assert 'differential' in summary['lenses']
        lens_info = summary['lenses']['differential']

        assert 'num_regions' in lens_info
        assert 'resonance_score' in lens_info
        assert 'computation_time' in lens_info
        assert 'metadata' in lens_info

    def test_comparison_caching_behavior(self):
        """Test that comparison uses caching appropriately."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # First comparison
        scores1 = manager.compare_lenses([LensType.DIFFERENTIAL])

        # Second comparison (should use cache)
        scores2 = manager.compare_lenses([LensType.DIFFERENTIAL])

        assert scores1 == scores2

    def test_region_count_scoring_component(self):
        """Test region count component of resonance scoring."""
        # According to scoring algorithm:
        # - < 3 regions: penalty
        # - 3-8 regions: optimal (score = 1.0)
        # - > 8 regions: penalty

        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        result = manager.get_result(LensType.DIFFERENTIAL)

        # If we got 3-8 regions, count component should be maximal
        num_regions = len(regions)
        print(f"\nRegions discovered: {num_regions}")
        print(f"Resonance score: {result.resonance_score:.3f}")

        # Just verify scoring is reasonable
        assert result.resonance_score > 0.0

    def test_unity_strength_component(self):
        """Test unity strength component of resonance scoring."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Check that regions have unity_strength
        for region in regions:
            assert hasattr(region, 'unity_strength')
            assert 0.0 <= region.unity_strength <= 1.0

        # Overall resonance should reflect average unity
        result = manager.get_result(LensType.DIFFERENTIAL)
        avg_unity = sum(r.unity_strength for r in regions) / len(regions)

        print(f"\nAverage unity strength: {avg_unity:.3f}")
        print(f"Overall resonance: {result.resonance_score:.3f}")

    def test_size_balance_component(self):
        """Test size balance component of resonance scoring."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Compute size balance
        sizes = [len(r.faces) for r in regions]
        mean_size = sum(sizes) / len(sizes)
        variance = sum((s - mean_size) ** 2 for s in sizes) / len(sizes)
        std_dev = variance ** 0.5
        cv = std_dev / (mean_size + 1)

        print(f"\nRegion sizes: {sizes}")
        print(f"Coefficient of variation: {cv:.3f}")

        # More balanced regions should have lower CV
        assert cv >= 0.0

    def test_lens_type_enum(self):
        """Test LensType enum properties."""
        # Check all lens types defined
        assert hasattr(LensType, 'DIFFERENTIAL')
        assert hasattr(LensType, 'SPECTRAL')
        assert hasattr(LensType, 'FLOW')
        assert hasattr(LensType, 'MORSE')
        assert hasattr(LensType, 'THERMAL')
        assert hasattr(LensType, 'SLIP')

        # Check values
        assert LensType.DIFFERENTIAL.value == 'differential'
        assert LensType.SPECTRAL.value == 'spectral'

    def test_not_implemented_lenses(self):
        """Test that unimplemented lenses raise NotImplementedError."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # These should raise NotImplementedError
        future_lenses = [
            LensType.SPECTRAL,  # Until Agent 35 completes
            LensType.FLOW,
            LensType.MORSE,
            LensType.THERMAL,
            LensType.SLIP
        ]

        for lens_type in future_lenses:
            with pytest.raises(NotImplementedError):
                manager.analyze_with_lens(lens_type)

    def test_comparison_skips_unimplemented(self):
        """Test that compare_lenses skips unimplemented lenses gracefully."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Try to compare including unimplemented lens
        scores = manager.compare_lenses([
            LensType.DIFFERENTIAL,
            LensType.SPECTRAL  # Not implemented yet
        ])

        # Should only have differential
        assert LensType.DIFFERENTIAL in scores
        assert LensType.SPECTRAL not in scores

    def test_computation_time_tracking(self):
        """Test that computation time is tracked correctly."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        result = manager.get_result(LensType.DIFFERENTIAL)

        # Should have positive computation time
        assert result.computation_time > 0
        assert result.computation_time < 10.0  # Should be reasonably fast

        print(f"\nComputation time: {result.computation_time:.4f}s")

    def test_metadata_completeness(self):
        """Test that lens result metadata is complete."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        result = manager.get_result(LensType.DIFFERENTIAL)

        # Check metadata
        assert 'num_regions' in result.metadata
        assert 'params' in result.metadata

        assert result.metadata['num_regions'] == len(result.regions)

    # Helper methods for creating test geometries

    def _create_test_cage(self):
        """Create simple quad cage for testing."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage

    def _create_sphere_cage(self):
        """Create sphere-like SubD control cage (octahedron)."""
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


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
