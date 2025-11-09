"""
Integration Tests for Complete Analysis Pipeline

Tests the entire analysis system end-to-end:
- Differential lens (curvature-based)
- Spectral lens (eigenfunction-based) - when available
- LensManager unified interface
- Region discovery and scoring

This validates that all Day 4-5 components integrate correctly.

Author: Agent 39, Ceramic Mold Analyzer
Date: November 2025
"""

import pytest
import numpy as np
import time
from typing import List

# Import analysis components
from app.analysis.lens_manager import LensManager, LensType, LensResult
from app.analysis.differential_lens import DifferentialLens, DifferentialLensParams
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
        pytestmark = pytest.mark.skip("cpp_core bindings incomplete - skipping analysis pipeline tests")
except ImportError:
    CPP_CORE_AVAILABLE = False
    pytestmark = pytest.mark.skip("cpp_core not available - skipping analysis pipeline tests")


class TestAnalysisPipeline:
    """Integration tests for complete analysis pipeline."""

    def test_end_to_end_differential(self):
        """Test complete differential analysis workflow."""
        # Create geometry
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Run differential analysis through LensManager
        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Verify results
        assert len(regions) > 0, "Should discover at least one region"
        assert all(isinstance(r, ParametricRegion) for r in regions), \
            "All results should be ParametricRegion objects"

        # Check metadata
        for region in regions:
            assert hasattr(region, 'metadata'), "Region should have metadata"
            assert 'lens' in region.metadata, "Should specify lens type"
            assert region.metadata['lens'] == 'differential', \
                "Should be from differential lens"
            assert hasattr(region, 'unity_strength'), "Should have unity strength"
            assert 0.0 <= region.unity_strength <= 1.0, \
                "Unity strength should be in [0,1]"

    def test_end_to_end_spectral_stub(self):
        """Test spectral analysis workflow (stub until Agent 35 completes)."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Spectral lens not yet implemented
        with pytest.raises(NotImplementedError):
            regions = manager.analyze_with_lens(LensType.SPECTRAL)

    def test_lens_manager_initialization(self):
        """Test LensManager properly initializes with evaluator."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Check initialization
        assert manager.evaluator is evaluator
        assert manager.differential_lens is not None
        assert isinstance(manager.differential_lens, DifferentialLens)

    def test_lens_manager_requires_initialized_evaluator(self):
        """Test that LensManager requires initialized evaluator."""
        evaluator = cpp_core.SubDEvaluator()
        # Don't initialize

        with pytest.raises(ValueError, match="initialized"):
            LensManager(evaluator)

    def test_analysis_caching(self):
        """Test that analysis results are cached properly."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # First analysis
        start = time.time()
        regions1 = manager.analyze_with_lens(LensType.DIFFERENTIAL)
        time1 = time.time() - start

        # Second analysis (should use cache)
        start = time.time()
        regions2 = manager.analyze_with_lens(LensType.DIFFERENTIAL)
        time2 = time.time() - start

        # Should return same regions
        assert len(regions1) == len(regions2)

        # Second call should be much faster (cached)
        assert time2 < time1 * 0.1, "Cached access should be much faster"

    def test_force_recompute(self):
        """Test force_recompute parameter."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # First analysis
        regions1 = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Force recompute
        regions2 = manager.analyze_with_lens(
            LensType.DIFFERENTIAL,
            force_recompute=True
        )

        # Should still get valid results
        assert len(regions2) > 0

    def test_clear_cache(self):
        """Test clearing analysis cache."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze
        manager.analyze_with_lens(LensType.DIFFERENTIAL)
        assert len(manager._results) > 0

        # Clear cache
        manager.clear_cache()
        assert len(manager._results) == 0

    def test_get_result(self):
        """Test retrieving cached LensResult."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Get result
        result = manager.get_result(LensType.DIFFERENTIAL)

        assert result is not None
        assert isinstance(result, LensResult)
        assert result.lens_type == LensType.DIFFERENTIAL
        assert len(result.regions) > 0
        assert 0.0 <= result.resonance_score <= 1.0
        assert result.computation_time > 0
        assert 'num_regions' in result.metadata

    def test_analysis_summary(self):
        """Test getting analysis summary."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Before analysis
        summary = manager.get_analysis_summary()
        assert summary['status'] == 'no_analyses_cached'

        # After analysis
        manager.analyze_with_lens(LensType.DIFFERENTIAL)
        summary = manager.get_analysis_summary()

        assert 'num_lenses_analyzed' in summary
        assert summary['num_lenses_analyzed'] == 1
        assert 'lenses' in summary
        assert 'differential' in summary['lenses']
        assert 'best_lens' in summary
        assert summary['best_lens'] == 'differential'

    def test_parametric_region_properties(self):
        """Test that discovered regions have all required properties."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        for region in regions:
            # Check ParametricRegion interface
            assert hasattr(region, 'id')
            assert hasattr(region, 'faces')
            assert hasattr(region, 'boundary')
            assert hasattr(region, 'unity_principle')
            assert hasattr(region, 'unity_strength')
            assert hasattr(region, 'pinned')
            assert hasattr(region, 'metadata')

            # Check values
            assert isinstance(region.faces, list)
            assert len(region.faces) > 0
            assert isinstance(region.unity_principle, str)
            assert len(region.unity_principle) > 0

    def test_different_geometries(self):
        """Test analysis on different geometric shapes."""
        geometries = [
            ('cube', self._create_test_cage()),
            ('sphere', self._create_sphere_cage()),
            ('cylinder', self._create_cylinder_cage())
        ]

        for name, cage in geometries:
            evaluator = cpp_core.SubDEvaluator()
            evaluator.initialize(cage)

            manager = LensManager(evaluator)
            regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

            # Each geometry should produce regions
            assert len(regions) > 0, f"{name} should produce regions"

            # Check resonance score
            result = manager.get_result(LensType.DIFFERENTIAL)
            assert 0.0 <= result.resonance_score <= 1.0, \
                f"{name} resonance score should be in [0,1]"

    def test_performance_target(self):
        """Test that analysis meets performance targets (<2 seconds total)."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Time the analysis
        start = time.time()
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)
        elapsed = time.time() - start

        print(f"\nDifferential analysis time: {elapsed:.3f}s")
        print(f"Regions discovered: {len(regions)}")

        # Should complete in under 2 seconds
        assert elapsed < 2.0, \
            f"Analysis took {elapsed:.3f}s, should be < 2.0s"

    def test_curvature_field_access(self):
        """Test accessing curvature field data from differential lens."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Access curvature field
        curvature_field = manager.differential_lens.get_curvature_field()

        assert curvature_field is not None
        assert isinstance(curvature_field, dict)
        assert len(curvature_field) > 0

        # Check curvature data structure
        for face_idx, stats in curvature_field.items():
            assert 'mean_K' in stats  # Gaussian curvature
            assert 'mean_H' in stats  # Mean curvature
            assert 'mean_abs_H' in stats
            assert 'std_K' in stats
            assert 'std_H' in stats

    def test_custom_parameters(self):
        """Test passing custom parameters to lens."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Custom parameters
        custom_params = {
            'samples_per_face': 4,
            'mean_curvature_threshold': 0.02,
            'min_region_size': 2
        }

        regions = manager.analyze_with_lens(
            LensType.DIFFERENTIAL,
            params=custom_params
        )

        assert len(regions) > 0

    def test_resonance_scoring(self):
        """Test resonance score computation."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        result = manager.get_result(LensType.DIFFERENTIAL)
        score = result.resonance_score

        # Score should be reasonable for sphere decomposition
        assert score > 0.2, "Sphere decomposition should have decent resonance"

        # Should reflect region quality
        assert 0.0 <= score <= 1.0

    def test_region_unity_principle(self):
        """Test that regions have descriptive unity principles."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        for region in regions:
            # Should have descriptive principle
            assert len(region.unity_principle) > 10
            assert 'curvature' in region.unity_principle.lower() or \
                   'coherence' in region.unity_principle.lower()

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
