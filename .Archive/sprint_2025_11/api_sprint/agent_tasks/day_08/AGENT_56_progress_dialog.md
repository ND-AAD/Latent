# Agent 56: Progress Feedback UI

**Day**: 8
**Duration**: 2-3 hours
**Cost**: $2-4 (40K tokens)

---

## Mission

Create progress dialog showing mold generation steps (validation, NURBS fitting, draft, export).

---

## Deliverables

**File**: `app/ui/progress_dialog.py`

---

## Requirements

```python
# app/ui/progress_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QProgressBar,
                             QLabel, QPushButton)
from PyQt6.QtCore import Qt


class ProgressDialog(QDialog):
    """
    Progress feedback for long-running operations.
    
    Shows:
    - Current step description
    - Progress bar (0-100%)
    - Cancel button
    """
    
    def __init__(self, title: str = "Processing...", parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.canceled = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)
    
    def set_progress(self, value: int, status: str = ""):
        """Update progress (0-100) and optional status."""
        self.progress.setValue(value)
        if status:
            self.status_label.setText(status)
    
    def _on_cancel(self):
        self.canceled = True
        self.reject()
```

---

## Success Criteria

- [ ] Progress bar updates correctly
- [ ] Status text descriptive
- [ ] Cancel button functional
- [ ] Modal dialog blocks interaction

---

**Ready to begin!**
