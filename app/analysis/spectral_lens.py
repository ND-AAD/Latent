"""
Spectral Lens - Mathematical Lens Interface for Spectral Analysis

Provides high-level interface for spectral (eigenfunction) decomposition.

This lens reveals the surface's natural vibration modes through eigenfunction
analysis of the Laplace-Beltrami operator.

Author: Ceramic Mold Analyzer - Agent 35
Date: November 2025
"""

from typing import List, Dict, Tuple
import numpy as np
import cpp_core
from app.state.parametric_region import ParametricRegion
from app.analysis.spectral_decomposition import SpectralDecomposer, EigenMode
from app.analysis.nodal_extraction import (
    NodalLineExtractor,
    TessellationVertex,
    TessellationTriangle,
    extract_nodal_lines_from_eigenfunction,
    ParametricPoint,
    ParametricCurve
)


class SpectralLens:
    """
    Mathematical lens using spectral (eigenfunction) analysis.

    Implements v5.0 spec section 3.1.1 Spectral Lens.
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
            region.unity_strength = resonance

        return all_regions

    def get_eigenmode(self, index: int) -> EigenMode:
        """Get specific eigenmode."""
        if not self.modes:
            raise ValueError("Must call analyze() first")
        return self.modes[index]

    def extract_nodal_curves(
        self,
        eigenfunction_index: int = 1,
        threshold: float = 0.0
    ) -> List[ParametricCurve]:
        """
        Extract nodal lines from a specific eigenfunction.

        Args:
            eigenfunction_index: Which eigenfunction to use (0=first, 1=second, etc.)
            threshold: Value to extract (0.0 for nodal lines)

        Returns:
            List of nodal curves in parametric space
        """
        # Ensure eigenfunctions are computed
        if not self.modes:
            self.modes = self.decomposer.compute_eigenmodes(num_modes=10)

        if eigenfunction_index >= len(self.modes):
            raise ValueError(f"Eigenfunction {eigenfunction_index} not available")

        eigenfunction = self.modes[eigenfunction_index].eigenfunction

        # Get tessellation data
        vertices, triangles, parametric_coords = self._get_tessellation_with_params()

        # Extract nodal lines
        curves = extract_nodal_lines_from_eigenfunction(
            eigenfunction,
            vertices,
            triangles,
            parametric_coords
        )

        return curves

    def extract_all_nodal_curves(
        self,
        num_eigenfunctions: int = 5
    ) -> Dict[int, List[ParametricCurve]]:
        """
        Extract nodal lines from multiple eigenfunctions.

        Args:
            num_eigenfunctions: Number of eigenfunctions to process

        Returns:
            Dict mapping eigenfunction index to its nodal curves
        """
        result = {}

        for i in range(num_eigenfunctions):
            try:
                curves = self.extract_nodal_curves(eigenfunction_index=i)
                if curves:
                    result[i] = curves
            except (ValueError, IndexError):
                break

        return result

    def discover_regions_with_boundaries(
        self,
        num_eigenfunctions: int = 3
    ) -> List[dict]:
        """
        Discover regions and extract their boundary curves from nodal lines.

        Returns list of dicts with region info including boundary curves.
        """
        # Get base regions
        regions = self.analyze(num_modes=num_eigenfunctions)

        # Extract nodal lines from first few eigenfunctions
        all_curves = self.extract_all_nodal_curves(num_eigenfunctions)

        # TODO: Match curves to regions based on spatial relationship
        # For now, attach all curves from eigenfunction i to region i
        result = []
        for i in range(min(len(regions), num_eigenfunctions)):
            region = regions[i]
            curves = all_curves.get(i + 1, [])  # Skip mode 0 (constant)
            region_dict = {
                "id": region.id,
                "unity_principle": region.unity_principle,
                "resonance_score": region.unity_strength,
                "boundary_curves": [c.to_control_points() for c in curves],
                "eigenfunction_index": i + 1
            }
            result.append(region_dict)

        return result

    def _get_tessellation_with_params(self) -> Tuple[np.ndarray, np.ndarray, List[ParametricPoint]]:
        """
        Get tessellation with parametric coordinates.

        Returns:
            vertices: Nx3 array of vertex positions
            triangles: Mx3 array of triangle vertex indices
            parametric_coords: List of ParametricPoint for each vertex
        """
        # Get tessellation
        mesh = self.evaluator.tessellate(self.decomposer.tessellation_level)
        vertices = mesh.vertices
        triangles = mesh.triangles

        # Get parametric coordinates
        # TODO: The evaluator should provide parametric coords
        # For now, create dummy parametric coords based on mesh structure
        parametric_coords = []
        for i, vertex in enumerate(vertices):
            # Map to approximate (u,v) based on position
            # This is a placeholder - real implementation needs proper parametric mapping
            u = (vertex[0] + 1) / 2  # Normalize to [0,1]
            v = (vertex[1] + 1) / 2  # Normalize to [0,1]
            face_id = mesh.face_parents[min(i, len(mesh.face_parents) - 1)]
            parametric_coords.append(ParametricPoint(int(face_id), float(u), float(v)))

        return vertices, triangles, parametric_coords
