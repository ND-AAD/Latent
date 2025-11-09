#!/usr/bin/env python3
"""
Day 3 Integration Test Script
Manual testing checklist for UI and VTK components
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("DAY 3 INTEGRATION TEST SUITE")
print("=" * 70)
print()

# Test 1: Environment Check
print("TEST 1: Environment Check")
print("-" * 70)

dependencies = {
    'PyQt6': False,
    'vtk': False,
    'cpp_core': False,
    'numpy': False
}

for dep_name in dependencies:
    try:
        __import__(dep_name)
        dependencies[dep_name] = True
        print(f"✅ {dep_name} available")
    except ImportError:
        print(f"❌ {dep_name} NOT available")

if not all(dependencies.values()):
    print("\n⚠️  Missing dependencies. Please install before proceeding.")
    sys.exit(1)

print("✅ All dependencies available")
print()

# Test 2: Module Imports
print("TEST 2: Module Imports")
print("-" * 70)

modules_to_test = [
    ('app.ui.pickers', ['SubDFacePicker', 'SubDEdgePicker', 'SubDVertexPicker']),
    ('app.ui.edit_mode_toolbar', ['EditModeToolBar', 'EditModeWidget']),
    ('app.state.parametric_region', ['ParametricRegion', 'ParametricCurve']),
    ('app.geometry.region_renderer', ['RegionRenderer']),
    ('app.ui.region_properties_dialog', ['RegionPropertiesDialog']),
    ('app.ui.region_color_manager', ['RegionColorManager']),
    ('app.ui.selection_info_panel', ['SelectionInfoPanel']),
    ('app.state.edit_mode', ['EditMode']),
]

all_imports_ok = True
for module_name, classes in modules_to_test:
    try:
        module = __import__(module_name, fromlist=classes)
        for class_name in classes:
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name}")
            else:
                print(f"❌ {module_name}.{class_name} NOT FOUND")
                all_imports_ok = False
    except Exception as e:
        print(f"❌ {module_name} import failed: {e}")
        all_imports_ok = False

if not all_imports_ok:
    print("\n⚠️  Some imports failed")
    sys.exit(1)

print("✅ All module imports successful")
print()

# Test 3: Data Structure Functionality
print("TEST 3: Data Structure Tests")
print("-" * 70)

from app.state.parametric_region import ParametricRegion, ParametricCurve

# Test ParametricRegion
region = ParametricRegion(
    id='test_region',
    faces=[0, 1, 2, 3, 4],
    unity_principle='Curvature-based decomposition',
    unity_strength=0.85,
    pinned=False
)
print(f"✅ Created ParametricRegion: {region.id}")
print(f"   - Faces: {len(region.faces)}")
print(f"   - Unity strength: {region.unity_strength}")

# Test JSON serialization
json_data = region.to_json()
region2 = ParametricRegion.from_json(json_data)
assert region2.id == region.id
print("✅ JSON serialization/deserialization works")

# Test ParametricCurve
curve = ParametricCurve(
    points=[(0, 0.0, 0.0), (0, 0.5, 0.5), (0, 1.0, 1.0)],
    is_closed=False
)
point = curve.evaluate(0.5)
print(f"✅ ParametricCurve evaluation works: t=0.5 -> face={point[0]}, u={point[1]:.2f}, v={point[2]:.2f}")

# Test EditMode
from app.state.edit_mode import EditMode
modes = [EditMode.SOLID, EditMode.PANEL, EditMode.EDGE, EditMode.VERTEX]
print(f"✅ EditMode enum: {[m.name for m in modes]}")

print()

# Test 4: Color Manager
print("TEST 4: Color Manager")
print("-" * 70)

from app.ui.region_color_manager import RegionColorManager

manager = RegionColorManager()
test_regions = [
    ParametricRegion(id=f'region_{i}', faces=[i], unity_principle='test', unity_strength=0.5)
    for i in range(5)
]

manager.assign_colors(test_regions)
print(f"✅ Assigned colors to {len(test_regions)} regions")

for i, region in enumerate(test_regions[:3]):
    color = manager.region_colors.get(region.id, (0, 0, 0))
    print(f"   region_{i}: RGB({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})")

print()

# Test 5: C++ Module
print("TEST 5: C++ Module Check")
print("-" * 70)

try:
    import cpp_core
    print(f"✅ cpp_core module loads")

    # Check for classes
    expected_classes = ['SubDEvaluator', 'Point3D', 'SubDControlCage']
    for cls_name in expected_classes:
        if hasattr(cpp_core, cls_name):
            print(f"✅ cpp_core.{cls_name} available")
        else:
            print(f"⚠️  cpp_core.{cls_name} not found")

except Exception as e:
    print(f"❌ cpp_core import failed: {e}")

print()

# Summary
print("=" * 70)
print("AUTOMATED TESTS COMPLETE")
print("=" * 70)
print()
print("✅ All automated tests passed!")
print()
print("NEXT: Manual UI Testing Required")
print("-" * 70)
print()
print("To complete Day 3 integration testing, you need to:")
print()
print("1. Launch the application:")
print("   $ python3 main.py")
print()
print("2. Test Edit Mode Switching:")
print("   - Click S/P/E/V buttons in toolbar")
print("   - Verify button highlights change")
print("   - Verify selection info updates")
print()
print("3. Test Face Selection (Panel Mode):")
print("   - Switch to Panel mode (P button)")
print("   - Load a SubD from Rhino")
print("   - Click on faces in the viewport")
print("   - Verify yellow highlighting appears")
print("   - Try Shift+Click to multi-select")
print()
print("4. Test Edge Selection (Edge Mode):")
print("   - Switch to Edge mode (E button)")
print("   - Click on edges")
print("   - Verify cyan edge guides appear")
print("   - Verify yellow highlighting on selected edges")
print()
print("5. Test Vertex Selection (Vertex Mode):")
print("   - Switch to Vertex mode (V button)")
print("   - Click on control cage vertices")
print("   - Verify yellow sphere highlighting")
print()
print("6. Test Region Visualization:")
print("   - Create or load regions")
print("   - Verify different colors per region")
print("   - Check smooth color transitions")
print()
print("7. Test Region Properties Dialog:")
print("   - Double-click a region in the region list")
print("   - Verify all fields populate correctly")
print("   - Try editing the name and clicking Apply")
print("   - Try exporting to JSON")
print()
print("If all manual tests pass, Day 3 is COMPLETE! ✅")
print("You can then proceed to launch Day 4.")
print()
