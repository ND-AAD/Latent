"""
Structure verification for ConstraintPanel (no Qt execution required)
This validates that the code is correctly structured even if Qt is not available.
"""

import ast
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def verify_constraint_panel_structure():
    """Verify the ConstraintPanel implementation has all required elements"""

    panel_file = Path(__file__).parent.parent / "app" / "ui" / "constraint_panel.py"

    with open(panel_file, 'r') as f:
        source = f.read()

    tree = ast.parse(source)

    # Track found elements
    found_elements = {
        'ConstraintPanel_class': False,
        'violation_selected_signal': False,
        'display_report_method': False,
        '_on_item_clicked_method': False,
        'clear_method': False,
        '_setup_ui_method': False,
        'tree_widget': False,
        'cpp_core_import': False,
        'QTreeWidget_import': False,
        'pyqtSignal_import': False,
    }

    # Check imports
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == 'PyQt6.QtWidgets':
                for alias in node.names:
                    if alias.name == 'QTreeWidget':
                        found_elements['QTreeWidget_import'] = True
            elif node.module == 'PyQt6.QtCore':
                for alias in node.names:
                    if alias.name == 'pyqtSignal':
                        found_elements['pyqtSignal_import'] = True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == 'cpp_core':
                    found_elements['cpp_core_import'] = True

    # Check class and methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name == 'ConstraintPanel':
                found_elements['ConstraintPanel_class'] = True

                # Check class body for signal and methods
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == 'violation_selected':
                                found_elements['violation_selected_signal'] = True

                    if isinstance(item, ast.FunctionDef):
                        if item.name == 'display_report':
                            found_elements['display_report_method'] = True
                            # Check it has the right parameter
                            if len(item.args.args) >= 2:  # self + report
                                # Check annotation mentions cpp_core.ConstraintReport
                                if item.args.args[1].annotation:
                                    annotation = ast.unparse(item.args.args[1].annotation)
                                    if 'ConstraintReport' in annotation:
                                        print("  ✓ display_report has correct signature")

                        elif item.name == '_on_item_clicked':
                            found_elements['_on_item_clicked_method'] = True

                        elif item.name == 'clear':
                            found_elements['clear_method'] = True

                        elif item.name == '_setup_ui':
                            found_elements['_setup_ui_method'] = True

                            # Check for tree widget creation
                            for stmt in ast.walk(item):
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute) and target.attr == 'tree':
                                            found_elements['tree_widget'] = True

    # Print results
    print("ConstraintPanel Structure Verification")
    print("=" * 50)

    all_passed = True
    for element, found in found_elements.items():
        status = "✓" if found else "✗"
        print(f"{status} {element.replace('_', ' ').title()}")
        if not found:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("✓ All required elements found!")
        return True
    else:
        print("✗ Some elements missing")
        return False


def verify_test_file_structure():
    """Verify the test file has proper structure"""

    test_file = Path(__file__).parent / "test_constraint_panel.py"

    with open(test_file, 'r') as f:
        source = f.read()

    tree = ast.parse(source)

    test_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            test_functions.append(node.name)

    print("\nTest File Structure Verification")
    print("=" * 50)
    print(f"Found {len(test_functions)} test functions:")
    for test in test_functions:
        print(f"  ✓ {test}")

    # Check for key tests
    key_tests = [
        'test_constraint_panel_initialization',
        'test_constraint_panel_display_report_with_errors',
        'test_constraint_panel_display_report_with_warnings',
        'test_constraint_panel_display_report_with_features',
        'test_constraint_panel_click_emits_signal',
        'test_constraint_panel_clear',
    ]

    print("\nKey Tests:")
    all_key_tests_found = True
    for key_test in key_tests:
        found = key_test in test_functions
        status = "✓" if found else "✗"
        print(f"{status} {key_test}")
        if not found:
            all_key_tests_found = False

    print("=" * 50)

    if all_key_tests_found:
        print("✓ All key tests present!")
        return True
    else:
        print("✗ Some key tests missing")
        return False


def verify_deliverables():
    """Verify all deliverables from the task file"""

    print("\nDeliverables Verification")
    print("=" * 50)

    deliverables = []

    # Check file exists
    panel_file = Path(__file__).parent.parent / "app" / "ui" / "constraint_panel.py"
    test_file = Path(__file__).parent / "test_constraint_panel.py"

    deliverables.append(("constraint_panel.py created", panel_file.exists()))
    deliverables.append(("test_constraint_panel.py created", test_file.exists()))

    # Check for 3-tier structure in code
    with open(panel_file, 'r') as f:
        content = f.read()

    deliverables.append(("ERROR level mentioned", "ERROR" in content))
    deliverables.append(("WARNING level mentioned", "WARNING" in content))
    deliverables.append(("FEATURE level mentioned", "FEATURE" in content))
    deliverables.append(("Tree widget used", "QTreeWidget" in content))
    deliverables.append(("Color coding (QColor)", "QColor" in content))
    deliverables.append(("violation_selected signal", "violation_selected" in content))

    all_passed = True
    for name, passed in deliverables:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("✓ All deliverables verified!")
        return True
    else:
        print("✗ Some deliverables not found")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("CONSTRAINT PANEL VERIFICATION")
    print("=" * 50 + "\n")

    results = []

    results.append(verify_constraint_panel_structure())
    results.append(verify_test_file_structure())
    results.append(verify_deliverables())

    print("\n" + "=" * 50)
    if all(results):
        print("✓✓✓ ALL VERIFICATIONS PASSED ✓✓✓")
        print("=" * 50)
        sys.exit(0)
    else:
        print("✗✗✗ SOME VERIFICATIONS FAILED ✗✗✗")
        print("=" * 50)
        sys.exit(1)
