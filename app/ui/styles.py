"""
Global Stylesheets for Ceramic Mold Analyzer

Provides consistent styling across the application using PyQt6 stylesheets.
"""


# Color palette
COLORS = {
    # Primary colors
    'primary': '#007AFF',
    'primary_hover': '#0051D5',
    'primary_pressed': '#003D99',

    # Success/Error/Warning
    'success': '#34C759',
    'success_hover': '#30B350',
    'error': '#FF3B30',
    'error_hover': '#D32F2F',
    'warning': '#FFCC00',
    'warning_hover': '#E6B800',

    # Neutral colors
    'background': '#FFFFFF',
    'surface': '#F5F5F5',
    'border': '#CCCCCC',
    'text': '#333333',
    'text_secondary': '#666666',
    'text_disabled': '#999999',

    # Selection/Highlight
    'selection': '#E3F2FD',
    'highlight': '#FFF9C4',
}


# Button styles
BUTTON_PRIMARY = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        min-width: 80px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['primary_hover']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['primary_pressed']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['border']};
        color: {COLORS['text_disabled']};
    }}
"""

BUTTON_SUCCESS = f"""
    QPushButton {{
        background-color: {COLORS['success']};
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        min-width: 80px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['success_hover']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['border']};
        color: {COLORS['text_disabled']};
    }}
"""

BUTTON_DANGER = f"""
    QPushButton {{
        background-color: {COLORS['error']};
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        min-width: 80px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['error_hover']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['border']};
        color: {COLORS['text_disabled']};
    }}
"""

BUTTON_SECONDARY = f"""
    QPushButton {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        padding: 8px 16px;
        border-radius: 4px;
        min-width: 80px;
    }}
    QPushButton:hover {{
        background-color: #E0E0E0;
        border-color: {COLORS['primary']};
    }}
    QPushButton:pressed {{
        background-color: #D0D0D0;
    }}
    QPushButton:disabled {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_disabled']};
        border-color: {COLORS['border']};
    }}
"""

TOOLBUTTON_STYLE = f"""
    QToolButton {{
        background-color: transparent;
        border: none;
        padding: 4px;
        border-radius: 3px;
    }}
    QToolButton:hover {{
        background-color: rgba(0, 122, 255, 0.1);
    }}
    QToolButton:pressed {{
        background-color: rgba(0, 122, 255, 0.2);
    }}
    QToolButton:checked {{
        background-color: {COLORS['primary']};
        color: white;
    }}
    QToolButton:disabled {{
        color: {COLORS['text_disabled']};
    }}
"""


# Input styles
INPUT_STYLE = f"""
    QLineEdit, QTextEdit, QPlainTextEdit {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
        background-color: white;
        selection-background-color: {COLORS['primary']};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {COLORS['primary']};
    }}
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_disabled']};
    }}
"""

COMBOBOX_STYLE = f"""
    QComboBox {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
        background-color: white;
        min-width: 80px;
    }}
    QComboBox:hover {{
        border-color: {COLORS['primary']};
    }}
    QComboBox:disabled {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_disabled']};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {COLORS['text']};
        margin-right: 5px;
    }}
"""

SPINBOX_STYLE = f"""
    QSpinBox, QDoubleSpinBox {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 6px;
        background-color: white;
    }}
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {COLORS['primary']};
    }}
    QSpinBox:disabled, QDoubleSpinBox:disabled {{
        background-color: {COLORS['surface']};
        color: {COLORS['text_disabled']};
    }}
"""


# Progress bar style
PROGRESSBAR_STYLE = f"""
    QProgressBar {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        text-align: center;
        background-color: {COLORS['surface']};
    }}
    QProgressBar::chunk {{
        background-color: {COLORS['primary']};
        border-radius: 3px;
    }}
"""


# Group box style
GROUPBOX_STYLE = f"""
    QGroupBox {{
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 8px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 5px;
        color: {COLORS['text']};
    }}
"""


# List and tree widget styles
LISTWIDGET_STYLE = f"""
    QListWidget {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        background-color: white;
        outline: none;
    }}
    QListWidget::item {{
        padding: 6px;
        border-radius: 3px;
    }}
    QListWidget::item:hover {{
        background-color: {COLORS['selection']};
    }}
    QListWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}
"""

TREEWIDGET_STYLE = f"""
    QTreeWidget {{
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        background-color: white;
        outline: none;
    }}
    QTreeWidget::item {{
        padding: 4px;
    }}
    QTreeWidget::item:hover {{
        background-color: {COLORS['selection']};
    }}
    QTreeWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}
"""


# Toolbar style
TOOLBAR_STYLE = f"""
    QToolBar {{
        background-color: {COLORS['surface']};
        border: none;
        border-bottom: 1px solid {COLORS['border']};
        spacing: 3px;
        padding: 3px;
    }}
    QToolBar::separator {{
        background-color: {COLORS['border']};
        width: 1px;
        margin: 4px;
    }}
"""


# Status bar style
STATUSBAR_STYLE = f"""
    QStatusBar {{
        background-color: {COLORS['surface']};
        border-top: 1px solid {COLORS['border']};
    }}
    QStatusBar::item {{
        border: none;
    }}
"""


# Dock widget style
DOCKWIDGET_STYLE = f"""
    QDockWidget {{
        border: 1px solid {COLORS['border']};
        titlebar-close-icon: url(close.png);
        titlebar-normal-icon: url(undock.png);
    }}
    QDockWidget::title {{
        background-color: {COLORS['surface']};
        padding: 6px;
        border-bottom: 1px solid {COLORS['border']};
        font-weight: bold;
    }}
    QDockWidget::close-button, QDockWidget::float-button {{
        border: none;
        background: transparent;
        padding: 0px;
    }}
    QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
        background-color: rgba(0, 122, 255, 0.1);
    }}
"""


# Menu style
MENU_STYLE = f"""
    QMenuBar {{
        background-color: {COLORS['surface']};
        border-bottom: 1px solid {COLORS['border']};
    }}
    QMenuBar::item {{
        padding: 6px 12px;
    }}
    QMenuBar::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}
    QMenu {{
        background-color: white;
        border: 1px solid {COLORS['border']};
    }}
    QMenu::item {{
        padding: 6px 30px 6px 20px;
    }}
    QMenu::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}
"""


# Global application stylesheet
GLOBAL_STYLESHEET = f"""
    /* Base styling */
    QWidget {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        color: {COLORS['text']};
    }}

    /* Tooltips */
    QToolTip {{
        border: 1px solid {COLORS['border']};
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        padding: 5px;
        border-radius: 3px;
    }}

    {INPUT_STYLE}
    {COMBOBOX_STYLE}
    {SPINBOX_STYLE}
    {PROGRESSBAR_STYLE}
    {GROUPBOX_STYLE}
    {LISTWIDGET_STYLE}
    {TREEWIDGET_STYLE}
    {TOOLBAR_STYLE}
    {STATUSBAR_STYLE}
    {MENU_STYLE}
"""


def get_button_style(variant: str = 'primary') -> str:
    """
    Get button stylesheet for specified variant.

    Args:
        variant: 'primary', 'success', 'danger', or 'secondary'

    Returns:
        Button stylesheet string
    """
    styles = {
        'primary': BUTTON_PRIMARY,
        'success': BUTTON_SUCCESS,
        'danger': BUTTON_DANGER,
        'secondary': BUTTON_SECONDARY,
    }
    return styles.get(variant, BUTTON_PRIMARY)


def get_loading_button_style(base_variant: str = 'primary') -> str:
    """
    Get button style for loading state (disabled with spinner).

    Args:
        base_variant: Base button variant

    Returns:
        Loading button stylesheet
    """
    return get_button_style(base_variant) + f"""
        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_disabled']};
        }}
    """
