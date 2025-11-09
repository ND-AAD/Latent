"""
Region Editor Widget - UI for region manipulation operations

Provides controls for merging adjacent regions and splitting regions along curves.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget,
    QHBoxLayout, QGroupBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Optional
from app.state.parametric_region import ParametricRegion


class RegionEditorWidget(QWidget):
    """
    UI for region editing operations.

    Signals:
        merge_requested: User clicked merge with selected region IDs
        split_requested: User clicked split with region ID
        selection_changed: User selected different regions
    """

    merge_requested = pyqtSignal(list)  # List of region IDs to merge
    split_requested = pyqtSignal(str)   # Region ID to split
    selection_changed = pyqtSignal(list)  # List of selected region IDs

    def __init__(self, parent=None):
        super().__init__(parent)
        self.regions: List[ParametricRegion] = []
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Title
        title_label = QLabel("Region Editing")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)

        # Selection group
        selection_group = QGroupBox("Selected Regions")
        selection_layout = QVBoxLayout()

        # Region list for multi-selection
        self.region_list = QListWidget()
        self.region_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.region_list.itemSelectionChanged.connect(self._on_selection_changed)
        selection_layout.addWidget(self.region_list)

        # Selection info
        self.selection_info = QLabel("No regions selected")
        self.selection_info.setStyleSheet("color: gray; font-size: 9pt;")
        selection_layout.addWidget(self.selection_info)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Merge group
        merge_group = QGroupBox("Merge Operations")
        merge_layout = QVBoxLayout()

        # Merge button
        self.merge_btn = QPushButton("Merge Selected Regions")
        self.merge_btn.setToolTip("Combine multiple regions into one")
        self.merge_btn.clicked.connect(self._on_merge_clicked)
        self.merge_btn.setEnabled(False)
        merge_layout.addWidget(self.merge_btn)

        # Merge info
        merge_info = QLabel("Select 2+ regions to merge")
        merge_info.setStyleSheet("color: gray; font-size: 9pt;")
        merge_info.setWordWrap(True)
        merge_layout.addWidget(merge_info)

        merge_group.setLayout(merge_layout)
        layout.addWidget(merge_group)

        # Split group
        split_group = QGroupBox("Split Operations")
        split_layout = QVBoxLayout()

        # Split button
        self.split_btn = QPushButton("Split Region...")
        self.split_btn.setToolTip("Divide region along a curve")
        self.split_btn.clicked.connect(self._on_split_clicked)
        self.split_btn.setEnabled(False)
        split_layout.addWidget(self.split_btn)

        # Split info
        split_info = QLabel("Select 1 region to split")
        split_info.setStyleSheet("color: gray; font-size: 9pt;")
        split_info.setWordWrap(True)
        split_layout.addWidget(split_info)

        split_group.setLayout(split_layout)
        layout.addWidget(split_group)

        # Add stretch to push everything to top
        layout.addStretch()

    def set_regions(self, regions: List[ParametricRegion]):
        """
        Update the list of available regions.

        Args:
            regions: List of ParametricRegion objects
        """
        self.regions = regions
        self._update_region_list()

    def _update_region_list(self):
        """Refresh the region list display"""
        # Store current selection
        selected_ids = self.get_selected_region_ids()

        # Clear and rebuild
        self.region_list.clear()

        for region in self.regions:
            # Create display text
            pin_icon = "📌 " if region.pinned else ""
            modified_icon = "✏️ " if region.modified else ""
            item_text = f"{pin_icon}{modified_icon}{region.id}"

            if region.unity_principle:
                item_text += f" ({region.unity_principle})"

            if region.unity_strength > 0:
                item_text += f" [{region.unity_strength:.2f}]"

            item_text += f" - {len(region.faces)} faces"

            # Add to list
            self.region_list.addItem(item_text)
            item = self.region_list.item(self.region_list.count() - 1)
            item.setData(Qt.ItemDataRole.UserRole, region.id)

            # Restore selection
            if region.id in selected_ids:
                item.setSelected(True)

    def _on_selection_changed(self):
        """Handle region selection changes"""
        selected_ids = self.get_selected_region_ids()
        count = len(selected_ids)

        # Update info label
        if count == 0:
            self.selection_info.setText("No regions selected")
        elif count == 1:
            region = self._get_region_by_id(selected_ids[0])
            if region:
                self.selection_info.setText(
                    f"1 region: {len(region.faces)} faces, "
                    f"strength={region.unity_strength:.2f}"
                )
        else:
            total_faces = sum(
                len(self._get_region_by_id(rid).faces)
                for rid in selected_ids
                if self._get_region_by_id(rid)
            )
            self.selection_info.setText(
                f"{count} regions selected, {total_faces} total faces"
            )

        # Enable/disable buttons
        self.merge_btn.setEnabled(count >= 2)
        self.split_btn.setEnabled(count == 1)

        # Emit signal
        self.selection_changed.emit(selected_ids)

    def _on_merge_clicked(self):
        """Handle merge button click"""
        selected_ids = self.get_selected_region_ids()

        if len(selected_ids) < 2:
            QMessageBox.warning(
                self,
                "Cannot Merge",
                "Please select at least 2 regions to merge."
            )
            return

        # Confirm merge
        reply = QMessageBox.question(
            self,
            "Confirm Merge",
            f"Merge {len(selected_ids)} regions into one?\n\n"
            f"This will create a new region and remove the selected regions.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.merge_requested.emit(selected_ids)

    def _on_split_clicked(self):
        """Handle split button click"""
        selected_ids = self.get_selected_region_ids()

        if len(selected_ids) != 1:
            QMessageBox.warning(
                self,
                "Cannot Split",
                "Please select exactly 1 region to split."
            )
            return

        # For now, emit split request
        # Future: Show curve drawing interface
        QMessageBox.information(
            self,
            "Split Region",
            "Split functionality will draw a curve on the surface.\n\n"
            "For now, this performs an automatic split of the region."
        )

        self.split_requested.emit(selected_ids[0])

    def get_selected_region_ids(self) -> List[str]:
        """
        Get the IDs of currently selected regions.

        Returns:
            List of region ID strings
        """
        selected_ids = []
        for item in self.region_list.selectedItems():
            region_id = item.data(Qt.ItemDataRole.UserRole)
            if region_id:
                selected_ids.append(region_id)
        return selected_ids

    def select_region(self, region_id: str):
        """
        Programmatically select a region by ID.

        Args:
            region_id: ID of region to select
        """
        for i in range(self.region_list.count()):
            item = self.region_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == region_id:
                item.setSelected(True)
                return

    def clear_selection(self):
        """Clear all region selections"""
        self.region_list.clearSelection()

    def _get_region_by_id(self, region_id: str) -> Optional[ParametricRegion]:
        """
        Get region object by ID.

        Args:
            region_id: Region ID to find

        Returns:
            ParametricRegion or None if not found
        """
        for region in self.regions:
            if region.id == region_id:
                return region
        return None
