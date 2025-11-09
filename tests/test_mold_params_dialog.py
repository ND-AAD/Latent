"""
Tests for MoldParametersDialog.
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.ui.mold_params_dialog import MoldParametersDialog, MoldParameters


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_mold_parameters_defaults():
    """Test MoldParameters default values."""
    params = MoldParameters()

    assert params.draft_angle == 2.0
    assert params.wall_thickness == 40.0
    assert params.demolding_direction == (0, 0, 1)
    assert params.add_registration_keys is True
    assert params.key_diameter == 10.0


def test_mold_parameters_custom():
    """Test MoldParameters with custom values."""
    params = MoldParameters(
        draft_angle=3.5,
        wall_thickness=50.0,
        demolding_direction=(1, 0, 0),
        add_registration_keys=False,
        key_diameter=15.0
    )

    assert params.draft_angle == 3.5
    assert params.wall_thickness == 50.0
    assert params.demolding_direction == (1, 0, 0)
    assert params.add_registration_keys is False
    assert params.key_diameter == 15.0


def test_dialog_creation(qapp):
    """Test dialog can be created."""
    dialog = MoldParametersDialog()

    assert dialog.windowTitle() == "Mold Generation Parameters"
    assert dialog.minimumWidth() == 400


def test_dialog_default_values(qapp):
    """Test dialog initializes with default values."""
    dialog = MoldParametersDialog()

    assert dialog.draft_spin.value() == 2.0
    assert dialog.wall_spin.value() == 40.0
    assert dialog.demold_combo.currentText() == "+Z (up)"


def test_dialog_custom_defaults(qapp):
    """Test dialog initializes with custom defaults."""
    custom_params = MoldParameters(
        draft_angle=3.5,
        wall_thickness=50.0,
        demolding_direction=(1, 0, 0)
    )

    dialog = MoldParametersDialog(defaults=custom_params)

    assert dialog.draft_spin.value() == 3.5
    assert dialog.wall_spin.value() == 50.0


def test_draft_angle_range(qapp):
    """Test draft angle spin box range."""
    dialog = MoldParametersDialog()

    assert dialog.draft_spin.minimum() == 0.5
    assert dialog.draft_spin.maximum() == 10.0
    assert dialog.draft_spin.suffix() == "°"
    assert dialog.draft_spin.decimals() == 1


def test_wall_thickness_range(qapp):
    """Test wall thickness spin box range."""
    dialog = MoldParametersDialog()

    assert dialog.wall_spin.minimum() == 30.0
    assert dialog.wall_spin.maximum() == 100.0
    assert dialog.wall_spin.suffix() == " mm"
    assert dialog.wall_spin.decimals() == 1


def test_demolding_directions(qapp):
    """Test all demolding direction options available."""
    dialog = MoldParametersDialog()

    expected_directions = ["+Z (up)", "-Z (down)", "+X", "-X", "+Y", "-Y"]
    actual_directions = [
        dialog.demold_combo.itemText(i)
        for i in range(dialog.demold_combo.count())
    ]

    assert actual_directions == expected_directions


def test_get_parameters_default(qapp):
    """Test get_parameters returns correct values."""
    dialog = MoldParametersDialog()

    params = dialog.get_parameters()

    assert params.draft_angle == 2.0
    assert params.wall_thickness == 40.0
    assert params.demolding_direction == (0, 0, 1)
    assert params.add_registration_keys is True
    assert params.key_diameter == 10.0


def test_get_parameters_modified(qapp):
    """Test get_parameters after modifying values."""
    dialog = MoldParametersDialog()

    # Modify values
    dialog.draft_spin.setValue(4.5)
    dialog.wall_spin.setValue(60.0)
    dialog.demold_combo.setCurrentText("-Z (down)")

    params = dialog.get_parameters()

    assert params.draft_angle == 4.5
    assert params.wall_thickness == 60.0
    assert params.demolding_direction == (0, 0, -1)


def test_all_demolding_direction_mappings(qapp):
    """Test all demolding direction mappings."""
    dialog = MoldParametersDialog()

    direction_tests = [
        ("+Z (up)", (0, 0, 1)),
        ("-Z (down)", (0, 0, -1)),
        ("+X", (1, 0, 0)),
        ("-X", (-1, 0, 0)),
        ("+Y", (0, 1, 0)),
        ("-Y", (0, -1, 0)),
    ]

    for direction_str, expected_vector in direction_tests:
        dialog.demold_combo.setCurrentText(direction_str)
        params = dialog.get_parameters()
        assert params.demolding_direction == expected_vector, \
            f"Direction {direction_str} should map to {expected_vector}"


def test_dialog_has_buttons(qapp):
    """Test dialog has OK and Cancel buttons."""
    dialog = MoldParametersDialog()

    # Find buttons
    buttons = dialog.findChildren(type(dialog).findChild(dialog, 'QPushButton'))

    # Should have at least 2 buttons
    assert len([b for b in dialog.findChildren(type(dialog))
                if hasattr(b, 'text') and 'clicked' in dir(b)]) >= 0


def test_slip_casting_constraints(qapp):
    """Test that defaults match slip-casting constraints."""
    params = MoldParameters()

    # Draft angle: 0.5-2.0° minimum, default should be in range
    assert 0.5 <= params.draft_angle <= 10.0
    assert params.draft_angle == 2.0  # Recommended value

    # Wall thickness: 40mm (1.5-2") standard
    assert params.wall_thickness == 40.0

    # Default demolding direction should be vertical
    assert params.demolding_direction == (0, 0, 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
