# app/ui/mold_params_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                             QDoubleSpinBox, QPushButton, QComboBox,
                             QLabel, QGroupBox, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from dataclasses import dataclass
from typing import Optional

from app.utils.error_handling import get_logger

logger = get_logger(__name__)


@dataclass
class MoldParameters:
    """Mold generation parameters."""
    draft_angle: float = 2.0  # degrees
    wall_thickness: float = 40.0  # mm
    demolding_direction: tuple = (0, 0, 1)  # (x, y, z)
    add_registration_keys: bool = True
    key_diameter: float = 10.0  # mm


class MoldParametersDialog(QDialog):
    """
    Dialog for configuring mold generation parameters.

    Integrates slip-casting constraints:
    - Draft angle: 0.5-2.0° minimum
    - Wall thickness: 40mm (1.5-2") standard
    """

    # Signal emitted when validation fails
    validation_failed = pyqtSignal(str)  # error message

    def __init__(self, parent=None, defaults: MoldParameters = None):
        super().__init__(parent)

        self.params = defaults or MoldParameters()
        self.validation_errors = []
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Mold Generation Parameters")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Draft angle
        draft_group = QGroupBox("Draft Angle")
        draft_layout = QFormLayout()

        self.draft_spin = QDoubleSpinBox()
        self.draft_spin.setRange(0.5, 10.0)
        self.draft_spin.setValue(self.params.draft_angle)
        self.draft_spin.setSuffix("°")
        self.draft_spin.setDecimals(1)
        self.draft_spin.valueChanged.connect(self._validate_draft_angle)
        draft_layout.addRow("Angle:", self.draft_spin)

        draft_info = QLabel("Minimum: 0.5° (rigid plaster)\nRecommended: 2.0°")
        draft_info.setStyleSheet("color: #666; font-size: 10px;")
        draft_layout.addRow("", draft_info)

        draft_group.setLayout(draft_layout)
        layout.addWidget(draft_group)

        # Wall thickness
        wall_group = QGroupBox("Wall Thickness")
        wall_layout = QFormLayout()

        self.wall_spin = QDoubleSpinBox()
        self.wall_spin.setRange(30.0, 100.0)
        self.wall_spin.setValue(self.params.wall_thickness)
        self.wall_spin.setSuffix(" mm")
        self.wall_spin.setDecimals(1)
        self.wall_spin.valueChanged.connect(self._validate_wall_thickness)
        wall_layout.addRow("Thickness:", self.wall_spin)

        wall_info = QLabel("Standard: 40mm (1.5-2 inches)")
        wall_info.setStyleSheet("color: #666; font-size: 10px;")
        wall_layout.addRow("", wall_info)

        wall_group.setLayout(wall_layout)
        layout.addWidget(wall_group)

        # Demolding direction
        demold_group = QGroupBox("Demolding Direction")
        demold_layout = QFormLayout()

        self.demold_combo = QComboBox()
        self.demold_combo.addItems(["+Z (up)", "-Z (down)", "+X", "-X", "+Y", "-Y"])
        demold_layout.addRow("Direction:", self.demold_combo)

        demold_group.setLayout(demold_layout)
        layout.addWidget(demold_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.ok_btn = QPushButton("Generate Molds")
        self.ok_btn.clicked.connect(self._on_accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(self.ok_btn)

        layout.addLayout(button_layout)

        # Initial validation
        self._validate_all()

    def _validate_draft_angle(self, value: float):
        """Validate draft angle value."""
        if value < 0.5:
            self.draft_spin.setStyleSheet("QDoubleSpinBox { background-color: #ffcccc; }")
            logger.warning(f"Draft angle {value}° below minimum 0.5°")
        elif value < 2.0:
            self.draft_spin.setStyleSheet("QDoubleSpinBox { background-color: #ffffcc; }")
            logger.info(f"Draft angle {value}° below recommended 2.0°")
        else:
            self.draft_spin.setStyleSheet("")

    def _validate_wall_thickness(self, value: float):
        """Validate wall thickness value."""
        if value < 30.0:
            self.wall_spin.setStyleSheet("QDoubleSpinBox { background-color: #ffcccc; }")
            logger.warning(f"Wall thickness {value}mm below minimum 30mm")
        elif value < 40.0 or value > 60.0:
            self.wall_spin.setStyleSheet("QDoubleSpinBox { background-color: #ffffcc; }")
            logger.info(f"Wall thickness {value}mm outside recommended range 40-60mm")
        else:
            self.wall_spin.setStyleSheet("")

    def _validate_all(self) -> bool:
        """
        Validate all parameters.

        Returns:
            True if all parameters valid
        """
        self.validation_errors.clear()

        # Validate draft angle
        draft = self.draft_spin.value()
        if draft < 0.5:
            self.validation_errors.append(
                f"Draft angle {draft}° is below minimum 0.5° (demolding may be impossible)"
            )
        elif draft > 10.0:
            self.validation_errors.append(
                f"Draft angle {draft}° is very high (may distort form significantly)"
            )

        # Validate wall thickness
        wall = self.wall_spin.value()
        if wall < 30.0:
            self.validation_errors.append(
                f"Wall thickness {wall}mm is below minimum 30mm (structural integrity risk)"
            )
        elif wall > 100.0:
            self.validation_errors.append(
                f"Wall thickness {wall}mm is excessive (material waste, slow drying)"
            )

        return len(self.validation_errors) == 0

    def _on_accept(self):
        """Handle dialog acceptance with validation."""
        if not self._validate_all():
            # Show validation errors
            error_msg = "Parameter validation issues:\n\n" + "\n".join(
                f"• {err}" for err in self.validation_errors
            )

            reply = QMessageBox.warning(
                self,
                "Parameter Validation",
                error_msg + "\n\nContinue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                logger.info("User cancelled due to validation warnings")
                return

            logger.warning("User proceeded despite validation warnings")

        # Validation passed or user confirmed
        logger.info("Mold parameters accepted")
        self.accept()

    def get_parameters(self) -> MoldParameters:
        """
        Get configured parameters.

        Returns:
            MoldParameters with validated values
        """
        # Parse demolding direction
        direction_map = {
            "+Z (up)": (0, 0, 1),
            "-Z (down)": (0, 0, -1),
            "+X": (1, 0, 0),
            "-X": (-1, 0, 0),
            "+Y": (0, 1, 0),
            "-Y": (0, -1, 0)
        }

        direction_str = self.demold_combo.currentText()

        params = MoldParameters(
            draft_angle=self.draft_spin.value(),
            wall_thickness=self.wall_spin.value(),
            demolding_direction=direction_map.get(direction_str, (0, 0, 1)),
            add_registration_keys=True,
            key_diameter=10.0
        )

        logger.info(
            f"Parameters: draft={params.draft_angle}°, "
            f"wall={params.wall_thickness}mm, "
            f"direction={params.demolding_direction}"
        )

        return params
