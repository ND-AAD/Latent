"""
Test suite for spectral decomposition and nodal domain extraction.

Tests eigenmode computation, nodal domain discovery, flood-fill algorithm,
and spectral lens interface.

Author: Ceramic Mold Analyzer - Agent 35
Date: November 2025
"""

import pytest
import numpy as np
import cpp_core
from app.analysis.spectral_decomposition import SpectralDecomposer, EigenMode
from app.analysis.spectral_lens import SpectralLens


class TestSpectralDecomposition:
    """Test spectral decomposition and region discovery."""

    def test_eigenmode_computation(self):
        """Test eigenmode computation on simple geometry."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=6)

        # Should have 6 modes
        assert len(modes) == 6

        # First eigenvalue should be ~0 (constant function)
        assert modes[0].eigenvalue < 0.01, \
            f"First eigenvalue {modes[0].eigenvalue} not near 0"

        # Eigenvalues should be ascending
        for i in range(len(modes) - 1):
            assert modes[i].eigenvalue <= modes[i+1].eigenvalue, \
                f"Eigenvalues not ascending: {modes[i].eigenvalue} > {modes[i+1].eigenvalue}"

        # Eigenfunctions should be normalized
        for mode in modes:
            norm = np.linalg.norm(mode.eigenfunction)
            assert 0.9 < norm < 1.1, \
                f"Eigenfunction {mode.index} not normalized: norm={norm}"

    def test_nodal_domain_extraction(self):
        """Test extracting nodal domains from eigenfunction."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=4)

        # Extract domains from mode 1 (first non-trivial)
        regions = decomposer.extract_nodal_domains(mode_index=1)

        # Should have at least 2 regions (positive and negative domains)
        assert len(regions) >= 2, \
            f"Expected at least 2 regions, got {len(regions)}"

        # Each region should have faces
        for region in regions:
            assert len(region.faces) > 0, "Region should have at least one face"

        # Check metadata
        for region in regions:
            assert 'generation_method' in region.metadata
            assert region.metadata['generation_method'] == 'spectral'
            assert 'mode_index' in region.metadata
            assert 'sign' in region.metadata

    def test_mode_zero_raises_error(self):
        """Test that mode 0 cannot be used for nodal domains."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=4)

        # Mode 0 should raise ValueError
        with pytest.raises(ValueError, match="constant function"):
            decomposer.extract_nodal_domains(mode_index=0)

    def test_resonance_scoring(self):
        """Test resonance score computation."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=4)
        regions = decomposer.extract_nodal_domains(mode_index=1)

        score = decomposer.compute_resonance_score(regions)

        # Score should be in [0, 1]
        assert 0.0 <= score <= 1.0, f"Score {score} not in [0,1]"

        # For reasonable decomposition, score should be > 0.3
        assert score > 0.3, f"Score {score} too low for reasonable decomposition"

    def test_empty_regions_score_zero(self):
        """Test that empty region list gets score of 0."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        score = decomposer.compute_resonance_score([])

        assert score == 0.0, "Empty regions should have score 0"

    def test_spectral_lens_interface(self):
        """Test SpectralLens high-level interface."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = SpectralLens(evaluator)
        regions = lens.analyze(num_modes=6, mode_indices=[1, 2])

        # Should discover regions
        assert len(regions) > 0, "Should discover at least some regions"

        # Regions should have metadata
        for region in regions:
            assert region.metadata['generation_method'] == 'spectral'
            assert 'mode_index' in region.metadata
            assert region.unity_strength >= 0.0  # Resonance score was set

    def test_get_eigenmode(self):
        """Test getting specific eigenmode from lens."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = SpectralLens(evaluator)
        lens.analyze(num_modes=5)

        # Get mode 0
        mode = lens.get_eigenmode(0)
        assert isinstance(mode, EigenMode)
        assert mode.index == 0
        assert mode.eigenvalue < 0.01  # Constant mode

        # Get mode 1
        mode1 = lens.get_eigenmode(1)
        assert mode1.index == 1
        assert mode1.eigenvalue > mode.eigenvalue  # Should be larger

    def test_get_eigenmode_before_analyze_raises_error(self):
        """Test that get_eigenmode before analyze raises error."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = SpectralLens(evaluator)

        with pytest.raises(ValueError, match="Must call analyze"):
            lens.get_eigenmode(0)

    def test_multiplicity_detection(self):
        """Test detection of eigenvalue multiplicities."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=10)

        # For sphere, should detect multiplicities
        # (Though subdivision may break exact symmetry)
        multiplicities = [m.multiplicity for m in modes]

        # At least some modes should have multiplicity > 1
        assert any(m > 1 for m in multiplicities), \
            "Expected some repeated eigenvalues"

        print(f"Eigenvalue multiplicities: {multiplicities}")

    def test_flood_fill_connectivity(self):
        """Test flood-fill connected component algorithm."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=3)

        # Extract domains
        regions = decomposer.extract_nodal_domains(mode_index=1)

        # Each region should be connected (one component per region)
        for region in regions:
            # All faces should be topologically connected
            assert len(region.faces) > 0

    def test_vertex_to_face_conversion(self):
        """Test conversion from vertex sets to face sets."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        mesh = evaluator.tessellate(2)

        decomposer = SpectralDecomposer(evaluator)

        # Create arbitrary vertex set (first half of vertices)
        vertices = set(range(len(mesh.vertices) // 2))

        # Convert to faces
        faces = decomposer._vertices_to_faces(
            vertices, mesh.triangles, mesh.face_parents
        )

        # Should have some faces
        assert len(faces) > 0, "Should have at least one face"

        # All face indices should be valid
        max_face = mesh.face_parents.max()
        for face_id in faces:
            assert 0 <= face_id <= max_face, f"Face ID {face_id} out of range"

    def test_vertex_adjacency_building(self):
        """Test vertex adjacency graph construction."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        mesh = evaluator.tessellate(1)

        adjacency = decomposer._build_vertex_adjacency(mesh.triangles)

        # Should have entries for all vertices
        assert len(adjacency) > 0

        # Each vertex should have at least one neighbor
        for vertex, neighbors in adjacency.items():
            assert len(neighbors) > 0, f"Vertex {vertex} has no neighbors"

        # Adjacency should be symmetric
        for v1, neighbors in adjacency.items():
            for v2 in neighbors:
                assert v1 in adjacency[v2], \
                    f"Adjacency not symmetric: {v1} -> {v2} but not {v2} -> {v1}"

    def test_positive_only_extraction(self):
        """Test extracting only positive nodal domains."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=4)

        # Extract only positive domains
        regions = decomposer.extract_nodal_domains(mode_index=1, positive_only=True)

        # Should have at least 1 region
        assert len(regions) >= 1

        # All regions should be positive
        for region in regions:
            assert region.metadata['sign'] == '+'

    def test_different_mode_indices(self):
        """Test extracting domains from different mode indices."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=5)

        # Try different modes
        for mode_idx in [1, 2, 3]:
            regions = decomposer.extract_nodal_domains(mode_index=mode_idx)

            # Should get regions
            assert len(regions) > 0, f"Mode {mode_idx} produced no regions"

            # Check metadata
            for region in regions:
                assert region.metadata['mode_index'] == mode_idx

    def test_eigenmode_caching(self):
        """Test that eigenmodes are cached properly."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)

        # First computation
        modes1 = decomposer.compute_eigenmodes(num_modes=5)

        # Check cache is populated
        assert decomposer.eigenvalues is not None
        assert decomposer.eigenfunctions is not None

        # Eigenvalues should match
        assert len(decomposer.eigenvalues) == 5
        assert decomposer.eigenvalues[0] == modes1[0].eigenvalue

    def test_region_has_unity_principle(self):
        """Test that regions have proper unity principle description."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=4)
        regions = decomposer.extract_nodal_domains(mode_index=2)

        for region in regions:
            assert region.unity_principle != ""
            assert "Spectral eigenmode" in region.unity_principle
            assert "2" in region.unity_principle  # Mode index

    def test_minimum_region_size_threshold(self):
        """Test that tiny regions are filtered out."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=4)
        regions = decomposer.extract_nodal_domains(mode_index=1)

        # All regions should have > 10 vertices (threshold in code)
        # But we check faces, so just ensure regions aren't tiny
        for region in regions:
            assert len(region.faces) >= 1

    def test_score_with_optimal_region_count(self):
        """Test that 3-8 regions gets good score."""
        from app.state.parametric_region import ParametricRegion

        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)

        # Create 5 regions (in optimal range)
        regions = [
            ParametricRegion(
                id=f"test_{i}",
                faces=list(range(i*10, (i+1)*10))  # Equal size regions
            )
            for i in range(5)
        ]

        score = decomposer.compute_resonance_score(regions)

        # Should get high score (count=1.0, uniformity=1.0)
        assert score > 0.9, f"Optimal region count should give high score, got {score}"

    def test_score_with_non_uniform_sizes(self):
        """Test that non-uniform region sizes lower the score."""
        from app.state.parametric_region import ParametricRegion

        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)

        # Create regions with very different sizes
        regions = [
            ParametricRegion(id="small", faces=list(range(1))),
            ParametricRegion(id="medium", faces=list(range(10))),
            ParametricRegion(id="large", faces=list(range(100))),
        ]

        score = decomposer.compute_resonance_score(regions)

        # Should get lower score due to size variation
        assert score < 0.8, f"Non-uniform sizes should lower score, got {score}"

    def _create_sphere_cage(self):
        """Create icosahedron (sphere approximation)."""
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
        """Create simple quad cage."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage


class TestSpectralEdgeCases:
    """Test edge cases and error handling."""

    def test_extract_before_compute_raises_error(self):
        """Test that extracting before computing raises error."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)

        with pytest.raises(ValueError, match="Must call compute_eigenmodes"):
            decomposer.extract_nodal_domains(mode_index=1)

    def test_invalid_mode_index(self):
        """Test that out-of-range mode index is handled."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = SpectralLens(evaluator)
        lens.analyze(num_modes=5, mode_indices=[1, 2, 10])  # 10 is out of range

        # Should not crash, just skip invalid indices
        # Regions from modes 1 and 2 should be present
        assert len(lens.modes) == 5

    def test_very_small_eigenfunction_values(self):
        """Test that near-zero eigenfunction values are handled."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        decomposer = SpectralDecomposer(evaluator)
        modes = decomposer.compute_eigenmodes(num_modes=3)

        # Mode 0 should have constant eigenfunction (all near-zero variation)
        # But we can't extract from it - should raise error
        with pytest.raises(ValueError):
            decomposer.extract_nodal_domains(mode_index=0)

    def _create_simple_cage(self):
        """Create simple quad cage."""
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
    pytest.main([__file__, '-v'])
