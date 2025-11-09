# Curvature Visualization System

**Agent 29 Deliverable** - Day 4 Morning
**Date**: November 2025
**Author**: Ceramic Mold Analyzer

## Overview

The curvature visualization system provides false-color mapping of surface curvature analysis results in VTK. This enables visual exploration of differential geometry properties for subdivision surface analysis and mold design.

## Features

### Curvature Types Supported

1. **Gaussian Curvature** (K = κ₁ × κ₂)
   - Classifies surface type: elliptic (K > 0), hyperbolic (K < 0), parabolic (K ≈ 0)
   - Reveals intrinsic geometry independent of embedding

2. **Mean Curvature** (H = (κ₁ + κ₂) / 2)
   - Measures bending/deviation from planarity
   - Critical for minimal surface analysis

3. **Principal Curvatures** (κ₁, κ₂)
   - Minimum and maximum normal curvatures
   - Define principal directions of bending

4. **Absolute Mean Curvature** (|H|)
   - Magnitude-only visualization
   - Useful for identifying high-curvature regions

### Color Maps

#### Diverging Colormaps (for signed curvature)
- **Blue-White-Red**: Blue = negative, white = zero, red = positive
- **Cool-Warm**: Paraview-style diverging map
- **Red-White-Blue**: Inverted BWR

#### Sequential Colormaps (for unsigned curvature)
- **Rainbow**: Classic spectrum (blue → red)
- **Viridis**: Perceptually uniform (purple → yellow)
- **Grayscale**: Black to white

### Visualization Controls

- **Auto-range**: Automatically scale to data min/max
- **Manual range**: Clamp to specified [min, max] for comparison
- **Edge visibility**: Toggle mesh edges on/off
- **Scalar bar**: Color legend with customizable labels

## Usage

### Basic Example

```python
from app.geometry.curvature_renderer import (
    CurvatureRenderer,
    CurvatureType,
    ColorMapType
)
import vtk

# Create test sphere
sphere_source = vtk.vtkSphereSource()
sphere_source.SetRadius(5.0)
sphere_source.Update()
polydata = sphere_source.GetOutput()

# Initialize renderer
renderer = CurvatureRenderer()

# Compute Gaussian curvature
gaussian_values = renderer.compute_curvature_from_mesh(
    polydata,
    CurvatureType.GAUSSIAN
)

# Create color-mapped actor
actor = renderer.create_curvature_actor(
    polydata,
    gaussian_values,
    curvature_type=CurvatureType.GAUSSIAN,
    color_map=ColorMapType.DIVERGING_BWR,
    auto_range=True,
    show_edges=False
)

# Create scalar bar (legend)
scalar_bar = renderer.create_scalar_bar(num_labels=5)

# Add to VTK renderer
vtk_renderer = vtk.vtkRenderer()
vtk_renderer.AddActor(actor)
vtk_renderer.AddActor2D(scalar_bar)
```

### Advanced Example: Manual Range Control

```python
# Compute curvature
mean_values = renderer.compute_curvature_from_mesh(
    polydata,
    CurvatureType.MEAN
)

# Get statistics
stats = renderer.get_curvature_statistics(mean_values)
print(f"Mean curvature range: [{stats['min']:.3f}, {stats['max']:.3f}]")
print(f"Mean: {stats['mean']:.3f} ± {stats['std']:.3f}")

# Create actor with manual range (for comparing multiple surfaces)
actor = renderer.create_curvature_actor(
    polydata,
    mean_values,
    curvature_type=CurvatureType.MEAN,
    color_map=ColorMapType.COOL_WARM,
    auto_range=False,
    manual_range=(-1.0, 1.0)  # Fixed range for all surfaces
)
```

### Custom Curvature Values

If you have curvature values from exact SubD limit surface evaluation (via C++ analyzer):

```python
import numpy as np

# Example: Custom curvature values from C++ analyzer
# (per-vertex or per-face)
custom_curvatures = np.array([...])  # From cpp_core.CurvatureAnalyzer

# Visualize
actor = renderer.create_curvature_actor(
    polydata,
    custom_curvatures,
    curvature_type=CurvatureType.GAUSSIAN,
    color_map=ColorMapType.DIVERGING_BWR
)
```

### Updating Color Map

```python
# Create initial visualization
actor = renderer.create_curvature_actor(
    polydata,
    values,
    color_map=ColorMapType.RAINBOW
)

# Later, change to different color map
renderer.update_color_map(ColorMapType.VIRIDIS)
vtk_renderer.Render()  # Update display
```

## Integration with Analysis Pipeline

### Workflow for Exact SubD Curvature

```python
# 1. Get SubD control cage from Rhino
cage_data = rhino_bridge.get_subd_control_cage()

# 2. Build C++ SubD evaluator (when available)
# evaluator = cpp_core.SubDEvaluator(cage_data)

# 3. Compute exact curvature (when C++ analyzer available)
# curvature_analyzer = cpp_core.CurvatureAnalyzer(evaluator)
# gaussian_values = curvature_analyzer.compute_gaussian_at_grid(...)

# 4. For now, use mesh-based approximation
renderer = CurvatureRenderer()
gaussian_values = renderer.compute_curvature_from_mesh(
    display_mesh,
    CurvatureType.GAUSSIAN
)

# 5. Visualize
actor = renderer.create_curvature_actor(
    display_mesh,
    gaussian_values,
    curvature_type=CurvatureType.GAUSSIAN
)
```

## Mathematical Background

### Gaussian Curvature (K)

**Definition**: Product of principal curvatures
K = κ₁ × κ₂

**Interpretation**:
- K > 0: Elliptic point (bowl-like, both principal curvatures same sign)
- K < 0: Hyperbolic point (saddle-like, principal curvatures opposite signs)
- K ≈ 0: Parabolic point (cylinder-like, one principal curvature zero)

**Examples**:
- Sphere (radius r): K = 1/r²
- Plane: K = 0
- Saddle: K < 0

### Mean Curvature (H)

**Definition**: Average of principal curvatures
H = (κ₁ + κ₂) / 2

**Interpretation**:
- H > 0: Convex (bulging outward)
- H < 0: Concave (indented inward)
- H = 0: Minimal surface

**Examples**:
- Sphere (radius r): H = 1/r
- Plane: H = 0
- Minimal surfaces (soap films): H = 0

### Principal Curvatures (κ₁, κ₂)

**Definition**: Eigenvalues of shape operator (second fundamental form)

**Computation**: From first and second fundamental forms:
```
Shape operator S = I⁻¹ × II
κ₁, κ₂ = eigenvalues of S
```

## Color Map Selection Guide

### For Gaussian Curvature
- **Recommended**: `DIVERGING_BWR` or `COOL_WARM`
- **Reason**: Clearly shows sign (elliptic vs. hyperbolic regions)
- **Blue regions**: Saddle-like (negative K)
- **Red regions**: Bowl-like (positive K)
- **White**: Cylindrical (K ≈ 0)

### For Mean Curvature
- **Recommended**: `DIVERGING_BWR` or `COOL_WARM`
- **Reason**: Shows convex vs. concave regions
- **Blue**: Concave (indented)
- **Red**: Convex (bulging)
- **White**: Flat (H ≈ 0)

### For Principal Curvatures
- **Recommended**: `RAINBOW` or `VIRIDIS`
- **Reason**: Emphasizes magnitude gradients
- **Blue**: Low curvature
- **Red**: High curvature

### For Absolute Mean Curvature
- **Recommended**: `VIRIDIS` or `GRAYSCALE`
- **Reason**: Highlights high-curvature regions without sign
- **Dark**: Low bending
- **Bright**: High bending

## Testing

Comprehensive test suite in `tests/test_curvature_visualization.py`:

```bash
python -m pytest tests/test_curvature_visualization.py -v
```

**Test Coverage**:
- Renderer initialization
- All curvature types (Gaussian, mean, principal)
- All color maps (6 types)
- Sphere validation (K = 1/r², H = 1/r)
- Manual vs. auto range control
- Scalar bar creation
- Statistics computation
- Edge visibility toggle
- Per-vertex and per-cell data
- Integration workflows

**Results**: 19/19 tests passing ✅

## Performance Considerations

### Mesh-Based Curvature (VTK)
- **Speed**: Fast (1000s of vertices/sec)
- **Accuracy**: Approximate (discrete differential geometry)
- **Use case**: Quick visualization, preview

### Exact SubD Curvature (C++ - future)
- **Speed**: Medium (100s of evaluations/sec)
- **Accuracy**: Exact (analytical derivatives)
- **Use case**: Final analysis, mold generation

## API Reference

### CurvatureRenderer Class

#### Methods

**`create_curvature_actor()`**
```python
create_curvature_actor(
    polydata: vtk.vtkPolyData,
    curvature_values: np.ndarray,
    curvature_type: CurvatureType = CurvatureType.GAUSSIAN,
    color_map: ColorMapType = ColorMapType.DIVERGING_BWR,
    auto_range: bool = True,
    manual_range: Optional[Tuple[float, float]] = None,
    show_edges: bool = True
) -> vtk.vtkActor
```

**`create_scalar_bar()`**
```python
create_scalar_bar(
    title: Optional[str] = None,
    num_labels: int = 5,
    width: float = 0.1,
    height: float = 0.6
) -> vtk.vtkScalarBarActor
```

**`compute_curvature_from_mesh()`**
```python
compute_curvature_from_mesh(
    polydata: vtk.vtkPolyData,
    curvature_type: CurvatureType = CurvatureType.GAUSSIAN
) -> np.ndarray
```

**`get_curvature_statistics()`**
```python
get_curvature_statistics(
    values: np.ndarray
) -> Dict[str, float]
# Returns: {min, max, mean, std, median, percentile_5, percentile_95, count}
```

**`update_color_map()`**
```python
update_color_map(color_map: ColorMapType)
```

### Enums

**CurvatureType**
- `GAUSSIAN`: K = κ₁ × κ₂
- `MEAN`: H = (κ₁ + κ₂) / 2
- `PRINCIPAL_MIN`: κ₁
- `PRINCIPAL_MAX`: κ₂
- `ABSOLUTE_MEAN`: |H|

**ColorMapType**
- `DIVERGING_BWR`: Blue-white-red diverging
- `DIVERGING_RWB`: Red-white-blue diverging
- `RAINBOW`: Blue to red sequential
- `VIRIDIS`: Perceptually uniform
- `COOL_WARM`: Paraview-style diverging
- `GRAYSCALE`: Black to white

## Future Enhancements

1. **C++ Integration**: Use exact curvature from `cpp_core.CurvatureAnalyzer`
2. **Curvature Directions**: Visualize principal direction vectors
3. **Curvature Histograms**: Statistical distribution plots
4. **Comparison View**: Side-by-side comparison of multiple curvature types
5. **Export**: Save curvature data to CSV/JSON
6. **Interactive Probing**: Click to query curvature value at point

## Related Modules

- `app/geometry/curvature.py`: Mesh-based curvature estimation (Python)
- `cpp_core/analysis/curvature_analyzer.h`: Exact curvature analysis (C++)
- `app/geometry/subd_renderer.py`: SubD surface rendering
- `app/ui/viewport_3d.py`: VTK viewport for display

## References

1. **Meyer et al. (2003)**: "Discrete Differential-Geometry Operators for Triangulated 2-Manifolds"
2. **do Carmo (1976)**: "Differential Geometry of Curves and Surfaces"
3. **Stam (1998)**: "Exact Evaluation of Catmull-Clark Subdivision Surfaces at Arbitrary Parameter Values"

---

**Status**: ✅ Implemented and tested (Agent 29)
**Next**: Agent 30 will add comprehensive curvature test suite
**Dependencies**: VTK 9.x, NumPy
