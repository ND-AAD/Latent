# Agent 37: Region Merge/Split Tools

**Day**: 5
**Phase**: Phase 1a - Mathematical Analysis
**Duration**: 4-5 hours
**Estimated Cost**: $4-7 (70K tokens, Sonnet)

---

## Mission

Implement interactive region manipulation tools for merging adjacent regions and splitting regions along user-defined curves.

---

## Context

Users need to refine automatically discovered regions through manual editing. This agent provides:
- Merge: Combine adjacent regions into one
- Split: Divide region along user-drawn curve
- **CRITICAL**: Maintain parametric definitions throughout

**Dependencies**:
- Day 3: ParametricRegion, region management
- Day 2: VTK viewport (for curve drawing)

---

## Deliverables

1. `app/operations/region_operations.py` (merge/split logic)
2. `app/ui/region_editor_widget.py` (UI controls)
3. `tests/test_region_operations.py` (tests)

---

## Requirements

### 1. Region Operations

```python
# app/operations/region_operations.py

from typing import List, Tuple
from app.state.parametric_region import ParametricRegion, ParametricCurve


class RegionOperations:
    """Operations for manipulating parametric regions."""

    @staticmethod
    def merge_regions(r1: ParametricRegion,
                     r2: ParametricRegion) -> ParametricRegion:
        """
        Merge two adjacent regions.

        Returns:
            New ParametricRegion with combined faces
        """
        merged = ParametricRegion(
            faces=list(set(r1.faces) | set(r2.faces)),
            boundary=[],  # TODO: Compute merged boundary
            generation_method="merged",
            generation_parameters={
                'parent_ids': [id(r1), id(r2)]
            }
        )
        return merged

    @staticmethod
    def split_region(region: ParametricRegion,
                    split_curve: ParametricCurve) -> Tuple[ParametricRegion, ParametricRegion]:
        """
        Split region along parametric curve.

        Args:
            region: Region to split
            split_curve: Curve in (face_id, u, v) space

        Returns:
            (region1, region2) on either side of curve
        """
        # Classify faces as left/right of curve
        # SIMPLIFIED: Use face center classification
        left_faces = []
        right_faces = []

        for face_id in region.faces:
            # Determine side (placeholder logic)
            # TODO: Implement proper geometric classification
            if hash(face_id) % 2 == 0:
                left_faces.append(face_id)
            else:
                right_faces.append(face_id)

        r1 = ParametricRegion(
            faces=left_faces,
            boundary=[],
            generation_method="split",
            generation_parameters={'side': 'left'}
        )

        r2 = ParametricRegion(
            faces=right_faces,
            boundary=[],
            generation_method="split",
            generation_parameters={'side': 'right'}
        )

        return r1, r2
```

---

### 2. UI Controls

```python
# app/ui/region_editor_widget.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QLabel, QListWidget)
from PyQt6.QtCore import pyqtSignal


class RegionEditorWidget(QWidget):
    """
    UI for region editing operations.

    Signals:
        merge_requested: User clicked merge
        split_requested: User clicked split
    """

    merge_requested = pyqtSignal()
    split_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        layout.addWidget(QLabel("Region Editing"))

        # Merge button
        self.merge_btn = QPushButton("Merge Selected Regions")
        self.merge_btn.clicked.connect(self.merge_requested.emit)
        layout.addWidget(self.merge_btn)

        # Split button
        self.split_btn = QPushButton("Split Region...")
        self.split_btn.clicked.connect(self.split_requested.emit)
        layout.addWidget(self.split_btn)

        layout.addStretch()
```

---

## Success Criteria

- [ ] Merge combines face sets correctly
- [ ] Split divides regions
- [ ] Parametric definitions maintained
- [ ] UI signals work
- [ ] Tests pass

---

**Ready to begin!**
