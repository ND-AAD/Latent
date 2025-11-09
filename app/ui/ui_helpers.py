"""
UI Helper Functions and Widgets

Provides utility functions and reusable widgets for common UI patterns.
"""

from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QMovie
from typing import Optional


class LoadingButton(QPushButton):
    """
    Button with built-in loading state.

    Shows a spinner and disables interaction when loading.
    Automatically restores text and state when loading completes.
    """

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._original_text = text
        self._is_loading = False

        # Style for loading state
        self._loading_style = """
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """

    def set_loading(self, loading: bool, loading_text: str = "Processing..."):
        """
        Set loading state.

        Args:
            loading: True to show loading state, False to restore normal state
            loading_text: Text to show during loading
        """
        self._is_loading = loading

        if loading:
            self._original_text = self.text()
            self.setText(loading_text)
            self.setEnabled(False)
        else:
            self.setText(self._original_text)
            self.setEnabled(True)

    def is_loading(self) -> bool:
        """Check if button is in loading state"""
        return self._is_loading


class StatusIndicator(QLabel):
    """
    Colored dot status indicator with tooltip.

    Colors:
    - Green: Connected/Active
    - Orange: Warning/Partial
    - Red: Error/Disconnected
    - Gray: Inactive/Unknown
    """

    def __init__(self, parent=None):
        super().__init__("●", parent)
        self.setStyleSheet("font-size: 16px;")
        self._status = 'unknown'

    def set_status(self, status: str, tooltip: str = ""):
        """
        Set status indicator.

        Args:
            status: 'success', 'warning', 'error', or 'unknown'
            tooltip: Optional tooltip text
        """
        self._status = status

        colors = {
            'success': 'green',
            'warning': 'orange',
            'error': 'red',
            'unknown': 'gray'
        }

        color = colors.get(status, 'gray')
        self.setStyleSheet(f"color: {color}; font-size: 16px;")

        if tooltip:
            self.setToolTip(tooltip)

    def get_status(self) -> str:
        """Get current status"""
        return self._status


class FlashMessage(QLabel):
    """
    Temporary flash message that auto-hides after duration.

    Shows styled message for success, error, warning, or info.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()

        self._timer = QTimer()
        self._timer.timeout.connect(self.hide)

    def show_message(self, message: str, msg_type: str = 'info', duration: int = 3000):
        """
        Show flash message.

        Args:
            message: Message text
            msg_type: 'success', 'error', 'warning', or 'info'
            duration: Display duration in milliseconds
        """
        styles = {
            'success': 'background-color: #34C759; color: white;',
            'error': 'background-color: #FF3B30; color: white;',
            'warning': 'background-color: #FFCC00; color: #333333;',
            'info': 'background-color: #007AFF; color: white;'
        }

        style = styles.get(msg_type, styles['info'])
        self.setStyleSheet(f"""
            {style}
            padding: 10px;
            border-radius: 4px;
            font-weight: bold;
        """)

        self.setText(message)
        self.show()

        # Auto-hide after duration
        self._timer.start(duration)


def set_button_busy(button: QPushButton, busy: bool, busy_text: str = "Processing..."):
    """
    Helper function to set button busy state.

    Args:
        button: Button to modify
        busy: True for busy state, False to restore
        busy_text: Text to show when busy
    """
    if not hasattr(button, '_original_text'):
        button._original_text = button.text()

    if busy:
        button._original_text = button.text()
        button.setText(busy_text)
        button.setEnabled(False)
    else:
        button.setText(button._original_text)
        button.setEnabled(True)


def add_tooltip_shortcut(widget, tooltip: str, shortcut: str = ""):
    """
    Add tooltip with optional keyboard shortcut hint.

    Args:
        widget: Widget to add tooltip to
        tooltip: Tooltip text
        shortcut: Optional keyboard shortcut (e.g., "Ctrl+Z")
    """
    if shortcut:
        full_tooltip = f"{tooltip} ({shortcut})"
    else:
        full_tooltip = tooltip

    widget.setToolTip(full_tooltip)


def show_loading_overlay(parent, message: str = "Loading..."):
    """
    Show a loading overlay on parent widget.

    Args:
        parent: Parent widget to overlay
        message: Loading message

    Returns:
        Overlay widget (call .hide() to remove)
    """
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PyQt6.QtCore import Qt

    overlay = QWidget(parent)
    overlay.setStyleSheet("""
        background-color: rgba(0, 0, 0, 0.5);
    """)
    overlay.setGeometry(parent.rect())

    layout = QVBoxLayout(overlay)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    label = QLabel(message)
    label.setStyleSheet("""
        color: white;
        font-size: 18px;
        font-weight: bold;
        background-color: rgba(0, 0, 0, 0.8);
        padding: 20px;
        border-radius: 10px;
    """)
    layout.addWidget(label)

    overlay.show()
    overlay.raise_()

    return overlay
