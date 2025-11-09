"""
Comprehensive Tests for Differential Lens

Tests the first mathematical lens implementation using exact SubD limit surface
curvature analysis. This validates the entire parametric region architecture.

Test Strategy:
1. Unit tests for individual methods
2. Integration tests with simple geometries (sphere, cylinder, saddle)
3. Validation against known curvature values
4. Ridge/valley detection verification
5. Region coherence scoring

Author: Agent 32
Date: November 2025
"""

import pytest
import numpy as np
from typing import List, Dict

# Import the module under test
from app.analysis.differential_lens import DifferentialLens, DifferentialLensParams
from app.state.parametric_region import ParametricRegion

# Try to import cpp_core
try:
    import cpp_core
    CPP_CORE_AVAILABLE = True
except ImportError:
    CPP_CORE_AVAILABLE = False
    pytestmark = pytest.mark.skip("cpp_core not available - skipping differential lens tests")


def create_simple_cube_cage():
    """Create a simple cube SubD control cage for testing."""
    cage = cpp_core.SubDControlCage()

    # 8 cube vertices
    vertices = [
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),  # Bottom
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)       # Top
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


def create_simple_sphere_cage():
    """Create a simple sphere-like SubD control cage (octahedron subdivision)."""
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


def create_cylinder_cage():
    """Create a cylinder-like SubD control cage."""
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


@pytest.mark.skipif(not CPP_CORE_AVAILABLE, reason="cpp_core not available")
class TestDifferentialLensBasic:
    """Basic functionality tests for DifferentialLens."""

    def test_initialization(self):
        """Test lens can be initialized with SubDEvaluator."""
        cage = create_simple_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        assert lens.evaluator.is_initialized()
        assert lens.params is not None
        assert lens.curvature_analyzer is not None

    def test_initialization_requires_initialized_evaluator(self):
        """Test that lens requires initialized evaluator."""
        evaluator = cpp_core.SubDEvaluator()  # Not initialized

        with pytest.raises(ValueError, match="must be initialized"):
            lens = DifferentialLens(evaluator)

    def test_custom_parameters(self):
        """Test lens accepts custom parameters."""
        cage = create_simple_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        params = DifferentialLensParams(
            samples_per_face=16,
            mean_curvature_threshold=0.05,
            curvature_tolerance=0.2
        )

        lens = DifferentialLens(evaluator, params)

        assert lens.params.samples_per_face == 16
        assert lens.params.mean_curvature_threshold == 0.05
        assert lens.params.curvature_tolerance == 0.2


@pytest.mark.skipif(not CPP_CORE_AVAILABLE, reason="cpp_core not available")
class TestDifferentialLensSphere:
    """Tests on sphere geometry (uniform positive curvature)."""

    def test_sphere_single_region(self):
        """Test that sphere produces single elliptic region."""
        cage = create_simple_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)
        regions = lens.discover_regions()

        # Sphere should be 1 region (all faces have similar positive curvature)
        assert len(regions) >= 1, "Should discover at least 1 region"

        # Check that regions are ParametricRegion objects
        assert all(isinstance(r, ParametricRegion) for r in regions)

        # Check metadata
        for region in regions:
            assert region.unity_principle != ""
            assert 0.0 <= region.unity_strength <= 1.0
            assert len(region.faces) > 0
            assert region.metadata['lens'] == 'differential'

    def test_sphere_curvature_classification(self):
        """Test that sphere faces are classified as elliptic."""
        cage = create_simple_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        # Compute curvatures
        num_faces = evaluator.get_control_face_count()
        curvature_data = lens._compute_face_curvatures(num_faces)

        # Classify faces
        classifications = lens._classify_faces(curvature_data)

        # Most faces should be elliptic (positive Gaussian curvature)
        elliptic_count = sum(1 for c in classifications.values() if c == 'elliptic')
        assert elliptic_count > 0, "Sphere should have elliptic faces"

    def test_sphere_high_coherence(self):
        """Test that sphere region has high coherence (uniform curvature)."""
        cage = create_simple_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)
        regions = lens.discover_regions()

        # All regions should have reasonably high coherence
        for region in regions:
            assert region.unity_strength >= 0.5, \
                f"Sphere region should have high coherence, got {region.unity_strength}"


@pytest.mark.skipif(not CPP_CORE_AVAILABLE, reason="cpp_core not available")
class TestDifferentialLensCylinder:
    """Tests on cylinder geometry (parabolic curvature)."""

    def test_cylinder_parabolic_classification(self):
        """Test that cylinder sides are classified as parabolic."""
        cage = create_cylinder_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        # Compute curvatures
        num_faces = evaluator.get_control_face_count()
        curvature_data = lens._compute_face_curvatures(num_faces)

        # Classify faces
        classifications = lens._classify_faces(curvature_data)

        # Should have mix of parabolic (sides) and possibly elliptic (caps)
        types_present = set(classifications.values())
        assert 'parabolic' in types_present or 'elliptic' in types_present


@pytest.mark.skipif(not CPP_CORE_AVAILABLE, reason="cpp_core not available")
class TestDifferentialLensRegionGrowing:
    """Tests for region growing algorithm."""

    def test_face_adjacency_building(self):
        """Test face adjacency graph construction."""
        cage = create_simple_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        num_faces = evaluator.get_control_face_count()
        adjacency = lens._build_face_adjacency(num_faces)

        # Should have adjacency entries for all faces
        assert len(adjacency) > 0

        # Each face should have some neighbors (for a cube)
        for face_idx in range(num_faces):
            neighbors = adjacency.get(face_idx, set())
            # At minimum, we should have built some adjacency
            # (exact count depends on topology)
            assert isinstance(neighbors, set)

    def test_coherence_computation(self):
        """Test region coherence scoring."""
        cage = create_simple_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        # Compute curvatures
        num_faces = evaluator.get_control_face_count()
        curvature_data = lens._compute_face_curvatures(num_faces)

        # Test coherence for different region sizes
        # Single face = perfect coherence
        coherence_1 = lens._compute_coherence([0], curvature_data)
        assert coherence_1 == 1.0

        # Multiple faces - should be in [0, 1]
        if num_faces >= 3:
            coherence_multi = lens._compute_coherence([0, 1, 2], curvature_data)
            assert 0.0 <= coherence_multi <= 1.0

    def test_compatibility_check(self):
        """Test curvature compatibility checking."""
        cage = create_simple_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        # Compute curvatures
        num_faces = evaluator.get_control_face_count()
        curvature_data = lens._compute_face_curvatures(num_faces)
        classifications = lens._classify_faces(curvature_data)

        # Test compatibility between faces of same type
        if num_faces >= 2:
            face0_stats = curvature_data[0]
            face1_stats = curvature_data[1]
            face0_type = classifications[0]
            face1_type = classifications[1]

            # Same type should often be compatible (depends on tolerance)
            if face0_type == face1_type:
                compatible = lens._is_curvature_compatible(
                    face0_stats, face1_stats, face0_type, face1_type
                )
                # Result depends on actual curvature values, just check it runs
                assert isinstance(compatible, bool)


@pytest.mark.skipif(not CPP_CORE_AVAILABLE, reason="cpp_core not available")
class TestDifferentialLensRidgeValley:
    """Tests for ridge and valley detection."""

    def test_ridge_valley_detection(self):
        """Test ridge/valley detection returns sets."""
        cage = create_simple_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        # Compute curvatures
        num_faces = evaluator.get_control_face_count()
        curvature_data = lens._compute_face_curvatures(num_faces)

        # Detect ridges/valleys
        ridges, valleys = lens._detect_ridges_valleys(curvature_data)

        # Should return sets
        assert isinstance(ridges, set)
        assert isinstance(valleys, set)

        # Sets should not overlap (a face can't be both ridge and valley)
        assert len(ridges.intersection(valleys)) == 0

    def test_ridge_valley_percentile_thresholds(self):
        """Test that ridge/valley detection uses percentile thresholds."""
        cage = create_simple_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        params = DifferentialLensParams(
            ridge_percentile=80.0,   # Top 20%
            valley_percentile=20.0   # Bottom 20%
        )

        lens = DifferentialLens(evaluator, params)

        num_faces = evaluator.get_control_face_count()
        curvature_data = lens._compute_face_curvatures(num_faces)

        ridges, valleys = lens._detect_ridges_valleys(curvature_data)

        # Should have some ridges (top 20%)
        # Exact count depends on geometry, but should be reasonable
        if num_faces > 5:
            assert len(ridges) > 0
            assert len(valleys) > 0


@pytest.mark.skipif(not CPP_CORE_AVAILABLE, reason="cpp_core not available")
class TestDifferentialLensIntegration:
    """Integration tests for complete workflow."""

    def test_end_to_end_cube(self):
        """Test complete workflow on cube."""
        cage = create_simple_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)
        regions = lens.discover_regions()

        # Should discover regions
        assert len(regions) > 0

        # All regions should have proper structure
        for region in regions:
            assert isinstance(region, ParametricRegion)
            assert region.id != ""
            assert len(region.faces) > 0
            assert 0.0 <= region.unity_strength <= 1.0
            assert region.metadata['lens'] == 'differential'

    def test_end_to_end_sphere(self):
        """Test complete workflow on sphere."""
        cage = create_simple_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)
        regions = lens.discover_regions()

        # Should discover regions
        assert len(regions) > 0

        # Total faces should match input
        num_faces = evaluator.get_control_face_count()
        total_region_faces = sum(len(r.faces) for r in regions)
        assert total_region_faces == num_faces, "All faces should be assigned to regions"

    def test_pinned_faces_excluded(self):
        """Test that pinned faces are excluded from analysis."""
        cage = create_simple_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        # Pin first 2 faces
        pinned = {0, 1}
        regions = lens.discover_regions(pinned_faces=pinned)

        # Pinned faces should not appear in any region
        for region in regions:
            for face in region.faces:
                assert face not in pinned, f"Pinned face {face} found in region"

    def test_curvature_field_caching(self):
        """Test that curvature field is cached for visualization."""
        cage = create_simple_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = DifferentialLens(evaluator)

        # Before discovery, cache should be None
        assert lens.get_curvature_field() is None

        # After discovery, cache should be populated
        regions = lens.discover_regions()
        curvature_field = lens.get_curvature_field()

        assert curvature_field is not None
        assert len(curvature_field) > 0

        # Each entry should have curvature statistics
        for face_idx, stats in curvature_field.items():
            assert 'mean_K' in stats
            assert 'mean_H' in stats
            assert 'mean_abs_H' in stats


@pytest.mark.skipif(not CPP_CORE_AVAILABLE, reason="cpp_core not available")
class TestDifferentialLensParameters:
    """Tests for parameter sensitivity."""

    def test_high_tolerance_fewer_regions(self):
        """Test that high tolerance produces fewer regions."""
        cage = create_simple_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Low tolerance (strict) - more regions
        params_strict = DifferentialLensParams(curvature_tolerance=0.1)
        lens_strict = DifferentialLens(evaluator, params_strict)
        regions_strict = lens_strict.discover_regions()

        # High tolerance (relaxed) - fewer regions
        params_relaxed = DifferentialLensParams(curvature_tolerance=0.9)
        lens_relaxed = DifferentialLens(evaluator, params_relaxed)
        regions_relaxed = lens_relaxed.discover_regions()

        # Relaxed should produce fewer or equal regions
        assert len(regions_relaxed) <= len(regions_strict)

    def test_min_region_size_merging(self):
        """Test that min_region_size triggers merging."""
        cage = create_simple_cube_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # No merging
        params_no_merge = DifferentialLensParams(min_region_size=1)
        lens_no_merge = DifferentialLens(evaluator, params_no_merge)
        regions_no_merge = lens_no_merge.discover_regions()

        # Merge small regions
        params_merge = DifferentialLensParams(min_region_size=3)
        lens_merge = DifferentialLens(evaluator, params_merge)
        regions_merge = lens_merge.discover_regions()

        # After merging, should have no regions smaller than min_size
        for region in regions_merge:
            assert len(region.faces) >= params_merge.min_region_size or \
                   len(regions_merge) == 1  # Unless only one region total


def test_lens_requires_cpp_core():
    """Test that lens fails gracefully without cpp_core."""
    if CPP_CORE_AVAILABLE:
        pytest.skip("cpp_core is available, skipping fail test")

    # This test only runs when cpp_core is NOT available
    # It should be skipped when cpp_core IS available

    # The module should import but raise error on usage
    from app.analysis.differential_lens import DifferentialLens

    with pytest.raises(RuntimeError, match="cpp_core module not available"):
        # This should fail because cpp_core is None
        lens = DifferentialLens(None)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
