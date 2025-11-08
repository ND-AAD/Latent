"""
Edit Mode Toolbar for Ceramic Mold Analyzer
Provides UI for switching between edit modes
"""

from PyQt6.QtWidgets import (
    QToolBar, QButtonGroup, QToolButton, QWidget,
    QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

from app.state.edit_mode import EditMode


class EditModeToolBar(QToolBar):
    """Toolbar for edit mode selection"""

    # Signal when mode changes
    mode_changed = pyqtSignal(EditMode)

    def __init__(self, parent=None):
        super().__init__("Edit Mode", parent)

        self.setMovable(False)
        self.setFloatable(False)

        # Create button group for exclusive selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Store buttons for later access
        self.mode_buttons = {}

        # Add separator
        self.addWidget(self._create_label("Edit Mode:"))
        self.addSeparator()

        # Create mode buttons
        self._create_mode_buttons()

        # Add separator after mode buttons
        self.addSeparator()

        # Add selection info label
        self.selection_info = QLabel("No selection")
        self.selection_info.setStyleSheet("padding: 0 10px;")
        self.addWidget(self.selection_info)

        # Connect signals
        self.button_group.idClicked.connect(self._on_mode_button_clicked)

    def _create_label(self, text: str) -> QLabel:
        """Create a label for the toolbar"""
        label = QLabel(text)
        label.setStyleSheet("padding: 0 10px; font-weight: bold;")
        return label

    def _create_mode_buttons(self):
        """Create buttons for each edit mode"""
        modes = [
            (EditMode.SOLID, "Solid", "Select entire objects", "⬛"),
            (EditMode.PANEL, "Panel", "Select faces/panels", "▦"),
            (EditMode.EDGE, "Edge", "Select edges", "╱"),
            (EditMode.VERTEX, "Vertex", "Select vertices", "•")
        ]

        for i, (mode, name, tooltip, icon_text) in enumerate(modes):
            button = QToolButton()
            button.setText(icon_text + " " + name)
            button.setToolTip(tooltip)
            button.setCheckable(True)
            button.setAutoRaise(True)

            # Style the button
            button.setStyleSheet("""
                QToolButton {
                    padding: 5px 10px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: #f0f0f0;
                    min-width: 60px;
                }
                QToolButton:checked {
                    background-color: #007AFF;
                    color: white;
                    border-color: #0051D5;
                }
                QToolButton:hover {
                    background-color: #e0e0e0;
                }
                QToolButton:checked:hover {
                    background-color: #0051D5;
                }
            """)

            # Set default selection
            if mode == EditMode.SOLID:
                button.setChecked(True)

            # Add to button group with ID
            self.button_group.addButton(button, i)
            self.mode_buttons[mode] = button

            # Add to toolbar
            self.addWidget(button)

    def _on_mode_button_clicked(self, button_id: int):
        """Handle mode button click"""
        # Map button ID to mode
        modes = list(EditMode)
        if 0 <= button_id < len(modes):
            mode = modes[button_id]
            self.mode_changed.emit(mode)

    def set_mode(self, mode: EditMode):
        """Set the current mode programmatically"""
        if mode in self.mode_buttons:
            self.mode_buttons[mode].setChecked(True)

    def update_selection_info(self, info: str):
        """Update the selection information display"""
        self.selection_info.setText(info)


class EditModeWidget(QWidget):
    """
    Compact edit mode selector widget for integration in main UI
    Can be used in control panel instead of toolbar
    """

    mode_changed = pyqtSignal(EditMode)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create frame for visual grouping
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 4px; }")

        frame_layout = QHBoxLayout(frame)
        frame_layout.setSpacing(0)
        frame_layout.setContentsMargins(2, 2, 2, 2)

        # Button group for exclusive selection
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Create compact buttons
        self.mode_buttons = {}
        modes = [
            (EditMode.SOLID, "S", "Solid Mode - Select objects"),
            (EditMode.PANEL, "P", "Panel Mode - Select faces"),
            (EditMode.EDGE, "E", "Edge Mode - Select edges"),
            (EditMode.VERTEX, "V", "Vertex Mode - Select vertices")
        ]

        for i, (mode, text, tooltip) in enumerate(modes):
            button = QToolButton()
            button.setText(text)
            button.setToolTip(tooltip)
            button.setCheckable(True)
            button.setAutoRaise(False)
            button.setMinimumSize(30, 30)
            button.setMaximumSize(30, 30)

            # Compact button styling
            button.setStyleSheet("""
                QToolButton {
                    border: none;
                    background-color: transparent;
                    font-weight: bold;
                    font-size: 14px;
                }
                QToolButton:checked {
                    background-color: #007AFF;
                    color: white;
                    border-radius: 3px;
                }
                QToolButton:hover {
                    background-color: rgba(0, 122, 255, 0.1);
                }
                QToolButton:checked:hover {
                    background-color: #0051D5;
                }
            """)

            if mode == EditMode.SOLID:
                button.setChecked(True)

            self.button_group.addButton(button, i)
            self.mode_buttons[mode] = button
            frame_layout.addWidget(button)

        layout.addWidget(frame)
        layout.addStretch()

        # Connect signal
        self.button_group.idClicked.connect(self._on_mode_clicked)

    def _on_mode_clicked(self, button_id: int):
        """Handle mode button click"""
        modes = list(EditMode)
        if 0 <= button_id < len(modes):
            self.mode_changed.emit(modes[button_id])

    def set_mode(self, mode: EditMode):
        """Set the current mode"""
        if mode in self.mode_buttons:
            self.mode_buttons[mode].setChecked(True)

    def get_mode(self) -> EditMode:
        """Get the currently selected mode"""
        checked_id = self.button_group.checkedId()
        modes = list(EditMode)
        if 0 <= checked_id < len(modes):
            return modes[checked_id]
        return EditMode.SOLID