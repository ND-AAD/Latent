# Agent 38: Lens Integration Manager

**Day**: 5
**Phase**: Phase 1a - Mathematical Analysis
**Duration**: 3-4 hours
**Estimated Cost**: $4-6 (60K tokens, Sonnet)

---

## Mission

Create unified LensManager interface for coordinating multiple mathematical lenses (Differential and Spectral).

---

## Context

The system now has two lenses implemented:
- Day 4: Differential (curvature-based)
- Day 5: Spectral (eigenfunction-based)

Need unified interface for:
- Switching between lenses
- Comparing resonance scores
- Storing lens parameters with regions

**Dependencies**:
- Day 4: Differential lens
- Agent 35: Spectral lens

---

## Deliverables

1. `app/analysis/lens_manager.py` (unified interface)
2. `tests/test_lens_manager.py` (tests)

---

## Requirements

```python
# app/analysis/lens_manager.py

from enum import Enum
from typing import List, Dict, Optional
import cpp_core
from app.state.parametric_region import ParametricRegion
from app.analysis.spectral_lens import SpectralLens
# from app.analysis.differential_lens import DifferentialLens  # Day 4


class LensType(Enum):
    """Available mathematical lenses."""
    DIFFERENTIAL = "differential"  # Curvature-based
    SPECTRAL = "spectral"          # Eigenfunction-based
    FLOW = "flow"                  # Future
    MORSE = "morse"                # Future
    THERMAL = "thermal"            # Future


class LensManager:
    """
    Unified interface for all mathematical lenses.

    Manages lens selection, analysis, and result comparison.
    """

    def __init__(self, evaluator: cpp_core.SubDEvaluator):
        self.evaluator = evaluator

        # Initialize available lenses
        self.lenses = {
            LensType.SPECTRAL: SpectralLens(evaluator),
            # LensType.DIFFERENTIAL: DifferentialLens(evaluator),
        }

        self.current_lens: Optional[LensType] = None
        self.analysis_results: Dict[LensType, List[ParametricRegion]] = {}

    def analyze_with_lens(self,
                         lens_type: LensType,
                         **parameters) -> List[ParametricRegion]:
        """
        Run analysis with specified lens.

        Args:
            lens_type: Which lens to use
            **parameters: Lens-specific parameters

        Returns:
            List of discovered regions
        """
        lens = self.lenses.get(lens_type)
        if not lens:
            raise ValueError(f"Lens {lens_type} not available")

        # Run analysis
        regions = lens.analyze(**parameters)

        # Cache results
        self.analysis_results[lens_type] = regions
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
                # Use first region's score (all have same score)
                scores[lens_type] = regions[0].resonance_score

        return scores

    def get_best_lens(self) -> Optional[LensType]:
        """Return lens with highest resonance score."""
        scores = self.compare_lenses()
        if not scores:
            return None

        return max(scores.keys(), key=lambda k: scores[k])
```

---

## Success Criteria

- [ ] LensManager coordinates multiple lenses
- [ ] Lens switching works
- [ ] Resonance comparison functional
- [ ] Results cached by lens type
- [ ] Tests pass

---

**Ready to begin!**
