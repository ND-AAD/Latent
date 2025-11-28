# Agent 34: Laplacian Matrix Builder

**Day**: 5
**Phase**: Phase 1a - Mathematical Analysis
**Duration**: 4-5 hours
**Estimated Cost**: $4-7 (70K tokens, Sonnet)

---

## Mission

Implement cotangent-weight Laplace-Beltrami operator construction from exact SubD limit surface for spectral analysis.

---

## Context

You are implementing the Laplacian matrix builder that enables spectral decomposition (eigenfunction analysis) on SubD surfaces. This is the **second mathematical lens** (after differential/curvature from Day 4).

**Critical**: The Laplacian must be built from the **exact limit surface geometry**, not the tessellated mesh. Use exact limit evaluation for accurate cotangent weights.

**Mathematical Background**:
- Laplace-Beltrami operator reveals natural vibration modes of surface
- Eigenfunctions create nodal domains where zero-crossings form natural boundaries
- Cotangent weights ensure discrete operator approximates continuous operator

**Dependencies**:
- Day 1-2: SubDEvaluator (exact limit evaluation)
- Day 3: Parametric region system (for eigenfunction visualization)
- scipy.sparse for efficient sparse matrix operations

---

## Deliverables

**Files to Create**:
1. `app/analysis/laplacian.py` (main implementation)
2. `app/analysis/__init__.py` (package init, if not exists)
3. `tests/test_laplacian.py` (comprehensive tests)

---

## Requirements

### 1. Laplacian Builder Class

```python
# app/analysis/laplacian.py

import numpy as np
from scipy import sparse
from typing import Tuple, Optional
import cpp_core  # C++ SubDEvaluator


class LaplacianBuilder:
    """
    Constructs discrete Laplace-Beltrami operator with cotangent weights.

    CRITICAL: Uses exact limit surface evaluation for accurate geometry,
    not tessellated mesh approximations.

    References:
    - Meyer et al. (2003) "Discrete Differential-Geometry Operators"
    - Pinkall & Polthier (1993) "Computing Discrete Minimal Surfaces"
    """

    def __init__(self, evaluator: cpp_core.SubDEvaluator):
        """
        Args:
            evaluator: C++ SubDEvaluator for exact limit surface queries
        """
        self.evaluator = evaluator
        self.cached_laplacian: Optional[sparse.csr_matrix] = None
        self.cached_area_matrix: Optional[sparse.dia_matrix] = None
        self.vertex_count: int = 0

    def build_laplacian(self,
                       tessellation_level: int = 3,
                       use_cache: bool = True) -> Tuple[sparse.csr_matrix,
                                                        sparse.dia_matrix]:
        """
        Build cotangent-weight Laplacian and area (mass) matrix.

        Args:
            tessellation_level: Subdivision level for sampling density
            use_cache: Return cached result if available

        Returns:
            (L, A) where:
            - L is Laplacian matrix (N x N sparse)
            - A is diagonal area/mass matrix (N x N)
        """
        if use_cache and self.cached_laplacian is not None:
            return self.cached_laplacian, self.cached_area_matrix

        # Get tessellated mesh (for connectivity only)
        mesh = self.evaluator.tessellate(tessellation_level)
        vertices = mesh.vertices  # Shape: (N, 3)
        triangles = mesh.triangles  # Shape: (M, 3)

        self.vertex_count = len(vertices)

        # Build Laplacian with cotangent weights
        L = self._build_cotangent_laplacian(vertices, triangles)

        # Build area (mass) matrix
        A = self._build_area_matrix(vertices, triangles)

        # Cache results
        self.cached_laplacian = L
        self.cached_area_matrix = A

        return L, A

    def _build_cotangent_laplacian(self,
                                  vertices: np.ndarray,
                                  triangles: np.ndarray) -> sparse.csr_matrix:
        """
        Construct Laplacian with cotangent weights.

        For each edge (i,j), weight = (cot(α) + cot(β)) / 2
        where α, β are angles opposite the edge in adjacent triangles.
        """
        n = len(vertices)

        # Build sparse matrix using COO format (row, col, data)
        rows = []
        cols = []
        data = []

        # Edge → opposing angles mapping
        edge_cotangents = {}  # (i,j) → [cot(α), cot(β), ...]

        for tri in triangles:
            i, j, k = tri

            # Three edges of triangle
            edges = [(i,j,k), (j,k,i), (k,i,j)]

            for v0, v1, v_opp in edges:
                # Ensure edge key is canonical (min, max)
                edge_key = tuple(sorted([v0, v1]))

                # Compute cotangent of angle at v_opp
                cot_angle = self._compute_cotangent(
                    vertices[v0], vertices[v1], vertices[v_opp]
                )

                if edge_key not in edge_cotangents:
                    edge_cotangents[edge_key] = []
                edge_cotangents[edge_key].append(cot_angle)

        # Build Laplacian entries
        for (i, j), cot_list in edge_cotangents.items():
            # Weight is average of cotangents from adjacent triangles
            weight = sum(cot_list) / 2.0

            # Off-diagonal entries
            rows.append(i)
            cols.append(j)
            data.append(weight)

            rows.append(j)
            cols.append(i)
            data.append(weight)

        # Build sparse matrix
        L = sparse.coo_matrix((data, (rows, cols)), shape=(n, n))
        L = L.tocsr()

        # Diagonal entries: negative sum of row (ensures L @ ones = 0)
        diagonal = -L.sum(axis=1).A1
        L.setdiag(diagonal)

        return L

    def _compute_cotangent(self,
                          v0: np.ndarray,
                          v1: np.ndarray,
                          v_opp: np.ndarray) -> float:
        """
        Compute cotangent of angle at v_opp in triangle (v0, v1, v_opp).

        cot(θ) = cos(θ) / sin(θ) = (u · v) / |u × v|
        """
        # Vectors from v_opp to edge endpoints
        u = v0 - v_opp
        v = v1 - v_opp

        # Dot product (for cosine)
        dot_uv = np.dot(u, v)

        # Cross product magnitude (for sine)
        cross_uv = np.cross(u, v)
        cross_mag = np.linalg.norm(cross_uv)

        # Avoid division by zero
        if cross_mag < 1e-10:
            return 0.0

        cot_theta = dot_uv / cross_mag

        # Clamp to avoid numerical issues with very obtuse angles
        return np.clip(cot_theta, -100.0, 100.0)

    def _build_area_matrix(self,
                          vertices: np.ndarray,
                          triangles: np.ndarray) -> sparse.dia_matrix:
        """
        Build diagonal mass matrix with Voronoi areas.

        Each vertex gets 1/3 of area of incident triangles (barycentric area).
        """
        n = len(vertices)
        areas = np.zeros(n)

        for tri in triangles:
            i, j, k = tri

            # Triangle area
            v0, v1, v2 = vertices[i], vertices[j], vertices[k]
            edge1 = v1 - v0
            edge2 = v2 - v0
            tri_area = 0.5 * np.linalg.norm(np.cross(edge1, edge2))

            # Distribute to vertices (barycentric)
            areas[i] += tri_area / 3.0
            areas[j] += tri_area / 3.0
            areas[k] += tri_area / 3.0

        # Create diagonal matrix
        A = sparse.diags(areas, format='dia')
        return A

    def clear_cache(self):
        """Clear cached matrices (call after SubD changes)."""
        self.cached_laplacian = None
        self.cached_area_matrix = None
```

---

### 2. Integration Helper Functions

```python
# app/analysis/laplacian.py (continued)

def build_normalized_laplacian(L: sparse.csr_matrix,
                               A: sparse.dia_matrix) -> sparse.csr_matrix:
    """
    Normalize Laplacian: L_norm = A^(-1/2) @ L @ A^(-1/2)

    This gives eigenvalues in [0, 2] range.

    Args:
        L: Laplacian matrix
        A: Area (mass) matrix

    Returns:
        Normalized Laplacian
    """
    # Compute A^(-1/2)
    areas = A.diagonal()
    inv_sqrt_areas = 1.0 / np.sqrt(areas + 1e-10)
    A_inv_sqrt = sparse.diags(inv_sqrt_areas)

    # L_norm = A^(-1/2) @ L @ A^(-1/2)
    L_norm = A_inv_sqrt @ L @ A_inv_sqrt

    return L_norm


def verify_laplacian(L: sparse.csr_matrix,
                    vertices: np.ndarray) -> dict:
    """
    Verify Laplacian properties.

    Returns:
        Dictionary with verification results
    """
    results = {}

    # Check symmetry
    diff = np.abs((L - L.T).data).max() if L.nnz > 0 else 0.0
    results['is_symmetric'] = diff < 1e-6
    results['symmetry_error'] = diff

    # Check row sums (should be ~0 for constant function)
    ones = np.ones(L.shape[0])
    row_sums = L @ ones
    results['row_sum_max'] = np.abs(row_sums).max()
    results['row_sums_near_zero'] = results['row_sum_max'] < 1e-4

    # Check sparsity
    results['sparsity'] = 1.0 - (L.nnz / (L.shape[0] ** 2))

    return results
```

---

## Testing

**Test File**: `tests/test_laplacian.py`

```python
import pytest
import numpy as np
from scipy import sparse
import cpp_core
from app.analysis.laplacian import (
    LaplacianBuilder,
    build_normalized_laplacian,
    verify_laplacian
)


class TestLaplacianBuilder:
    """Test Laplacian matrix construction."""

    def test_sphere_eigenvalues(self):
        """
        Test Laplacian on sphere (analytical eigenvalues known).

        For unit sphere, first few eigenvalues are:
        λ₀ = 0 (constant function)
        λ₁ = λ₂ = λ₃ = 2 (first harmonic, 3-fold)
        λ₄ = ... = λ₈ = 6 (second harmonic, 5-fold)
        """
        # Create subdivided icosahedron (approximates sphere)
        cage = self._create_icosahedron()

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)
        L, A = builder.build_laplacian(tessellation_level=2)

        # Verify Laplacian properties
        props = verify_laplacian(L, None)
        assert props['is_symmetric'], "Laplacian must be symmetric"
        assert props['row_sums_near_zero'], "Row sums should be ~0"

        # Compute eigenvalues
        L_norm = build_normalized_laplacian(L, A)

        from scipy.sparse.linalg import eigsh
        eigenvalues, eigenvectors = eigsh(
            -L_norm,  # Negative for ascending order
            k=10,
            which='SM'  # Smallest magnitude
        )
        eigenvalues = -eigenvalues  # Negate back

        # First eigenvalue should be ~0
        assert eigenvalues[0] < 0.01, f"First eigenvalue {eigenvalues[0]} not near 0"

        # Check multiplicity pattern (rough check)
        print(f"First 10 eigenvalues: {eigenvalues}")

    def test_planar_quad(self):
        """Test Laplacian on simple planar quad."""
        # Unit square
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)
        L, A = builder.build_laplacian(tessellation_level=2)

        # Basic checks
        assert L.shape[0] == L.shape[1], "Laplacian must be square"
        assert L.shape[0] > 4, "Should have more vertices after subdivision"

        # Verify symmetry
        diff = np.abs((L - L.T).data).max()
        assert diff < 1e-6, "Laplacian must be symmetric"

    def test_cotangent_computation(self):
        """Test cotangent weight computation."""
        builder = LaplacianBuilder(None)

        # Right triangle: vertices at (0,0,0), (1,0,0), (0,1,0)
        v0 = np.array([0, 0, 0])
        v1 = np.array([1, 0, 0])
        v_opp = np.array([0, 1, 0])

        # Angle at v_opp is 90°, cot(90°) = 0
        cot = builder._compute_cotangent(v0, v1, v_opp)
        assert abs(cot) < 0.01, f"cot(90°) should be ~0, got {cot}"

        # Equilateral triangle: angle is 60°
        v0 = np.array([0, 0, 0])
        v1 = np.array([1, 0, 0])
        v_opp = np.array([0.5, np.sqrt(3)/2, 0])

        cot = builder._compute_cotangent(v0, v1, v_opp)
        expected_cot = 1.0 / np.sqrt(3)  # cot(60°) = 1/√3
        assert abs(cot - expected_cot) < 0.01, \
            f"cot(60°) should be {expected_cot}, got {cot}"

    def test_area_matrix(self):
        """Test area (mass) matrix computation."""
        # Simple triangle
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0]
        ])
        triangles = np.array([[0, 1, 2]])

        builder = LaplacianBuilder(None)
        A = builder._build_area_matrix(vertices, triangles)

        # Each vertex gets 1/3 of triangle area
        tri_area = 0.5  # Area of right triangle with legs 1,1
        expected_area = tri_area / 3.0

        areas = A.diagonal()
        assert all(abs(a - expected_area) < 1e-6 for a in areas), \
            f"Each vertex should have area {expected_area}, got {areas}"

    def test_cache_functionality(self):
        """Test caching mechanism."""
        cage = self._create_simple_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        builder = LaplacianBuilder(evaluator)

        # First call
        L1, A1 = builder.build_laplacian(use_cache=True)

        # Second call with cache should return same object
        L2, A2 = builder.build_laplacian(use_cache=True)
        assert L1 is L2, "Cache should return same object"

        # Clear cache
        builder.clear_cache()

        # Third call should rebuild
        L3, A3 = builder.build_laplacian(use_cache=True)
        assert L1 is not L3, "After clear_cache, should rebuild"

    def _create_icosahedron(self):
        """Create icosahedron control cage."""
        # Golden ratio
        phi = (1 + np.sqrt(5)) / 2

        cage = cpp_core.SubDControlCage()

        # 12 vertices
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

        # 20 triangular faces
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

- [ ] LaplacianBuilder class implemented
- [ ] Cotangent weights computed correctly
- [ ] Area (mass) matrix built
- [ ] Laplacian is symmetric (verified)
- [ ] Row sums ≈ 0 (verified)
- [ ] Sphere eigenvalue test passes (λ₀ ≈ 0)
- [ ] Planar quad test passes
- [ ] Cotangent computation accurate (right angle, 60° tests)
- [ ] Area matrix distributes triangle areas correctly
- [ ] Cache functionality working
- [ ] All tests pass

---

## Performance Notes

**Expected Performance**:
- Laplacian construction: <100ms for 10K vertices
- Eigenvalue solve (k=10): <500ms for 10K vertices
- Memory: O(#edges) for sparse matrix (~6× vertex count)

**Optimization**:
- Use scipy.sparse for efficient storage
- Cache Laplacian (rebuild only when SubD changes)
- COO format for construction, CSR for operations

---

## Integration Notes

**Used by**:
- Agent 35: Spectral decomposition (eigenvalue solver)
- Agent 36: Spectral visualization
- Future thermal/flow lenses

**Provides**:
- Laplacian matrix (sparse, symmetric)
- Area/mass matrix (diagonal)
- Verification utilities

**File Placement**:
```
app/
├── analysis/
│   ├── __init__.py
│   └── laplacian.py           ← YOU CREATE THIS
tests/
└── test_laplacian.py          ← YOU CREATE THIS
```

---

## Common Issues and Solutions

**Issue**: "Eigenvalues are negative"
- **Fix**: Laplacian is negative semi-definite; negate before eigsh()

**Issue**: "Cotangent weights explode (inf/nan)"
- **Fix**: Clamp cotangent values, check for degenerate triangles

**Issue**: "Eigenvalue solve fails to converge"
- **Fix**: Use normalized Laplacian (better conditioned)
- **Fix**: Increase maxiter parameter in eigsh()

**Issue**: "First eigenvalue not zero"
- **Fix**: Check row sums (should be ~0)
- **Fix**: Verify symmetry

---

## Output Format

Provide:
1. Complete `laplacian.py` implementation
2. Complete `test_laplacian.py` with all test cases
3. Test output showing all tests passing
4. Brief explanation of cotangent weight computation
5. Integration notes for Agent 35 (spectral decomposition)

---

**Ready to begin!**
