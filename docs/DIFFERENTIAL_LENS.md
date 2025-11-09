# Differential Lens - First Mathematical Lens

**Status**: ✅ Complete (Agent 32, Day 4 Evening)

## Overview

The **Differential Lens** is the first mathematical lens implemented for the Ceramic Mold Analyzer. It discovers natural mold decomposition regions based on differential geometry properties computed from the **exact SubD limit surface** (not discretized meshes).

This implementation validates the entire parametric region architecture and the lossless-until-fabrication principle.

## Mathematical Foundation

### Curvature Analysis

The differential lens uses exact curvature computation from the SubD limit surface:

- **Principal curvatures** κ₁, κ₂: Maximum and minimum normal curvatures at each point
- **Gaussian curvature** K = κ₁ × κ₂: Intrinsic curvature (positive = bowl-like, negative = saddle-like)
- **Mean curvature** H = (κ₁ + κ₂) / 2: Extrinsic curvature (sign indicates convex/concave)

All curvatures are computed using exact second derivatives from the limit surface via the C++ `CurvatureAnalyzer`.

### Surface Classification

Faces are classified based on their curvature signatures:

| Type | Gaussian K | Mean H | Example |
|------|-----------|--------|---------|
| **Elliptic** | K > 0 | Any | Sphere, bowl (convex/concave) |
| **Hyperbolic** | K < 0 | Any | Saddle, hyperboloid (anticlastic) |
| **Parabolic** | K ≈ 0 | \|H\| > 0 | Cylinder, cone (developable) |
| **Planar** | K ≈ 0 | H ≈ 0 | Flat plane |

### Ridge and Valley Detection

- **Ridges**: Local maxima of \|κ₁\| (maximum principal curvature magnitude)
- **Valleys**: Local minima of \|κ₁\| (or local maxima of \|κ₂\|)

These features serve as natural boundaries between regions.

## Algorithm

### 1. Curvature Sampling

For each control face:
- Sample 3×3 grid of (u,v) points in parameter space
- Evaluate exact limit surface position and second derivatives
- Compute curvature tensor at each sample point
- Aggregate statistics (mean, std, min, max)

**Key**: Uses `CurvatureAnalyzer.compute_curvature(evaluator, face_id, u, v)` for exact computation.

### 2. Face Classification

Classify each face based on aggregated curvature:
- Compute mean Gaussian curvature K̄ and mean curvature H̄
- Apply thresholds to determine elliptic/hyperbolic/parabolic/planar

### 3. Ridge/Valley Detection

- Extract \|κ₁\| for all faces
- Use percentile thresholds (default: top 10% = ridges, bottom 10% = valleys)
- Mark candidate boundary features

### 4. Region Growing

Start from faces with highest curvature magnitude (seeds):

1. Create region from seed face
2. Grow by adding adjacent faces with compatible curvature:
   - Same classification type
   - Similar K and H values (within tolerance)
3. Continue until no more compatible neighbors
4. Repeat for remaining unassigned faces

### 5. Small Region Merging

Merge regions smaller than `min_region_size` into best-matching neighbors based on curvature coherence.

### 6. Coherence Scoring

For each region, compute coherence (resonance) score:

```
coherence = 1 / (1 + coefficient_of_variation)
```

High coherence indicates uniform curvature = strong mathematical unity.

## Usage

### Basic Usage

```python
import cpp_core
from app.analysis.differential_lens import DifferentialLens

# Initialize SubD evaluator
cage = cpp_core.SubDControlCage()
# ... populate cage with vertices and faces ...

evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

# Create differential lens
lens = DifferentialLens(evaluator)

# Discover regions
regions = lens.discover_regions()

# Examine results
for region in regions:
    print(f"Region {region.id}:")
    print(f"  Unity: {region.unity_principle}")
    print(f"  Strength: {region.unity_strength:.3f}")
    print(f"  Faces: {len(region.faces)}")
    print(f"  Type: {region.metadata['curvature_type']}")
```

### Custom Parameters

```python
from app.analysis.differential_lens import DifferentialLensParams

params = DifferentialLensParams(
    samples_per_face=16,                # Higher resolution sampling
    mean_curvature_threshold=0.05,      # Stricter classification
    curvature_tolerance=0.2,            # Tighter region coherence
    min_region_size=5,                  # Larger minimum regions
    ridge_percentile=85.0,              # Top 15% are ridges
    valley_percentile=15.0              # Bottom 15% are valleys
)

lens = DifferentialLens(evaluator, params)
regions = lens.discover_regions()
```

### With Pinned Regions

Exclude specific faces from re-analysis (preserve user edits):

```python
# Pin faces 0, 1, 2 (already assigned to user-defined regions)
pinned_faces = {0, 1, 2}

regions = lens.discover_regions(pinned_faces=pinned_faces)
```

### Accessing Curvature Field

Get cached curvature data for visualization:

```python
lens = DifferentialLens(evaluator)
regions = lens.discover_regions()

# Get curvature field
curvature_field = lens.get_curvature_field()

for face_idx, stats in curvature_field.items():
    print(f"Face {face_idx}:")
    print(f"  K (Gaussian): {stats['mean_K']:.4f}")
    print(f"  H (Mean): {stats['mean_H']:.4f}")
    print(f"  |H|: {stats['mean_abs_H']:.4f}")
```

## Region Metadata

Each discovered region includes metadata:

```python
region.metadata = {
    'lens': 'differential',              # Lens type
    'curvature_type': 'elliptic',        # Surface classification
    'is_ridge': False,                   # Ridge feature?
    'is_valley': False,                  # Valley feature?
    'face_count': 12                     # Number of faces
}
```

## Integration with Application State

The differential lens produces `ParametricRegion` objects compatible with the application's state management:

```python
from app.state.app_state import ApplicationState

# Discover regions
lens = DifferentialLens(evaluator)
regions = lens.discover_regions()

# Add to application state
state = ApplicationState()
for region in regions:
    state.add_region(region)

# Regions are now visualized, selectable, and editable in the UI
```

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Sampling** | 9 points/face default (3×3 grid) |
| **Complexity** | O(n × s) where n = faces, s = samples |
| **Memory** | O(n) curvature cache |
| **Typical Time** | ~0.1-1 sec for 100 faces |

Higher `samples_per_face` increases accuracy but also computation time.

## Validation

### Sphere Test

Expected behavior:
- Single elliptic region (uniform positive curvature)
- High coherence score (>0.8)
- No ridges or valleys (uniform surface)

```python
# Create sphere cage (octahedron subdivision)
cage = create_sphere_cage()
evaluator = cpp_core.SubDEvaluator()
evaluator.initialize(cage)

lens = DifferentialLens(evaluator)
regions = lens.discover_regions()

assert len(regions) == 1
assert regions[0].metadata['curvature_type'] == 'elliptic'
assert regions[0].unity_strength > 0.8
```

### Cylinder Test

Expected behavior:
- Parabolic regions (sides) and possibly elliptic (caps)
- Medium coherence (curvature varies)
- Potential ridges along creases

### Saddle Test

Expected behavior:
- Hyperbolic region (negative Gaussian curvature)
- Clear ridge/valley features
- Moderate coherence

## Comparison with Mesh-Based Approach

| Aspect | Mesh-Based | Differential Lens (Exact) |
|--------|-----------|---------------------------|
| **Input** | Discretized triangle mesh | SubD control cage |
| **Curvature** | Finite differences | Exact second derivatives |
| **Resolution** | Fixed by mesh density | Arbitrary (parametric) |
| **Accuracy** | Approximate | Exact (up to subdivision) |
| **Lossless?** | ❌ No | ✅ Yes |

The differential lens maintains the lossless-until-fabrication principle by working entirely in parameter space with exact evaluations.

## Limitations and Future Work

### Current Limitations

1. **Face Adjacency**: Currently uses simplified adjacency graph
   - **TODO**: Query actual edge connectivity from control cage

2. **Boundary Extraction**: Boundary curves not yet computed
   - **TODO**: Extract exact parametric curves at region boundaries

3. **Sampling Strategy**: Uniform grid sampling
   - **TODO**: Adaptive sampling in high-curvature areas

### Future Enhancements

1. **Principal Direction Alignment**: Use `dir1`, `dir2` from curvature result for smoother boundaries
2. **Adaptive Subdivision**: Refine regions based on local curvature complexity
3. **Multi-scale Analysis**: Analyze at multiple subdivision levels
4. **Boundary Smoothing**: Apply curve fitting to extracted boundaries

## References

- **Differential Geometry**: do Carmo, "Differential Geometry of Curves and Surfaces"
- **SubD Evaluation**: Stam, "Exact Evaluation of Catmull-Clark Subdivision Surfaces"
- **Discrete Curvature**: Meyer et al., "Discrete Differential-Geometry Operators"

## Integration Notes for Subsequent Agents

### For Agent 33 (Iteration System)

The differential lens should be stored in iteration snapshots:

```python
snapshot = {
    'lens_type': 'differential',
    'lens_params': params.__dict__,
    'regions': [r.to_json() for r in regions],
    'curvature_field': lens.get_curvature_field()
}
```

### For Agent 35 (Spectral Lens)

The spectral lens can use curvature data as initialization:

```python
# Use differential lens results as prior
diff_lens = DifferentialLens(evaluator)
diff_regions = diff_lens.discover_regions()

# Initialize spectral lens with curvature hints
spectral_lens = SpectralLens(evaluator, curvature_prior=diff_lens.get_curvature_field())
```

### For Agent 38 (Lens Integration)

Register the differential lens in the lens manager:

```python
from app.analysis.lens_manager import LensManager, LensType

manager = LensManager(evaluator)
manager.register_lens(LensType.DIFFERENTIAL, DifferentialLens)

# User can now select and compare lenses
regions = manager.analyze(LensType.DIFFERENTIAL)
```

## Success Criteria

- [x] **Uses exact limit surface**: CurvatureAnalyzer with SubDEvaluator
- [x] **Ridge/valley detection**: Local extrema of |κ₁|
- [x] **Region classification**: Elliptic/hyperbolic/parabolic/planar
- [x] **Coherence scoring**: Based on curvature uniformity
- [x] **Parametric regions**: Output as ParametricRegion objects
- [x] **Comprehensive tests**: All test cases pass
- [x] **Documentation**: Complete API and usage docs

**Status**: ✅ All criteria met - First mathematical lens operational!

---

**Agent 32 Complete** | November 2025
