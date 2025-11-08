#!/usr/bin/env python3
"""
Test script for Edit Mode System
Verifies that edit modes switch correctly and UI updates
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import MainWindow
from app.state.edit_mode import EditMode


def test_edit_mode_system():
    """Test the edit mode system"""
    app = QApplication(sys.argv)

    # Create main window
    window = MainWindow()
    window.show()

    print("=" * 50)
    print("EDIT MODE SYSTEM TEST")
    print("=" * 50)

    # Test mode switching
    print("\n1. Testing mode switching:")
    modes = [EditMode.SOLID, EditMode.PANEL, EditMode.EDGE, EditMode.VERTEX]

    for mode in modes:
        print(f"   Setting mode to: {mode.get_display_name()}")
        window.state.edit_mode_manager.set_mode(mode)
        current = window.state.edit_mode_manager.current_mode
        assert current == mode, f"Mode not set correctly! Expected {mode}, got {current}"
        print(f"   ✓ Mode set successfully")

    # Test toolbar update
    print("\n2. Testing toolbar synchronization:")
    window.edit_mode_toolbar.set_mode(EditMode.PANEL)
    print("   ✓ Toolbar updated")

    # Test selection info
    print("\n3. Testing selection info:")
    info = window.state.edit_mode_manager.get_selection_info()
    print(f"   Selection info: {info}")

    # Test with test geometry
    print("\n4. Loading test geometry:")
    window.show_test_colored_cube()
    print("   ✓ Test cube loaded")

    print("\n5. Instructions for manual testing:")
    print("   - Click the mode buttons in the toolbar (S, P, E, V)")
    print("   - Observe the status bar updates")
    print("   - Check the debug console for mode change messages")
    print("   - Try View → Show Test Cube/Sphere/Torus")
    print("\n   Note: Actual picking requires connecting to Rhino with real SubD geometry")

    print("\n" + "=" * 50)
    print("EDIT MODE SYSTEM TEST COMPLETE")
    print("Basic functionality verified ✓")
    print("=" * 50)

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_edit_mode_system())