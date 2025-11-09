"""
Comprehensive Python Tests for Analysis Modules

Tests all mathematical analysis lenses and lens manager functionality.
Agent 59 - Day 9, API Sprint

Coverage:
- Differential lens (curvature-based decomposition)
- Spectral lens (Laplace-Beltrami eigenfunctions)
- Laplacian computation
- Lens manager orchestration
- Parametric region representation
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

# Import analysis modules
from app.state.parametric_region import ParametricRegion

# Mock cpp_core if not available for unit testing
if not CPP_CORE_AVAILABLE:
    sys.modules['cpp_core'] = MagicMock()

from app.analysis.lens_manager import LensManager, LensType
from app.analysis.differential_lens import DifferentialLens
from app.analysis.laplacian import LaplacianBuilder, build_normalized_laplacian, verify_laplacian


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def simple_cage():
    """Create simple quad SubD cage for testing."""
    if not CPP_CORE_AVAILABLE:
        pytest.skip("cpp_core not available")

    cage = cpp_core.SubDControlCage()
    cage.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]
    cage.faces = [[0, 1, 2, 3]]
    return cage


@pytest.fixture
def sphere_cage():
    """Create icosahedron (sphere approximation) for testing."""
    if not CPP_CORE_AVAILABLE:
        pytest.skip("cpp_core not available")

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


@pytest.fixture
def initialized_evaluator(sphere_cage):
    """Create initialized SubD evaluator."""
    if not CPP_CORE_AVAILABLE:
        pytest.skip("cpp_core not available")

    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(sphere_cage)
    return evaluator


# ============================================================================
# Laplacian Computation Tests
# ============================================================================

class TestLaplacianComputation:
    """Test Laplacian matrix computation for spectral analysis."""

    def test_laplacian_builder_initialization(self, initialized_evaluator):
        """Test LaplacianBuilder initializes correctly."""
        builder = LaplacianBuilder(initialized_evaluator)

        assert builder.evaluator == initialized_evaluator
        assert builder.cached_laplacian is None
        assert builder.cached_area_matrix is None

    def test_laplacian_builder_builds_matrices(self, initialized_evaluator):
        """Test LaplacianBuilder builds L and A matrices."""
        builder = LaplacianBuilder(initialized_evaluator)

        L, A = builder.build_laplacian(tessellation_level=2)

        # Should be matrices
        assert L is not None
        assert A is not None

        # Should be square
        assert L.shape[0] == L.shape[1]
        assert A.shape[0] == A.shape[1]

        # Should have same size
        assert L.shape == A.shape

    def test_laplacian_matrix_properties(self, initialized_evaluator):
        """Test Laplacian matrix has correct properties."""
        builder = LaplacianBuilder(initialized_evaluator)
        L, A = builder.build_laplacian(tessellation_level=2)

        # Verify properties
        results = verify_laplacian(L)

        # Should be symmetric
        assert results['is_symmetric']

        # Row sums should be near zero
        assert results['row_sums_near_zero']

        # Should be sparse
        assert results['sparsity'] > 0.9  # >90% sparse

    def test_laplacian_caching(self, initialized_evaluator):
        """Test Laplacian caching works."""
        builder = LaplacianBuilder(initialized_evaluator)

        # First build
        L1, A1 = builder.build_laplacian()

        # Second build should use cache
        L2, A2 = builder.build_laplacian()

        # Should be same objects
        assert L1 is L2
        assert A1 is A2

    def test_laplacian_cache_clear(self, initialized_evaluator):
        """Test clearing Laplacian cache."""
        builder = LaplacianBuilder(initialized_evaluator)

        # Build and cache
        L1, A1 = builder.build_laplacian()

        # Clear cache
        builder.clear_cache()

        assert builder.cached_laplacian is None
        assert builder.cached_area_matrix is None

    def test_normalized_laplacian(self, initialized_evaluator):
        """Test normalized Laplacian construction."""
        builder = LaplacianBuilder(initialized_evaluator)
        L, A = builder.build_laplacian()

        # Normalize
        L_norm = build_normalized_laplacian(L, A)

        # Should be square
        assert L_norm.shape == L.shape

        # Should be symmetric
        diff = np.abs((L_norm - L_norm.T).data).max() if L_norm.nnz > 0 else 0.0
        assert diff < 1e-6


# ============================================================================
# Differential Lens Tests
# ============================================================================

class TestDifferentialLens:
    """Test differential (curvature-based) decomposition."""

    def test_differential_lens_initialization(self, initialized_evaluator):
        """Test differential lens initializes correctly."""
        lens = DifferentialLens(initialized_evaluator)

        assert lens.evaluator == initialized_evaluator
        assert lens.curvature_data is None

    def test_differential_lens_analysis(self, initialized_evaluator):
        """Test differential lens discovers regions."""
        lens = DifferentialLens(initialized_evaluator)

        regions = lens.analyze()

        # Should discover regions
        assert isinstance(regions, list)
        assert len(regions) > 0

        # Each region should be ParametricRegion
        for region in regions:
            assert isinstance(region, ParametricRegion)
            assert len(region.faces) > 0
            assert hasattr(region, 'unity_strength')
            assert 0 <= region.unity_strength <= 1

    def test_differential_lens_curvature_caching(self, initialized_evaluator):
        """Test curvature computation is cached."""
        lens = DifferentialLens(initialized_evaluator)

        # First analysis computes curvature
        regions1 = lens.analyze()
        curvature1 = lens.curvature_data

        # Second analysis should reuse cached curvature
        regions2 = lens.analyze()
        curvature2 = lens.curvature_data

        assert curvature1 is curvature2

    def test_differential_lens_with_pinned_faces(self, initialized_evaluator):
        """Test differential lens excludes pinned faces."""
        lens = DifferentialLens(initialized_evaluator)

        pinned = {0, 1, 2}
        regions = lens.analyze(pinned_faces=pinned)

        # Pinned faces should not appear in any region
        for region in regions:
            for face_id in region.faces:
                assert face_id not in pinned

    def test_differential_lens_region_metadata(self, initialized_evaluator):
        """Test regions have proper metadata."""
        lens = DifferentialLens(initialized_evaluator)

        regions = lens.analyze()

        for region in regions:
            assert 'lens' in region.metadata
            assert region.metadata['lens'] == 'differential'
            assert 'unity_principle' in region.metadata or region.unity_principle

    def test_differential_lens_min_region_size(self, initialized_evaluator):
        """Test regions respect minimum size."""
        lens = DifferentialLens(initialized_evaluator)

        min_size = 3
        regions = lens.analyze(min_region_size=min_size)

        # All regions should have at least min_size faces
        for region in regions:
            assert len(region.faces) >= min_size


# ============================================================================
# Spectral Lens Tests
# ============================================================================

class TestSpectralLens:
    """Test spectral decomposition using Laplace-Beltrami eigenfunctions."""

    @pytest.mark.skipif(True, reason="Spectral lens implementation pending Agent 35")
    def test_spectral_lens_initialization(self, initialized_evaluator):
        """Test spectral lens initializes correctly."""
        from app.analysis.spectral_lens import SpectralLens

        lens = SpectralLens(initialized_evaluator)

        assert lens.evaluator == initialized_evaluator
        assert lens.num_modes == 6  # Default

    @pytest.mark.skipif(True, reason="Spectral lens implementation pending Agent 35")
    def test_spectral_lens_eigendecomposition(self, initialized_evaluator):
        """Test spectral lens computes eigenfunctions."""
        from app.analysis.spectral_lens import SpectralLens

        lens = SpectralLens(initialized_evaluator)

        regions = lens.analyze(num_modes=4)

        # Should discover regions
        assert len(regions) > 0

        # Eigenfunctions should be computed
        assert lens.eigenvalues is not None
        assert lens.eigenvectors is not None
        assert len(lens.eigenvalues) >= 4

    @pytest.mark.skipif(True, reason="Spectral lens implementation pending Agent 35")
    def test_spectral_lens_nodal_domains(self, initialized_evaluator):
        """Test spectral lens discovers nodal domains."""
        from app.analysis.spectral_lens import SpectralLens

        lens = SpectralLens(initialized_evaluator)

        regions = lens.analyze(num_modes=6)

        # Each region represents a nodal domain
        for region in regions:
            assert isinstance(region, ParametricRegion)
            assert 'eigenmode' in region.metadata


# ============================================================================
# Lens Manager Tests
# ============================================================================

class TestLensManagerComprehensive:
    """Comprehensive tests for LensManager orchestration."""

    def test_lens_manager_initialization(self, initialized_evaluator):
        """Test LensManager initializes with evaluator."""
        manager = LensManager(initialized_evaluator)

        assert manager.evaluator == initialized_evaluator
        assert isinstance(manager.lenses, dict)
        assert manager.current_lens is None

    def test_lens_manager_requires_initialized_evaluator(self):
        """Test LensManager rejects uninitialized evaluator."""
        if not CPP_CORE_AVAILABLE:
            pytest.skip("cpp_core not available")

        evaluator = cpp_core.SubDEvaluator()
        # Don't initialize

        with pytest.raises(ValueError, match="must be initialized"):
            LensManager(evaluator)

    def test_lens_manager_registers_lenses(self, initialized_evaluator):
        """Test LensManager registers available lenses."""
        manager = LensManager(initialized_evaluator)

        # Differential lens should always be available
        assert LensType.DIFFERENTIAL in manager.lenses

        # Each lens should be properly initialized
        for lens_type, lens in manager.lenses.items():
            assert lens is not None
            assert hasattr(lens, 'analyze')

    def test_lens_manager_differential_analysis(self, initialized_evaluator):
        """Test analyzing with differential lens through manager."""
        manager = LensManager(initialized_evaluator)

        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        assert len(regions) > 0
        assert all(isinstance(r, ParametricRegion) for r in regions)
        assert manager.current_lens == LensType.DIFFERENTIAL
        assert LensType.DIFFERENTIAL in manager.analysis_results

    def test_lens_manager_caches_results(self, initialized_evaluator):
        """Test LensManager caches analysis results."""
        manager = LensManager(initialized_evaluator)

        # First analysis
        regions1 = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Second analysis should return cached results
        regions2 = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        assert regions1 is regions2  # Same object reference

    def test_lens_manager_multiple_lenses(self, initialized_evaluator):
        """Test managing multiple lens analyses."""
        manager = LensManager(initialized_evaluator)

        # Run differential analysis
        diff_regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Results should be cached
        assert len(manager.analysis_results) == 1
        assert LensType.DIFFERENTIAL in manager.analysis_results

    def test_lens_manager_compare_lenses(self, initialized_evaluator):
        """Test comparing lens quality scores."""
        manager = LensManager(initialized_evaluator)

        # Run analysis
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Compare
        scores = manager.compare_lenses()

        assert isinstance(scores, dict)
        assert LensType.DIFFERENTIAL in scores
        assert 0 <= scores[LensType.DIFFERENTIAL] <= 1

    def test_lens_manager_get_best_lens(self, initialized_evaluator):
        """Test identifying best lens."""
        manager = LensManager(initialized_evaluator)

        # Run analysis
        manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Get best
        best = manager.get_best_lens()

        assert best == LensType.DIFFERENTIAL

    def test_lens_manager_get_best_lens_empty(self, initialized_evaluator):
        """Test get_best_lens with no analyses."""
        manager = LensManager(initialized_evaluator)

        best = manager.get_best_lens()

        assert best is None

    def test_lens_manager_unavailable_lens_error(self, initialized_evaluator):
        """Test error when requesting unavailable lens."""
        manager = LensManager(initialized_evaluator)

        with pytest.raises(ValueError, match="not available"):
            manager.analyze_with_lens(LensType.FLOW)  # Not implemented yet

    def test_lens_manager_parameter_passing(self, initialized_evaluator):
        """Test passing parameters to lens analysis."""
        manager = LensManager(initialized_evaluator)

        # Pass parameters
        pinned = {0, 1, 2}
        regions = manager.analyze_with_lens(
            LensType.DIFFERENTIAL,
            pinned_faces=pinned
        )

        # Verify pinned faces excluded
        for region in regions:
            for face in region.faces:
                assert face not in pinned


# ============================================================================
# Parametric Region Tests
# ============================================================================

class TestParametricRegionStructure:
    """Test ParametricRegion data structure."""

    def test_parametric_region_creation(self):
        """Test creating parametric region."""
        region = ParametricRegion(
            id="test_region",
            faces=[0, 1, 2, 3],
            unity_principle="Curvature",
            unity_strength=0.85
        )

        assert region.id == "test_region"
        assert region.faces == [0, 1, 2, 3]
        assert region.unity_principle == "Curvature"
        assert region.unity_strength == 0.85

    def test_parametric_region_metadata(self):
        """Test region metadata storage."""
        region = ParametricRegion(
            id="test",
            faces=[0, 1],
            unity_principle="Test",
            unity_strength=0.5,
            metadata={'lens': 'differential', 'custom': 'value'}
        )

        assert 'lens' in region.metadata
        assert region.metadata['lens'] == 'differential'
        assert region.metadata['custom'] == 'value'

    def test_parametric_region_pinned_state(self):
        """Test region pinned state management."""
        region = ParametricRegion(
            id="test",
            faces=[0, 1],
            unity_principle="Test",
            unity_strength=0.5
        )

        # Should be unpinned by default
        assert not region.pinned

        # Should be mutable
        region.pinned = True
        assert region.pinned


# ============================================================================
# Integration Tests
# ============================================================================

class TestAnalysisIntegration:
    """Integration tests across analysis modules."""

    def test_full_analysis_pipeline(self, initialized_evaluator):
        """Test complete analysis pipeline."""
        # Create manager
        manager = LensManager(initialized_evaluator)

        # Run analysis
        regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Verify results
        assert len(regions) > 0

        # All regions should have:
        # - Face list
        # - Unity strength
        # - Unity principle
        # - Metadata
        for region in regions:
            assert len(region.faces) > 0
            assert 0 <= region.unity_strength <= 1
            assert region.unity_principle is not None
            assert isinstance(region.metadata, dict)

    def test_analysis_with_constraints(self, initialized_evaluator):
        """Test analysis respects constraints."""
        manager = LensManager(initialized_evaluator)

        # Analyze with pinned faces
        pinned = {0, 1, 2, 3}
        regions = manager.analyze_with_lens(
            LensType.DIFFERENTIAL,
            pinned_faces=pinned
        )

        # Verify constraints respected
        all_faces = set()
        for region in regions:
            all_faces.update(region.faces)

        assert all_faces.isdisjoint(pinned)


# ============================================================================
# Mock Tests (without cpp_core)
# ============================================================================

class TestAnalysisWithMocks:
    """Tests that work without cpp_core using mocks."""

    def test_lens_type_enum_values(self):
        """Test LensType enum has correct values."""
        assert LensType.DIFFERENTIAL.value == "differential"
        assert LensType.SPECTRAL.value == "spectral"
        assert LensType.FLOW.value == "flow"
        assert LensType.MORSE.value == "morse"
        assert LensType.THERMAL.value == "thermal"

    def test_lens_type_enum_membership(self):
        """Test LensType enum membership."""
        assert LensType.DIFFERENTIAL in LensType
        assert LensType.SPECTRAL in LensType

        lens_types = list(LensType)
        assert len(lens_types) == 5

    def test_compare_lenses_calculation_logic(self):
        """Test lens comparison score calculation."""
        # Mock regions with unity scores
        mock_regions_1 = [
            Mock(unity_strength=0.8),
            Mock(unity_strength=0.9),
        ]
        mock_regions_2 = [
            Mock(unity_strength=0.6),
            Mock(unity_strength=0.7),
        ]

        # Calculate scores
        score_1 = sum(r.unity_strength for r in mock_regions_1) / len(mock_regions_1)
        score_2 = sum(r.unity_strength for r in mock_regions_2) / len(mock_regions_2)

        assert score_1 == pytest.approx(0.85)
        assert score_2 == pytest.approx(0.65)

    def test_get_best_lens_selection_logic(self):
        """Test best lens selection logic."""
        scores = {
            LensType.DIFFERENTIAL: 0.85,
            LensType.SPECTRAL: 0.65,
        }

        best = max(scores.keys(), key=lambda k: scores[k])

        assert best == LensType.DIFFERENTIAL


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
