"""
Test for Analysis Panel UI with Curvature Controls

Tests the enhanced analysis panel with:
- Curvature type selection
- Histogram display
- Export functionality
- Color mapping controls

Run with: python3 tests/test_analysis_panel_ui.py
"""

import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

# Add parent directory to path
sys.path.insert(0, '/home/user/Latent')

from app.ui.analysis_panel import AnalysisPanel


class TestWindow(QMainWindow):
    """Test window for analysis panel"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analysis Panel Test - Agent 31")
        self.setGeometry(100, 100, 500, 800)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Create analysis panel
        self.panel = AnalysisPanel()
        layout.addWidget(self.panel)

        # Connect signals
        self.panel.analysis_requested.connect(self.on_analysis_requested)
        self.panel.lens_changed.connect(self.on_lens_changed)
        self.panel.curvature_type_changed.connect(self.on_curvature_type_changed)

        # Simulate curvature data after a delay
        QTimer.singleShot(1000, self.simulate_curvature_data)

    def on_analysis_requested(self, lens_type):
        """Handle analysis request"""
        print(f"Analysis requested with lens: {lens_type}")
        self.panel.set_analyzing(True)

        # Simulate analysis completion after 2 seconds
        QTimer.singleShot(2000, lambda: self.complete_analysis())

    def on_lens_changed(self, lens_type):
        """Handle lens change"""
        print(f"Lens changed to: {lens_type}")

    def on_curvature_type_changed(self, curvature_type):
        """Handle curvature type change"""
        print(f"Curvature type changed to: {curvature_type}")

        # Update histogram with new data based on type
        if hasattr(self, 'current_data'):
            # Simulate different curvature types
            if curvature_type == "mean":
                data = self.current_data
            elif curvature_type == "gaussian":
                data = self.current_data ** 2  # K ≈ H² for sphere
            elif curvature_type == "k1":
                data = self.current_data * 0.9
            elif curvature_type == "k2":
                data = self.current_data * 1.1
            else:
                data = self.current_data

            self.panel.set_curvature_data(data, curvature_type)

    def simulate_curvature_data(self):
        """Simulate curvature computation results"""
        print("Simulating curvature data...")

        # Generate synthetic curvature data
        # Simulate a sphere: H = 1/r, K = 1/r²
        # For unit sphere: H = 1.0, K = 1.0
        # Add some noise to make it realistic
        n_points = 1000
        mean_curvature = np.random.normal(1.0, 0.1, n_points)
        self.current_data = mean_curvature

        # Set the data in the panel
        self.panel.set_curvature_data(mean_curvature, "mean")
        print(f"Loaded {len(mean_curvature)} curvature values")
        print(f"Mean: {np.mean(mean_curvature):.4f}")
        print(f"Std: {np.std(mean_curvature):.4f}")

    def complete_analysis(self):
        """Complete the analysis simulation"""
        self.panel.set_analysis_complete(5)
        print("Analysis complete!")


def test_analysis_panel_ui():
    """Test the analysis panel UI"""
    print("=" * 60)
    print("AGENT 31: Analysis Panel UI Test")
    print("=" * 60)

    app = QApplication(sys.argv)

    window = TestWindow()
    window.show()

    print("\nTest Instructions:")
    print("1. Check that Curvature lens is selected by default")
    print("2. Verify histogram displays with mean/median lines")
    print("3. Try changing curvature type (Mean, Gaussian, K1, K2)")
    print("4. Try changing colormap")
    print("5. Toggle auto-range and adjust min/max values")
    print("6. Click 'Export Curvature Data' to test export")
    print("7. Switch to other lenses - curvature controls should hide")
    print("8. Click 'Analyze' button to test analysis workflow")
    print("\nPress Ctrl+C to exit")
    print("-" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    test_analysis_panel_ui()
