"""
Styled Dialog Helpers for Ceramic Mold Analyzer

Provides consistent, polished dialogs for errors, warnings, info, and confirmations.
"""

from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from typing import Optional


class StyledMessageBox:
    """Factory for creating consistently styled message dialogs"""

    @staticmethod
    def error(parent: Optional[QWidget], title: str, message: str, details: str = "") -> None:
        """
        Show error dialog with styled appearance.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Main error message
            details: Optional detailed error information
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color: #d32f2f;'>{title}</h3>")
        msg.setInformativeText(message)

        if details:
            msg.setDetailedText(details)

        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        # Style the dialog
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)

        msg.exec()

    @staticmethod
    def warning(parent: Optional[QWidget], title: str, message: str, details: str = "") -> None:
        """
        Show warning dialog with styled appearance.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Main warning message
            details: Optional detailed warning information
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color: #f57c00;'>{title}</h3>")
        msg.setInformativeText(message)

        if details:
            msg.setDetailedText(details)

        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)

        msg.exec()

    @staticmethod
    def info(parent: Optional[QWidget], title: str, message: str, details: str = "") -> None:
        """
        Show info dialog with styled appearance.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Main info message
            details: Optional detailed information
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color: #007AFF;'>{title}</h3>")
        msg.setInformativeText(message)

        if details:
            msg.setDetailedText(details)

        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)

        msg.exec()

    @staticmethod
    def question(parent: Optional[QWidget], title: str, message: str) -> bool:
        """
        Show question dialog with Yes/No buttons.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Question message

        Returns:
            True if user clicked Yes, False otherwise
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color: #007AFF;'>{title}</h3>")
        msg.setInformativeText(message)
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.No)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)

        result = msg.exec()
        return result == QMessageBox.StandardButton.Yes

    @staticmethod
    def success(parent: Optional[QWidget], title: str, message: str) -> None:
        """
        Show success dialog with styled appearance.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Success message
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color: #34C759;'>✓ {title}</h3>")
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #30B350;
            }
        """)

        msg.exec()
