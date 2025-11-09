"""
Lens Manager - Unified Interface for Mathematical Lenses

Provides coordinated access to multiple mathematical analysis lenses:
- Differential (curvature-based) - Day 4
- Spectral (eigenfunction-based) - Day 5
- Flow, Morse, Thermal (future)

Each lens reveals different aspects of the form's mathematical structure.
The manager allows switching between lenses, comparing results, and finding
the best decomposition for a given form.

Author: Agent 38, Ceramic Mold Analyzer
Date: November 2025
"""

from enum import Enum
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass

try:
    import cpp_core
except ImportError:
    cpp_core = None

from app.state.parametric_region import ParametricRegion

# Import available lenses
try:
    from app.analysis.differential_lens import DifferentialLens
    DIFFERENTIAL_AVAILABLE = True
except ImportError:
    DIFFERENTIAL_AVAILABLE = False

try:
    from app.analysis.spectral_lens import SpectralLens
    SPECTRAL_AVAILABLE = True
except (ImportError, AttributeError):
    # AttributeError can occur if cpp_core bindings are incomplete
    SPECTRAL_AVAILABLE = False


class LensType(Enum):
    """Available mathematical lenses."""
    DIFFERENTIAL = "differential"  # Curvature-based
    SPECTRAL = "spectral"          # Eigenfunction-based
    FLOW = "flow"                  # Future
    MORSE = "morse"                # Future
    THERMAL = "thermal"            # Future


@dataclass
class LensResult:
    """Results from analyzing with a specific lens."""
    lens_type: LensType
    regions: List[ParametricRegion]
    resonance_score: float
    computation_time: float  # seconds
    metadata: Dict[str, Any]


class LensManager:
    """
    Unified interface for all mathematical lenses.

    Manages lens selection, analysis, and result comparison.
    """

    def __init__(self, evaluator: 'cpp_core.SubDEvaluator'):
        """
        Initialize lens manager.

        Args:
            evaluator: Initialized SubDEvaluator with control cage
        """
        if cpp_core is None:
            raise RuntimeError("cpp_core module not available")

        if not evaluator.is_initialized():
            raise ValueError("SubDEvaluator must be initialized with control cage")

        self.evaluator = evaluator

        # Initialize available lenses
        self.lenses = {}

        if DIFFERENTIAL_AVAILABLE:
            self.lenses[LensType.DIFFERENTIAL] = DifferentialLens(evaluator)

        if SPECTRAL_AVAILABLE:
            self.lenses[LensType.SPECTRAL] = SpectralLens(evaluator)

        self.current_lens: Optional[LensType] = None
        self.analysis_results: Dict[LensType, List[ParametricRegion]] = {}
        self._results: Dict[LensType, LensResult] = {}  # Full result objects with metadata

    def analyze_with_lens(self,
                         lens_type: LensType,
                         params: Optional[Dict[str, Any]] = None,
                         force_recompute: bool = False,
                         **parameters) -> List[ParametricRegion]:
        """
        Run analysis with specified lens.

        Args:
            lens_type: Which lens to use
            params: Lens-specific parameters as dictionary (alternative to **parameters)
            force_recompute: If True, recompute even if cached
            **parameters: Lens-specific parameters as kwargs

        Returns:
            List of discovered regions
        """
        import time

        # Check cache first
        if not force_recompute and lens_type in self._results:
            return self._results[lens_type].regions

        lens = self.lenses.get(lens_type)
        if not lens:
            raise NotImplementedError(f"Lens {lens_type} not yet implemented")

        # Merge params and parameters
        all_params = {**(params or {}), **parameters}

        # Time the analysis
        start_time = time.time()

        # Run analysis - handle different lens interfaces
        if lens_type == LensType.DIFFERENTIAL:
            # DifferentialLens uses discover_regions(pinned_faces)
            pinned_faces = all_params.get('pinned_faces', None)
            regions = lens.discover_regions(pinned_faces=pinned_faces)
        elif lens_type == LensType.SPECTRAL:
            # SpectralLens uses analyze(num_modes, mode_indices)
            regions = lens.analyze(**all_params)
        else:
            # Future lenses - try generic analyze()
            if hasattr(lens, 'analyze'):
                regions = lens.analyze(**all_params)
            else:
                raise NotImplementedError(f"Lens {lens_type} has no known interface")

        computation_time = time.time() - start_time

        # Compute resonance score
        if regions:
            unity_scores = [r.unity_strength for r in regions if hasattr(r, 'unity_strength')]
            resonance_score = sum(unity_scores) / len(unity_scores) if unity_scores else 0.5
        else:
            resonance_score = 0.0

        # Create LensResult object
        result = LensResult(
            lens_type=lens_type,
            regions=regions,
            resonance_score=resonance_score,
            computation_time=computation_time,
            metadata={
                'num_regions': len(regions),
                'params': all_params
            }
        )

        # Cache results
        self.analysis_results[lens_type] = regions
        self._results[lens_type] = result
        self.current_lens = lens_type

        return regions

    def compare_lenses(self) -> Dict[LensType, float]:
        """
        Compare resonance scores across all lenses.

        Returns:
            {lens_type: resonance_score}
        """
        scores = {}
        for lens_type, regions in self.analysis_results.items():
            if regions:
                # Use average unity_strength across all regions
                unity_scores = [r.unity_strength for r in regions]
                scores[lens_type] = sum(unity_scores) / len(unity_scores)

        return scores

    def get_best_lens(self) -> Optional[LensType]:
        """Return lens with highest resonance score."""
        scores = self.compare_lenses()
        if not scores:
            return None

        return max(scores.keys(), key=lambda k: scores[k])

    def get_result(self, lens_type: LensType) -> Optional[LensResult]:
        """Get cached result for a specific lens."""
        return self._results.get(lens_type)

    def clear_cache(self):
        """Clear all cached analysis results."""
        self.analysis_results.clear()
        self._results.clear()

    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get summary of all cached analyses.

        Returns:
            Dictionary with statistics and comparisons
        """
        if not self._results:
            return {'status': 'no_analyses_cached'}

        summary = {
            'num_lenses_analyzed': len(self._results),
            'lenses': {}
        }

        for lens_type, result in self._results.items():
            summary['lenses'][lens_type.value] = {
                'num_regions': len(result.regions),
                'resonance_score': result.resonance_score,
                'computation_time': result.computation_time,
                'metadata': result.metadata
            }

        # Add best lens
        best = self.get_best_lens()
        if best:
            summary['best_lens'] = best.value
            summary['best_score'] = self._results[best].resonance_score

        return summary

    @property
    def differential_lens(self):
        """Access to differential lens for direct manipulation if needed."""
        return self.lenses.get(LensType.DIFFERENTIAL)
