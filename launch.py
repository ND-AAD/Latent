#!/usr/bin/env python3
"""
Quick launcher for Ceramic Mold Analyzer
Run this to start the application
"""

import subprocess
import sys
import os
import fcntl
from pathlib import Path

# Single instance check
lock_file = '/tmp/ceramic_mold_analyzer.lock'
fp = open(lock_file, 'w')
try:
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    print("Another instance is already running. Exiting.")
    sys.exit(0)

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import PyQt6
        return True
    except ImportError:
        return False

def main():
    print("=" * 60)
    print("CERAMIC MOLD ANALYZER")
    print("Desktop Application for Mathematical Mold Decomposition")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        print("\n⚠️  PyQt6 not found!")
        print("\nTo install dependencies:")
        print("1. Create virtual environment: python3 -m venv venv")
        print("2. Activate it: source venv/bin/activate")
        print("3. Install: pip install PyQt6")
        print("\nOr simply: pip install PyQt6")
        sys.exit(1)

    # Set Qt plugin path for PyQt6 to find platform plugins
    # This is needed for Anaconda environments on macOS
    try:
        import PyQt6
        pyqt6_path = Path(PyQt6.__file__).parent
        qt_plugin_path = pyqt6_path / "Qt6" / "plugins"
        if qt_plugin_path.exists():
            os.environ["QT_PLUGIN_PATH"] = str(qt_plugin_path)
            print("\n✅ Qt plugin path configured")
    except ImportError:
        pass

    # Launch the application
    print("✅ Dependencies found")
    print("🚀 Launching application...\n")

    app_path = Path(__file__).parent / "main.py"

    # Pass environment variables to subprocess explicitly
    env = os.environ.copy()
    if "QT_PLUGIN_PATH" in os.environ:
        print(f"📍 Using Qt plugin path: {os.environ['QT_PLUGIN_PATH']}")

    subprocess.run([sys.executable, str(app_path)], env=env)

if __name__ == "__main__":
    main()
