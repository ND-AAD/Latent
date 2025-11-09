"""
Selection Info Panel for Ceramic Mold Analyzer
Displays detailed information about current selection
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.state.edit_mode import EditMode, Selection


class SelectionInfoPanel(QWidget):
    """Panel showing detailed selection information"""

    # Signals
    export_to_region_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_selection = None

    def _setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Selection summary group
        summary_group = QGroupBox("Selection Summary")
        summary_layout = QVBoxLayout()

        # Mode label
        self.mode_label = QLabel("Mode: Solid")
        self.mode_label.setStyleSheet("font-weight: bold; padding: 5px;")
        summary_layout.addWidget(self.mode_label)

        # Count labels
        self.faces_label = QLabel("Faces: 0")
        self.edges_label = QLabel("Edges: 0")
        self.vertices_label = QLabel("Vertices: 0")

        for label in [self.faces_label, self.edges_label, self.vertices_label]:
            label.setStyleSheet("padding: 2px 5px;")
            summary_layout.addWidget(label)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Selected indices group
        indices_group = QGroupBox("Selected Indices")
        indices_layout = QVBoxLayout()

        # List widget for showing indices
        self.indices_list = QListWidget()
        self.indices_list.setMaximumHeight(150)
        self.indices_list.setStyleSheet("""
            QListWidget {
                font-family: monospace;
                font-size: 11px;
            }
        """)
        indices_layout.addWidget(self.indices_list)

        indices_group.setLayout(indices_layout)
        layout.addWidget(indices_group)

        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()

        self.area_label = QLabel("Area: N/A")
        self.length_label = QLabel("Length: N/A")
        self.bounds_label = QLabel("Bounds: N/A")

        for label in [self.area_label, self.length_label, self.bounds_label]:
            label.setStyleSheet("padding: 2px 5px; font-size: 11px;")
            stats_layout.addWidget(label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Actions group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()

        # Export to region button
        self.export_btn = QPushButton("Export Selection to Region")
        self.export_btn.setToolTip("Create a new parametric region from selected faces")
        self.export_btn.clicked.connect(self.export_to_region_requested.emit)
        self.export_btn.setEnabled(False)
        actions_layout.addWidget(self.export_btn)

        # Copy indices button
        self.copy_btn = QPushButton("Copy Indices")
        self.copy_btn.setToolTip("Copy selected indices to clipboard")
        self.copy_btn.clicked.connect(self._copy_indices)
        self.copy_btn.setEnabled(False)
        actions_layout.addWidget(self.copy_btn)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # Add stretch to push everything to the top
        layout.addStretch()

    def update_selection(self, selection: Selection):
        """Update the panel with new selection data

        Args:
            selection: Selection object containing current selection state
        """
        self._current_selection = selection

        # Update mode
        mode_name = selection.mode.get_display_name()
        self.mode_label.setText(f"Mode: {mode_name}")

        # Update counts
        face_count = len(selection.faces) if selection.faces else 0
        edge_count = len(selection.edges) if selection.edges else 0
        vertex_count = len(selection.vertices) if selection.vertices else 0

        self.faces_label.setText(f"Faces: {face_count}")
        self.edges_label.setText(f"Edges: {edge_count}")
        self.vertices_label.setText(f"Vertices: {vertex_count}")

        # Update indices list
        self.indices_list.clear()

        if face_count > 0:
            self.indices_list.addItem("--- Faces ---")
            for face_id in sorted(selection.faces):
                self.indices_list.addItem(f"  Face {face_id}")

        if edge_count > 0:
            self.indices_list.addItem("--- Edges ---")
            for edge_id in sorted(selection.edges):
                self.indices_list.addItem(f"  Edge {edge_id}")

        if vertex_count > 0:
            self.indices_list.addItem("--- Vertices ---")
            for vertex_id in sorted(selection.vertices):
                self.indices_list.addItem(f"  Vertex {vertex_id}")

        if face_count == 0 and edge_count == 0 and vertex_count == 0:
            self.indices_list.addItem("(No selection)")

        # Enable/disable export button (only for face selections)
        self.export_btn.setEnabled(face_count > 0)
        self.copy_btn.setEnabled(face_count + edge_count + vertex_count > 0)

        # Update statistics (placeholder for now)
        # In the future, these will query the actual SubD geometry
        total_elements = face_count + edge_count + vertex_count
        if total_elements > 0:
            self.area_label.setText(f"Area: (requires geometry)")
            self.length_label.setText(f"Length: (requires geometry)")
            self.bounds_label.setText(f"Bounds: (requires geometry)")
        else:
            self.area_label.setText("Area: N/A")
            self.length_label.setText("Length: N/A")
            self.bounds_label.setText("Bounds: N/A")

    def _copy_indices(self):
        """Copy selected indices to clipboard"""
        if not self._current_selection:
            return

        from PyQt6.QtWidgets import QApplication

        lines = []

        if self._current_selection.faces:
            lines.append("Faces:")
            lines.append(", ".join(str(f) for f in sorted(self._current_selection.faces)))

        if self._current_selection.edges:
            lines.append("Edges:")
            lines.append(", ".join(str(e) for e in sorted(self._current_selection.edges)))

        if self._current_selection.vertices:
            lines.append("Vertices:")
            lines.append(", ".join(str(v) for v in sorted(self._current_selection.vertices)))

        text = "\n".join(lines)
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def clear(self):
        """Clear the selection display"""
        empty_selection = Selection(mode=EditMode.SOLID)
        self.update_selection(empty_selection)
