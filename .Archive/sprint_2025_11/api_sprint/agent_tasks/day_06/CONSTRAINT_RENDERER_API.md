# ConstraintRenderer Quick API Reference

## Import
```python
from app.geometry.constraint_renderer import ConstraintRenderer
```

## Initialization
```python
renderer = ConstraintRenderer(vtk_renderer)
```

## Core Methods

### Show Undercuts (Tier 1 Constraints)
```python
renderer.show_undercuts(
    face_ids: List[int],    # Face indices with undercuts
    mesh: vtk.vtkPolyData   # Surface mesh
)
```

### Show Draft Angles (Tier 2 Constraints)
```python
renderer.show_draft_angles(
    draft_map: Dict[int, float],  # face_id -> draft_angle (degrees)
    mesh: vtk.vtkPolyData          # Surface mesh
)
```

### Show Demolding Direction
```python
renderer.show_demolding_direction(
    direction: Tuple[float, float, float],  # Unit vector (x, y, z)
    origin: Optional[Tuple[float, float, float]] = None,  # Arrow base
    scale: float = 2.0                      # Arrow length multiplier
)
```

## Cleanup Methods
```python
renderer.clear_undercuts()      # Clear undercut visualization
renderer.clear_draft()          # Clear draft angle visualization
renderer.clear_demold_arrow()   # Clear demolding arrow
renderer.clear_all()            # Clear everything
```

## Statistics
```python
stats = renderer.get_draft_statistics(draft_map)
# Returns: {
#   'min', 'max', 'mean', 'std', 'median',
#   'count_insufficient', 'count_marginal', 'count_good',
#   'total_faces'
# }
```

## Configuration
```python
renderer.update_draft_thresholds(
    insufficient: float,  # Angle below which is insufficient (default: 0.5°)
    marginal: float       # Angle below which is marginal (default: 2.0°)
)
```

## Color Scheme

| Constraint Type | Color | Meaning |
|----------------|-------|---------|
| Undercuts | Red (1.0, 0.0, 0.0) | Tier 1: Must fix |
| Draft <0.5° | Red | Insufficient |
| Draft 0.5-2.0° | Yellow | Marginal |
| Draft >2.0° | Green | Good |
| Demolding Arrow | Blue (0.0, 0.5, 1.0) | Pull direction |

## Complete Example
```python
import vtk
from app.geometry.constraint_renderer import ConstraintRenderer

# Setup
vtk_renderer = vtk.vtkRenderer()
constraint_renderer = ConstraintRenderer(vtk_renderer)

# Visualize constraints
constraint_renderer.show_undercuts([0, 1, 2], mesh)
constraint_renderer.show_draft_angles(
    {0: 0.3, 1: 1.0, 2: 3.0},  # face_id -> degrees
    mesh
)
constraint_renderer.show_demolding_direction((0, 0, 1))

# Get statistics
stats = constraint_renderer.get_draft_statistics({0: 0.3, 1: 1.0, 2: 3.0})
print(f"Draft range: {stats['min']:.1f}° to {stats['max']:.1f}°")

# Cleanup when done
constraint_renderer.clear_all()
```

---
*Agent 45 - Constraint Visualization*
