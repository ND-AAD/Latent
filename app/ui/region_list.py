"""
Region List Widget - Shows discovered regions with pin/edit controls
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QHBoxLayout, QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt


class RegionListWidget(QWidget):
    """Widget for displaying and managing discovered regions"""
    
    # Signals
    region_selected = pyqtSignal(str)  # region_id
    region_pinned = pyqtSignal(str, bool)  # region_id, is_pinned
    region_edit_requested = pyqtSignal(str)  # region_id
    
    def __init__(self):
        super().__init__()
        self.regions = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.pin_btn = QPushButton("📌 Pin")
        self.pin_btn.clicked.connect(self.toggle_pin)
        self.pin_btn.setEnabled(False)
        button_layout.addWidget(self.pin_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self.edit_region)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)
        
        layout.addLayout(button_layout)
    
    def set_regions(self, regions):
        """Update the displayed regions"""
        self.regions = regions
        self.list_widget.clear()
        
        for region in regions:
            # Create list item
            item_text = f"{'📌 ' if region.pinned else ''}{region.id}"
            if region.unity_strength > 0:
                item_text += f" (Unity: {region.unity_strength:.2f})"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, region.id)
            
            # Style based on state
            if region.pinned:
                item.setBackground(Qt.GlobalColor.lightGray)
            
            self.list_widget.addItem(item)
    
    def on_selection_changed(self):
        """Handle selection change"""
        current_item = self.list_widget.currentItem()
        if current_item:
            region_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.region_selected.emit(region_id)
            
            # Enable buttons
            self.pin_btn.setEnabled(True)
            self.edit_btn.setEnabled(True)
            
            # Update pin button text
            region = self.get_region_by_id(region_id)
            if region and region.pinned:
                self.pin_btn.setText("📌 Unpin")
            else:
                self.pin_btn.setText("📌 Pin")
        else:
            self.pin_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
    
    def toggle_pin(self):
        """Toggle pin state of selected region"""
        current_item = self.list_widget.currentItem()
        if current_item:
            region_id = current_item.data(Qt.ItemDataRole.UserRole)
            region = self.get_region_by_id(region_id)
            if region:
                new_pinned = not region.pinned
                self.region_pinned.emit(region_id, new_pinned)
                
                # Update display
                region.pinned = new_pinned
                self.set_regions(self.regions)
                
                # Restore selection
                self.select_region(region_id)
    
    def edit_region(self):
        """Request to edit selected region"""
        current_item = self.list_widget.currentItem()
        if current_item:
            region_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.region_edit_requested.emit(region_id)
    
    def select_region(self, region_id):
        """Select a region by ID"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == region_id:
                self.list_widget.setCurrentItem(item)
                break
    
    def get_region_by_id(self, region_id):
        """Get region object by ID"""
        for region in self.regions:
            if region.id == region_id:
                return region
        return None
