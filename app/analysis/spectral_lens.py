"""
Spectral Lens - Mathematical Lens Interface for Spectral Analysis

Provides high-level interface for spectral (eigenfunction) decomposition.

This lens reveals the surface's natural vibration modes through eigenfunction
analysis of the Laplace-Beltrami operator.

Author: Ceramic Mold Analyzer - Agent 35
Date: November 2025
"""

from typing import List
import cpp_core
from app.state.parametric_region import ParametricRegion
from app.analysis.spectral_decomposition import SpectralDecomposer, EigenMode


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
