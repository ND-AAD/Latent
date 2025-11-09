# Agent 54: Mold Parameters Dialog

**Day**: 8
**Duration**: 3-4 hours
**Cost**: $4-6 (60K tokens)

---

## Mission

Create UI dialog for setting mold generation parameters (draft angle, wall thickness, demolding direction).

---

## Deliverables

**File**: `app/ui/mold_params_dialog.py`

---

## Requirements

```python
# app/ui/mold_params_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QDoubleSpinBox, QPushButton, QComboBox,
                             QLabel, QGroupBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from dataclasses import dataclass


@dataclass
class MoldParameters:
    """Mold generation parameters."""
    draft_angle: float = 2.0  # degrees
    wall_thickness: float = 40.0  # mm
    demolding_direction: tuple = (0, 0, 1)  # (x, y, z)
    add_registration_keys: bool = True
    key_diameter: float = 10.0  # mm


class MoldParametersDialog(QDialog):
    """
    Dialog for configuring mold generation parameters.
    
    Integrates slip-casting constraints:
    - Draft angle: 0.5-2.0° minimum
    - Wall thickness: 40mm (1.5-2") standard
    """
    
    def __init__(self, parent=None, defaults: MoldParameters = None):
        super().__init__(parent)
        
        self.params = defaults or MoldParameters()
        self._setup_ui()
    
    def _setup_ui(self):
        self.setWindowTitle("Mold Generation Parameters")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Draft angle
        draft_group = QGroupBox("Draft Angle")
        draft_layout = QFormLayout()
        
        self.draft_spin = QDoubleSpinBox()
        self.draft_spin.setRange(0.5, 10.0)
        self.draft_spin.setValue(self.params.draft_angle)
        self.draft_spin.setSuffix("°")
        self.draft_spin.setDecimals(1)
        draft_layout.addRow("Angle:", self.draft_spin)
        
        draft_info = QLabel("Minimum: 0.5° (rigid plaster)\nRecommended: 2.0°")
        draft_info.setStyleSheet("color: #666; font-size: 10px;")
        draft_layout.addRow("", draft_info)
        
        draft_group.setLayout(draft_layout)
        layout.addWidget(draft_group)
        
        # Wall thickness
        wall_group = QGroupBox("Wall Thickness")
        wall_layout = QFormLayout()
        
        self.wall_spin = QDoubleSpinBox()
        self.wall_spin.setRange(30.0, 100.0)
        self.wall_spin.setValue(self.params.wall_thickness)
        self.wall_spin.setSuffix(" mm")
        self.wall_spin.setDecimals(1)
        wall_layout.addRow("Thickness:", self.wall_spin)
        
        wall_info = QLabel("Standard: 40mm (1.5-2 inches)")
        wall_info.setStyleSheet("color: #666; font-size: 10px;")
        wall_layout.addRow("", wall_info)
        
        wall_group.setLayout(wall_layout)
        layout.addWidget(wall_group)
        
        # Demolding direction
        demold_group = QGroupBox("Demolding Direction")
        demold_layout = QFormLayout()
        
        self.demold_combo = QComboBox()
        self.demold_combo.addItems(["+Z (up)", "-Z (down)", "+X", "-X", "+Y", "-Y"])
        demold_layout.addRow("Direction:", self.demold_combo)
        
        demold_group.setLayout(demold_layout)
        layout.addWidget(demold_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Generate Molds")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def get_parameters(self) -> MoldParameters:
        """Get configured parameters."""
        # Parse demolding direction
        direction_map = {
            "+Z (up)": (0, 0, 1),
            "-Z (down)": (0, 0, -1),
            "+X": (1, 0, 0),
            "-X": (-1, 0, 0),
            "+Y": (0, 1, 0),
            "-Y": (0, -1, 0)
        }
        
        direction_str = self.demold_combo.currentText()
        
        return MoldParameters(
            draft_angle=self.draft_spin.value(),
            wall_thickness=self.wall_spin.value(),
            demolding_direction=direction_map[direction_str],
            add_registration_keys=True,
            key_diameter=10.0
        )
```

---

## Success Criteria

- [ ] Draft angle configurable (0.5-10°)
- [ ] Wall thickness configurable (30-100mm)
- [ ] Demolding direction selectable
- [ ] Defaults match slip-casting specs
- [ ] Dialog accepts/rejects correctly
- [ ] Parameters returned via get_parameters()

---

**Ready to begin!**
