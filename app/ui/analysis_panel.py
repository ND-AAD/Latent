"""
Analysis Panel Widget
Provides controls for selecting mathematical lenses and running analysis
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QRadioButton, QButtonGroup, QLabel, QGroupBox,
    QProgressBar, QComboBox
)
from PyQt6.QtCore import pyqtSignal, Qt


class AnalysisPanel(QWidget):
    """Panel for analysis controls and lens selection"""

    # Signals
    analysis_requested = pyqtSignal(str)  # lens_type
    lens_changed = pyqtSignal(str)  # lens_type

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_lens = "Flow"
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Mathematical Lens Selection
        lens_group = QGroupBox("Mathematical Lens")
        lens_layout = QVBoxLayout()

        self.lens_buttons = QButtonGroup()
        lenses = [
            ("Flow", "Geodesic flow analysis"),
            ("Spectral", "Vibration mode analysis"),
            ("Curvature", "Ridge/valley detection"),
            ("Topological", "Topological features")
        ]

        for i, (lens_name, tooltip) in enumerate(lenses):
            radio = QRadioButton(lens_name)
            radio.setToolTip(tooltip)
            if i == 0:
                radio.setChecked(True)
            self.lens_buttons.addButton(radio, i)
            lens_layout.addWidget(radio)

        # Connect lens selection
        self.lens_buttons.idClicked.connect(self._on_lens_changed)

        lens_group.setLayout(lens_layout)
        layout.addWidget(lens_group)

        # Analysis Controls
        controls_group = QGroupBox("Analysis")
        controls_layout = QVBoxLayout()

        # Analyze button
        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.setToolTip("Run analysis with selected lens")
        self.analyze_btn.clicked.connect(self._on_analyze_clicked)
        self.analyze_btn.setStyleSheet("""
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
        controls_layout.addWidget(self.analyze_btn)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        controls_layout.addWidget(self.progress_bar)

        # Analysis status label
        self.status_label = QLabel("Ready to analyze")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        self.status_label.setWordWrap(True)
        controls_layout.addWidget(self.status_label)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Advanced Options (collapsed by default)
        advanced_group = QGroupBox("Advanced Options")
        advanced_group.setCheckable(True)
        advanced_group.setChecked(False)
        advanced_layout = QVBoxLayout()

        # Resolution setting
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolution:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["Low", "Medium", "High", "Ultra"])
        self.resolution_combo.setCurrentIndex(1)  # Default to Medium
        res_layout.addWidget(self.resolution_combo)
        advanced_layout.addLayout(res_layout)

        # Minimum region size
        min_size_layout = QHBoxLayout()
        min_size_layout.addWidget(QLabel("Min Region Size:"))
        self.min_size_combo = QComboBox()
        self.min_size_combo.addItems(["Tiny", "Small", "Medium", "Large"])
        self.min_size_combo.setCurrentIndex(1)  # Default to Small
        min_size_layout.addWidget(self.min_size_combo)
        advanced_layout.addLayout(min_size_layout)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        layout.addStretch()

    def _on_lens_changed(self, button_id):
        """Handle lens selection change"""
        lens_names = ["Flow", "Spectral", "Curvature", "Topological"]
        if 0 <= button_id < len(lens_names):
            self.current_lens = lens_names[button_id]
            self.lens_changed.emit(self.current_lens)
            self.status_label.setText(f"Ready to analyze with {self.current_lens} lens")

    def _on_analyze_clicked(self):
        """Handle analyze button click"""
        self.analysis_requested.emit(self.current_lens)

    def set_analyzing(self, is_analyzing):
        """Set analyzing state (show/hide progress bar)"""
        self.analyze_btn.setEnabled(not is_analyzing)
        self.progress_bar.setVisible(is_analyzing)
        if is_analyzing:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.status_label.setText(f"Analyzing with {self.current_lens} lens...")
        else:
            self.status_label.setText(f"Ready to analyze with {self.current_lens} lens")

    def set_analysis_complete(self, num_regions):
        """Set analysis complete state"""
        self.set_analyzing(False)
        self.status_label.setText(f"✅ Found {num_regions} regions")

    def set_analysis_failed(self, error_msg):
        """Set analysis failed state"""
        self.set_analyzing(False)
        self.status_label.setText(f"❌ Analysis failed: {error_msg}")

    def get_current_lens(self):
        """Get the currently selected lens"""
        return self.current_lens

    def get_resolution(self):
        """Get the selected resolution setting"""
        return self.resolution_combo.currentText()

    def get_min_region_size(self):
        """Get the minimum region size setting"""
        return self.min_size_combo.currentText()

    def enable_analysis(self, enabled):
        """Enable/disable analysis button"""
        self.analyze_btn.setEnabled(enabled)
        if not enabled:
            self.status_label.setText("Load geometry before analyzing")
