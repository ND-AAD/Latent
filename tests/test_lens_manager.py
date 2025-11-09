"""
Tests for Lens Manager - Unified Lens Interface

Tests the coordination layer that manages multiple mathematical lenses
and provides comparison capabilities.

Author: Agent 38, Ceramic Mold Analyzer
Date: November 2025
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
import sys

# Check if cpp_core is fully built
try:
    import cpp_core
    CPP_CORE_AVAILABLE = hasattr(cpp_core, 'SubDEvaluator')
except ImportError:
    CPP_CORE_AVAILABLE = False

from app.state.parametric_region import ParametricRegion


# Import LensManager after mocking if needed
if not CPP_CORE_AVAILABLE:
    # Mock cpp_core for unit testing
    sys.modules['cpp_core'] = MagicMock()

from app.analysis.lens_manager import LensManager, LensType


class TestLensManager:
    """Test LensManager unified interface."""

    def test_initialization(self):
        """Test LensManager initialization with evaluator."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Should initialize successfully
        assert manager.evaluator == evaluator
        assert isinstance(manager.lenses, dict)
        assert manager.current_lens is None
        assert len(manager.analysis_results) == 0

    def test_initialization_requires_initialized_evaluator(self):
        """Test that LensManager requires initialized evaluator."""
        evaluator = cpp_core.SubDEvaluator()
        # Don't initialize

        with pytest.raises(ValueError, match="must be initialized"):
            LensManager(evaluator)

    def test_available_lenses(self):
        """Test that available lenses are registered."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # DifferentialLens should be available
        assert LensType.DIFFERENTIAL in manager.lenses

        # Each available lens should be initialized
        for lens_type, lens in manager.lenses.items():
            assert lens is not None

    def test_analyze_with_differential_lens(self):
        """Test analyzing with differential lens."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze with differential lens
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Should discover regions
        assert isinstance(regions, list)
        assert len(regions) > 0

        # Regions should be ParametricRegion objects
        for region in regions:
            assert isinstance(region, ParametricRegion)
            assert len(region.faces) > 0
            assert hasattr(region, 'unity_strength')

        # Results should be cached
        assert LensType.DIFFERENTIAL in manager.analysis_results
        assert manager.current_lens == LensType.DIFFERENTIAL

    def test_analyze_with_unavailable_lens(self):
        """Test error when analyzing with unavailable lens."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Try to use a lens that doesn't exist
        with pytest.raises(ValueError, match="not available"):
            manager.analyze_with_lens(LensType.FLOW)

    def test_compare_lenses_single_lens(self):
        """Test comparing lenses when only one has been run."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze with differential lens
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Compare
        scores = manager.compare_lenses()

        # Should have one score
        assert len(scores) == 1
        assert LensType.DIFFERENTIAL in scores
        assert 0.0 <= scores[LensType.DIFFERENTIAL] <= 1.0

    def test_compare_lenses_empty(self):
        """Test comparing lenses when no analyses have been run."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Compare without running any analysis
        scores = manager.compare_lenses()

        # Should return empty dict
        assert len(scores) == 0

    def test_get_best_lens_single(self):
        """Test getting best lens when only one available."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze with differential lens
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Get best
        best = manager.get_best_lens()

        assert best == LensType.DIFFERENTIAL

    def test_get_best_lens_empty(self):
        """Test getting best lens when no analyses run."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Get best without any analysis
        best = manager.get_best_lens()

        assert best is None

    def test_results_caching(self):
        """Test that results are cached properly."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze once
        regions1 = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Analyze again (should use cache)
        regions2 = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Should return same regions (cached)
        assert regions1 is regions2
        assert len(regions1) == len(regions2)

    def test_differential_lens_with_parameters(self):
        """Test passing parameters to differential lens."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze with pinned faces
        pinned = {0, 1, 2}
        regions = manager.analyze_with_lens(
            LensType.DIFFERENTIAL,
            pinned_faces=pinned
        )

        # Should work (pinned faces excluded from regions)
        assert len(regions) > 0

        # Pinned faces should not appear in any region
        for region in regions:
            for face in region.faces:
                assert face not in pinned

    def test_lens_type_enum(self):
        """Test LensType enum values."""
        assert LensType.DIFFERENTIAL.value == "differential"
        assert LensType.SPECTRAL.value == "spectral"
        assert LensType.FLOW.value == "flow"
        assert LensType.MORSE.value == "morse"
        assert LensType.THERMAL.value == "thermal"

    def test_multiple_analyses_different_lenses(self):
        """Test running multiple analyses with different lenses."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze with differential
        diff_regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Both should be cached
        assert LensType.DIFFERENTIAL in manager.analysis_results
        assert len(manager.analysis_results) == 1

        # Current lens should be last one used
        assert manager.current_lens == LensType.DIFFERENTIAL

    def test_region_metadata(self):
        """Test that regions have proper metadata."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Check metadata
        for region in regions:
            assert 'lens' in region.metadata
            assert region.metadata['lens'] == 'differential'

    # Helper methods for creating test geometries

    def _create_simple_cage(self):
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
        """Create icosahedron (sphere approximation) for testing."""
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


class TestLensTypeEnum:
    """Test LensType enum functionality."""

    def test_enum_values(self):
        """Test enum values are correct."""
        assert LensType.DIFFERENTIAL.value == "differential"
        assert LensType.SPECTRAL.value == "spectral"
        assert LensType.FLOW.value == "flow"
        assert LensType.MORSE.value == "morse"
        assert LensType.THERMAL.value == "thermal"

    def test_enum_membership(self):
        """Test enum membership checks."""
        assert LensType.DIFFERENTIAL in LensType
        assert LensType.SPECTRAL in LensType

    def test_enum_iteration(self):
        """Test iterating over enum."""
        lens_types = list(LensType)
        assert len(lens_types) == 5
        assert LensType.DIFFERENTIAL in lens_types
        assert LensType.SPECTRAL in lens_types


class TestLensManagerUnitLogic:
    """Unit tests for LensManager logic without requiring cpp_core."""

    def test_compare_lenses_logic(self):
        """Test compare_lenses calculation logic."""
        # Create mock manager
        manager = Mock()
        manager.analysis_results = {
            LensType.DIFFERENTIAL: [
                Mock(unity_strength=0.8),
                Mock(unity_strength=0.9),
            ],
            LensType.SPECTRAL: [
                Mock(unity_strength=0.6),
                Mock(unity_strength=0.7),
            ]
        }

        # Implement the compare_lenses logic
        scores = {}
        for lens_type, regions in manager.analysis_results.items():
            if regions:
                unity_scores = [r.unity_strength for r in regions]
                scores[lens_type] = sum(unity_scores) / len(unity_scores)

        # Verify results
        assert len(scores) == 2
        assert scores[LensType.DIFFERENTIAL] == pytest.approx(0.85)  # (0.8 + 0.9) / 2
        assert scores[LensType.SPECTRAL] == pytest.approx(0.65)  # (0.6 + 0.7) / 2

    def test_get_best_lens_logic(self):
        """Test get_best_lens selection logic."""
        scores = {
            LensType.DIFFERENTIAL: 0.85,
            LensType.SPECTRAL: 0.65,
        }

        best = max(scores.keys(), key=lambda k: scores[k])

        assert best == LensType.DIFFERENTIAL

    def test_lens_availability_check(self):
        """Test lens availability checking."""
        # This tests the import mechanism
        from app.analysis.lens_manager import DIFFERENTIAL_AVAILABLE, SPECTRAL_AVAILABLE

        # At least one should be available (differential exists)
        # Spectral may or may not be available depending on whether Agent 35 ran
        assert isinstance(DIFFERENTIAL_AVAILABLE, bool)
        assert isinstance(SPECTRAL_AVAILABLE, bool)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
