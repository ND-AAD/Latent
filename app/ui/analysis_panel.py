"""
Analysis Panel Widget
Provides controls for selecting mathematical lenses and running analysis.
Includes specialized controls for curvature analysis with histogram display and export.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QRadioButton, QButtonGroup, QLabel, QGroupBox,
    QProgressBar, QComboBox, QCheckBox, QDoubleSpinBox,
    QSlider, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
import numpy as np
from typing import Optional

# Matplotlib for histogram
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    FigureCanvasQTAgg = None
    Figure = None


class CurvatureHistogramWidget(QWidget):
    """Widget for displaying curvature histogram using matplotlib"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.curvature_data = None
        self.init_ui()

    def init_ui(self):
        """Initialize the histogram widget"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        if not MATPLOTLIB_AVAILABLE:
            label = QLabel("Matplotlib not available.\nInstall matplotlib to view histograms.")
            label.setStyleSheet("color: gray; font-style: italic;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(4, 2), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumHeight(150)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.axes = self.figure.add_subplot(111)
        self.axes.set_title("Curvature Distribution", fontsize=9)
        self.axes.set_xlabel("Curvature Value", fontsize=8)
        self.axes.set_ylabel("Frequency", fontsize=8)
        self.axes.tick_params(labelsize=7)
        self.figure.tight_layout()

        layout.addWidget(self.canvas)

        # Stats label
        self.stats_label = QLabel("No data")
        self.stats_label.setStyleSheet("font-size: 9px; color: gray;")
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)

    def update_histogram(self, data: np.ndarray, title: str = "Curvature Distribution"):
        """Update histogram with new curvature data"""
        if not MATPLOTLIB_AVAILABLE or data is None or len(data) == 0:
            return

        self.curvature_data = data

        # Clear previous plot
        self.axes.clear()

        # Compute histogram
        n_bins = min(50, max(10, len(data) // 10))
        counts, bins, patches = self.axes.hist(data, bins=n_bins, color='steelblue',
                                                 alpha=0.7, edgecolor='black', linewidth=0.5)

        # Add mean and median lines
        mean_val = np.mean(data)
        median_val = np.median(data)

        self.axes.axvline(mean_val, color='red', linestyle='--', linewidth=1.5,
                          label=f'Mean: {mean_val:.4f}')
        self.axes.axvline(median_val, color='green', linestyle='--', linewidth=1.5,
                          label=f'Median: {median_val:.4f}')

        self.axes.set_title(title, fontsize=9)
        self.axes.set_xlabel("Curvature Value", fontsize=8)
        self.axes.set_ylabel("Frequency", fontsize=8)
        self.axes.tick_params(labelsize=7)
        self.axes.legend(fontsize=7)
        self.axes.grid(True, alpha=0.3)

        self.figure.tight_layout()
        self.canvas.draw()

        # Update statistics
        std_val = np.std(data)
        min_val = np.min(data)
        max_val = np.max(data)

        stats_text = (f"Stats: min={min_val:.4f}, max={max_val:.4f}, "
                      f"std={std_val:.4f}, n={len(data)}")
        self.stats_label.setText(stats_text)

    def clear(self):
        """Clear the histogram"""
        if MATPLOTLIB_AVAILABLE:
            self.axes.clear()
            self.axes.set_title("Curvature Distribution", fontsize=9)
            self.axes.set_xlabel("Curvature Value", fontsize=8)
            self.axes.set_ylabel("Frequency", fontsize=8)
            self.figure.tight_layout()
            self.canvas.draw()
        self.stats_label.setText("No data")
        self.curvature_data = None


class AnalysisPanel(QWidget):
    """Panel for analysis controls and lens selection"""

    # Signals
    analysis_requested = pyqtSignal(str)  # lens_type
    lens_changed = pyqtSignal(str)  # lens_type
    curvature_type_changed = pyqtSignal(str)  # curvature_type: "mean", "gaussian", "k1", "k2"
    export_requested = pyqtSignal(str)  # export_type

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_lens = "Flow"
        self.curvature_data = None  # Store current curvature data for export
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
            if lens_name == "Curvature":  # Default to Curvature for Day 4
                radio.setChecked(True)
                self.current_lens = "Curvature"
            self.lens_buttons.addButton(radio, i)
            lens_layout.addWidget(radio)

        # Connect lens selection
        self.lens_buttons.idClicked.connect(self._on_lens_changed)

        lens_group.setLayout(lens_layout)
        layout.addWidget(lens_group)

        # Curvature-specific controls (shown only when Curvature lens selected)
        self.curvature_group = QGroupBox("Curvature Options")
        curvature_layout = QVBoxLayout()

        # Curvature type selection
        curv_type_layout = QHBoxLayout()
        curv_type_layout.addWidget(QLabel("Type:"))
        self.curvature_type_combo = QComboBox()
        self.curvature_type_combo.addItems([
            "Mean Curvature (H)",
            "Gaussian Curvature (K)",
            "Principal K1 (κ₁)",
            "Principal K2 (κ₂)"
        ])
        self.curvature_type_combo.setCurrentIndex(0)
        self.curvature_type_combo.currentIndexChanged.connect(self._on_curvature_type_changed)
        curv_type_layout.addWidget(self.curvature_type_combo)
        curvature_layout.addLayout(curv_type_layout)

        # Color map selection
        colormap_layout = QHBoxLayout()
        colormap_layout.addWidget(QLabel("Colormap:"))
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems([
            "viridis", "plasma", "coolwarm", "RdYlBu", "seismic",
            "turbo", "jet", "rainbow"
        ])
        self.colormap_combo.setCurrentIndex(2)  # Default to coolwarm
        colormap_layout.addWidget(self.colormap_combo)
        curvature_layout.addLayout(colormap_layout)

        # Auto-range checkbox
        self.auto_range_cb = QCheckBox("Auto Range")
        self.auto_range_cb.setChecked(True)
        self.auto_range_cb.toggled.connect(self._on_auto_range_toggled)
        curvature_layout.addWidget(self.auto_range_cb)

        # Manual range controls
        range_layout = QVBoxLayout()
        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("Min:"))
        self.range_min_spin = QDoubleSpinBox()
        self.range_min_spin.setRange(-1000.0, 1000.0)
        self.range_min_spin.setSingleStep(0.1)
        self.range_min_spin.setValue(-1.0)
        self.range_min_spin.setEnabled(False)
        min_layout.addWidget(self.range_min_spin)
        range_layout.addLayout(min_layout)

        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("Max:"))
        self.range_max_spin = QDoubleSpinBox()
        self.range_max_spin.setRange(-1000.0, 1000.0)
        self.range_max_spin.setSingleStep(0.1)
        self.range_max_spin.setValue(1.0)
        self.range_max_spin.setEnabled(False)
        max_layout.addWidget(self.range_max_spin)
        range_layout.addLayout(max_layout)
        curvature_layout.addLayout(range_layout)

        # Histogram display
        self.histogram_widget = CurvatureHistogramWidget()
        curvature_layout.addWidget(self.histogram_widget)

        # Export button
        self.export_btn = QPushButton("Export Curvature Data")
        self.export_btn.setToolTip("Export curvature values to CSV")
        self.export_btn.clicked.connect(self._on_export_clicked)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #30B350;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.export_btn.setEnabled(False)
        curvature_layout.addWidget(self.export_btn)

        self.curvature_group.setLayout(curvature_layout)
        layout.addWidget(self.curvature_group)
        # Initially show curvature options since it's the default
        self.curvature_group.setVisible(True)

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

            # Show/hide curvature-specific controls
            is_curvature = (self.current_lens == "Curvature")
            self.curvature_group.setVisible(is_curvature)

    def _on_curvature_type_changed(self, index):
        """Handle curvature type selection change"""
        curvature_types = ["mean", "gaussian", "k1", "k2"]
        if 0 <= index < len(curvature_types):
            self.curvature_type_changed.emit(curvature_types[index])

    def _on_auto_range_toggled(self, checked):
        """Handle auto-range checkbox toggle"""
        self.range_min_spin.setEnabled(not checked)
        self.range_max_spin.setEnabled(not checked)

    def _on_export_clicked(self):
        """Handle export button click"""
        if self.curvature_data is None:
            return

        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Curvature Data",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                self._export_curvature_to_csv(file_path)
                self.status_label.setText(f"✅ Exported to {file_path}")
            except Exception as e:
                self.status_label.setText(f"❌ Export failed: {str(e)}")

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

    # Curvature-specific methods

    def set_curvature_data(self, data: np.ndarray, curvature_type: str = "mean"):
        """
        Set curvature data and update histogram.

        Args:
            data: Array of curvature values
            curvature_type: Type of curvature ("mean", "gaussian", "k1", "k2")
        """
        self.curvature_data = data
        self.export_btn.setEnabled(True)

        # Update histogram
        type_names = {
            "mean": "Mean Curvature (H)",
            "gaussian": "Gaussian Curvature (K)",
            "k1": "Principal Curvature K1 (κ₁)",
            "k2": "Principal Curvature K2 (κ₂)"
        }
        title = type_names.get(curvature_type, "Curvature Distribution")
        self.histogram_widget.update_histogram(data, title)

        # Update range spinners if auto-range is enabled
        if self.auto_range_cb.isChecked() and data is not None and len(data) > 0:
            self.range_min_spin.setValue(float(np.min(data)))
            self.range_max_spin.setValue(float(np.max(data)))

    def clear_curvature_data(self):
        """Clear curvature data and histogram"""
        self.curvature_data = None
        self.export_btn.setEnabled(False)
        self.histogram_widget.clear()

    def get_curvature_type(self) -> str:
        """Get the currently selected curvature type"""
        index = self.curvature_type_combo.currentIndex()
        curvature_types = ["mean", "gaussian", "k1", "k2"]
        if 0 <= index < len(curvature_types):
            return curvature_types[index]
        return "mean"

    def get_colormap(self) -> str:
        """Get the currently selected colormap"""
        return self.colormap_combo.currentText()

    def get_curvature_range(self) -> tuple:
        """Get the curvature range (min, max)"""
        return (self.range_min_spin.value(), self.range_max_spin.value())

    def is_auto_range(self) -> bool:
        """Check if auto-range is enabled"""
        return self.auto_range_cb.isChecked()

    def _export_curvature_to_csv(self, file_path: str):
        """Export curvature data to CSV file"""
        if self.curvature_data is None:
            return

        import csv

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            curvature_type = self.get_curvature_type()
            writer.writerow(['Index', f'{curvature_type.upper()} Curvature'])

            # Write data
            for i, value in enumerate(self.curvature_data):
                writer.writerow([i, value])

            # Write statistics at the end
            writer.writerow([])
            writer.writerow(['Statistics', ''])
            writer.writerow(['Mean', np.mean(self.curvature_data)])
            writer.writerow(['Median', np.median(self.curvature_data)])
            writer.writerow(['Std Dev', np.std(self.curvature_data)])
            writer.writerow(['Min', np.min(self.curvature_data)])
            writer.writerow(['Max', np.max(self.curvature_data)])
            writer.writerow(['Count', len(self.curvature_data)])
