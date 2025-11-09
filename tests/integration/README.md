# Integration Tests for Analysis Pipeline

**Author**: Agent 39
**Date**: November 2025
**Status**: Ready to run once C++ bindings are built

## Overview

This directory contains comprehensive integration tests for the complete mathematical analysis pipeline, including:
- Differential lens (curvature-based region discovery)
- Spectral lens (eigenfunction-based region discovery) - when available
- LensManager unified interface
- Lens comparison and selection
- Performance verification

## Test Files

### test_analysis_pipeline.py
End-to-end tests for the complete analysis workflow:
- **16 tests** covering full pipeline integration
- Tests differential lens analysis from start to finish
- Tests caching, force recompute, and result storage
- Tests analysis on multiple geometries (cube, sphere, cylinder)
- Verifies performance targets (<2 seconds)
- Tests curvature field access and custom parameters

### test_lens_comparison.py
Tests for lens comparison and selection functionality:
- **17 tests** covering lens comparison system
- Tests single and multiple lens comparison
- Tests best lens selection algorithm
- Tests resonance score computation components
- Tests LensResult data structure
- Tests graceful handling of unimplemented lenses
- Verifies metadata completeness and computation time tracking

## Prerequisites

### C++ Bindings Must Be Built

These tests require fully functional C++ Python bindings. Before running:

```bash
# 1. Install OpenSubdiv (Day 0 requirement)
# On macOS:
brew install opensubdiv

# On Linux:
apt-get install libosd-dev

# 2. Build C++ module
cd cpp_core/build
cmake ..
make

# 3. Verify bindings are complete
python -c "import cpp_core; print(dir(cpp_core))"
# Should show: SubDControlCage, SubDEvaluator, Point3D, CurvatureAnalyzer, etc.
```

## Running Tests

### Run All Integration Tests
```bash
pytest tests/integration/ -v
```

### Run Specific Test File
```bash
pytest tests/integration/test_analysis_pipeline.py -v
pytest tests/integration/test_lens_comparison.py -v
```

### Run Single Test
```bash
pytest tests/integration/test_analysis_pipeline.py::TestAnalysisPipeline::test_end_to_end_differential -v
```

### Check Why Tests Are Skipping
```bash
pytest tests/integration/ -v --tb=short
# Will show: "cpp_core bindings incomplete" if bindings not built
```

## Current Status

**Tests Status**: ✅ All tests written and verified to skip gracefully
**Bindings Status**: ⚠️ C++ bindings not yet fully implemented
**Action Required**: Build C++ bindings with OpenSubdiv support

When C++ bindings are complete, all 33 tests should pass, verifying:
- ✅ End-to-end analysis pipeline
- ✅ Differential lens functionality
- ✅ LensManager interface
- ✅ Caching and performance
- ✅ Lens comparison logic
- ✅ Resonance scoring
- ✅ Multi-geometry support

## Test Coverage

### Analysis Pipeline Tests (16 tests)
1. `test_end_to_end_differential` - Complete differential analysis workflow
2. `test_end_to_end_spectral_stub` - Spectral lens placeholder
3. `test_lens_manager_initialization` - LensManager setup
4. `test_lens_manager_requires_initialized_evaluator` - Validation
5. `test_analysis_caching` - Result caching behavior
6. `test_force_recompute` - Cache bypass
7. `test_clear_cache` - Cache clearing
8. `test_get_result` - LensResult retrieval
9. `test_analysis_summary` - Summary generation
10. `test_parametric_region_properties` - Region data structure
11. `test_different_geometries` - Multi-geometry analysis
12. `test_performance_target` - Performance verification (<2s)
13. `test_curvature_field_access` - Curvature data access
14. `test_custom_parameters` - Parameter passing
15. `test_resonance_scoring` - Resonance computation
16. `test_region_unity_principle` - Unity principle descriptions

### Lens Comparison Tests (17 tests)
1. `test_single_lens_comparison` - Single lens baseline
2. `test_get_best_lens_single` - Best lens selection
3. `test_compare_lenses_default` - Default comparison
4. `test_lens_result_structure` - LensResult data structure
5. `test_comparison_with_parameters` - Parameterized comparison
6. `test_resonance_score_properties` - Score validation
7. `test_multiple_geometry_comparison` - Cross-geometry comparison
8. `test_analysis_summary_format` - Summary formatting
9. `test_comparison_caching_behavior` - Cache behavior
10. `test_region_count_scoring_component` - Region count scoring
11. `test_unity_strength_component` - Unity strength scoring
12. `test_size_balance_component` - Size balance scoring
13. `test_lens_type_enum` - LensType enum validation
14. `test_not_implemented_lenses` - Future lens handling
15. `test_comparison_skips_unimplemented` - Graceful skipping
16. `test_computation_time_tracking` - Time tracking
17. `test_metadata_completeness` - Metadata validation

## Success Criteria

All tests must pass with:
- ✅ Regions discovered for each geometry
- ✅ Resonance scores in [0, 1] range
- ✅ Analysis completes in <2 seconds
- ✅ All metadata fields present
- ✅ Caching works correctly
- ✅ Best lens selection functional

## Integration Notes for Future Agents

### For Agent 40+ (Day 6+)
When building on this analysis system:
1. Import LensManager from `app.analysis.lens_manager`
2. Use `LensType` enum for type-safe lens selection
3. Call `analyze_with_lens(LensType.DIFFERENTIAL)` for analysis
4. Access results via `get_result(lens_type)` for full metadata
5. Use `compare_lenses()` to evaluate multiple lenses

### Adding New Lenses
To add a new lens (e.g., Flow, Morse, Thermal):
1. Create lens class in `app/analysis/your_lens.py`
2. Implement `analyze(**params)` method returning `List[ParametricRegion]`
3. Add lens type to `LensType` enum in lens_manager.py
4. Update `LensManager.analyze_with_lens()` dispatch logic
5. Add tests following patterns in test_lens_comparison.py

### Spectral Lens Integration
When Agent 35 completes spectral analysis:
1. Uncomment spectral tests in test_analysis_pipeline.py
2. Update `test_end_to_end_spectral_stub` to test real spectral lens
3. Add spectral-specific tests (eigenmode validation, nodal domains)
4. Verify spectral lens integrates with LensManager

## Performance Targets

- **Differential analysis**: <2 seconds for typical forms
- **Spectral analysis**: <1 second for eigenmode computation (when available)
- **Lens comparison**: <5 seconds for all available lenses
- **Caching**: Second access should be <1ms

## Known Issues

None - tests are comprehensive and ready for use once bindings are built.

## References

- Task file: `docs/reference/api_sprint/agent_tasks/day_05/AGENT_39_analysis_tests.md`
- Differential lens: `app/analysis/differential_lens.py`
- LensManager: `app/analysis/lens_manager.py`
- ParametricRegion: `app/state/parametric_region.py`
