"""
Region List Widget - Enhanced version for dockable panels
Shows discovered regions with pin/edit controls and sorting/filtering
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QComboBox, QLineEdit, QToolButton
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QBrush


class RegionListWidget(QWidget):
    """Enhanced widget for displaying and managing discovered regions"""

    # Signals
    region_selected = pyqtSignal(str)  # region_id
    region_pinned = pyqtSignal(str, bool)  # region_id, is_pinned
    region_edit_requested = pyqtSignal(str)  # region_id
    region_deleted = pyqtSignal(str)  # region_id
    region_properties_requested = pyqtSignal(str)  # region_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.regions = []
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Header with count
        header_layout = QHBoxLayout()
        self.count_label = QLabel("Regions: 0")
        self.count_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Filter/Sort controls
        filter_layout = QHBoxLayout()

        # Search/filter box
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter regions...")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)

        # Sort combo
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Unity ↓", "Unity ↑", "Pinned First"])
        self.sort_combo.currentIndexChanged.connect(self.apply_sort)
        self.sort_combo.setMaximumWidth(100)
        filter_layout.addWidget(self.sort_combo)

        layout.addLayout(filter_layout)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)

        # Action buttons row
        button_layout = QHBoxLayout()

        self.pin_btn = QPushButton("📌")
        self.pin_btn.setToolTip("Pin/Unpin selected region")
        self.pin_btn.setMaximumWidth(40)
        self.pin_btn.clicked.connect(self.toggle_pin)
        self.pin_btn.setEnabled(False)
        button_layout.addWidget(self.pin_btn)

        self.edit_btn = QPushButton("✏️")
        self.edit_btn.setToolTip("Edit region boundary")
        self.edit_btn.setMaximumWidth(40)
        self.edit_btn.clicked.connect(self.edit_region)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setToolTip("Delete region")
        self.delete_btn.setMaximumWidth(40)
        self.delete_btn.clicked.connect(self.delete_region)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        button_layout.addStretch()

        # Batch actions
        self.pin_all_btn = QPushButton("Pin All")
        self.pin_all_btn.setMaximumWidth(70)
        self.pin_all_btn.clicked.connect(self.pin_all)
        button_layout.addWidget(self.pin_all_btn)

        self.unpin_all_btn = QPushButton("Unpin All")
        self.unpin_all_btn.setMaximumWidth(80)
        self.unpin_all_btn.clicked.connect(self.unpin_all)
        button_layout.addWidget(self.unpin_all_btn)

        layout.addLayout(button_layout)

        # Statistics
        self.stats_label = QLabel("Select a region to view details")
        self.stats_label.setStyleSheet("color: gray; font-size: 10px;")
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)

    def set_regions(self, regions):
        """Update the displayed regions"""
        self.regions = regions
        self.refresh_list()
        self.update_count()

    def refresh_list(self):
        """Refresh the list display with current regions"""
        # Store current selection
        current_item = self.list_widget.currentItem()
        current_id = current_item.data(Qt.ItemDataRole.UserRole) if current_item else None

        self.list_widget.clear()

        # Apply sorting
        sorted_regions = self.get_sorted_regions()

        # Apply filter
        filter_text = self.filter_input.text().lower()

        for region in sorted_regions:
            # Filter check
            if filter_text and filter_text not in region.id.lower():
                continue

            # Create list item
            item_text = f"{region.id}"
            if region.unity_strength > 0:
                item_text += f" (Unity: {region.unity_strength:.2f})"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, region.id)

            # Style based on state
            if region.pinned:
                # Pinned regions have special styling
                item.setForeground(QBrush(QColor(0, 122, 255)))  # Blue text
                item.setText("📌 " + item_text)
                item.setBackground(QBrush(QColor(240, 247, 255)))  # Light blue bg
            else:
                item.setForeground(QBrush(QColor(0, 0, 0)))

            # Color code by unity strength
            if region.unity_strength >= 0.8:
                # High unity - green tint
                if not region.pinned:
                    item.setBackground(QBrush(QColor(240, 255, 240)))
            elif region.unity_strength < 0.6:
                # Low unity - yellow tint
                if not region.pinned:
                    item.setBackground(QBrush(QColor(255, 255, 230)))

            self.list_widget.addItem(item)

        # Restore selection
        if current_id:
            self.select_region(current_id)

    def get_sorted_regions(self):
        """Get regions sorted according to current sort setting"""
        sort_method = self.sort_combo.currentText()

        if sort_method == "Name":
            return sorted(self.regions, key=lambda r: r.id)
        elif sort_method == "Unity ↓":
            return sorted(self.regions, key=lambda r: r.unity_strength, reverse=True)
        elif sort_method == "Unity ↑":
            return sorted(self.regions, key=lambda r: r.unity_strength)
        elif sort_method == "Pinned First":
            return sorted(self.regions, key=lambda r: (not r.pinned, r.id))
        else:
            return self.regions

    def apply_filter(self):
        """Apply filter to region list"""
        self.refresh_list()

    def apply_sort(self):
        """Apply sort to region list"""
        self.refresh_list()

    def update_count(self):
        """Update region count display"""
        total = len(self.regions)
        pinned = sum(1 for r in self.regions if r.pinned)
        self.count_label.setText(f"Regions: {total} ({pinned} pinned)")

    def on_selection_changed(self):
        """Handle selection change"""
        current_item = self.list_widget.currentItem()
        if current_item:
            region_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.region_selected.emit(region_id)

            # Enable buttons
            self.pin_btn.setEnabled(True)
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)

            # Update pin button icon
            region = self.get_region_by_id(region_id)
            if region:
                if region.pinned:
                    self.pin_btn.setText("📍")
                    self.pin_btn.setToolTip("Unpin region")
                else:
                    self.pin_btn.setText("📌")
                    self.pin_btn.setToolTip("Pin region")

                # Update stats
                self.update_stats(region)
        else:
            self.pin_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.stats_label.setText("Select a region to view details")

    def on_item_double_clicked(self, item):
        """Handle double-click on region item to open properties"""
        if item:
            region_id = item.data(Qt.ItemDataRole.UserRole)
            self.region_properties_requested.emit(region_id)

    def update_stats(self, region):
        """Update statistics display for selected region"""
        stats = f"<b>{region.id}</b><br>"
        stats += f"Unity: {region.unity_strength:.3f}<br>"
        stats += f"Faces: {len(region.faces)}<br>"
        stats += f"Principle: {region.unity_principle}<br>"
        stats += f"Status: {'Pinned' if region.pinned else 'Unpinned'}"
        self.stats_label.setText(stats)

    def toggle_pin(self):
        """Toggle pin state of selected region"""
        current_item = self.list_widget.currentItem()
        if current_item:
            region_id = current_item.data(Qt.ItemDataRole.UserRole)
            region = self.get_region_by_id(region_id)
            if region:
                new_pinned = not region.pinned
                self.region_pinned.emit(region_id, new_pinned)

                # Update local state for immediate feedback
                region.pinned = new_pinned
                self.refresh_list()
                self.update_count()

                # Restore selection
                self.select_region(region_id)

    def pin_all(self):
        """Pin all regions"""
        for region in self.regions:
            if not region.pinned:
                self.region_pinned.emit(region.id, True)
                region.pinned = True
        self.refresh_list()
        self.update_count()

    def unpin_all(self):
        """Unpin all regions"""
        for region in self.regions:
            if region.pinned:
                self.region_pinned.emit(region.id, False)
                region.pinned = False
        self.refresh_list()
        self.update_count()

    def edit_region(self):
        """Request to edit selected region"""
        current_item = self.list_widget.currentItem()
        if current_item:
            region_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.region_edit_requested.emit(region_id)

    def delete_region(self):
        """Delete selected region"""
        current_item = self.list_widget.currentItem()
        if current_item:
            region_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.region_deleted.emit(region_id)

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

    def clear(self):
        """Clear all regions"""
        self.regions = []
        self.list_widget.clear()
        self.update_count()
        self.stats_label.setText("No regions discovered yet")
