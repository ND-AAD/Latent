# Agent 39: Analysis Integration Tests

**Day**: 5
**Phase**: Phase 1a - Mathematical Analysis
**Duration**: 3-4 hours
**Estimated Cost**: $2-4 (60K tokens, Sonnet)

---

## Mission

Create comprehensive integration tests for complete analysis pipeline (Differential + Spectral lenses).

---

## Context

Final Day 5 agent ensures entire analysis system works end-to-end:
- Laplacian construction
- Spectral decomposition
- Differential decomposition (from Day 4)
- Lens comparison
- Region operations

**Dependencies**: All previous Day 4-5 agents

---

## Deliverables

1. `tests/integration/test_analysis_pipeline.py`
2. `tests/integration/test_lens_comparison.py`

---

## Requirements

```python
# tests/integration/test_analysis_pipeline.py

import pytest
import cpp_core
from app.analysis.lens_manager import LensManager, LensType


class TestAnalysisPipeline:
    """Integration tests for complete analysis pipeline."""

    def test_end_to_end_spectral(self):
        """Test complete spectral analysis workflow."""
        # Create geometry
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        # Run spectral analysis
        manager = LensManager(evaluator)
        regions = manager.analyze_with_lens(
            LensType.SPECTRAL,
            num_modes=6
        )

        # Verify results
        assert len(regions) > 0
        assert all(r.generation_method == "spectral" for r in regions)
        assert all(hasattr(r, 'resonance_score') for r in regions)

    def test_lens_comparison(self):
        """Test comparing multiple lenses."""
        cage = self._create_test_cage()
        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        manager = LensManager(evaluator)

        # Analyze with both lenses
        spectral_regions = manager.analyze_with_lens(LensType.SPECTRAL)
        # diff_regions = manager.analyze_with_lens(LensType.DIFFERENTIAL)

        # Compare scores
        scores = manager.compare_lenses()
        assert LensType.SPECTRAL in scores

        # Get best lens
        best = manager.get_best_lens()
        assert best is not None

    def _create_test_cage(self):
        """Create test geometry."""
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]
        return cage
```

---

## Success Criteria

- [ ] End-to-end spectral test passes
- [ ] Lens comparison test passes
- [ ] All Day 5 components integrate correctly
- [ ] Performance acceptable (<2 seconds total)

---

**Ready to begin!**
