"""
Pytest configuration for Latent test suite.

Provides:
- PyQt6 availability checking
- Test environment setup
- Common fixtures
"""

import pytest
import sys

# Check if PyQt6 is available with full GUI support
PYQT6_AVAILABLE = False
try:
    from PyQt6.QtWidgets import QApplication
    PYQT6_AVAILABLE = True
except (ImportError, OSError):
    # OSError happens when Qt libraries are not available (e.g., no EGL)
    PYQT6_AVAILABLE = False


def pytest_collection_modifyitems(config, items):
    """
    Automatically skip tests that require PyQt6 if it's not available.
    """
    if not PYQT6_AVAILABLE:
        skip_pyqt = pytest.mark.skip(reason="PyQt6 not available or GUI support missing")
        for item in items:
            # Skip UI component tests when PyQt6 is not available
            if "test_ui_components" in item.nodeid:
                item.add_marker(skip_pyqt)
