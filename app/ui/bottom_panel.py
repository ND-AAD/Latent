"""
BottomPanel Component with Collapsible Debug Console

Provides the main bottom interface with:
- Connection status indicator and control
- Command input field with history
- System status (activity and memory)
- Collapsible debug console with logging
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFrame, QSizePolicy, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSettings, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QKeyEvent
from app.ui.styles import ThemeManager
import resource
import datetime


class CommandLineEdit(QLineEdit):
    """
    Custom QLineEdit with keyboard shortcuts for command history.
    """

    # Signals
    upPressed = pyqtSignal()
    downPressed = pyqtSignal()
    escapePressed = pyqtSignal()
    tabPressed = pyqtSignal()

    def keyPressEvent(self, event: QKeyEvent):
        """Override key press to handle special keys"""
        if event.key() == Qt.Key.Key_Up:
            self.upPressed.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_Down:
            self.downPressed.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.escapePressed.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_Tab:
            self.tabPressed.emit()
            event.accept()
        else:
            super().keyPressEvent(event)


class ConnectionStatus(QWidget):
    """
    Connection status widget showing Rhino connection state.

    Displays:
    - Colored status indicator (green=connected, red=disconnected, orange=connecting)
    - Status label ("Rhino" or "Disconnected")
    - Disconnect/Reconnect button
    """

    # Signals
    disconnect_clicked = pyqtSignal()
    reconnect_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected = False
        self.connecting = False
        self.connection_timer = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Status indicator row
        status_row = QHBoxLayout()
        status_row.setSpacing(6)

        # Colored dot indicator
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet(f"color: {ThemeManager.get_color('error')}; font-size: 16px;")

        # Status text
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet(f"color: {ThemeManager.get_color('text_primary')}; font-size: 12px;")

        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.status_label)
        status_row.addStretch()

        # Action button
        self.action_button = QPushButton("Reconnect")
        self.action_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ThemeManager.get_color('text_secondary')};
                border: 1px solid {ThemeManager.get_color('border')};
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.get_color('bg_secondary')};
                border-color: {ThemeManager.get_color('accent')};
            }}
        """)
        self.action_button.clicked.connect(self._on_action_clicked)

        layout.addLayout(status_row)
        layout.addWidget(self.action_button)

        self.setLayout(layout)
        self.setFixedWidth(140)

    def apply_theme(self, theme: str):
        """Apply theme to connection status widget"""
        # Reapply colors based on connection state
        if self.connected:
            self.set_connected(True)
        elif self.connecting:
            self.set_connecting(True)
        else:
            self.set_connected(False)

        # Update button style
        text_sec = ThemeManager.get_color('text_secondary')
        border = ThemeManager.get_color('border')
        surface = ThemeManager.get_color('bg_secondary')
        primary = ThemeManager.get_color('accent')

        self.action_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {text_sec};
                border: 1px solid {border};
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {surface};
                border-color: {primary};
            }}
        """)

    def _on_action_clicked(self):
        """Handle action button click"""
        if self.connected:
            self.disconnect_clicked.emit()
        else:
            self.reconnect_clicked.emit()
            self.set_connecting(True)

            # Start connection timeout timer (5 seconds)
            if self.connection_timer:
                self.connection_timer.stop()
            self.connection_timer = QTimer()
            self.connection_timer.timeout.connect(self._on_connection_timeout)
            self.connection_timer.setSingleShot(True)
            self.connection_timer.start(5000)

    def _on_connection_timeout(self):
        """Handle connection timeout"""
        if self.connecting:
            self.set_connecting(False)
            # Notify parent via custom signal or direct call
            if self.parent() and hasattr(self.parent(), 'log'):
                self.parent().log("[ERROR] Connection timeout: Failed to connect to Rhino after 5 seconds", "error")

    def set_connected(self, connected: bool):
        """Update connection status"""
        self.connected = connected
        self.connecting = False

        # Stop connection timer if running
        if self.connection_timer:
            self.connection_timer.stop()

        if connected:
            self.status_dot.setStyleSheet(f"color: {ThemeManager.get_color('success')}; font-size: 16px;")
            self.status_label.setText("Rhino")
            self.action_button.setText("Disconnect")
        else:
            self.status_dot.setStyleSheet(f"color: {ThemeManager.get_color('error')}; font-size: 16px;")
            self.status_label.setText("Disconnected")
            self.action_button.setText("Reconnect")

    def set_connecting(self, connecting: bool):
        """Show connecting state"""
        self.connecting = connecting

        if connecting:
            self.status_dot.setStyleSheet(f"color: {ThemeManager.get_color('warning')}; font-size: 16px;")
            self.status_label.setText("Connecting...")
            self.action_button.setEnabled(False)
        else:
            self.action_button.setEnabled(True)


class CommandInput(QWidget):
    """
    Command input widget with prompt prefix, history, and autocomplete support.

    Provides:
    - ">" prompt prefix
    - Text input field
    - Command history (up/down arrows)
    - Keyboard shortcuts (Escape to clear, Tab for autocomplete)
    """

    # Signals
    command_entered = pyqtSignal(str)  # Emitted when user presses Enter

    MAX_HISTORY = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_history = []
        self.history_index = -1
        self.current_input = ""
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """Setup UI components"""
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # Prompt prefix
        prompt_label = QLabel(">")
        prompt_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')}; font-size: 12px; font-weight: bold;")

        # Command input with custom key handling
        self.input_field = CommandLineEdit(self)
        self.input_field.setPlaceholderText("Type command or press Tab to autocomplete...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background-color: transparent;
                color: {ThemeManager.get_color('text_primary')};
                font-size: 12px;
                padding: 4px;
            }}
            QLineEdit::placeholder {{
                color: {ThemeManager.get_color('disabled_text')};
            }}
        """)
        self.input_field.returnPressed.connect(self._on_return_pressed)
        self.input_field.upPressed.connect(self._on_history_up)
        self.input_field.downPressed.connect(self._on_history_down)
        self.input_field.escapePressed.connect(self._on_escape)
        self.input_field.tabPressed.connect(self._on_tab)

        layout.addWidget(prompt_label)
        layout.addWidget(self.input_field, stretch=1)

        self.setLayout(layout)

    def apply_theme(self, theme: str):
        """Apply theme to command input widget"""
        text_sec = ThemeManager.get_color('text_secondary')
        text = ThemeManager.get_color('text_primary')
        text_disabled = ThemeManager.get_color('text_disabled')

        # Update prompt label
        prompt_label = self.findChildren(QLabel)[0]
        prompt_label.setStyleSheet(f"color: {text_sec}; font-size: 12px; font-weight: bold;")

        # Update input field
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                border: none;
                background-color: transparent;
                color: {text};
                font-size: 12px;
                padding: 4px;
            }}
            QLineEdit::placeholder {{
                color: {text_disabled};
            }}
        """)

    def _on_return_pressed(self):
        """Handle Enter key press"""
        command = self.input_field.text().strip()
        if command:
            # Add to history
            self.add_to_history(command)

            # Emit signal
            self.command_entered.emit(command)

            # Clear input and reset history index
            self.input_field.clear()
            self.history_index = -1
            self.current_input = ""

    def _on_history_up(self):
        """Navigate to previous command in history"""
        if not self.command_history:
            return

        # Store current input when starting history navigation
        if self.history_index == -1:
            self.current_input = self.input_field.text()

        # Move up in history
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_field.setText(self.command_history[-(self.history_index + 1)])

    def _on_history_down(self):
        """Navigate to next command in history"""
        if self.history_index <= -1:
            return

        # Move down in history
        self.history_index -= 1

        if self.history_index == -1:
            # Restore current input
            self.input_field.setText(self.current_input)
        else:
            self.input_field.setText(self.command_history[-(self.history_index + 1)])

    def _on_escape(self):
        """Handle Escape key - clear input"""
        self.input_field.clear()
        self.history_index = -1
        self.current_input = ""

    def _on_tab(self):
        """Handle Tab key - autocomplete placeholder"""
        # TODO: Implement autocomplete logic
        pass

    def add_to_history(self, command: str):
        """Add command to history"""
        # Avoid duplicate consecutive commands
        if self.command_history and self.command_history[-1] == command:
            return

        # Add to history
        self.command_history.append(command)

        # Limit history size
        if len(self.command_history) > self.MAX_HISTORY:
            self.command_history.pop(0)

        # Save to settings
        self.save_history()

    def load_history(self):
        """Load command history from QSettings"""
        settings = QSettings("ND-AAD", "CeramicMoldAnalyzer")
        history = settings.value("command_history", [])
        if isinstance(history, list):
            self.command_history = history[-self.MAX_HISTORY:]  # Limit on load

    def save_history(self):
        """Save command history to QSettings"""
        settings = QSettings("ND-AAD", "CeramicMoldAnalyzer")
        settings.setValue("command_history", self.command_history)

    def clear(self):
        """Clear the input field"""
        self.input_field.clear()
        self.history_index = -1
        self.current_input = ""


class SystemStatus(QWidget):
    """
    System status widget showing activity and memory usage.

    Displays:
    - Activity indicator (Idle/Analyzing/Loading/Exporting)
    - Memory usage in MB (updated every 5 seconds)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = "Idle"
        self.setup_ui()
        self.start_memory_timer()

    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Activity indicator
        activity_row = QHBoxLayout()
        activity_row.setSpacing(6)

        self.activity_icon = QLabel("◉")
        self.activity_icon.setStyleSheet(f"color: {ThemeManager.get_color('disabled_text')}; font-size: 14px;")

        self.activity_label = QLabel("Idle")
        self.activity_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')}; font-size: 12px;")

        activity_row.addWidget(self.activity_icon)
        activity_row.addWidget(self.activity_label)
        activity_row.addStretch()

        # Memory usage
        self.memory_label = QLabel("245 MB")
        self.memory_label.setStyleSheet(f"color: {ThemeManager.get_color('disabled_text')}; font-size: 11px;")

        layout.addLayout(activity_row)
        layout.addWidget(self.memory_label)

        self.setLayout(layout)
        self.setFixedWidth(128)

        # Update memory on startup
        self.update_memory()

    def start_memory_timer(self):
        """Start timer to update memory usage every 5 seconds"""
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self.update_memory)
        self.memory_timer.start(5000)  # 5 seconds

    def update_memory(self):
        """Update memory usage from system"""
        try:
            # Get memory in MB
            memory_mb = self.get_memory_mb()
            self.set_memory_usage(int(memory_mb))
        except Exception as e:
            # Fallback if resource module fails
            pass

    def get_memory_mb(self):
        """Get current memory usage in MB"""
        try:
            # macOS/Linux: resource.getrusage returns bytes
            usage = resource.getrusage(resource.RUSAGE_SELF)
            # On macOS, ru_maxrss is in bytes; on Linux it's in kilobytes
            import platform
            if platform.system() == 'Darwin':  # macOS
                return usage.ru_maxrss / 1024 / 1024
            else:  # Linux
                return usage.ru_maxrss / 1024
        except:
            return 0

    def apply_theme(self, theme: str):
        """Apply theme to system status widget"""
        text_sec = ThemeManager.get_color('text_secondary')
        text_disabled = ThemeManager.get_color('text_disabled')

        # Reapply activity state with new colors
        if hasattr(self, '_is_working') and self._is_working:
            self.set_activity(True)
        else:
            self.set_activity(False)

        # Update memory label color
        self.memory_label.setStyleSheet(f"color: {text_disabled}; font-size: 11px;")

    def set_activity(self, working: bool):
        """
        Update activity indicator (deprecated - use set_status instead).

        Args:
            working: True for Working, False for Idle
        """
        self._is_working = working  # Store state for theme changes

        if working:
            self.set_status("Working")
        else:
            self.set_status("Idle")

    def set_status(self, status: str):
        """
        Set activity status with custom message.

        Args:
            status: Status text (e.g., "Idle", "Analyzing...", "Loading...", "Exporting...")
        """
        self.current_status = status
        self._is_working = status != "Idle"

        # Update label
        self.activity_label.setText(status)
        self.activity_label.setStyleSheet(f"color: {ThemeManager.get_color('text_secondary')}; font-size: 12px;")

        # Update icon based on status
        if status == "Idle":
            text_disabled = ThemeManager.get_color('text_disabled')
            self.activity_icon.setStyleSheet(f"color: {text_disabled}; font-size: 14px;")
        else:
            primary = ThemeManager.get_color('accent')
            self.activity_icon.setStyleSheet(f"color: {primary}; font-size: 14px;")

    def set_memory_usage(self, mb: int):
        """Update memory usage display"""
        self.memory_label.setText(f"{mb} MB")


class DebugConsole(QWidget):
    """
    Debug console widget with logging output.

    Provides:
    - Header with title and action buttons (Clear/Export/Close)
    - Scrollable text output area
    - Color-coded log levels
    - Maximum 1000 lines
    - Auto-scroll to bottom
    """

    # Signals
    close_requested = pyqtSignal()

    MAX_LINES = 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_count = 0
        self.setup_ui()

    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background-color: #2D2D30; border-bottom: 1px solid #3E3E42;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 6, 12, 6)
        header_layout.setSpacing(8)

        # Title
        title_label = QLabel("⌨ Debug Console")
        title_label.setStyleSheet("color: #D4D4D4; font-size: 12px; font-weight: bold;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #D4D4D4;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3E3E42;
            }
        """)
        clear_btn.clicked.connect(self.clear)

        # Export button
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #D4D4D4;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #3E3E42;
            }
        """)
        export_btn.clicked.connect(self.export_logs)

        # Close button
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #D4D4D4;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3E3E42;
            }
        """)
        close_btn.clicked.connect(self.close_requested.emit)

        header_layout.addWidget(clear_btn)
        header_layout.addWidget(export_btn)
        header_layout.addWidget(close_btn)

        header.setLayout(header_layout)

        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)

        # Monospace font for console
        font = QFont("Monaco, Menlo, Consolas, monospace")
        font.setPointSize(11)
        self.console_output.setFont(font)

        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                padding: 8px;
            }
        """)

        # Add welcome message
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] Debug console initialized", "info")

        layout.addWidget(header)
        layout.addWidget(self.console_output)

        self.setLayout(layout)
        self.setFixedHeight(140)

    def log(self, message: str, level: str = "info"):
        """
        Add a log message to the console.

        Args:
            message: Log message text
            level: Log level (info, success, warning, error, debug)
        """
        colors = {
            "info": "#569CD6",      # Blue
            "success": "#4EC9B0",   # Green
            "warning": "#DCDCAA",   # Yellow
            "error": "#F48771",     # Red / Orange
            "debug": "#808080"      # Gray
        }

        color = colors.get(level, colors["info"])

        # Check line limit
        if self.line_count >= self.MAX_LINES:
            # Remove first line
            cursor = self.console_output.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # Remove newline
            self.line_count -= 1

        # Add new message
        self.console_output.append(f'<span style="color: {color};">{message}</span>')
        self.line_count += 1

        # Auto-scroll to bottom
        scrollbar = self.console_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear(self):
        """Clear all console output"""
        self.console_output.clear()
        self.line_count = 0

        # Add cleared message
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] Console cleared", "info")

    def export_logs(self):
        """Export logs to file"""
        # Open file save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Console Logs",
            f"console_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                # Get all text from console
                text = self.console_output.toPlainText()

                # Write to file
                with open(file_path, 'w') as f:
                    f.write(text)

                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                self.log(f"[{timestamp}] Logs exported to: {file_path}", "success")
            except Exception as e:
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                self.log(f"[{timestamp}] ERROR: Failed to export logs: {str(e)}", "error")


class BottomPanel(QWidget):
    """
    Bottom panel component with connection status, command input, and collapsible debug console.

    Layout (left to right):
    - ConnectionStatus (140px): Rhino connection indicator + action button
    - CommandInput (flexible): Command input field with prompt
    - SystemStatus (128px): Activity and memory usage
    - DebugToggle (48px): Chevron button to expand/collapse console

    Debug console appears ABOVE the main bar when expanded.

    Signals:
        command_entered(str): User entered a command
        console_toggled(bool): Debug console expanded/collapsed
    """

    # Signals
    command_entered = pyqtSignal(str)
    console_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.console_expanded = False
        self.setup_ui()
        self.load_console_state()
        self.install_keyboard_shortcuts()

    def setup_ui(self):
        """Setup UI components"""
        # Main vertical layout (console above, main bar below)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Debug console (initially hidden)
        self.debug_console = DebugConsole()
        self.debug_console.setVisible(False)
        self.debug_console.close_requested.connect(self.toggle_console)

        # Main bottom bar
        bottom_bar = QFrame()
        bottom_bar.setStyleSheet(f"""
            QFrame {{
                background-color: #FAFAFA;
                border-top: 1px solid #D1D1D6;
            }}
        """)

        bar_layout = QHBoxLayout()
        bar_layout.setContentsMargins(0, 0, 0, 0)
        bar_layout.setSpacing(0)

        # Connection status
        self.connection_status = ConnectionStatus()
        # Forward signals
        self.connection_status.reconnect_clicked.connect(self._on_reconnect_clicked)
        self.connection_status.disconnect_clicked.connect(self._on_disconnect_clicked)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet(f"background-color: {ThemeManager.get_color('border')}; max-width: 1px;")

        # Command input
        self.command_input = CommandInput()
        self.command_input.command_entered.connect(self.command_entered.emit)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setStyleSheet(f"background-color: {ThemeManager.get_color('border')}; max-width: 1px;")

        # System status
        self.system_status = SystemStatus()

        # Separator
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.Shape.VLine)
        sep3.setStyleSheet(f"background-color: {ThemeManager.get_color('border')}; max-width: 1px;")

        # Debug toggle button
        self.debug_toggle = QPushButton("▲")
        self.debug_toggle.setFixedSize(48, 100)
        self.debug_toggle.setToolTip("Toggle Debug Console")
        self.debug_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {ThemeManager.get_color('disabled_text')};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ThemeManager.get_color('bg_secondary')};
                color: {ThemeManager.get_color('text_primary')};
            }}
        """)
        self.debug_toggle.clicked.connect(self.toggle_console)

        # Assemble main bar
        bar_layout.addWidget(self.connection_status)
        bar_layout.addWidget(sep1)
        bar_layout.addWidget(self.command_input, stretch=1)
        bar_layout.addWidget(sep2)
        bar_layout.addWidget(self.system_status)
        bar_layout.addWidget(sep3)
        bar_layout.addWidget(self.debug_toggle)

        bottom_bar.setLayout(bar_layout)
        bottom_bar.setFixedHeight(100)

        # Assemble main layout
        main_layout.addWidget(self.debug_console)
        main_layout.addWidget(bottom_bar)

        self.setLayout(main_layout)

    def install_keyboard_shortcuts(self):
        """Install keyboard shortcuts for console toggle"""
        from PyQt6.QtGui import QShortcut, QKeySequence

        # Ctrl+` to toggle console
        self.console_shortcut = QShortcut(QKeySequence("Ctrl+`"), self)
        self.console_shortcut.activated.connect(self.toggle_console)

    def load_console_state(self):
        """Load console expanded state from settings"""
        settings = QSettings("ND-AAD", "CeramicMoldAnalyzer")
        expanded = settings.value("console_expanded", False, type=bool)

        if expanded:
            # Expand console
            self.toggle_console()

    def save_console_state(self):
        """Save console expanded state to settings"""
        settings = QSettings("ND-AAD", "CeramicMoldAnalyzer")
        settings.setValue("console_expanded", self.console_expanded)

    def _on_reconnect_clicked(self):
        """Handle reconnect button click"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] Attempting to reconnect to Rhino...", "info")
        # Application should handle actual connection logic

    def _on_disconnect_clicked(self):
        """Handle disconnect button click"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log(f"[{timestamp}] Disconnecting from Rhino...", "info")
        # Application should handle actual disconnection logic

    def toggle_console(self):
        """Toggle debug console visibility"""
        self.console_expanded = not self.console_expanded
        self.debug_console.setVisible(self.console_expanded)

        # Save state
        self.save_console_state()

        # Update toggle button icon
        if self.console_expanded:
            self.debug_toggle.setText("▼")
            self.debug_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ThemeManager.get_color('bg_secondary')};
                    border: none;
                    color: {ThemeManager.get_color('accent')};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {ThemeManager.get_color('hover_bg')};
                }}
            """)
        else:
            self.debug_toggle.setText("▲")
            self.debug_toggle.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: {ThemeManager.get_color('disabled_text')};
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {ThemeManager.get_color('bg_secondary')};
                    color: {ThemeManager.get_color('text_primary')};
                }}
            """)

        self.console_toggled.emit(self.console_expanded)

    def set_connected(self, connected: bool):
        """Update connection status"""
        self.connection_status.set_connected(connected)

    def set_connecting(self, connecting: bool):
        """Set connecting state"""
        self.connection_status.set_connecting(connecting)

    def set_activity(self, working: bool):
        """
        Update activity status (deprecated - use set_status instead).

        Args:
            working: True for Working, False for Idle
        """
        self.system_status.set_activity(working)

    def set_status(self, status: str):
        """
        Set activity status with custom message.

        Args:
            status: Status text (e.g., "Idle", "Analyzing...", "Loading...", "Exporting...")
        """
        self.system_status.set_status(status)

    def set_memory_usage(self, mb: int):
        """Update memory usage display"""
        self.system_status.set_memory_usage(mb)

    def log(self, message: str, level: str = "info"):
        """
        Add message to debug console.

        Args:
            message: Log message text
            level: Log level (info, success, warning, error, debug)

        Level colors:
            - info: Blue
            - success: Green
            - warning: Yellow
            - error: Red/Orange
            - debug: Gray
        """
        self.debug_console.log(message, level)

    def apply_theme(self, theme: str):
        """
        Apply theme to BottomPanel and all child components.

        Args:
            theme: 'light' or 'dark'
        """
        # Update main bar background
        border = ThemeManager.get_color('border')
        bg = ThemeManager.get_color('bg_secondary')

        # Find bottom_bar frame and update it
        for child in self.findChildren(QFrame):
            if hasattr(child, 'objectName') or child.parent() == self:
                child.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg};
                        border-top: 1px solid {border};
                    }}
                """)
                break

        # Update connection status
        if hasattr(self, 'connection_status'):
            self.connection_status.apply_theme(theme)

        # Update command input
        if hasattr(self, 'command_input'):
            self.command_input.apply_theme(theme)

        # Update system status
        if hasattr(self, 'system_status'):
            self.system_status.apply_theme(theme)

        # Update debug toggle button
        if hasattr(self, 'debug_toggle'):
            text_disabled = ThemeManager.get_color('text_disabled')
            text = ThemeManager.get_color('text_primary')
            surface = ThemeManager.get_color('bg_secondary')

            if self.console_expanded:
                primary = ThemeManager.get_color('accent')
                self.debug_toggle.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {surface};
                        border: none;
                        color: {primary};
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {ThemeManager.get_color('hover_bg')};
                    }}
                """)
            else:
                self.debug_toggle.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: none;
                        color: {text_disabled};
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {surface};
                        color: {text};
                    }}
                """)

        # Update debug console (dark theme always for console)
        # Debug console stays dark regardless of app theme
