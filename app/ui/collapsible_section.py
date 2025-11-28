"""
Collapsible Section Widget for Space-Efficient UI
Provides accordion-style panels that can expand/collapse to save vertical space
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QLabel, QSizePolicy, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QIcon, QPalette


class CollapsibleSection(QWidget):
    """
    A collapsible section widget with header and content area.

    The header remains visible and clicking it toggles the content visibility.
    Provides smooth animation and visual indicators.
    """

    # Signals
    toggled = pyqtSignal(bool)  # Emitted when section is expanded/collapsed
    pinned = pyqtSignal(bool)   # Emitted when pinned state changes

    def __init__(self, title="", parent=None, start_collapsed=True):
        super().__init__(parent)

        self.title = title
        self.is_collapsed = start_collapsed
        self.is_pinned = False
        self.status_indicator = None

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header frame (always visible)
        self.header_frame = QFrame()
        self.header_frame.setFrameStyle(QFrame.Shape.Box)
        self.header_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 2px;
            }
            QFrame:hover {
                background-color: #e8e8e8;
            }
        """)
        self.header_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_frame.mousePressEvent = self.toggle_collapsed

        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setContentsMargins(5, 3, 5, 3)

        # Collapse/expand arrow
        self.arrow = QLabel()
        self.update_arrow()

        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold;")

        # Status indicator (optional - for showing counts, errors, etc.)
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")

        # Pin button
        self.pin_button = QToolButton()
        self.pin_button.setText("📌")
        self.pin_button.setCheckable(True)
        self.pin_button.setChecked(self.is_pinned)
        self.pin_button.setMaximumSize(24, 24)
        self.pin_button.setStyleSheet("""
            QToolButton {
                border: none;
                background: transparent;
            }
            QToolButton:checked {
                background-color: #d0e0ff;
                border-radius: 3px;
            }
        """)
        self.pin_button.clicked.connect(self.on_pin_clicked)
        self.pin_button.setToolTip("Pin to keep expanded")

        # Assemble header
        header_layout.addWidget(self.arrow)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()
        header_layout.addWidget(self.pin_button)

        self.header_frame.setLayout(header_layout)

        # Content frame (collapsible)
        self.content_frame = QFrame()
        self.content_frame.setFrameStyle(QFrame.Shape.Box)
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-top: none;
                border-bottom-left-radius: 3px;
                border-bottom-right-radius: 3px;
            }
        """)

        # Content layout (where child widgets go)
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_frame.setLayout(self.content_layout)

        # Add to main layout
        main_layout.addWidget(self.header_frame)
        main_layout.addWidget(self.content_frame)

        self.setLayout(main_layout)

        # Set initial collapsed state
        self.set_collapsed(self.is_collapsed)

    def set_content_widget(self, widget):
        """Set the widget to display in the content area"""
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new widget
        self.content_layout.addWidget(widget)

    def set_collapsed(self, collapsed):
        """Set the collapsed state"""
        self.is_collapsed = collapsed
        self.content_frame.setVisible(not collapsed)
        self.update_arrow()
        self.toggled.emit(not collapsed)

    def toggle_collapsed(self, event=None):
        """Toggle between collapsed and expanded state"""
        # Don't toggle if pinned and trying to collapse
        if self.is_pinned and not self.is_collapsed:
            return

        self.set_collapsed(not self.is_collapsed)

    def update_arrow(self):
        """Update the arrow indicator"""
        if self.is_collapsed:
            self.arrow.setText("▶")  # Right arrow when collapsed
        else:
            self.arrow.setText("▼")  # Down arrow when expanded

    def set_status_text(self, text):
        """Set status text (e.g., "(3 errors)" or "(12 regions)")"""
        self.status_label.setText(text)

    def set_status_indicator(self, indicator):
        """Set status indicator (e.g., error/warning/success symbol)"""
        if indicator == "error":
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        elif indicator == "warning":
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        elif indicator == "success":
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #666; font-size: 11px;")

    def on_pin_clicked(self):
        """Handle pin button click"""
        self.is_pinned = self.pin_button.isChecked()

        # If pinning, expand the section
        if self.is_pinned and self.is_collapsed:
            self.set_collapsed(False)

        self.pinned.emit(self.is_pinned)

    def set_pinned(self, pinned):
        """Set pinned state programmatically"""
        self.is_pinned = pinned
        self.pin_button.setChecked(pinned)

    def get_header_height(self):
        """Get the height of just the header"""
        return self.header_frame.sizeHint().height()

    def get_total_height(self):
        """Get total height when expanded"""
        if self.is_collapsed:
            return self.get_header_height()
        else:
            return self.header_frame.height() + self.content_frame.height()


class SmartCollapsibleManager:
    """
    Manages multiple collapsible sections with smart behavior:
    - Auto-collapse others when one expands (accordion mode)
    - Remember user preferences
    - Respect pinned sections
    """

    def __init__(self, sections=None, accordion_mode=True):
        self.sections = sections or []
        self.accordion_mode = accordion_mode

        # Connect signals
        for section in self.sections:
            section.toggled.connect(lambda expanded, s=section: self.on_section_toggled(s, expanded))

    def add_section(self, section):
        """Add a section to manage"""
        self.sections.append(section)
        section.toggled.connect(lambda expanded, s=section: self.on_section_toggled(s, expanded))

    def on_section_toggled(self, toggled_section, expanded):
        """Handle section toggle in accordion mode"""
        if not self.accordion_mode or not expanded:
            return

        # Collapse other non-pinned sections
        for section in self.sections:
            if section != toggled_section and not section.is_pinned:
                section.set_collapsed(True)

    def expand_only(self, target_section):
        """Expand only the specified section, collapse others"""
        for section in self.sections:
            if section == target_section:
                section.set_collapsed(False)
            elif not section.is_pinned:
                section.set_collapsed(True)

    def collapse_all(self):
        """Collapse all non-pinned sections"""
        for section in self.sections:
            if not section.is_pinned:
                section.set_collapsed(True)

    def expand_all(self):
        """Expand all sections (disables accordion mode)"""
        self.accordion_mode = False
        for section in self.sections:
            section.set_collapsed(False)