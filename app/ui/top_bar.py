"""
TopBar Component - Main navigation and primary actions area

Provides two-row layout:
- Row 1: Tab navigation (FILE/ANALYZE/EDIT/VALIDATE/FABRICATE/VIEW) + Settings button
- Row 2: Primary actions bar that changes based on active tab
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QLabel, QComboBox, QDialog, QScrollArea, QSizePolicy, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QPoint
from PyQt6.QtGui import QIcon

from app.ui.styles import ThemeManager


class TopBar(QWidget):
    """
    Main TopBar component with tab navigation and primary actions.

    Signals:
        tab_changed(str): Emitted when tab selection changes
        action_triggered(str, str): Emitted when action clicked (tab_name, action_name)
        settings_changed(dict): Emitted when settings are modified
        theme_changed(str): Emitted specifically for theme changes
    """

    tab_changed = pyqtSignal(str)
    action_triggered = pyqtSignal(str, str)
    settings_changed = pyqtSignal(dict)
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_tab = 'file'
        self.settings_dropdown = None

        # Load settings from QSettings
        self.qsettings = QSettings('CeramicMoldAnalyzer', 'LatentApp')
        self.settings = self._load_settings()

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Setup the two-row layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Row 1: Tab Navigation
        tab_row = self._create_tab_row()
        layout.addWidget(tab_row)

        # Row 2: Primary Actions (context-specific)
        self.actions_container = QWidget()
        self.actions_layout = QHBoxLayout(self.actions_container)
        self.actions_layout.setContentsMargins(8, 8, 8, 8)
        self.actions_layout.setSpacing(8)

        # Create all action bars (only one visible at a time)
        self.action_bars = {
            'file': FileActions(self),
            'analyze': AnalyzeActions(self),
            'edit': EditActions(self),
            'validate': ValidateActions(self),
            'fabricate': FabricateActions(self),
            'view': ViewActions(self)
        }

        for tab_name, action_bar in self.action_bars.items():
            action_bar.action_triggered.connect(
                lambda action, tab=tab_name: self.action_triggered.emit(tab, action)
            )
            self.actions_layout.addWidget(action_bar)
            action_bar.setVisible(tab_name == self.active_tab)

        self.actions_layout.addStretch()
        layout.addWidget(self.actions_container)

    def _create_tab_row(self):
        """Create the tab navigation row with settings button"""
        tab_widget = QFrame()
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(8, 0, 8, 0)
        tab_layout.setSpacing(4)

        # Tab buttons
        tabs = [
            ('file', 'FILE', 'F1'),
            ('analyze', 'ANALYZE', 'F2'),
            ('edit', 'EDIT', 'F3'),
            ('validate', 'VALIDATE', 'F4'),
            ('fabricate', 'FABRICATE', 'F5'),
            ('view', 'VIEW', 'F6')
        ]

        self.tab_buttons = {}
        for tab_id, label, shortcut in tabs:
            btn = TabButton(label, shortcut)
            btn.clicked.connect(lambda checked, tid=tab_id: self._on_tab_clicked(tid))
            self.tab_buttons[tab_id] = btn
            tab_layout.addWidget(btn)

        # Update initial active state
        self.tab_buttons[self.active_tab].set_active(True)

        tab_layout.addStretch()

        # Settings button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setToolTip("Program Settings")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.clicked.connect(self._toggle_settings)
        tab_layout.addWidget(self.settings_btn)

        return tab_widget

    def _on_tab_clicked(self, tab_id: str):
        """Handle tab button click"""
        if tab_id == self.active_tab:
            return

        # Update button states
        self.tab_buttons[self.active_tab].set_active(False)
        self.tab_buttons[tab_id].set_active(True)

        # Update action bars visibility
        self.action_bars[self.active_tab].setVisible(False)
        self.action_bars[tab_id].setVisible(True)

        self.active_tab = tab_id
        self.tab_changed.emit(tab_id)

    def set_active_tab(self, tab_id: str):
        """Programmatically set the active tab (for keyboard shortcuts)"""
        if tab_id in self.tab_buttons:
            self._on_tab_clicked(tab_id)

    def _toggle_settings(self):
        """Toggle settings dropdown"""
        if self.settings_dropdown and self.settings_dropdown.isVisible():
            self.settings_dropdown.hide()
        else:
            if not self.settings_dropdown:
                self.settings_dropdown = SettingsDropdown(self.settings, parent=self)
                self.settings_dropdown.settings_changed.connect(self._on_settings_changed)
                self.settings_dropdown.theme_changed.connect(self._on_theme_changed)

            # Position dropdown below settings button, right-aligned
            btn_pos = self.settings_btn.mapToGlobal(self.settings_btn.rect().bottomRight())
            dropdown_width = 288
            self.settings_dropdown.move(btn_pos.x() - dropdown_width, btn_pos.y() + 4)
            self.settings_dropdown.show()
            self.settings_dropdown.raise_()

    def _on_settings_changed(self, settings: dict):
        """Handle settings change"""
        self.settings = settings
        self._save_settings()
        self.settings_changed.emit(settings)

    def _on_theme_changed(self, theme: str):
        """Handle theme change"""
        ThemeManager.set_theme(theme)
        self.theme_changed.emit(theme)

    def _load_settings(self) -> dict:
        """Load settings from QSettings"""
        return {
            'theme': self.qsettings.value('theme', 'light'),
            'length_units': self.qsettings.value('length_units', 'mm'),
            'mass_units': self.qsettings.value('mass_units', 'kg'),
            'volume_units': self.qsettings.value('volume_units', 'ml'),
            'tolerance': self.qsettings.value('tolerance', '0.001')
        }

    def _save_settings(self):
        """Save settings to QSettings"""
        for key, value in self.settings.items():
            self.qsettings.setValue(key, value)
        self.qsettings.sync()

    def _apply_styles(self):
        """Apply component styles"""
        bg = ThemeManager.get_color('bg_primary')
        surface = ThemeManager.get_color('bg_secondary')
        border = ThemeManager.get_color('border')

        self.setStyleSheet(f"""
            TopBar {{
                background-color: {bg};
                border-bottom: 1px solid {border};
            }}
        """)

        self.actions_container.setStyleSheet(f"""
            QWidget {{
                background-color: {surface};
                border-top: 1px solid {border};
            }}
        """)

    def apply_theme(self, theme: str):
        """
        Apply theme to TopBar and all child components.

        Args:
            theme: 'light' or 'dark'
        """
        # Reapply styles with new theme colors
        self._apply_styles()

        # Update tab buttons
        for btn in self.tab_buttons.values():
            btn._apply_styles()

        # Update action bars
        for action_bar in self.action_bars.values():
            if hasattr(action_bar, 'apply_theme'):
                action_bar.apply_theme(theme)

        # Update settings dropdown if it exists
        if self.settings_dropdown:
            if hasattr(self.settings_dropdown, 'apply_theme'):
                self.settings_dropdown.apply_theme(theme)


class TabButton(QPushButton):
    """Individual tab button with active state"""

    def __init__(self, label: str, shortcut: str = '', parent=None):
        super().__init__(label, parent)
        self.label = label
        self.shortcut = shortcut
        self.is_active = False

        if shortcut:
            self.setToolTip(f"{label} ({shortcut})")

        self.setFixedHeight(32)
        self.setMinimumWidth(80)
        self._apply_styles()

    def set_active(self, active: bool):
        """Set active state and update styling"""
        self.is_active = active
        self._apply_styles()

    def _apply_styles(self):
        """Apply button styles based on state"""
        surface = ThemeManager.get_color('bg_secondary')
        text = ThemeManager.get_color('text_primary')
        text_secondary = ThemeManager.get_color('text_secondary')
        accent = ThemeManager.get_color('accent')
        hover_bg = ThemeManager.get_color('hover_bg')

        if self.is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {surface};
                    color: {text};
                    border: none;
                    border-bottom: 2px solid {accent};
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_secondary};
                    border: none;
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }}
                QPushButton:hover {{
                    background-color: {hover_bg};
                    color: {text};
                }}
            """)


class ActionButton(QPushButton):
    """Standard action button for toolbar actions"""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(28)
        self.setMinimumWidth(60)
        self._apply_styles()

    def _apply_styles(self):
        bg = ThemeManager.get_color('bg_primary')
        text = ThemeManager.get_color('text_primary')
        border = ThemeManager.get_color('border')
        surface = ThemeManager.get_color('bg_secondary')
        accent = ThemeManager.get_color('accent')
        pressed = ThemeManager.get_color('pressed_bg')
        disabled_bg = ThemeManager.get_color('disabled_bg')
        disabled_text = ThemeManager.get_color('disabled_text')

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {surface};
                border-color: {accent};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
            QPushButton:disabled {{
                background-color: {disabled_bg};
                color: {disabled_text};
            }}
        """)


class PrimaryButton(QPushButton):
    """Primary action button (blue)"""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(28)
        self.setMinimumWidth(80)
        self._apply_styles()

    def _apply_styles(self):
        accent = ThemeManager.get_color('accent')
        accent_hover = ThemeManager.get_color('accent_hover')
        border = ThemeManager.get_color('border')
        disabled_text = ThemeManager.get_color('disabled_text')

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 16px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {accent_hover};
            }}
            QPushButton:disabled {{
                background-color: {border};
                color: {disabled_text};
            }}
        """)


class ToggleButton(QPushButton):
    """Toggle button for toolbar toggle groups"""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(24)
        self.setMinimumWidth(50)
        self._apply_styles()

    def _apply_styles(self):
        text = ThemeManager.get_color('text_primary')
        hover_bg = ThemeManager.get_color('hover_bg')
        bg_primary = ThemeManager.get_color('bg_primary')

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {text};
                border: none;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                color: {text};
            }}
            QPushButton:checked {{
                background-color: {bg_primary};
                color: {text};
                font-weight: 600;
            }}
        """)


class Separator(QFrame):
    """Vertical separator line"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setFixedWidth(1)
        border = ThemeManager.get_color('border')
        self.setStyleSheet(f"background-color: {border};")


class FileActions(QWidget):
    """Primary actions for FILE tab"""

    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Session actions
        for label in ['New Session', 'Open Session', 'Save Session', 'Save As']:
            btn = ActionButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addWidget(Separator())

        # Rhino actions
        for label in ['Import from Rhino', 'Export to Rhino']:
            btn = ActionButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addStretch()


class AnalyzeActions(QWidget):
    """Primary actions for ANALYZE tab"""

    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Analysis types
        for label in ['Curvature Analysis', 'Spectral Analysis', 'Flow Analysis', 'Topological Analysis']:
            btn = ActionButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addWidget(Separator())

        # Primary action
        analyze_btn = PrimaryButton('Analyze')
        analyze_btn.clicked.connect(lambda: self.action_triggered.emit('Analyze'))
        layout.addWidget(analyze_btn)

        layout.addStretch()


class EditActions(QWidget):
    """Primary actions for EDIT tab"""

    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Edit mode toggle group
        toggle_container = QFrame()
        toggle_container.setStyleSheet(f"background-color: #E0E0E0; border-radius: 4px; padding: 2px;")
        toggle_layout = QHBoxLayout(toggle_container)
        toggle_layout.setContentsMargins(2, 2, 2, 2)
        toggle_layout.setSpacing(2)

        for label in ['Solid', 'Panel', 'Edge', 'Vertex']:
            btn = ToggleButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(f'Mode: {l}'))
            toggle_layout.addWidget(btn)

        layout.addWidget(toggle_container)
        layout.addWidget(Separator())

        # Selection actions
        for label in ['Select All', 'Clear Selection', 'Invert Selection']:
            btn = ActionButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addWidget(Separator())

        # Region actions
        for label in ['Pin/Unpin Region', 'Delete Region']:
            btn = ActionButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addStretch()


class ValidateActions(QWidget):
    """Primary actions for VALIDATE tab"""

    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Primary action
        check_btn = PrimaryButton('Run Constraint Check')
        check_btn.clicked.connect(lambda: self.action_triggered.emit('Run Constraint Check'))
        layout.addWidget(check_btn)

        layout.addWidget(Separator())

        # Filter toggles
        for label in ['Show All Errors', 'Show All Warnings', 'Show Features']:
            btn = ToggleButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addWidget(Separator())

        # Validation actions
        for label in ['Clear Validation', 'Re-validate All']:
            btn = ActionButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addStretch()


class FabricateActions(QWidget):
    """Primary actions for FABRICATE tab"""

    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Generation actions
        for label in ['Generate Mold Shells', 'Add Registration Keys', 'Add Band Grooves', 'Add Pour Spouts']:
            btn = ActionButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addWidget(Separator())

        # Calculation action
        calc_btn = ActionButton('Calculate Slip Volume')
        calc_btn.clicked.connect(lambda: self.action_triggered.emit('Calculate Slip Volume'))
        layout.addWidget(calc_btn)

        # Primary action
        export_btn = PrimaryButton('Export for 3D Printing')
        export_btn.clicked.connect(lambda: self.action_triggered.emit('Export for 3D Printing'))
        layout.addWidget(export_btn)

        layout.addStretch()


class ViewActions(QWidget):
    """Primary actions for VIEW tab"""

    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # View reset actions
        for label in ['Reset All Views', 'Reset Current View', 'Frame All Geometry', 'Frame Selected']:
            btn = ActionButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addWidget(Separator())

        # Display toggles
        for label in ['Show/Hide Axes', 'Show/Hide Grid']:
            btn = ToggleButton(label)
            btn.clicked.connect(lambda checked, l=label: self.action_triggered.emit(l))
            layout.addWidget(btn)

        layout.addStretch()


class SettingsDropdown(QWidget):
    """Settings dropdown panel that appears below the settings gear icon"""

    settings_changed = pyqtSignal(dict)
    theme_changed = pyqtSignal(str)

    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self.current_settings = current_settings.copy()

        # Make it a popup window
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedWidth(288)

        self._setup_ui()
        self._apply_styles()

        # Install event filter to detect clicks outside
        self.installEventFilter(self)

    def _setup_ui(self):
        """Setup settings panel UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_title = QLabel("Program Settings")
        header_title.setStyleSheet("font-size: 11px; font-weight: 600;")
        header_layout.addWidget(header_title)
        main_layout.addWidget(header)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # View Mode section with toggle buttons
        layout.addWidget(self._create_label("View Mode"))
        theme_group = QWidget()
        theme_group_layout = QHBoxLayout(theme_group)
        theme_group_layout.setContentsMargins(4, 4, 4, 4)
        theme_group_layout.setSpacing(8)

        self.theme_button_group = QButtonGroup(self)
        self.light_btn = QPushButton("☀ Light")
        self.light_btn.setCheckable(True)
        self.light_btn.setFixedHeight(28)
        self.dark_btn = QPushButton("☾ Dark")
        self.dark_btn.setCheckable(True)
        self.dark_btn.setFixedHeight(28)

        self.theme_button_group.addButton(self.light_btn, 0)
        self.theme_button_group.addButton(self.dark_btn, 1)

        # Set initial state
        if self.current_settings['theme'] == 'light':
            self.light_btn.setChecked(True)
        else:
            self.dark_btn.setChecked(True)

        self.light_btn.clicked.connect(lambda: self._on_theme_changed('light'))
        self.dark_btn.clicked.connect(lambda: self._on_theme_changed('dark'))

        theme_group_layout.addWidget(self.light_btn)
        theme_group_layout.addWidget(self.dark_btn)
        layout.addWidget(theme_group)

        # Length Units
        layout.addWidget(self._create_label("Length Units"))
        self.length_combo = QComboBox()
        self.length_combo.addItem("Millimeters (mm)", "mm")
        self.length_combo.addItem("Centimeters (cm)", "cm")
        self.length_combo.addItem("Meters (m)", "m")
        self.length_combo.addItem("Fractional Feet & Inches (5' 3 1/2\")", "fractional")
        self.length_combo.addItem("Decimal Inches (63.5\")", "decimal-in")
        self.length_combo.addItem("Decimal Feet (5.29')", "decimal-ft")
        self._set_combo_value(self.length_combo, self.current_settings['length_units'])
        self.length_combo.currentIndexChanged.connect(self._emit_settings_changed)
        layout.addWidget(self.length_combo)

        # Mass Units
        layout.addWidget(self._create_label("Mass Units"))
        self.mass_combo = QComboBox()
        self.mass_combo.addItem("Milligrams (mg)", "mg")
        self.mass_combo.addItem("Grams (g)", "g")
        self.mass_combo.addItem("Kilograms (kg)", "kg")
        self.mass_combo.addItem("Ounces (oz)", "oz")
        self.mass_combo.addItem("Pounds (lb)", "lb")
        self._set_combo_value(self.mass_combo, self.current_settings['mass_units'])
        self.mass_combo.currentIndexChanged.connect(self._emit_settings_changed)
        layout.addWidget(self.mass_combo)

        # Volume Units
        layout.addWidget(self._create_label("Volume Units"))
        self.volume_combo = QComboBox()
        self.volume_combo.addItem("Milliliters (ml)", "ml")
        self.volume_combo.addItem("Liters (L)", "l")
        self.volume_combo.addItem("Cubic Meters (m³)", "m3")
        self.volume_combo.addItem("Fluid Ounces (fl oz)", "floz")
        self.volume_combo.addItem("Cups", "cup")
        self.volume_combo.addItem("Gallons (gal)", "gal")
        self.volume_combo.addItem("Cubic Feet (ft³)", "ft3")
        self._set_combo_value(self.volume_combo, self.current_settings['volume_units'])
        self.volume_combo.currentIndexChanged.connect(self._emit_settings_changed)
        layout.addWidget(self.volume_combo)

        # Tolerance
        layout.addWidget(self._create_label("Tolerance"))
        self.tolerance_combo = QComboBox()
        self.tolerance_combo.addItem("0.1 (coarse)", "0.1")
        self.tolerance_combo.addItem("0.01", "0.01")
        self.tolerance_combo.addItem("0.001 (standard)", "0.001")
        self.tolerance_combo.addItem("0.0001", "0.0001")
        self.tolerance_combo.addItem("0.00001 (fine)", "0.00001")
        self._set_combo_value(self.tolerance_combo, self.current_settings['tolerance'])
        self.tolerance_combo.currentIndexChanged.connect(self._emit_settings_changed)
        layout.addWidget(self.tolerance_combo)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(28)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Set max height to 80vh (approximate)
        screen_height = self.screen().geometry().height()
        max_height = int(screen_height * 0.8)
        self.setMaximumHeight(max_height)

    def _create_label(self, text: str) -> QLabel:
        """Create a styled label"""
        label = QLabel(text)
        label.setStyleSheet("font-size: 11px; font-weight: 600;")
        return label

    def _set_combo_value(self, combo: QComboBox, value: str):
        """Set combo box to value using data role"""
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return

    def _on_theme_changed(self, theme: str):
        """Handle theme toggle"""
        self.current_settings['theme'] = theme
        self.theme_changed.emit(theme)
        self._emit_settings_changed()

    def _emit_settings_changed(self):
        """Emit settings changed signal with current values"""
        self.current_settings = {
            'theme': 'light' if self.light_btn.isChecked() else 'dark',
            'length_units': self.length_combo.currentData(),
            'mass_units': self.mass_combo.currentData(),
            'volume_units': self.volume_combo.currentData(),
            'tolerance': self.tolerance_combo.currentData()
        }
        self.settings_changed.emit(self.current_settings)

    def keyPressEvent(self, event):
        """Handle Escape key to close dropdown"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    def _apply_styles(self):
        """Apply dropdown styles based on current theme"""
        is_dark = ThemeManager.current_theme == 'dark'
        bg = ThemeManager.get_color('bg_primary')
        bg_secondary = ThemeManager.get_color('bg_secondary')
        border = ThemeManager.get_color('border')
        text = ThemeManager.get_color('text_primary')
        text_secondary = ThemeManager.get_color('text_secondary')
        accent = ThemeManager.get_color('accent')
        hover_bg = ThemeManager.get_color('hover_bg')

        self.setStyleSheet(f"""
            SettingsDropdown {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_secondary};
            }}
            QComboBox {{
                background-color: {bg};
                color: {text};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
            }}
            QComboBox:hover {{
                border-color: {accent};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {text_secondary};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg};
                color: {text};
                border: 1px solid {border};
                selection-background-color: {accent};
                selection-color: white;
                outline: none;
            }}
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                border-color: {accent};
            }}
            QPushButton:checked {{
                background-color: {'#1A1A1A' if is_dark else '#FFFFFF'};
                color: {text};
                border-color: {accent};
                font-weight: 600;
            }}
            QScrollArea {{
                background-color: {bg};
                border: none;
            }}
        """)
