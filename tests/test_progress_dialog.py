"""
Tests for Progress Dialog UI

Verifies all success criteria:
- Progress bar updates correctly
- Status text descriptive
- Cancel button functional
- Modal dialog blocks interaction
"""

import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

# Ensure app module is importable
sys.path.insert(0, '/home/user/Latent')

from app.ui.progress_dialog import ProgressDialog


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def dialog(qapp):
    """Create a ProgressDialog instance."""
    dlg = ProgressDialog("Test Operation")
    yield dlg
    dlg.close()
    dlg.deleteLater()


class TestProgressDialogBasics:
    """Test basic dialog properties."""

    def test_dialog_creation(self, dialog):
        """Test dialog can be created."""
        assert dialog is not None
        assert dialog.windowTitle() == "Test Operation"

    def test_dialog_is_modal(self, dialog):
        """SUCCESS CRITERION: Modal dialog blocks interaction."""
        assert dialog.isModal() is True

    def test_dialog_minimum_width(self, dialog):
        """Test dialog has minimum width."""
        assert dialog.minimumWidth() == 400

    def test_initial_canceled_state(self, dialog):
        """Test canceled flag starts as False."""
        assert dialog.canceled is False


class TestProgressBarUpdates:
    """Test progress bar functionality."""

    def test_progress_bar_exists(self, dialog):
        """Test progress bar widget exists."""
        assert dialog.progress is not None

    def test_progress_bar_range(self, dialog):
        """Test progress bar has correct range."""
        assert dialog.progress.minimum() == 0
        assert dialog.progress.maximum() == 100

    def test_set_progress_updates_bar(self, dialog):
        """SUCCESS CRITERION: Progress bar updates correctly."""
        # Test various progress values
        test_values = [0, 25, 50, 75, 100]

        for value in test_values:
            dialog.set_progress(value)
            assert dialog.progress.value() == value

    def test_set_progress_without_status(self, dialog):
        """Test setting progress without status text."""
        initial_status = dialog.status_label.text()
        dialog.set_progress(50)
        # Status should remain unchanged
        assert dialog.status_label.text() == initial_status


class TestStatusText:
    """Test status label functionality."""

    def test_status_label_exists(self, dialog):
        """Test status label widget exists."""
        assert dialog.status_label is not None

    def test_initial_status_text(self, dialog):
        """Test initial status text."""
        assert dialog.status_label.text() == "Initializing..."

    def test_set_progress_updates_status(self, dialog):
        """SUCCESS CRITERION: Status text descriptive."""
        status_messages = [
            "Validating constraints...",
            "Fitting NURBS surfaces...",
            "Applying draft angles...",
            "Exporting mold geometry...",
            "Complete!"
        ]

        for i, status in enumerate(status_messages):
            dialog.set_progress(i * 20, status)
            assert dialog.status_label.text() == status

    def test_status_text_empty_string(self, dialog):
        """Test empty status string doesn't update label."""
        dialog.set_progress(50, "Test status")
        assert dialog.status_label.text() == "Test status"

        # Empty string should not update
        dialog.set_progress(75, "")
        assert dialog.status_label.text() == "Test status"


class TestCancelButton:
    """Test cancel button functionality."""

    def test_cancel_button_exists(self, dialog):
        """Test cancel button widget exists."""
        assert dialog.cancel_btn is not None

    def test_cancel_button_text(self, dialog):
        """Test cancel button has correct text."""
        assert dialog.cancel_btn.text() == "Cancel"

    def test_cancel_button_sets_flag(self, dialog):
        """SUCCESS CRITERION: Cancel button functional."""
        assert dialog.canceled is False

        # Simulate button click
        dialog.cancel_btn.click()

        assert dialog.canceled is True

    def test_cancel_button_closes_dialog(self, dialog):
        """Test cancel button closes the dialog."""
        dialog.show()
        assert dialog.isVisible()

        # Click cancel
        dialog.cancel_btn.click()

        # Dialog should be rejected (not accepted)
        assert not dialog.result()


class TestUsageScenario:
    """Test realistic usage scenarios."""

    def test_typical_mold_generation_workflow(self, dialog):
        """Test simulated mold generation progress."""
        steps = [
            (0, "Starting mold generation..."),
            (20, "Validating constraints..."),
            (40, "Fitting NURBS surfaces..."),
            (60, "Applying draft angles..."),
            (80, "Creating mold solids..."),
            (100, "Export complete!")
        ]

        for progress, status in steps:
            dialog.set_progress(progress, status)

            assert dialog.progress.value() == progress
            assert dialog.status_label.text() == status
            assert not dialog.canceled  # User hasn't canceled

    def test_user_cancellation_scenario(self, dialog):
        """Test user canceling during operation."""
        dialog.set_progress(30, "Processing...")

        # Simulate user clicking cancel mid-operation
        dialog.cancel_btn.click()

        # Check cancellation was registered
        assert dialog.canceled is True

    def test_custom_title(self, qapp):
        """Test dialog with custom title."""
        custom_dialog = ProgressDialog("Exporting Molds")
        assert custom_dialog.windowTitle() == "Exporting Molds"
        custom_dialog.close()
        custom_dialog.deleteLater()

    def test_default_title(self, qapp):
        """Test dialog with default title."""
        default_dialog = ProgressDialog()
        assert default_dialog.windowTitle() == "Processing..."
        default_dialog.close()
        default_dialog.deleteLater()


class TestIntegrationWithMainWindow:
    """Test integration scenarios."""

    def test_dialog_has_parent(self, qapp):
        """Test dialog can have parent widget."""
        from PyQt6.QtWidgets import QMainWindow

        parent = QMainWindow()
        dialog = ProgressDialog("Test", parent=parent)

        assert dialog.parent() == parent

        dialog.close()
        dialog.deleteLater()
        parent.close()
        parent.deleteLater()


def test_all_success_criteria(qapp):
    """
    Comprehensive test verifying ALL success criteria.

    Success Criteria:
    ✓ Progress bar updates correctly
    ✓ Status text descriptive
    ✓ Cancel button functional
    ✓ Modal dialog blocks interaction
    """
    dialog = ProgressDialog("Integration Test")

    # CRITERION 1: Progress bar updates correctly
    for value in range(0, 101, 10):
        dialog.set_progress(value)
        assert dialog.progress.value() == value
    print("✓ Progress bar updates correctly")

    # CRITERION 2: Status text descriptive
    descriptive_messages = [
        "Validating constraints...",
        "Fitting NURBS surfaces...",
        "Applying draft angles..."
    ]
    for msg in descriptive_messages:
        dialog.set_progress(50, msg)
        assert dialog.status_label.text() == msg
    print("✓ Status text descriptive")

    # CRITERION 3: Cancel button functional
    assert dialog.canceled is False
    dialog.cancel_btn.click()
    assert dialog.canceled is True
    print("✓ Cancel button functional")

    # CRITERION 4: Modal dialog blocks interaction
    assert dialog.isModal() is True
    print("✓ Modal dialog blocks interaction")

    dialog.close()
    dialog.deleteLater()

    print("\n✅ ALL SUCCESS CRITERIA VERIFIED")


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
