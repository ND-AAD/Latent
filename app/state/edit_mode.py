"""
Edit Mode System for Ceramic Mold Analyzer
Provides infrastructure for selecting and editing SubD elements

This module is designed to be compatible with future OpenSubdiv integration
where we'll have exact limit surface evaluation and true parametric editing.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple
from PyQt6.QtCore import QObject, pyqtSignal


class EditMode(Enum):
    """Edit modes for interacting with SubD geometry"""
    SOLID = auto()   # Select entire objects
    PANEL = auto()   # Select SubD faces/panels
    EDGE = auto()    # Select SubD edges
    VERTEX = auto()  # Select SubD vertices

    def get_display_name(self) -> str:
        """Get human-readable name for UI"""
        names = {
            EditMode.SOLID: "Solid",
            EditMode.PANEL: "Panel",
            EditMode.EDGE: "Edge",
            EditMode.VERTEX: "Vertex"
        }
        return names.get(self, "Unknown")

    def get_icon_name(self) -> str:
        """Get icon filename for this mode"""
        icons = {
            EditMode.SOLID: "solid_mode.svg",
            EditMode.PANEL: "panel_mode.svg",
            EditMode.EDGE: "edge_mode.svg",
            EditMode.VERTEX: "vertex_mode.svg"
        }
        return icons.get(self, "")


@dataclass
class Selection:
    """Container for selected SubD elements"""
    mode: EditMode
    faces: Set[int] = None      # Selected face indices
    edges: Set[int] = None      # Selected edge indices
    vertices: Set[int] = None   # Selected vertex indices

    def __post_init__(self):
        """Initialize empty sets if None"""
        if self.faces is None:
            self.faces = set()
        if self.edges is None:
            self.edges = set()
        if self.vertices is None:
            self.vertices = set()

    def clear(self):
        """Clear all selections"""
        self.faces.clear()
        self.edges.clear()
        self.vertices.clear()

    def is_empty(self) -> bool:
        """Check if selection is empty"""
        return not (self.faces or self.edges or self.vertices)

    def add_face(self, face_id: int):
        """Add a face to selection"""
        if self.mode == EditMode.PANEL:
            self.faces.add(face_id)

    def remove_face(self, face_id: int):
        """Remove a face from selection"""
        self.faces.discard(face_id)

    def toggle_face(self, face_id: int) -> bool:
        """Toggle face selection, returns True if added"""
        if face_id in self.faces:
            self.faces.discard(face_id)
            return False
        else:
            self.faces.add(face_id)
            return True

    def add_edge(self, edge_id: int):
        """Add an edge to selection"""
        if self.mode == EditMode.EDGE:
            self.edges.add(edge_id)

    def remove_edge(self, edge_id: int):
        """Remove an edge from selection"""
        self.edges.discard(edge_id)

    def toggle_edge(self, edge_id: int) -> bool:
        """Toggle edge selection, returns True if added"""
        if edge_id in self.edges:
            self.edges.discard(edge_id)
            return False
        else:
            self.edges.add(edge_id)
            return True

    def add_vertex(self, vertex_id: int):
        """Add a vertex to selection"""
        if self.mode == EditMode.VERTEX:
            self.vertices.add(vertex_id)

    def remove_vertex(self, vertex_id: int):
        """Remove a vertex from selection"""
        self.vertices.discard(vertex_id)

    def toggle_vertex(self, vertex_id: int) -> bool:
        """Toggle vertex selection, returns True if added"""
        if vertex_id in self.vertices:
            self.vertices.discard(vertex_id)
            return False
        else:
            self.vertices.add(vertex_id)
            return True


class EditModeManager(QObject):
    """
    Manages edit mode state and selection

    Future: When we integrate OpenSubdiv, this will handle:
    - Exact limit surface queries at selected elements
    - Parametric boundary editing in (face_id, u, v) space
    - Feature-adaptive refinement control
    """

    # Signals
    mode_changed = pyqtSignal(EditMode)
    selection_changed = pyqtSignal(Selection)

    def __init__(self):
        super().__init__()
        self._current_mode = EditMode.SOLID
        self._selection = Selection(mode=self._current_mode)
        self._multi_select = False  # Shift key held

    @property
    def current_mode(self) -> EditMode:
        """Get current edit mode"""
        return self._current_mode

    @property
    def selection(self) -> Selection:
        """Get current selection"""
        return self._selection

    def set_mode(self, mode: EditMode):
        """
        Change edit mode

        Args:
            mode: New edit mode to set
        """
        if mode != self._current_mode:
            # Clear selection when changing modes
            self._selection.clear()
            self._current_mode = mode
            self._selection.mode = mode

            self.mode_changed.emit(mode)
            self.selection_changed.emit(self._selection)

    def set_multi_select(self, enabled: bool):
        """Enable/disable multi-selection mode (Shift key)"""
        self._multi_select = enabled

    def select_face(self, face_id: int, add_to_selection: bool = False):
        """
        Select a SubD face

        Args:
            face_id: Face index in SubD
            add_to_selection: Add to existing selection (Shift+click)
        """
        if self._current_mode != EditMode.PANEL:
            return

        if not add_to_selection and not self._multi_select:
            self._selection.clear()

        self._selection.add_face(face_id)
        self.selection_changed.emit(self._selection)

    def select_edge(self, edge_id: int, add_to_selection: bool = False):
        """
        Select a SubD edge

        Args:
            edge_id: Edge index in SubD
            add_to_selection: Add to existing selection
        """
        if self._current_mode != EditMode.EDGE:
            return

        if not add_to_selection and not self._multi_select:
            self._selection.clear()

        self._selection.add_edge(edge_id)
        self.selection_changed.emit(self._selection)

    def select_vertex(self, vertex_id: int, add_to_selection: bool = False):
        """
        Select a SubD vertex

        Args:
            vertex_id: Vertex index in SubD
            add_to_selection: Add to existing selection
        """
        if self._current_mode != EditMode.VERTEX:
            return

        if not add_to_selection and not self._multi_select:
            self._selection.clear()

        self._selection.add_vertex(vertex_id)
        self.selection_changed.emit(self._selection)

    def clear_selection(self):
        """Clear all selections"""
        self._selection.clear()
        self.selection_changed.emit(self._selection)

    def create_region_from_selection(self) -> Optional[List[int]]:
        """
        Create a region from selected faces

        Returns:
            List of face indices for new region, or None if no faces selected
        """
        if self._current_mode == EditMode.PANEL and self._selection.faces:
            return list(self._selection.faces)
        return None

    def get_selection_info(self) -> str:
        """Get human-readable selection information"""
        if self._selection.is_empty():
            return "No selection"

        parts = []
        if self._selection.faces:
            parts.append(f"{len(self._selection.faces)} faces")
        if self._selection.edges:
            parts.append(f"{len(self._selection.edges)} edges")
        if self._selection.vertices:
            parts.append(f"{len(self._selection.vertices)} vertices")

        return ", ".join(parts)