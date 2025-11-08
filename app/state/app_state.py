"""
Application State Management
Handles all application state including regions, geometry, and history
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class ParametricRegion:
    """A region defined in parameter space"""
    id: str
    faces: List[int]  # Face indices in SubD
    boundary: Optional[Any] = None  # Will be ParametricCurve
    unity_principle: str = ""
    unity_strength: float = 0.0
    pinned: bool = False
    modified: bool = False
    surface: Optional[Any] = None  # Generated NURBS surface
    constraints_passed: bool = True
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class HistoryItem:
    """A single item in the undo/redo history"""
    timestamp: datetime
    action: str
    data: Dict[str, Any]
    description: str


class ApplicationState(QObject):
    """Central state manager for the application"""

    # Signals
    state_changed = pyqtSignal()
    regions_updated = pyqtSignal(list)
    region_pinned = pyqtSignal(str, bool)
    history_changed = pyqtSignal()
    edit_mode_changed = pyqtSignal(object)  # EditMode
    selection_changed = pyqtSignal(object)  # Selection

    def __init__(self):
        super().__init__()

        # Import here to avoid circular dependency
        from app.state.edit_mode import EditMode, EditModeManager

        # Core state
        self.subd_geometry = None
        self.regions: List[ParametricRegion] = []
        self.selected_region_id: Optional[str] = None
        self.current_lens: str = "Flow"

        # Edit mode manager
        self.edit_mode_manager = EditModeManager()
        self.edit_mode_manager.mode_changed.connect(
            lambda mode: self.edit_mode_changed.emit(mode)
        )
        self.edit_mode_manager.selection_changed.connect(
            lambda sel: self.selection_changed.emit(sel)
        )

        # History for undo/redo
        self.history: List[HistoryItem] = []
        self.history_index: int = -1
        self.max_history_size: int = 100

        # Generated geometry
        self.mold_pieces = []
        
    def set_subd_geometry(self, geometry):
        """Set the SubD geometry from Rhino"""
        self.subd_geometry = geometry
        self.state_changed.emit()

        # Add to history
        self._add_history_item(
            "set_geometry",
            {"geometry": geometry},
            "Loaded SubD from Rhino"
        )

    def get_current_geometry(self):
        """Get the current SubD geometry"""
        return self.subd_geometry
    
    def add_region(self, region: ParametricRegion):
        """Add a discovered region"""
        self.regions.append(region)
        self.regions_updated.emit(self.regions)
        self.state_changed.emit()
    
    def set_regions(self, regions: List[ParametricRegion]):
        """Set all regions at once"""
        self.regions = regions
        self.regions_updated.emit(self.regions)
        self.state_changed.emit()
        
        # Add to history
        self._add_history_item(
            "set_regions",
            {"regions": regions, "lens": self.current_lens},
            f"Discovered {len(regions)} regions using {self.current_lens} lens"
        )
    
    def get_region(self, region_id: str) -> Optional[ParametricRegion]:
        """Get a region by ID"""
        for region in self.regions:
            if region.id == region_id:
                return region
        return None
    
    def set_region_pinned(self, region_id: str, pinned: bool):
        """Set the pinned state of a region"""
        region = self.get_region(region_id)
        if region:
            old_state = region.pinned
            region.pinned = pinned
            self.region_pinned.emit(region_id, pinned)
            self.state_changed.emit()
            
            # Add to history
            self._add_history_item(
                "pin_region",
                {"region_id": region_id, "pinned": pinned, "old_pinned": old_state},
                f"{'Pinned' if pinned else 'Unpinned'} region {region_id}"
            )
    
    def get_pinned_regions(self) -> List[ParametricRegion]:
        """Get all pinned regions"""
        return [r for r in self.regions if r.pinned]
    
    def get_unpinned_regions(self) -> List[ParametricRegion]:
        """Get all unpinned regions"""
        return [r for r in self.regions if not r.pinned]
    
    def get_unpinned_faces(self) -> List[int]:
        """Get all face indices not in pinned regions"""
        if not self.subd_geometry:
            return []

        all_faces = set(range(len(self.subd_geometry.faces)))
        pinned_faces = set()

        for region in self.get_pinned_regions():
            pinned_faces.update(region.faces)

        return list(all_faces - pinned_faces)

    def get_pinned_face_indices(self) -> List[int]:
        """Get all face indices in pinned regions"""
        pinned_faces = []
        for region in self.get_pinned_regions():
            pinned_faces.extend(region.faces)
        return pinned_faces
    
    def select_region(self, region_id: str):
        """Select a region"""
        if region_id != self.selected_region_id:
            self.selected_region_id = region_id
            self.state_changed.emit()
    
    def set_current_lens(self, lens: str):
        """Set the current mathematical lens"""
        self.current_lens = lens
        self.state_changed.emit()
    
    def _add_history_item(self, action: str, data: Dict[str, Any], description: str):
        """Add an item to the history"""
        # Remove any items after current index (for redo)
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Add new item
        item = HistoryItem(
            timestamp=datetime.now(),
            action=action,
            data=data,
            description=description
        )
        self.history.append(item)
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history_size:
            self.history.pop(0)
            self.history_index -= 1
        
        self.history_changed.emit()
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return self.history_index >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return self.history_index < len(self.history) - 1
    
    def undo(self):
        """Undo the last action"""
        if not self.can_undo():
            return
        
        item = self.history[self.history_index]
        
        # Perform undo based on action type
        if item.action == "pin_region":
            # Restore previous pin state
            region_id = item.data["region_id"]
            old_pinned = item.data["old_pinned"]
            region = self.get_region(region_id)
            if region:
                region.pinned = old_pinned
                self.region_pinned.emit(region_id, old_pinned)
        
        # Add more undo operations as needed
        
        self.history_index -= 1
        self.state_changed.emit()
        self.history_changed.emit()
    
    def redo(self):
        """Redo the next action"""
        if not self.can_redo():
            return
        
        self.history_index += 1
        item = self.history[self.history_index]
        
        # Perform redo based on action type
        if item.action == "pin_region":
            # Apply the pin state
            region_id = item.data["region_id"]
            pinned = item.data["pinned"]
            region = self.get_region(region_id)
            if region:
                region.pinned = pinned
                self.region_pinned.emit(region_id, pinned)
        
        # Add more redo operations as needed
        
        self.state_changed.emit()
        self.history_changed.emit()
    
    def clear(self):
        """Clear all state"""
        self.subd_geometry = None
        self.regions = []
        self.selected_region_id = None
        self.mold_pieces = []
        self.history = []
        self.history_index = -1
        
        self.regions_updated.emit([])
        self.state_changed.emit()
        self.history_changed.emit()
