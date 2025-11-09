"""
Constraint Panel - 3-tier display of constraint validation results

Shows constraint violations in hierarchical tree:
- ERROR (red): Physical impossibilities that must be fixed
- WARNING (yellow): Manufacturing challenges that are negotiable
- FEATURE (blue): Mathematical tensions that are aesthetic features
"""

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
        """Initialize the UI components."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Constraint Validation")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Description", "Severity"])
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

        # Set column widths
        self.tree.setColumnWidth(0, 300)
        self.tree.setColumnWidth(1, 80)

    def display_report(self, report: cpp_core.ConstraintReport):
        """
        Display constraint violations from a ConstraintReport.

        Args:
            report: cpp_core.ConstraintReport containing violations
        """
        self.tree.clear()

        # Create top-level categories
        errors = QTreeWidgetItem(self.tree, ["Errors", ""])
        errors.setForeground(0, QColor(200, 0, 0))
        errors.setExpanded(True)

        warnings = QTreeWidgetItem(self.tree, ["Warnings", ""])
        warnings.setForeground(0, QColor(200, 150, 0))
        warnings.setExpanded(True)

        features = QTreeWidgetItem(self.tree, ["Features", ""])
        features.setForeground(0, QColor(0, 100, 200))
        features.setExpanded(True)

        # Populate with violations
        error_count = 0
        warning_count = 0
        feature_count = 0

        for v in report.violations:
            if v.level == cpp_core.ConstraintLevel.ERROR:
                item = QTreeWidgetItem(errors, [v.description, f"{v.severity:.2f}"])
                item.setData(0, Qt.ItemDataRole.UserRole, v.face_id)
                item.setForeground(0, QColor(150, 0, 0))
                item.setForeground(1, QColor(150, 0, 0))
                error_count += 1

            elif v.level == cpp_core.ConstraintLevel.WARNING:
                item = QTreeWidgetItem(warnings, [v.description, f"{v.severity:.2f}"])
                item.setData(0, Qt.ItemDataRole.UserRole, v.face_id)
                item.setForeground(0, QColor(180, 120, 0))
                item.setForeground(1, QColor(180, 120, 0))
                warning_count += 1

            elif v.level == cpp_core.ConstraintLevel.FEATURE:
                item = QTreeWidgetItem(features, [v.description, f"{v.severity:.2f}"])
                item.setData(0, Qt.ItemDataRole.UserRole, v.face_id)
                item.setForeground(0, QColor(0, 80, 180))
                item.setForeground(1, QColor(0, 80, 180))
                feature_count += 1

        # Update category labels with counts
        errors.setText(0, f"Errors ({error_count})")
        warnings.setText(0, f"Warnings ({warning_count})")
        features.setText(0, f"Features ({feature_count})")

        # Expand all categories
        self.tree.expandAll()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Handle item clicks in the tree.

        Emits violation_selected signal with face_id if the clicked item
        is a violation (not a category header).
        """
        face_id = item.data(0, Qt.ItemDataRole.UserRole)
        if face_id is not None:
            self.violation_selected.emit(face_id)

    def clear(self):
        """Clear the constraint display."""
        self.tree.clear()
