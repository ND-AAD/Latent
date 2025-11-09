"""
Progress Dialog for Long-Running Operations

Provides visual feedback during mold generation and other time-consuming tasks.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QProgressBar,
                             QLabel, QPushButton)
from PyQt6.QtCore import Qt


class ProgressDialog(QDialog):
    """
    Progress feedback for long-running operations.

    Shows:
    - Current step description
    - Progress bar (0-100%)
    - Cancel button

    Example:
        progress = ProgressDialog("Generating Molds", parent=main_window)
        progress.show()
        progress.set_progress(25, "Validating constraints...")
        # ... do work ...
        progress.set_progress(50, "Fitting NURBS surfaces...")
        # ... do work ...
        if progress.canceled:
            return  # User canceled
        progress.close()
    """

    def __init__(self, title: str = "Processing...", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)

        self.canceled = False

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 12px; padding: 5px;")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                text-align: center;
                background-color: #F5F5F5;
                min-height: 24px;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setToolTip("Cancel the current operation")
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF3B30;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        layout.addWidget(self.cancel_btn)

    def set_progress(self, value: int, status: str = ""):
        """Update progress (0-100) and optional status."""
        self.progress.setValue(value)
        if status:
            self.status_label.setText(status)

    def _on_cancel(self):
        self.canceled = True
        self.reject()
