"""
Spectral Visualization Widget - Interactive controls for eigenfunction analysis.

This widget provides user controls for:
- Selecting which eigenmode to visualize
- Toggling nodal line visibility
- Displaying eigenvalue information
- Extracting regions from eigenmodes

Author: Ceramic Mold Analyzer - Agent 36
Date: November 2025
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QSlider, QLabel, QCheckBox, QPushButton,
                             QComboBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional
from app.analysis.spectral_decomposition import EigenMode


class SpectralVizWidget(QWidget):
    """
    Interactive controls for spectral visualization.

    This widget allows users to:
    - Browse through different eigenmodes
    - View eigenvalue information
    - Toggle nodal line visualization
    - Extract regions from eigenfunction nodal domains

    Signals:
        mode_changed(int): Emitted when user selects different eigenmode (passes mode index)
        nodal_lines_toggled(bool): Emitted when nodal line visibility changes
        extract_regions_clicked(int): Emitted when user requests region extraction from mode
    """

    # Qt signals
    mode_changed = pyqtSignal(int)  # mode_index
    nodal_lines_toggled = pyqtSignal(bool)  # show_lines
    extract_regions_clicked = pyqtSignal(int)  # mode_index

    def __init__(self, parent=None):
        """Initialize the spectral visualization widget."""
        super().__init__(parent)

        # State
        self.modes: List[EigenMode] = []
        self.current_mode_idx = 0

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("Spectral Analysis")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Mode selection group
        mode_group = QGroupBox("Eigenmode Selection")
        mode_layout = QVBoxLayout()

        # Mode combo box
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Mode:"))

        self.mode_combo = QComboBox()
        self.mode_combo.setToolTip("Select eigenmode to visualize")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        combo_layout.addWidget(self.mode_combo, stretch=1)

        mode_layout.addLayout(combo_layout)

        # Eigenvalue display
        self.eigenvalue_label = QLabel("λ = 0.000000")
        self.eigenvalue_label.setStyleSheet("color: #666; font-family: monospace; font-size: 12px;")
        self.eigenvalue_label.setToolTip("Eigenvalue of current mode")
        mode_layout.addWidget(self.eigenvalue_label)

        # Mode slider (alternative navigation)
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Navigate:"))

        self.mode_slider = QSlider(Qt.Orientation.Horizontal)
        self.mode_slider.setMinimum(0)
        self.mode_slider.setMaximum(9)
        self.mode_slider.setToolTip("Navigate through eigenmodes")
        self.mode_slider.valueChanged.connect(self._on_slider_changed)
        slider_layout.addWidget(self.mode_slider, stretch=1)

        mode_layout.addLayout(slider_layout)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Visualization options
        viz_group = QGroupBox("Visualization Options")
        viz_layout = QVBoxLayout()

        # Nodal lines checkbox
        self.nodal_check = QCheckBox("Show Nodal Lines")
        self.nodal_check.setChecked(True)
        self.nodal_check.setToolTip("Display zero-crossing curves (nodal lines)")
        self.nodal_check.toggled.connect(self.nodal_lines_toggled.emit)
        viz_layout.addWidget(self.nodal_check)

        # Color bar info
        color_info = QLabel("Color: Blue (negative) → White (zero) → Red (positive)")
        color_info.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        color_info.setWordWrap(True)
        viz_layout.addWidget(color_info)

        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)

        # Region extraction
        extract_group = QGroupBox("Region Extraction")
        extract_layout = QVBoxLayout()

        extract_info = QLabel("Extract regions from nodal domains (connected areas of same sign).")
        extract_info.setStyleSheet("color: #666; font-size: 10px;")
        extract_info.setWordWrap(True)
        extract_layout.addWidget(extract_info)

        self.extract_btn = QPushButton("Extract Regions from Current Mode")
        self.extract_btn.setToolTip("Extract parametric regions from current eigenmode nodal domains")
        self.extract_btn.clicked.connect(self._on_extract_clicked)
        self.extract_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
            QPushButton:pressed {
                background-color: #003D99;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.extract_btn.setEnabled(False)  # Disabled until modes loaded
        extract_layout.addWidget(self.extract_btn)

        extract_group.setLayout(extract_layout)
        layout.addWidget(extract_group)

        # Mode statistics (read-only info)
        stats_group = QGroupBox("Mode Statistics")
        stats_layout = QVBoxLayout()

        self.stats_label = QLabel("No mode selected")
        self.stats_label.setStyleSheet("color: #666; font-size: 10px; font-family: monospace;")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        layout.addStretch()

    def set_modes(self, modes: List[EigenMode]):
        """
        Update available eigenmodes.

        Args:
            modes: List of EigenMode objects to display
        """
        self.modes = modes

        # Update combo box
        self.mode_combo.blockSignals(True)
        self.mode_combo.clear()
        for i, mode in enumerate(modes):
            label = f"Mode {i}: λ={mode.eigenvalue:.6f}"
            if mode.multiplicity > 1:
                label += f" (×{mode.multiplicity})"
            self.mode_combo.addItem(label)
        self.mode_combo.blockSignals(False)

        # Update slider range
        self.mode_slider.blockSignals(True)
        self.mode_slider.setMaximum(max(0, len(modes) - 1))
        self.mode_slider.blockSignals(False)

        # Select first non-trivial mode (skip mode 0 = constant)
        if len(modes) > 1:
            self.set_current_mode(1)
        elif len(modes) == 1:
            self.set_current_mode(0)

        # Enable extraction button if modes available
        self.extract_btn.setEnabled(len(modes) > 0)

    def set_current_mode(self, index: int):
        """
        Select eigenmode by index.

        Args:
            index: Mode index to select (0-indexed)
        """
        if 0 <= index < len(self.modes):
            self.current_mode_idx = index

            # Update UI controls
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentIndex(index)
            self.mode_combo.blockSignals(False)

            self.mode_slider.blockSignals(True)
            self.mode_slider.setValue(index)
            self.mode_slider.blockSignals(False)

            # Update eigenvalue display
            mode = self.modes[index]
            self.eigenvalue_label.setText(f"λ = {mode.eigenvalue:.6f}")

            # Update statistics
            self._update_statistics(mode)

    def _on_mode_changed(self, index: int):
        """Handle mode selection change from combo box."""
        if 0 <= index < len(self.modes):
            self.current_mode_idx = index

            # Sync slider
            self.mode_slider.blockSignals(True)
            self.mode_slider.setValue(index)
            self.mode_slider.blockSignals(False)

            # Update displays
            mode = self.modes[index]
            self.eigenvalue_label.setText(f"λ = {mode.eigenvalue:.6f}")
            self._update_statistics(mode)

            # Emit signal
            self.mode_changed.emit(index)

    def _on_slider_changed(self, value: int):
        """Handle mode selection change from slider."""
        if 0 <= value < len(self.modes):
            # Sync combo box
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentIndex(value)
            self.mode_combo.blockSignals(False)

            # Trigger mode change
            self._on_mode_changed(value)

    def _on_extract_clicked(self):
        """Handle extract regions button click."""
        if 0 <= self.current_mode_idx < len(self.modes):
            self.extract_regions_clicked.emit(self.current_mode_idx)

    def _update_statistics(self, mode: EigenMode):
        """Update statistics display for current mode."""
        ef = mode.eigenfunction

        # Compute statistics
        min_val = float(np.min(ef))
        max_val = float(np.max(ef))
        mean_val = float(np.mean(ef))
        std_val = float(np.std(ef))

        # Count sign changes (approximation of nodal domain count)
        sign_changes = int(np.sum(np.diff(np.sign(ef)) != 0))

        stats_text = (
            f"Index: {mode.index}\n"
            f"Eigenvalue: {mode.eigenvalue:.6f}\n"
            f"Multiplicity: {mode.multiplicity}\n"
            f"Range: [{min_val:.4f}, {max_val:.4f}]\n"
            f"Mean: {mean_val:.4f}, Std: {std_val:.4f}\n"
            f"Approx. sign changes: {sign_changes}\n"
            f"Vertices: {len(ef)}"
        )

        self.stats_label.setText(stats_text)

    def get_current_mode_index(self) -> int:
        """Get the currently selected mode index."""
        return self.current_mode_idx

    def get_show_nodal_lines(self) -> bool:
        """Check if nodal lines should be shown."""
        return self.nodal_check.isChecked()

    def clear(self):
        """Clear all modes and reset widget."""
        self.modes = []
        self.current_mode_idx = 0

        self.mode_combo.clear()
        self.mode_slider.setValue(0)
        self.eigenvalue_label.setText("λ = 0.000000")
        self.stats_label.setText("No mode selected")
        self.extract_btn.setEnabled(False)


# Import numpy for statistics
import numpy as np
