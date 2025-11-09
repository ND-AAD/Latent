"""
Iteration Timeline UI Widget
Provides visual management of design iteration snapshots
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QMessageBox, QInputDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage, QIcon

from app.state.app_state import ApplicationState
from app.state.iteration_manager import DesignIteration


class IterationListItem(QWidget):
    """
    Custom widget for displaying an iteration in the list with thumbnail
    """

    def __init__(self, iteration: DesignIteration, parent=None):
        super().__init__(parent)
        self.iteration = iteration

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(64, 64)
        self.thumbnail_label.setScaledContents(True)

        if iteration.thumbnail:
            # Load thumbnail from bytes
            image = QImage.fromData(iteration.thumbnail)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                self.thumbnail_label.setPixmap(pixmap)
            else:
                self.thumbnail_label.setText("No\nImage")
                self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.thumbnail_label.setText("No\nImage")
            self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.thumbnail_label.setStyleSheet("background-color: #333; color: #888;")
        layout.addWidget(self.thumbnail_label)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(iteration.name)
        name_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(name_label)

        lens_label = QLabel(f"Lens: {iteration.lens_used or 'Unknown'}")
        lens_label.setStyleSheet("font-size: 10px; color: #888;")
        info_layout.addWidget(lens_label)

        region_label = QLabel(f"{len(iteration.regions)} regions")
        region_label.setStyleSheet("font-size: 10px; color: #888;")
        info_layout.addWidget(region_label)

        time_label = QLabel(iteration.timestamp.strftime("%Y-%m-%d %H:%M"))
        time_label.setStyleSheet("font-size: 10px; color: #666;")
        info_layout.addWidget(time_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        self.setLayout(layout)


class IterationTimeline(QWidget):
    """
    Timeline panel for managing design iterations

    Provides UI for:
    - Viewing all iterations with thumbnails
    - Creating new iterations from current state
    - Duplicating existing iterations
    - Switching between iterations
    - Deleting iterations
    """

    # Signals
    iteration_selected = pyqtSignal(str)  # Emitted when user selects an iteration

    def __init__(self, state: ApplicationState, parent=None):
        super().__init__(parent)
        self.state = state

        self.setup_ui()
        self.connect_signals()
        self.refresh_list()

    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title = QLabel("Design Iterations")
        title.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title)

        # Button bar
        button_layout = QHBoxLayout()

        self.new_button = QPushButton("New")
        self.new_button.setToolTip("Create new iteration from current state")
        self.new_button.clicked.connect(self.create_new_iteration)
        button_layout.addWidget(self.new_button)

        self.duplicate_button = QPushButton("Duplicate")
        self.duplicate_button.setToolTip("Duplicate selected iteration")
        self.duplicate_button.clicked.connect(self.duplicate_iteration)
        button_layout.addWidget(self.duplicate_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setToolTip("Delete selected iteration")
        self.delete_button.clicked.connect(self.delete_iteration)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        # Iteration list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.setMinimumHeight(200)
        layout.addWidget(self.list_widget)

        # Info label
        self.info_label = QLabel("No iterations")
        self.info_label.setStyleSheet("font-size: 10px; color: #888;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        self.setLayout(layout)

    def connect_signals(self):
        """Connect to application state signals"""
        self.state.iteration_manager.iterations_changed.connect(self.refresh_list)
        self.state.iteration_manager.current_iteration_changed.connect(self.on_current_iteration_changed)

    def refresh_list(self):
        """Refresh the iteration list"""
        self.list_widget.clear()

        iterations = self.state.iteration_manager.get_all_iterations()

        for iteration in iterations:
            # Create list item
            item = QListWidgetItem(self.list_widget)
            item.setData(Qt.ItemDataRole.UserRole, iteration.id)

            # Create custom widget
            widget = IterationListItem(iteration)
            item.setSizeHint(widget.sizeHint())

            # Add to list
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

            # Highlight current iteration
            if iteration.id == self.state.iteration_manager.current_iteration_id:
                item.setSelected(True)

        # Update info label
        count = len(iterations)
        if count == 0:
            self.info_label.setText("No iterations")
        elif count == 1:
            self.info_label.setText("1 iteration")
        else:
            self.info_label.setText(f"{count} iterations")

        # Update button states
        has_selection = self.list_widget.currentItem() is not None
        self.duplicate_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def create_new_iteration(self):
        """Create a new iteration from current state"""
        # Prompt for name
        name, ok = QInputDialog.getText(
            self,
            "New Iteration",
            "Enter name for this iteration:",
            text=f"Design {self.state.iteration_manager.get_iteration_count() + 1}"
        )

        if not ok or not name.strip():
            return

        # Capture thumbnail (optional - could implement viewport screenshot later)
        thumbnail = None

        # Create iteration
        iteration_id = self.state.create_iteration_snapshot(name.strip(), thumbnail)

        # Emit signal
        self.iteration_selected.emit(iteration_id)

        # Refresh list
        self.refresh_list()

    def duplicate_iteration(self):
        """Duplicate the selected iteration"""
        current_item = self.list_widget.currentItem()
        if not current_item:
            return

        iteration_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Get original iteration
        original = self.state.iteration_manager.get_iteration(iteration_id)
        if not original:
            return

        # Prompt for new name
        name, ok = QInputDialog.getText(
            self,
            "Duplicate Iteration",
            "Enter name for duplicated iteration:",
            text=f"Copy of {original.name}"
        )

        if not ok or not name.strip():
            return

        # Duplicate
        new_iteration = self.state.iteration_manager.duplicate_iteration(iteration_id, name.strip())

        if new_iteration:
            self.iteration_selected.emit(new_iteration.id)
            self.refresh_list()

    def delete_iteration(self):
        """Delete the selected iteration"""
        current_item = self.list_widget.currentItem()
        if not current_item:
            return

        iteration_id = current_item.data(Qt.ItemDataRole.UserRole)

        # Get iteration info
        iteration = self.state.iteration_manager.get_iteration(iteration_id)
        if not iteration:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Iteration",
            f"Delete iteration '{iteration.name}'?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.state.iteration_manager.delete_iteration(iteration_id)
            self.refresh_list()

    def on_item_clicked(self, item):
        """Handle iteration item clicked"""
        iteration_id = item.data(Qt.ItemDataRole.UserRole)

        # Update button states
        self.duplicate_button.setEnabled(True)
        self.delete_button.setEnabled(True)

        # Switch to this iteration
        self.state.restore_from_iteration(iteration_id)
        self.iteration_selected.emit(iteration_id)

    def on_current_iteration_changed(self, iteration_id: str):
        """Handle current iteration changed externally"""
        # Update selection in list
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == iteration_id:
                item.setSelected(True)
                self.list_widget.setCurrentItem(item)
                break
