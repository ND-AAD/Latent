#!/usr/bin/env python3
"""
Verify ProgressDialog can be imported correctly from app.ui module.
"""

import sys
sys.path.insert(0, '/home/user/Latent')

print("=" * 60)
print("PROGRESS DIALOG IMPORT VERIFICATION")
print("=" * 60)

# Test 1: Direct import
print("\n[1] Testing direct import from app.ui.progress_dialog...")
try:
    from app.ui.progress_dialog import ProgressDialog
    print("✓ Direct import successful")
except ImportError as e:
    print(f"❌ Direct import failed: {e}")
    sys.exit(1)

# Test 2: Module-level import
print("\n[2] Testing module-level import from app.ui...")
try:
    from app.ui import ProgressDialog as PD
    print("✓ Module-level import successful")
except ImportError as e:
    print(f"❌ Module-level import failed: {e}")
    sys.exit(1)

# Test 3: Verify same class
print("\n[3] Verifying both imports reference same class...")
if ProgressDialog is PD:
    print("✓ Both imports reference the same class")
else:
    print("❌ Imports reference different classes!")
    sys.exit(1)

# Test 4: Check class attributes
print("\n[4] Checking class has required methods...")
required_methods = ['__init__', '_setup_ui', 'set_progress', '_on_cancel']
for method in required_methods:
    if hasattr(ProgressDialog, method):
        print(f"✓ Method '{method}' exists")
    else:
        print(f"❌ Missing method '{method}'")
        sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL IMPORT TESTS PASSED")
print("=" * 60)
print("\nBoth import styles work correctly:")
print("  from app.ui.progress_dialog import ProgressDialog")
print("  from app.ui import ProgressDialog")
print("\nProgressDialog is ready for use!")
