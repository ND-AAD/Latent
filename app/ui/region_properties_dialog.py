"""
Region Properties Dialog - Detailed view and editing of region properties
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QProgressBar, QGroupBox,
    QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional
import json


class RegionPropertiesDialog(QDialog):
    """
    Dialog for viewing and editing region properties

    Displays:
    - Region ID and editable name
    - Face count and topology info
    - Unity principle and strength
    - Parametric boundary visualization (future)
    - Export capabilities
    """

    # Signals
    properties_changed = pyqtSignal(str, dict)  # region_id, updated_properties

    def __init__(self, region, parent=None):
        """
        Initialize properties dialog

        Args:
            region: ParametricRegion instance to display/edit
            parent: Parent widget
        """
        super().__init__(parent)
        self.region = region
        self.init_ui()
        self.load_region_data()

    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Region Properties")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        self.setLayout(layout)

        # Header with region ID
        header_label = QLabel(f"Region: {self.region.id}")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)

        # Basic properties group
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout()
        basic_group.setLayout(basic_layout)

        # Region name (editable)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter region name...")
        basic_layout.addRow("Name:", self.name_edit)

        # Region ID (read-only)
        self.id_label = QLabel(self.region.id)
        self.id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        basic_layout.addRow("ID:", self.id_label)

        # Face count
        self.face_count_label = QLabel()
        basic_layout.addRow("Face Count:", self.face_count_label)

        # Pinned status
        self.pinned_checkbox = QCheckBox()
        self.pinned_checkbox.setChecked(self.region.pinned)
        basic_layout.addRow("Pinned:", self.pinned_checkbox)

        # Modified status
        self.modified_label = QLabel()
        basic_layout.addRow("Modified:", self.modified_label)

        layout.addWidget(basic_group)

        # Mathematical properties group
        math_group = QGroupBox("Mathematical Properties")
        math_layout = QFormLayout()
        math_group.setLayout(math_layout)

        # Unity principle
        self.principle_label = QLabel()
        self.principle_label.setWordWrap(True)
        math_layout.addRow("Unity Principle:", self.principle_label)

        # Unity strength with visual indicator
        strength_layout = QHBoxLayout()
        self.strength_label = QLabel()
        strength_layout.addWidget(self.strength_label)

        self.strength_bar = QProgressBar()
        self.strength_bar.setMaximum(100)
        self.strength_bar.setTextVisible(True)
        self.strength_bar.setFormat("%p%")
        strength_layout.addWidget(self.strength_bar, 1)

        math_layout.addRow("Unity Strength:", strength_layout)

        # Constraints status
        self.constraints_label = QLabel()
        math_layout.addRow("Constraints:", self.constraints_label)

        layout.addWidget(math_group)

        # Topology information group
        topology_group = QGroupBox("Topology Information")
        topology_layout = QVBoxLayout()
        topology_group.setLayout(topology_layout)

        # Face indices display
        face_label = QLabel("Face Indices:")
        topology_layout.addWidget(face_label)

        self.faces_text = QTextEdit()
        self.faces_text.setReadOnly(True)
        self.faces_text.setMaximumHeight(100)
        topology_layout.addWidget(self.faces_text)

        layout.addWidget(topology_group)

        # Parametric boundary group (placeholder for future)
        boundary_group = QGroupBox("Parametric Boundary")
        boundary_layout = QVBoxLayout()
        boundary_group.setLayout(boundary_layout)

        boundary_info = QLabel(
            "Parametric boundary visualization will be available in a future version.\n"
            "Boundaries are defined in (face_id, u, v) parameter space."
        )
        boundary_info.setWordWrap(True)
        boundary_info.setStyleSheet("color: gray; font-style: italic;")
        boundary_layout.addWidget(boundary_info)

        layout.addWidget(boundary_group)

        # Button row
        button_layout = QHBoxLayout()

        # Export button
        self.export_btn = QPushButton("Export to JSON...")
        self.export_btn.clicked.connect(self.export_region)
        button_layout.addWidget(self.export_btn)

        button_layout.addStretch()

        # Apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_btn)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def load_region_data(self):
        """Load region data into the UI"""
        # Basic properties
        # For now, region ID is used as name (no separate name field in ParametricRegion)
        self.name_edit.setText(self.region.id)

        # Face count
        face_count = len(self.region.faces)
        self.face_count_label.setText(str(face_count))

        # Modified status
        self.modified_label.setText("Yes" if self.region.modified else "No")
        self.modified_label.setStyleSheet(
            "color: orange;" if self.region.modified else "color: green;"
        )

        # Mathematical properties
        self.principle_label.setText(
            self.region.unity_principle if self.region.unity_principle
            else "No principle specified"
        )

        # Unity strength
        strength_percent = int(self.region.unity_strength * 100)
        self.strength_label.setText(f"{self.region.unity_strength:.3f}")
        self.strength_bar.setValue(strength_percent)

        # Color code the progress bar based on strength
        if self.region.unity_strength >= 0.8:
            # Excellent - green
            self.strength_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #4CAF50; }
            """)
        elif self.region.unity_strength >= 0.6:
            # Good - blue
            self.strength_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #2196F3; }
            """)
        elif self.region.unity_strength >= 0.4:
            # Moderate - orange
            self.strength_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #FF9800; }
            """)
        else:
            # Poor - red
            self.strength_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #F44336; }
            """)

        # Constraints
        if self.region.constraints_passed:
            self.constraints_label.setText("All constraints passed")
            self.constraints_label.setStyleSheet("color: green;")
        else:
            self.constraints_label.setText("Some constraints failed")
            self.constraints_label.setStyleSheet("color: red;")

        # Topology - face indices
        # Format as comma-separated list with line breaks every 10 items
        face_indices = self.region.faces
        face_text = ""
        for i, face_id in enumerate(face_indices):
            face_text += str(face_id)
            if i < len(face_indices) - 1:
                face_text += ", "
            if (i + 1) % 10 == 0:
                face_text += "\n"

        self.faces_text.setText(face_text)

    def apply_changes(self):
        """Apply changes to region properties"""
        updated_properties = {}

        # Check if pinned state changed
        if self.pinned_checkbox.isChecked() != self.region.pinned:
            updated_properties['pinned'] = self.pinned_checkbox.isChecked()

        # Emit signal if any properties changed
        if updated_properties:
            self.properties_changed.emit(self.region.id, updated_properties)

        # Update local region object
        self.region.pinned = self.pinned_checkbox.isChecked()

        # Show confirmation
        QMessageBox.information(
            self,
            "Properties Updated",
            "Region properties have been updated."
        )

    def export_region(self):
        """Export region data to JSON file"""
        # Open file dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Region to JSON",
            f"{self.region.id}.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if not filename:
            return

        try:
            # Create export data
            export_data = {
                'region_id': self.region.id,
                'face_count': len(self.region.faces),
                'faces': self.region.faces,
                'unity_principle': self.region.unity_principle,
                'unity_strength': self.region.unity_strength,
                'pinned': self.region.pinned,
                'modified': self.region.modified,
                'constraints_passed': self.region.constraints_passed,
            }

            # Write to file
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Region exported to:\n{filename}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export region:\n{str(e)}"
            )

    def get_updated_properties(self) -> dict:
        """
        Get dictionary of updated properties

        Returns:
            Dictionary of properties that were modified
        """
        updated = {}

        # Check pinned state
        if self.pinned_checkbox.isChecked() != self.region.pinned:
            updated['pinned'] = self.pinned_checkbox.isChecked()

        return updated
