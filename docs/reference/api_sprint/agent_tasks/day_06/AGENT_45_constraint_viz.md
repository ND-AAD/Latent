# Agent 45: Constraint Visualization

**Day**: 6
**Duration**: 3-4 hours
**Cost**: $4-6 (60K tokens)

---

## Mission

VTK visualization of undercuts and draft angles in viewport.

---

## Deliverables

**File**: `app/geometry/constraint_renderer.py`

---

## Requirements

```python
# app/geometry/constraint_renderer.py

import vtk
import numpy as np


class ConstraintRenderer:
    """
    Render constraint violations in VTK viewport.

    - Undercuts: Red highlighting
    - Insufficient draft: Yellow to green gradient
    - Demolding vector: Blue arrow
    """

    def __init__(self, renderer: vtk.vtkRenderer):
        self.renderer = renderer
        self.undercut_actor = None
        self.draft_actor = None
        self.demold_arrow = None

    def show_undercuts(self, face_ids, mesh):
        """Highlight undercut faces in red."""
        # [Create VTK actor with red color for undercut faces]
        pass

    def show_draft_angles(self, draft_map, mesh):
        """
        Color faces by draft angle.

        Red: <0.5° (insufficient)
        Yellow: 0.5-2.0° (marginal)
        Green: >2.0° (good)
        """
        # [Create VTK scalar field from draft_map]
        pass

    def show_demolding_direction(self, direction):
        """Display demolding vector as 3D arrow."""
        # [Create VTK arrow glyph]
        pass
```

---

## Success Criteria

- [ ] Undercuts highlighted red
- [ ] Draft angles color-coded
- [ ] Demolding arrow visible
- [ ] Tests pass

---

**Ready to begin!**
