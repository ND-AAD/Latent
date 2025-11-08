#!/usr/bin/env python3
"""
Test that left click no longer orbits with the final fix
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ui.viewport_3d import Viewport3D


def test_fixed_controls():
    """Test the fixed mouse controls"""
    app = QApplication(sys.argv)

    # Create simple window
    window = QMainWindow()
    window.setWindowTitle("FINAL FIX TEST - Left Click Should NOT Rotate")
    window.setGeometry(100, 100, 800, 600)

    # Create central widget with layout
    central = QWidget()
    layout = QVBoxLayout(central)

    # Add instruction label
    label = QLabel("""
    <h2>Mouse Controls Test - FINAL FIX</h2>
    <p><b>LEFT click and drag</b> - Should NOT rotate (for selection)</p>
    <p><b>RIGHT click and drag</b> - Should rotate view</p>
    <p><b>MIDDLE click and drag</b> - Should also rotate view</p>
    <p><b>Shift + RIGHT drag</b> - Should pan</p>
    <p><b>Mouse wheel</b> - Should zoom</p>
    """)
    layout.addWidget(label)

    # Create viewport
    viewport = Viewport3D()
    layout.addWidget(viewport)

    # Add test geometry
    viewport.create_test_cube()

    window.setCentralWidget(central)
    window.show()

    print("\n" + "="*60)
    print("FINAL FIX TEST")
    print("="*60)
    print("LEFT click and drag should NOT rotate the view!")
    print("If it still rotates, the issue is not fully fixed.")
    print("="*60 + "\n")

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_fixed_controls())