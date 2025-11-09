"""
Centralized Error Handling and Logging

Provides:
- Unified error dialog system
- Logging configuration
- Exception decorators
- User-friendly error messages
"""

import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps
from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import QObject, pyqtSignal


# ============================================================
# Logging Configuration
# ============================================================

def setup_logging(level=logging.INFO, log_file: Optional[str] = None):
    """
    Configure application-wide logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging output
    """
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers
    )

    # Set specific module levels
    logging.getLogger('app.bridge').setLevel(logging.DEBUG)
    logging.getLogger('app.workflow').setLevel(logging.INFO)
    logging.getLogger('app.export').setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(name)


# ============================================================
# Error Dialog System
# ============================================================

class ErrorHandler(QObject):
    """
    Centralized error handler with user-facing dialogs.

    Emits signals for error events that need special handling.
    """

    error_occurred = pyqtSignal(str, str)  # (title, message)
    critical_error = pyqtSignal(str, str)  # (title, message)

    def __init__(self):
        super().__init__()
        self.logger = get_logger('ErrorHandler')

    def show_error(self,
                   title: str,
                   message: str,
                   details: Optional[str] = None,
                   parent: Optional[QWidget] = None):
        """
        Show error dialog to user.

        Args:
            title: Error dialog title
            message: User-friendly error message
            details: Technical details (optional, shown in expandable section)
            parent: Parent widget for dialog
        """
        self.logger.error(f"{title}: {message}")
        if details:
            self.logger.debug(f"Details: {details}")

        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if details:
            msg_box.setDetailedText(details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

        self.error_occurred.emit(title, message)

    def show_warning(self,
                     title: str,
                     message: str,
                     details: Optional[str] = None,
                     parent: Optional[QWidget] = None):
        """
        Show warning dialog to user.

        Args:
            title: Warning dialog title
            message: User-friendly warning message
            details: Technical details (optional)
            parent: Parent widget for dialog
        """
        self.logger.warning(f"{title}: {message}")
        if details:
            self.logger.debug(f"Details: {details}")

        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if details:
            msg_box.setDetailedText(details)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def show_info(self,
                  title: str,
                  message: str,
                  parent: Optional[QWidget] = None):
        """Show informational dialog."""
        self.logger.info(f"{title}: {message}")

        QMessageBox.information(parent, title, message)

    def confirm(self,
                title: str,
                message: str,
                parent: Optional[QWidget] = None) -> bool:
        """
        Show confirmation dialog.

        Returns:
            True if user clicked Yes, False otherwise
        """
        reply = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        return reply == QMessageBox.StandardButton.Yes


# Global error handler instance
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """Get global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


# ============================================================
# Exception Decorators
# ============================================================

def handle_exceptions(error_title: str = "Error",
                      user_message: Optional[str] = None,
                      log_traceback: bool = True,
                      show_dialog: bool = True,
                      return_on_error: Any = None):
    """
    Decorator for handling exceptions with user feedback.

    Args:
        error_title: Title for error dialog
        user_message: Custom user-friendly message (or None to use exception message)
        log_traceback: Whether to log full traceback
        show_dialog: Whether to show error dialog to user
        return_on_error: Value to return if exception occurs

    Example:
        @handle_exceptions("Connection Error", "Failed to connect to Rhino")
        def connect_to_rhino():
            # ... risky code ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error
                logger.error(f"Exception in {func.__name__}: {str(e)}")
                if log_traceback:
                    logger.debug(traceback.format_exc())

                # Show dialog if requested
                if show_dialog:
                    message = user_message or str(e)
                    details = traceback.format_exc() if log_traceback else None
                    get_error_handler().show_error(
                        error_title,
                        message,
                        details=details
                    )

                return return_on_error

        return wrapper
    return decorator


def graceful_degradation(fallback_value: Any = None,
                         log_error: bool = True):
    """
    Decorator for graceful degradation on errors.

    Returns fallback value instead of raising exception.
    Does not show dialog to user.

    Args:
        fallback_value: Value to return on error
        log_error: Whether to log the error

    Example:
        @graceful_degradation(fallback_value=[])
        def get_analysis_results():
            # ... may fail, returns [] on error ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.warning(f"Graceful degradation in {func.__name__}: {str(e)}")
                return fallback_value

        return wrapper
    return decorator


# ============================================================
# User-Friendly Error Messages
# ============================================================

ERROR_MESSAGES = {
    # Connection errors
    'connection_refused': (
        "Cannot Connect to Rhino",
        "The Grasshopper server is not running.\n\n"
        "Please ensure:\n"
        "1. Rhino is open\n"
        "2. The Grasshopper script is loaded\n"
        "3. The HTTP server component is active"
    ),
    'connection_timeout': (
        "Connection Timeout",
        "The connection to Rhino timed out.\n\n"
        "The server may be busy or unresponsive.\n"
        "Try again in a moment."
    ),
    'server_error': (
        "Server Error",
        "The Grasshopper server encountered an error.\n\n"
        "Check the Rhino/Grasshopper console for details."
    ),

    # C++ errors
    'cpp_not_available': (
        "C++ Module Not Available",
        "The C++ core module (cpp_core) is not installed.\n\n"
        "Please build the C++ module:\n"
        "  cd cpp_core\n"
        "  mkdir build && cd build\n"
        "  cmake ..\n"
        "  make"
    ),
    'cpp_initialization_error': (
        "Initialization Error",
        "Failed to initialize the geometry evaluator.\n\n"
        "The SubD control cage may be invalid or corrupted."
    ),

    # NURBS errors
    'nurbs_fitting_failed': (
        "NURBS Fitting Failed",
        "Failed to fit NURBS surface to the geometry.\n\n"
        "The surface may be too complex or have issues.\n"
        "Try simplifying the region or adjusting parameters."
    ),
    'nurbs_quality_poor': (
        "Poor Fitting Quality",
        "NURBS fitting quality is below tolerance.\n\n"
        "Maximum deviation exceeds 0.1mm.\n"
        "Consider increasing sample density or simplifying geometry."
    ),

    # File I/O errors
    'file_not_found': (
        "File Not Found",
        "The specified file does not exist.\n\n"
        "Please check the file path and try again."
    ),
    'file_read_error': (
        "Cannot Read File",
        "Failed to read the file.\n\n"
        "The file may be corrupted or you may not have permission to access it."
    ),
    'file_write_error': (
        "Cannot Write File",
        "Failed to write to the file.\n\n"
        "Check that you have write permissions and sufficient disk space."
    ),
    'invalid_file_format': (
        "Invalid File Format",
        "The file format is not valid or supported.\n\n"
        "Please check the file and try again."
    ),

    # Validation errors
    'invalid_parameters': (
        "Invalid Parameters",
        "The provided parameters are not valid.\n\n"
        "Please check all values and try again."
    ),
    'constraint_violation': (
        "Constraint Violation",
        "The region violates manufacturing constraints.\n\n"
        "Please review the constraint report and adjust the decomposition."
    ),

    # General errors
    'unexpected_error': (
        "Unexpected Error",
        "An unexpected error occurred.\n\n"
        "Please check the log file for details."
    ),
}


def get_error_message(error_key: str) -> tuple[str, str]:
    """
    Get user-friendly error message by key.

    Args:
        error_key: Error message key

    Returns:
        (title, message) tuple
    """
    return ERROR_MESSAGES.get(error_key, ERROR_MESSAGES['unexpected_error'])
