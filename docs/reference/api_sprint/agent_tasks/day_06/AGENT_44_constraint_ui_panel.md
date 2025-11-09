# Agent 44: Constraint UI Panel

**Day**: 6
**Duration**: 4-5 hours
**Cost**: $4-7 (70K tokens)

---

## Mission

Create 3-tier constraint display UI (ERROR/WARNING/FEATURE).

---

## Deliverables

**File**: `app/ui/constraint_panel.py`

---

## Requirements

```python
# app/ui/constraint_panel.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget,
                             QTreeWidgetItem, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
import cpp_core


class ConstraintPanel(QWidget):
    """
    Display constraint validation results in 3-tier hierarchy.

    Red: Errors (must fix)
    Yellow: Warnings (negotiable)
    Blue: Features (mathematical tensions)
    """

    violation_selected = pyqtSignal(int)  # face_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        layout.addWidget(QLabel("Constraint Validation"))

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Description", "Severity"])
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

    def display_report(self, report: cpp_core.ConstraintReport):
        """Display constraint violations."""
        self.tree.clear()

        # Errors (red)
        errors = QTreeWidgetItem(self.tree, ["Errors", ""])
        errors.setForeground(0, QColor(200, 0, 0))

        # Warnings (yellow)
        warnings = QTreeWidgetItem(self.tree, ["Warnings", ""])
        warnings.setForeground(0, QColor(200, 150, 0))

        # Features (blue)
        features = QTreeWidgetItem(self.tree, ["Features", ""])
        features.setForeground(0, QColor(0, 100, 200))

        # Populate
        for v in report.violations:
            if v.level == cpp_core.ConstraintLevel.ERROR:
                item = QTreeWidgetItem(errors, [v.description, f"{v.severity:.2f}"])
                item.setData(0, Qt.ItemDataRole.UserRole, v.face_id)
            # ... similar for WARNING and FEATURE

        self.tree.expandAll()
```

---

## Success Criteria

- [ ] 3-tier tree structure
- [ ] Color-coded by severity
- [ ] Click shows face in viewport
- [ ] Tests pass

---

**Ready to begin!**
