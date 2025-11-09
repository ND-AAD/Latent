"""
Spectral Decomposition - Eigenfunction Analysis for Region Discovery

Implements the Spectral Lens from v5.0 specification (§3.1.1).

Mathematical Principle:
- Eigenfunctions of Laplace-Beltrami operator are like "modes of vibration"
- Zero-crossings (nodal lines) of eigenfunctions create natural boundaries
- Different eigenmodes reveal different structural patterns
- Forms an orthogonal basis for analyzing surface geometry

Author: Ceramic Mold Analyzer - Agent 35
Date: November 2025
"""

import numpy as np
from scipy.sparse.linalg import eigsh
from scipy import sparse
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import uuid

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
            vertex_signs, triangles, face_parents, positive_only, mode_index
        )

        return regions

    def _find_connected_components(self,
                                   vertex_signs: np.ndarray,
                                   triangles: np.ndarray,
                                   face_parents: np.ndarray,
                                   positive_only: bool,
                                   mode_index: int) -> List[ParametricRegion]:
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
                    id=f"spectral_mode{mode_index}_{'pos' if sign > 0 else 'neg'}_{uuid.uuid4().hex[:8]}",
                    faces=list(region_faces),
                    boundary=[],  # TODO: Extract boundary curves
                    unity_principle=f"Spectral eigenmode {mode_index} ({'positive' if sign > 0 else 'negative'} domain)",
                    unity_strength=0.0,  # Will be set by compute_resonance_score
                    metadata={
                        'generation_method': 'spectral',
                        'mode_index': mode_index,
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
