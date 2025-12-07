"""
Focus Visibility and Accessibility Styles

Provides enhanced focus indicators that work across both light and dark themes.
Ensures WCAG 2.1 Level AA compliance for focus visibility.
"""

from typing import Literal


def get_focus_stylesheet(theme: Literal['light', 'dark'] = 'light') -> str:
    """
    Get enhanced focus visibility stylesheet for accessibility.

    This ensures all focusable elements have clear, visible focus indicators
    that meet WCAG 2.1 Level AA requirements (minimum 2px outline, 3:1 contrast).

    Args:
        theme: 'light' or 'dark'

    Returns:
        QSS stylesheet string with focus enhancements
    """
    # Focus ring colors with sufficient contrast
    if theme == 'dark':
        focus_color = '#60A5FA'  # Lighter blue for dark backgrounds
        focus_background = '#1E3A5F'
    else:
        focus_color = '#2563EB'  # Darker blue for light backgrounds
        focus_background = '#E3F2FD'

    return f"""
        /* ===== ENHANCED FOCUS VISIBILITY ===== */

        /* Push Buttons */
        QPushButton:focus {{
            outline: 2px solid {focus_color};
            outline-offset: 2px;
            border-color: {focus_color};
        }}

        /* Tool Buttons */
        QToolButton:focus {{
            outline: 2px solid {focus_color};
            outline-offset: 2px;
            background-color: {focus_background};
        }}

        /* Radio Buttons */
        QRadioButton:focus {{
            outline: 2px solid {focus_color};
            outline-offset: 2px;
            border-radius: 4px;
        }}

        QRadioButton::indicator:focus {{
            border: 2px solid {focus_color};
        }}

        /* Check Boxes */
        QCheckBox:focus {{
            outline: 2px solid {focus_color};
            outline-offset: 2px;
            border-radius: 4px;
        }}

        QCheckBox::indicator:focus {{
            border: 2px solid {focus_color};
        }}

        /* Combo Boxes */
        QComboBox:focus {{
            border: 2px solid {focus_color};
            outline: 2px solid {focus_color}40;  /* 25% opacity */
            outline-offset: 1px;
        }}

        /* Line Edits */
        QLineEdit:focus {{
            border: 2px solid {focus_color};
            outline: 2px solid {focus_color}40;
            outline-offset: 1px;
        }}

        /* Text Edits */
        QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {focus_color};
            outline: 2px solid {focus_color}40;
            outline-offset: 1px;
        }}

        /* Spin Boxes */
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {focus_color};
            outline: 2px solid {focus_color}40;
            outline-offset: 1px;
        }}

        /* Sliders */
        QSlider:focus {{
            outline: 2px solid {focus_color};
            outline-offset: 2px;
        }}

        QSlider::handle:focus {{
            border: 2px solid {focus_color};
            outline: 2px solid {focus_color}40;
            outline-offset: 1px;
        }}

        /* List Widgets */
        QListWidget:focus {{
            border: 2px solid {focus_color};
        }}

        QListWidget::item:focus {{
            outline: 2px solid {focus_color};
            outline-offset: -2px;  /* Inside the item */
        }}

        /* Tree Widgets */
        QTreeWidget:focus, QTreeView:focus {{
            border: 2px solid {focus_color};
        }}

        QTreeWidget::item:focus, QTreeView::item:focus {{
            outline: 2px solid {focus_color};
            outline-offset: -2px;
        }}

        /* Table Widgets */
        QTableWidget:focus, QTableView:focus {{
            border: 2px solid {focus_color};
        }}

        QTableWidget::item:focus, QTableView::item:focus {{
            outline: 2px solid {focus_color};
            outline-offset: -2px;
        }}

        /* Tab Widgets */
        QTabBar::tab:focus {{
            outline: 2px solid {focus_color};
            outline-offset: 2px;
        }}

        /* Scroll Areas */
        QScrollArea:focus {{
            border: 2px solid {focus_color};
        }}

        /* Group Boxes */
        QGroupBox:focus {{
            border: 2px solid {focus_color};
        }}

        /* Splitters */
        QSplitter::handle:focus {{
            background-color: {focus_color};
        }}
    """


def get_high_contrast_adjustments(theme: Literal['light', 'dark'] = 'light') -> str:
    """
    Get high contrast mode adjustments for better visibility.

    Args:
        theme: 'light' or 'dark'

    Returns:
        QSS stylesheet string with high contrast adjustments
    """
    if theme == 'dark':
        # Dark high contrast
        bg = '#000000'
        fg = '#FFFFFF'
        border = '#FFFFFF'
        accent = '#00FFFF'  # Cyan
        hover = '#333333'
    else:
        # Light high contrast
        bg = '#FFFFFF'
        fg = '#000000'
        border = '#000000'
        accent = '#0000FF'  # Blue
        hover = '#EEEEEE'

    return f"""
        /* ===== HIGH CONTRAST MODE ===== */

        QWidget {{
            background-color: {bg};
            color: {fg};
        }}

        QPushButton, QToolButton {{
            border: 2px solid {border};
            color: {fg};
            background-color: {bg};
        }}

        QPushButton:hover, QToolButton:hover {{
            background-color: {hover};
        }}

        QPushButton:focus, QToolButton:focus {{
            outline: 3px solid {accent};
            outline-offset: 2px;
        }}

        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
            border: 2px solid {border};
            color: {fg};
            background-color: {bg};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
            outline: 3px solid {accent};
            outline-offset: 1px;
        }}

        QRadioButton, QCheckBox {{
            color: {fg};
        }}

        QRadioButton::indicator, QCheckBox::indicator {{
            border: 2px solid {border};
            background-color: {bg};
        }}

        QRadioButton::indicator:checked, QCheckBox::indicator:checked {{
            background-color: {accent};
        }}

        QListWidget::item:selected, QTreeWidget::item:selected,
        QTableWidget::item:selected {{
            background-color: {accent};
            color: {bg};
        }}

        QMenuBar::item:pressed, QMenu::item:selected {{
            background-color: {accent};
            color: {bg};
        }}
    """


def apply_keyboard_navigation_hints() -> str:
    """
    Get stylesheet for keyboard navigation visual hints.

    Returns:
        QSS stylesheet for keyboard nav hints
    """
    return """
        /* ===== KEYBOARD NAVIGATION HINTS ===== */

        /* Show tab order numbers (debugging only) */
        QWidget[showTabOrder="true"]::before {{
            content: attr(tabOrder);
            position: absolute;
            top: 0;
            left: 0;
            background-color: rgba(255, 0, 0, 0.8);
            color: white;
            padding: 2px 4px;
            font-size: 10px;
            font-weight: bold;
            border-radius: 2px;
        }}

        /* Indicate keyboard focusable elements */
        *:focus {{
            /* This is handled by get_focus_stylesheet */
        }}

        /* Skip links for screen readers (visually hidden but accessible) */
        .skip-link {{
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        }}

        .skip-link:focus {{
            position: static;
            width: auto;
            height: auto;
            overflow: visible;
        }}
    """


# Export combined accessibility stylesheet
def get_accessibility_stylesheet(theme: Literal['light', 'dark'] = 'light',
                                 high_contrast: bool = False) -> str:
    """
    Get complete accessibility stylesheet with focus and high contrast support.

    Args:
        theme: 'light' or 'dark'
        high_contrast: Enable high contrast mode

    Returns:
        Complete accessibility QSS stylesheet
    """
    styles = [
        get_focus_stylesheet(theme),
        apply_keyboard_navigation_hints(),
    ]

    if high_contrast:
        styles.append(get_high_contrast_adjustments(theme))

    return '\n\n'.join(styles)
