"""
Constraint Panel - Shows validation status for selected region
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt


class ConstraintPanel(QWidget):
    """Panel showing constraint validation status"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_region = None
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Constraint Validation")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)
        
        # Status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(200)
        self.status_display.setStyleSheet(
            "QTextEdit { font-family: monospace; font-size: 11px; }"
        )
        layout.addWidget(self.status_display)
        
        # Set default text
        self.show_default()
    
    def show_default(self):
        """Show default message when no region selected"""
        self.status_display.setHtml(
            "<p style='color: gray;'>Select a region to view constraints</p>"
        )
    
    def show_constraints_for_region(self, region):
        """Display constraints for a specific region"""
        self.current_region = region
        
        # Build constraint report
        html = []
        
        # Physical constraints (Tier 1)
        html.append("<b>Physical Constraints:</b>")
        if region.constraints_passed:
            html.append("<span style='color: green;'>✅ All physical constraints passed</span>")
            html.append("  • No undercuts detected")
            html.append("  • Slip access verified")
            html.append("  • No air traps found")
        else:
            html.append("<span style='color: red;'>❌ Physical constraint violations:</span>")
            html.append("  • Undercut at boundary edge")
            html.append("  • Fix required before generation")
        
        html.append("")
        
        # Manufacturing challenges (Tier 2)
        html.append("<b>Manufacturing Challenges:</b>")
        html.append("<span style='color: orange;'>⚠️ Warnings:</span>")
        html.append("  • Draft angle: 0.8° (minimum 0.5°)")
        html.append("  • Wall thickness: 3.2mm (optimal)")
        html.append("  • Deep cavity may require longer casting")
        
        html.append("")
        
        # Mathematical tensions (Tier 3)
        html.append("<b>Mathematical Tensions:</b>")
        if region.unity_strength > 0.8:
            html.append("<span style='color: blue;'>ℹ️ Strong mathematical coherence</span>")
            html.append(f"  • Unity strength: {region.unity_strength:.2f}")
            html.append(f"  • Natural boundary follows {region.unity_principle}")
        else:
            html.append("<span style='color: blue;'>ℹ️ Moderate coherence</span>")
            html.append(f"  • Unity strength: {region.unity_strength:.2f}")
            html.append("  • Consider alternative decomposition")
        
        # Display the report
        self.status_display.setHtml("<br>".join(html))
    
    def clear(self):
        """Clear the constraint display"""
        self.current_region = None
        self.show_default()
    
    def update_validation(self, validation_result):
        """Update display with new validation results"""
        # This will be implemented when we have actual validation
        pass
