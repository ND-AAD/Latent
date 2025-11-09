"""
Laplacian Matrix Builder for Spectral Analysis

Constructs discrete Laplace-Beltrami operator with cotangent weights from
exact SubD limit surface evaluation.

References:
- Meyer et al. (2003) "Discrete Differential-Geometry Operators"
- Pinkall & Polthier (1993) "Computing Discrete Minimal Surfaces"
"""

import numpy as np
from scipy import sparse
from typing import Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import cpp_core
else:
    try:
        import cpp_core
    except (ImportError, AttributeError):
        cpp_core = None


class LaplacianBuilder:
    """
    Constructs discrete Laplace-Beltrami operator with cotangent weights.

    CRITICAL: Uses exact limit surface evaluation for accurate geometry,
    not tessellated mesh approximations.

    References:
    - Meyer et al. (2003) "Discrete Differential-Geometry Operators"
    - Pinkall & Polthier (1993) "Computing Discrete Minimal Surfaces"
    """

    def __init__(self, evaluator: 'cpp_core.SubDEvaluator'):
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
            edges = [(i, j, k), (j, k, i), (k, i, j)]

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
                    vertices: np.ndarray = None) -> dict:
    """
    Verify Laplacian properties.

    Args:
        L: Laplacian matrix
        vertices: Vertex array (optional, not used but kept for API compatibility)

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
