# Agent 35: Spectral Decomposition

**Day**: 5
**Phase**: Phase 1a - Mathematical Analysis
**Duration**: 5-6 hours
**Estimated Cost**: $5-9 (90K tokens, Sonnet)

---

## Mission

Implement spectral decomposition using Laplace-Beltrami eigenfunctions to discover natural region boundaries via nodal domains.

---

## Context

You are implementing the **Spectral Lens** - the second mathematical lens (after Differential/curvature). This lens reveals the surface's natural vibration modes through eigenfunction analysis.

**Mathematical Principle**:
- Eigenfunctions of Laplace-Beltrami operator are like "modes of vibration"
- Zero-crossings (nodal lines) of eigenfunctions create natural boundaries
- Different eigenmodes reveal different structural patterns
- Forms an orthogonal basis for analyzing surface geometry

**From v5.0 Specification (§3.1.1)**:
> "Reveals natural vibration modes of the surface. Regions form at eigenfunction nodal lines. Produces aesthetically balanced decompositions. May generate non-convex regions requiring convexity post-processing."

**Dependencies**:
- Agent 34: LaplacianBuilder (provides L and A matrices)
- Day 3: ParametricRegion (to store discovered regions)
- Day 1-2: SubDEvaluator (for face topology)
- scipy.sparse.linalg for eigenvalue solving

---

## Deliverables

**Files to Create**:
1. `app/analysis/spectral_decomposition.py` (main implementation)
2. `app/analysis/spectral_lens.py` (lens interface)
3. `tests/test_spectral_decomposition.py` (comprehensive tests)

---

## Requirements

### 1. Spectral Decomposition Engine

```python
# app/analysis/spectral_decomposition.py

import numpy as np
from scipy.sparse.linalg import eigsh
from scipy import sparse
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

import cpp_core
from app.analysis.laplacian import LaplacianBuilder, build_normalized_laplacian
from app.state.parametric_region import ParametricRegion, ParametricCurve


@dataclass
class EigenMode:
    """Single eigenmode of the Laplacian."""
    eigenvalue: float
    eigenfunction: np.ndarray  # Per-vertex values
    index: int  # Mode number (0-indexed)
    multiplicity: int = 1  # Eigenvalue multiplicity


class SpectralDecomposer:
    """
    Discover regions using Laplace-Beltrami eigenfunction analysis.

    Implements the Spectral Lens from v5.0 specification (§3.1.1).
    """

    def __init__(self, evaluator: cpp_core.SubDEvaluator):
        """
        Args:
            evaluator: C++ SubDEvaluator for exact limit surface
        """
        self.evaluator = evaluator
        self.laplacian_builder = LaplacianBuilder(evaluator)

        # Cached eigendecomposition
        self.eigenvalues: Optional[np.ndarray] = None
        self.eigenfunctions: Optional[np.ndarray] = None
        self.tessellation_level: int = 3

    def compute_eigenmodes(self,
                          num_modes: int = 10,
                          tessellation_level: int = 3) -> List[EigenMode]:
        """
        Compute first k eigenmodes of Laplace-Beltrami operator.

        Args:
            num_modes: Number of eigenmodes to compute
            tessellation_level: Subdivision level for sampling

        Returns:
            List of EigenMode objects sorted by eigenvalue
        """
        # Build Laplacian
        L, A = self.laplacian_builder.build_laplacian(tessellation_level)

        # Normalize for better conditioning
        L_norm = build_normalized_laplacian(L, A)

        # Solve eigenvalue problem: L φ = λ φ
        # Note: eigsh finds smallest by magnitude
        # Laplacian is negative semi-definite, so negate
        eigenvalues, eigenfunctions = eigsh(
            -L_norm,
            k=num_modes,
            which='SM',  # Smallest magnitude
            maxiter=10000
        )

        # Negate back eigenvalues
        eigenvalues = -eigenvalues

        # Sort by eigenvalue (should already be sorted, but ensure)
        sort_idx = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[sort_idx]
        eigenfunctions = eigenfunctions[:, sort_idx]

        # Cache results
        self.eigenvalues = eigenvalues
        self.eigenfunctions = eigenfunctions
        self.tessellation_level = tessellation_level

        # Create EigenMode objects
        modes = []
        for i in range(num_modes):
            mode = EigenMode(
                eigenvalue=eigenvalues[i],
                eigenfunction=eigenfunctions[:, i],
                index=i
            )
            modes.append(mode)

        # Detect multiplicities (eigenvalues within tolerance)
        self._detect_multiplicities(modes, tol=1e-3)

        return modes

    def _detect_multiplicities(self, modes: List[EigenMode], tol: float = 1e-3):
        """
        Detect and mark eigenvalue multiplicities.

        For sphere: λ₁=λ₂=λ₃ (3-fold), λ₄=...=λ₈ (5-fold), etc.
        """
        for i, mode in enumerate(modes):
            # Count modes with similar eigenvalue
            count = sum(1 for m in modes
                       if abs(m.eigenvalue - mode.eigenvalue) < tol)
            mode.multiplicity = count

    def extract_nodal_domains(self,
                             mode_index: int,
                             positive_only: bool = False) -> List[ParametricRegion]:
        """
        Extract nodal domains from eigenfunction zero-crossings.

        Nodal domains are connected regions where eigenfunction has same sign.

        Args:
            mode_index: Which eigenmode to analyze (0 = constant, skip)
            positive_only: If True, only extract positive domains

        Returns:
            List of ParametricRegion objects
        """
        if mode_index == 0:
            raise ValueError("Mode 0 is constant function, has no nodal domains")

        if self.eigenfunctions is None:
            raise ValueError("Must call compute_eigenmodes() first")

        eigenfunction = self.eigenfunctions[:, mode_index]

        # Get tessellation (for connectivity)
        mesh = self.evaluator.tessellate(self.tessellation_level)
        triangles = mesh.triangles
        face_parents = mesh.face_parents

        # Classify vertices by sign
        vertex_signs = np.sign(eigenfunction)
        vertex_signs[np.abs(eigenfunction) < 1e-6] = 0  # Near-zero → boundary

        # Find connected components of same-sign regions
        regions = self._find_connected_components(
            vertex_signs, triangles, face_parents, positive_only
        )

        return regions

    def _find_connected_components(self,
                                   vertex_signs: np.ndarray,
                                   triangles: np.ndarray,
                                   face_parents: np.ndarray,
                                   positive_only: bool) -> List[ParametricRegion]:
        """
        Find connected regions of same-sign vertices.

        Uses flood-fill on triangle mesh to identify connected components.
        """
        n_vertices = len(vertex_signs)
        visited = np.zeros(n_vertices, dtype=bool)
        regions = []

        for start_vertex in range(n_vertices):
            if visited[start_vertex]:
                continue

            sign = vertex_signs[start_vertex]

            # Skip zero (boundary) vertices
            if sign == 0:
                visited[start_vertex] = True
                continue

            # Skip negative regions if positive_only
            if positive_only and sign < 0:
                visited[start_vertex] = True
                continue

            # Flood-fill to find connected component
            component_verts = self._flood_fill(
                start_vertex, vertex_signs, triangles, visited, sign
            )

            if len(component_verts) > 10:  # Minimum region size threshold
                # Convert vertex set to face set
                region_faces = self._vertices_to_faces(
                    component_verts, triangles, face_parents
                )

                # Create ParametricRegion
                region = ParametricRegion(
                    faces=list(region_faces),
                    boundary=[],  # TODO: Extract boundary curves
                    generation_method="spectral",
                    generation_parameters={
                        'mode_index': face_parents[0],  # Placeholder
                        'sign': '+' if sign > 0 else '-'
                    }
                )
                regions.append(region)

        return regions

    def _flood_fill(self,
                   start: int,
                   vertex_signs: np.ndarray,
                   triangles: np.ndarray,
                   visited: np.ndarray,
                   target_sign: int) -> set:
        """
        Flood-fill to find connected component of same-sign vertices.

        Args:
            start: Starting vertex index
            vertex_signs: Sign of eigenfunction at each vertex
            triangles: Triangle connectivity
            visited: Visited mask (modified in-place)
            target_sign: Sign to match (+1 or -1)

        Returns:
            Set of vertex indices in connected component
        """
        # Build adjacency graph (vertex → neighbor vertices)
        adjacency = self._build_vertex_adjacency(triangles)

        # BFS flood fill
        queue = [start]
        component = {start}
        visited[start] = True

        while queue:
            v = queue.pop(0)

            # Visit neighbors
            for neighbor in adjacency.get(v, []):
                if visited[neighbor]:
                    continue

                # Same sign and not zero?
                if vertex_signs[neighbor] == target_sign:
                    visited[neighbor] = True
                    queue.append(neighbor)
                    component.add(neighbor)

        return component

    def _build_vertex_adjacency(self, triangles: np.ndarray) -> Dict[int, List[int]]:
        """
        Build vertex→neighbors adjacency graph from triangles.
        """
        adjacency = {}

        for tri in triangles:
            i, j, k = tri

            # Add edges
            for v1, v2 in [(i,j), (j,k), (k,i)]:
                if v1 not in adjacency:
                    adjacency[v1] = []
                if v2 not in adjacency[v1]:
                    adjacency[v1].append(v2)

                if v2 not in adjacency:
                    adjacency[v2] = []
                if v1 not in adjacency[v2]:
                    adjacency[v2].append(v1)

        return adjacency

    def _vertices_to_faces(self,
                          vertices: set,
                          triangles: np.ndarray,
                          face_parents: np.ndarray) -> set:
        """
        Convert vertex set to set of SubD faces.

        A triangle belongs to region if majority of vertices are in the set.
        """
        face_set = set()

        for tri_idx, tri in enumerate(triangles):
            # Count vertices in region
            count = sum(1 for v in tri if v in vertices)

            # Majority voting
            if count >= 2:
                parent_face = face_parents[tri_idx]
                face_set.add(parent_face)

        return face_set

    def compute_resonance_score(self, regions: List[ParametricRegion]) -> float:
        """
        Compute resonance score for a decomposition (0-1).

        Higher score = decomposition aligns well with form's natural structure.

        Scoring criteria:
        - Region count balance (3-8 regions ideal)
        - Size uniformity (similar region sizes)
        - Convexity (more convex = better)
        - Boundary smoothness
        """
        if not regions:
            return 0.0

        # Count score (3-8 regions = optimal)
        num_regions = len(regions)
        if num_regions < 3:
            count_score = num_regions / 3.0
        elif num_regions <= 8:
            count_score = 1.0
        else:
            count_score = max(0.0, 1.0 - (num_regions - 8) / 10.0)

        # Size uniformity score
        sizes = [len(r.faces) for r in regions]
        mean_size = np.mean(sizes)
        std_size = np.std(sizes)
        uniformity_score = 1.0 - min(1.0, std_size / (mean_size + 1))

        # Weighted combination
        resonance = 0.6 * count_score + 0.4 * uniformity_score

        return float(np.clip(resonance, 0.0, 1.0))
```

---

### 2. Spectral Lens Interface

```python
# app/analysis/spectral_lens.py

from typing import List
import cpp_core
from app.state.parametric_region import ParametricRegion
from app.analysis.spectral_decomposition import SpectralDecomposer, EigenMode


class SpectralLens:
    """
    Mathematical lens using spectral (eigenfunction) analysis.

    Implements v5.0 spec §3.1.1 Spectral Lens.
    """

    def __init__(self, evaluator: cpp_core.SubDEvaluator):
        self.evaluator = evaluator
        self.decomposer = SpectralDecomposer(evaluator)
        self.modes: List[EigenMode] = []

    def analyze(self,
                num_modes: int = 10,
                mode_indices: List[int] = None) -> List[ParametricRegion]:
        """
        Discover regions using spectral analysis.

        Args:
            num_modes: Number of eigenmodes to compute
            mode_indices: Which modes to use (default: [1,2,3])

        Returns:
            List of discovered ParametricRegion objects
        """
        # Compute eigenmodes
        self.modes = self.decomposer.compute_eigenmodes(num_modes)

        # Default: use first non-trivial modes
        if mode_indices is None:
            mode_indices = [1, 2, 3]

        # Extract regions from each mode
        all_regions = []
        for mode_idx in mode_indices:
            if mode_idx >= len(self.modes):
                break

            regions = self.decomposer.extract_nodal_domains(
                mode_idx, positive_only=False
            )
            all_regions.extend(regions)

        # Compute resonance score
        resonance = self.decomposer.compute_resonance_score(all_regions)

        # Store resonance with regions
        for region in all_regions:
            region.resonance_score = resonance

        return all_regions

    def get_eigenmode(self, index: int) -> EigenMode:
        """Get specific eigenmode."""
        if not self.modes:
            raise ValueError("Must call analyze() first")
        return self.modes[index]
```

---

## Testing

**Test File**: `tests/test_spectral_decomposition.py`

```python
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
        assert modes[0].eigenvalue < 0.01

        # Eigenvalues should be ascending
        for i in range(len(modes) - 1):
            assert modes[i].eigenvalue <= modes[i+1].eigenvalue

        # Eigenfunctions should be normalized
        for mode in modes:
            norm = np.linalg.norm(mode.eigenfunction)
            assert 0.9 < norm < 1.1  # Approximately unit norm

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
        assert len(regions) >= 2

        # Each region should have faces
        for region in regions:
            assert len(region.faces) > 0

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
        assert 0.0 <= score <= 1.0

        # For reasonable decomposition, score should be > 0.3
        assert score > 0.3

    def test_spectral_lens_interface(self):
        """Test SpectralLens high-level interface."""
        cage = self._create_sphere_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        lens = SpectralLens(evaluator)
        regions = lens.analyze(num_modes=6, mode_indices=[1, 2])

        # Should discover regions
        assert len(regions) > 0

        # Regions should have metadata
        for region in regions:
            assert region.generation_method == "spectral"
            assert 'mode_index' in region.generation_parameters
            assert hasattr(region, 'resonance_score')

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
        assert len(faces) > 0

        # All face indices should be valid
        max_face = mesh.face_parents.max()
        for face_id in faces:
            assert 0 <= face_id <= max_face

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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## Success Criteria

- [ ] SpectralDecomposer implemented
- [ ] Eigenmode computation works (first λ ≈ 0)
- [ ] Nodal domain extraction functional
- [ ] Flood-fill connectivity correct
- [ ] Vertex→face conversion accurate
- [ ] Resonance scoring implemented
- [ ] Multiplicity detection working
- [ ] SpectralLens interface complete
- [ ] All tests pass
- [ ] Regions have metadata (method, parameters, score)

---

## Performance Notes

**Expected Performance**:
- Eigenvalue solve (k=10): <500ms for 10K vertices
- Nodal domain extraction: <100ms
- Total analysis: <1 second for typical forms

**Scaling**:
- Eigenvalue problem: O(k × n) where k=num_modes, n=vertices
- Flood-fill: O(n + e) where e=edges

---

## Integration Notes

**Used by**:
- Agent 36: Spectral visualization
- Agent 38: Lens manager (unified interface)
- Agent 39: Analysis tests

**Uses**:
- Agent 34: LaplacianBuilder
- Day 3: ParametricRegion

**File Placement**:
```
app/
├── analysis/
│   ├── laplacian.py              (Agent 34)
│   ├── spectral_decomposition.py ← YOU CREATE THIS
│   └── spectral_lens.py          ← YOU CREATE THIS
tests/
└── test_spectral_decomposition.py ← YOU CREATE THIS
```

---

## Common Issues and Solutions

**Issue**: "No regions discovered"
- **Fix**: Eigenfunction may be too smooth; try higher mode indices
- **Fix**: Adjust zero-crossing threshold (currently 1e-6)

**Issue**: "Too many tiny regions"
- **Fix**: Increase minimum region size threshold (currently 10 vertices)

**Issue**: "Regions not connected"
- **Fix**: Check flood-fill algorithm, verify adjacency graph

**Issue**: "Eigenvalue solve fails"
- **Fix**: Increase maxiter in eigsh()
- **Fix**: Check Laplacian construction (must be symmetric)

---

## Output Format

Provide:
1. Complete `spectral_decomposition.py` implementation
2. Complete `spectral_lens.py` interface
3. Complete `test_spectral_decomposition.py`
4. Test output showing all tests passing
5. Brief explanation of nodal domain extraction
6. Integration notes for Agent 36 (visualization)

---

**Ready to begin!**
