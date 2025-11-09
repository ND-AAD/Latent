"""
Tests for ConstraintPanel UI widget
"""

import pytest
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ui.constraint_panel import ConstraintPanel


# Mock cpp_core types for testing (until cpp_core is fully built)
class MockConstraintLevel:
    ERROR = 0
    WARNING = 1
    FEATURE = 2


class MockConstraintViolation:
    def __init__(self, level, description, face_id, severity):
        self.level = level
        self.description = description
        self.face_id = face_id
        self.severity = severity
        self.suggestion = ""


class MockConstraintReport:
    def __init__(self):
        self.violations = []

    def add_violation(self, level, description, face_id, severity):
        self.violations.append(
            MockConstraintViolation(level, description, face_id, severity)
        )


# Inject mocks into the module if cpp_core is not available
try:
    import cpp_core
except ImportError:
    import sys
    from unittest.mock import MagicMock

    cpp_core = MagicMock()
    cpp_core.ConstraintLevel = MockConstraintLevel
    cpp_core.ConstraintReport = MockConstraintReport
    sys.modules['cpp_core'] = cpp_core


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def constraint_panel(qapp):
    """Create ConstraintPanel instance for testing"""
    panel = ConstraintPanel()
    yield panel
    panel.close()


def test_constraint_panel_initialization(constraint_panel):
    """Test that constraint panel initializes properly"""
    assert constraint_panel is not None
    assert constraint_panel.tree is not None


def test_constraint_panel_has_tree_widget(constraint_panel):
    """Test that tree widget exists with correct headers"""
    assert constraint_panel.tree.columnCount() == 2
    assert constraint_panel.tree.headerItem().text(0) == "Description"
    assert constraint_panel.tree.headerItem().text(1) == "Severity"


def test_constraint_panel_empty_display(constraint_panel):
    """Test that panel starts empty"""
    assert constraint_panel.tree.topLevelItemCount() == 0


def test_constraint_panel_display_report_with_errors(constraint_panel):
    """Test displaying a report with errors"""
    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Undercut detected at edge 12",
        face_id=5,
        severity=0.85
    )
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Negative draft angle",
        face_id=7,
        severity=0.92
    )

    constraint_panel.display_report(report)

    # Should have 3 top-level items (Errors, Warnings, Features)
    assert constraint_panel.tree.topLevelItemCount() == 3

    # Get the Errors category
    errors_item = constraint_panel.tree.topLevelItem(0)
    assert "Errors" in errors_item.text(0)
    assert "(2)" in errors_item.text(0)  # Should show count
    assert errors_item.childCount() == 2  # Should have 2 error children


def test_constraint_panel_display_report_with_warnings(constraint_panel):
    """Test displaying a report with warnings"""
    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.WARNING,
        "Draft angle below recommended: 0.8°",
        face_id=3,
        severity=0.45
    )
    report.add_violation(
        MockConstraintLevel.WARNING,
        "Wall thickness below optimal: 2.5mm",
        face_id=4,
        severity=0.35
    )

    constraint_panel.display_report(report)

    # Get the Warnings category
    warnings_item = constraint_panel.tree.topLevelItem(1)
    assert "Warnings" in warnings_item.text(0)
    assert "(2)" in warnings_item.text(0)
    assert warnings_item.childCount() == 2


def test_constraint_panel_display_report_with_features(constraint_panel):
    """Test displaying a report with features"""
    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.FEATURE,
        "Mathematical tension at symmetry break",
        face_id=10,
        severity=0.75
    )

    constraint_panel.display_report(report)

    # Get the Features category
    features_item = constraint_panel.tree.topLevelItem(2)
    assert "Features" in features_item.text(0)
    assert "(1)" in features_item.text(0)
    assert features_item.childCount() == 1


def test_constraint_panel_display_mixed_report(constraint_panel):
    """Test displaying a report with all types of violations"""
    report = MockConstraintReport()

    # Add errors
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Critical error 1",
        face_id=1,
        severity=0.95
    )

    # Add warnings
    report.add_violation(
        MockConstraintLevel.WARNING,
        "Warning 1",
        face_id=2,
        severity=0.55
    )
    report.add_violation(
        MockConstraintLevel.WARNING,
        "Warning 2",
        face_id=3,
        severity=0.45
    )

    # Add features
    report.add_violation(
        MockConstraintLevel.FEATURE,
        "Feature 1",
        face_id=4,
        severity=0.70
    )

    constraint_panel.display_report(report)

    # Check counts
    errors_item = constraint_panel.tree.topLevelItem(0)
    warnings_item = constraint_panel.tree.topLevelItem(1)
    features_item = constraint_panel.tree.topLevelItem(2)

    assert "(1)" in errors_item.text(0)
    assert "(2)" in warnings_item.text(0)
    assert "(1)" in features_item.text(0)


def test_constraint_panel_severity_display(constraint_panel):
    """Test that severity values are displayed correctly"""
    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Test error",
        face_id=1,
        severity=0.856
    )

    constraint_panel.display_report(report)

    errors_item = constraint_panel.tree.topLevelItem(0)
    first_violation = errors_item.child(0)

    # Should display severity with 2 decimal places
    assert "0.86" in first_violation.text(1)


def test_constraint_panel_face_id_storage(constraint_panel):
    """Test that face IDs are stored in item data"""
    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Test error",
        face_id=42,
        severity=0.8
    )

    constraint_panel.display_report(report)

    errors_item = constraint_panel.tree.topLevelItem(0)
    first_violation = errors_item.child(0)

    # face_id should be stored in UserRole data
    stored_face_id = first_violation.data(0, Qt.ItemDataRole.UserRole)
    assert stored_face_id == 42


def test_constraint_panel_click_emits_signal(constraint_panel):
    """Test that clicking a violation emits signal with face_id"""
    signal_received = []

    def on_violation_selected(face_id):
        signal_received.append(face_id)

    constraint_panel.violation_selected.connect(on_violation_selected)

    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Test error",
        face_id=15,
        severity=0.8
    )

    constraint_panel.display_report(report)

    # Get the violation item and click it
    errors_item = constraint_panel.tree.topLevelItem(0)
    violation_item = errors_item.child(0)

    # Simulate click
    constraint_panel._on_item_clicked(violation_item, 0)

    # Signal should have been emitted with correct face_id
    assert len(signal_received) == 1
    assert signal_received[0] == 15


def test_constraint_panel_click_category_no_signal(constraint_panel):
    """Test that clicking a category header doesn't emit signal"""
    signal_received = []

    def on_violation_selected(face_id):
        signal_received.append(face_id)

    constraint_panel.violation_selected.connect(on_violation_selected)

    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Test error",
        face_id=15,
        severity=0.8
    )

    constraint_panel.display_report(report)

    # Click on the category header (not a violation)
    errors_item = constraint_panel.tree.topLevelItem(0)
    constraint_panel._on_item_clicked(errors_item, 0)

    # No signal should be emitted (category headers don't have face_id)
    assert len(signal_received) == 0


def test_constraint_panel_clear(constraint_panel):
    """Test clearing the constraint panel"""
    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Test error",
        face_id=1,
        severity=0.8
    )

    constraint_panel.display_report(report)
    assert constraint_panel.tree.topLevelItemCount() == 3

    constraint_panel.clear()
    assert constraint_panel.tree.topLevelItemCount() == 0


def test_constraint_panel_tree_expanded(constraint_panel):
    """Test that tree categories are expanded by default"""
    report = MockConstraintReport()
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Test error",
        face_id=1,
        severity=0.8
    )

    constraint_panel.display_report(report)

    # All categories should be expanded
    errors_item = constraint_panel.tree.topLevelItem(0)
    warnings_item = constraint_panel.tree.topLevelItem(1)
    features_item = constraint_panel.tree.topLevelItem(2)

    assert errors_item.isExpanded()
    assert warnings_item.isExpanded()
    assert features_item.isExpanded()


def test_constraint_panel_empty_categories(constraint_panel):
    """Test that empty categories show (0) count"""
    report = MockConstraintReport()
    # Add only one error, no warnings or features
    report.add_violation(
        MockConstraintLevel.ERROR,
        "Test error",
        face_id=1,
        severity=0.8
    )

    constraint_panel.display_report(report)

    errors_item = constraint_panel.tree.topLevelItem(0)
    warnings_item = constraint_panel.tree.topLevelItem(1)
    features_item = constraint_panel.tree.topLevelItem(2)

    assert "(1)" in errors_item.text(0)
    assert "(0)" in warnings_item.text(0)
    assert "(0)" in features_item.text(0)


def test_constraint_panel_color_coding(constraint_panel):
    """Test that violations are color-coded correctly"""
    report = MockConstraintReport()

    report.add_violation(
        MockConstraintLevel.ERROR,
        "Error",
        face_id=1,
        severity=0.9
    )

    report.add_violation(
        MockConstraintLevel.WARNING,
        "Warning",
        face_id=2,
        severity=0.5
    )

    report.add_violation(
        MockConstraintLevel.FEATURE,
        "Feature",
        face_id=3,
        severity=0.7
    )

    constraint_panel.display_report(report)

    # Get items
    errors_item = constraint_panel.tree.topLevelItem(0)
    warnings_item = constraint_panel.tree.topLevelItem(1)
    features_item = constraint_panel.tree.topLevelItem(2)

    # Check category colors
    error_color = errors_item.foreground(0).color()
    warning_color = warnings_item.foreground(0).color()
    feature_color = features_item.foreground(0).color()

    # Errors should be reddish
    assert error_color.red() > 150
    assert error_color.green() < 50

    # Warnings should be yellowish/orange
    assert warning_color.red() > 150
    assert warning_color.green() > 100

    # Features should be bluish
    assert feature_color.blue() > 150
    assert feature_color.red() < 50


def test_constraint_panel_signal_exists(constraint_panel):
    """Test that violation_selected signal is properly defined"""
    assert hasattr(constraint_panel, 'violation_selected')

    # Should be able to connect to the signal
    def dummy_handler(face_id):
        pass

    constraint_panel.violation_selected.connect(dummy_handler)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
