"""
Face Picker for SubD Panel Mode

Provides VTK-based picking of SubD faces with:
- Triangle → parent SubD face mapping via TessellationResult.face_parents
- Multi-select support (Shift+Click to add/remove)
- Yellow highlighting of selected faces
- Integration with EditModeManager

Architecture:
- Uses vtkCellPicker to pick triangles in the tessellated mesh
- Maps picked triangle IDs to parent SubD face IDs using face_parents array
- Manages selection state through EditModeManager
- Provides visual feedback through HighlightManager
"""

from typing import Optional, List, Set

try:
    from PyQt6.QtCore import QObject, pyqtSignal
except ImportError:
    # Mock for testing environments
    QObject = object
    def pyqtSignal(*args, **kwargs):
        return None

# Import VTK types from our bridge - DO NOT import vtk directly
from app import vtk_bridge as vtk


class SubDFacePicker(QObject):
    """
    Picker for SubD faces/panels with triangle→face mapping.

    This picker handles the mapping between tessellated triangles (displayed mesh)
    and parent SubD faces (mathematical surface). When a user clicks on a triangle,
    it looks up the parent face using the face_parents array from TessellationResult.

    Signals:
        face_picked: Emitted when a face is picked (face_id)
        selection_changed: Emitted when selection state changes (set of face_ids)
    """

    # Signals (class attributes for PyQt6)
    face_picked = pyqtSignal(int) if pyqtSignal else None  # SubD face ID (not triangle ID!)
    selection_changed = pyqtSignal(set) if pyqtSignal else None  # Set of selected SubD face IDs
    
    def __init__(self, renderer: vtk.vtkRenderer, render_window: vtk.vtkRenderWindow):
        """
        Initialize face picker.
        
        Args:
            renderer: VTK renderer for the viewport
            render_window: VTK render window for coordinate conversion
        """
        super().__init__()
        self.renderer = renderer
        self.render_window = render_window
        self.interactor = render_window.GetInteractor()
        
        # Create VTK cell picker for triangle selection
        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.005)  # Pick tolerance in world coordinates
        
        # Face mapping data
        self.face_parents = None  # Maps triangle_id → parent_face_id
        self.selected_faces = set()  # Set of selected SubD face IDs
        
        # Visual feedback
        self.highlight_callback = None
        
    def set_face_parents(self, face_parents: List[int]):
        """
        Set the triangle→face mapping from TessellationResult.
        
        Args:
            face_parents: Array mapping triangle indices to parent SubD face IDs.
                         face_parents[triangle_id] = parent_face_id
        """
        self.face_parents = face_parents
        print(f"🔧 Face picker: Loaded face_parents mapping with {len(face_parents)} triangles")
        
    def set_highlight_callback(self, callback):
        """
        Set callback for visual highlighting of selected faces.
        
        Args:
            callback: Function(face_ids: Set[int]) to highlight faces
        """
        self.highlight_callback = callback
        
    def pick(self, x: int, y: int, add_to_selection: bool = False) -> Optional[int]:
        """
        Pick a face at screen coordinates.
        
        Args:
            x, y: Screen coordinates
            add_to_selection: If True (Shift+Click), toggle face in selection.
                            If False, replace selection with picked face.
        
        Returns:
            Parent SubD face ID (NOT triangle ID), or None if nothing picked
        """
        mode_str = "TOGGLE" if add_to_selection else "NEW SELECTION"
        print(f"🎯 SubDFacePicker.pick() at ({x}, {y}) - {mode_str}")
        
        # Perform VTK pick to get triangle ID
        result = self.picker.Pick(x, y, 0, self.renderer)
        
        if result == 0:
            print(f"   ❌ No geometry under cursor")
            return None
            
        triangle_id = self.picker.GetCellId()
        
        if triangle_id < 0:
            print(f"   ❌ Invalid cell ID: {triangle_id}")
            return None
            
        print(f"   📍 Picked triangle {triangle_id}")
        
        # Map triangle to parent SubD face
        if self.face_parents is None:
            print(f"   ⚠️ No face_parents mapping! Using triangle_id as face_id")
            face_id = triangle_id
        elif triangle_id >= len(self.face_parents):
            print(f"   ⚠️ Triangle {triangle_id} out of range (max: {len(self.face_parents)-1})")
            print(f"   Using triangle_id as face_id")
            face_id = triangle_id
        else:
            face_id = self.face_parents[triangle_id]
            print(f"   ✅ Mapped triangle {triangle_id} → face {face_id}")
        
        # Update selection state
        if add_to_selection:
            # Toggle face in selection
            if face_id in self.selected_faces:
                self.selected_faces.remove(face_id)
                print(f"   ➖ Removed face {face_id} from selection (now {len(self.selected_faces)} selected)")
            else:
                self.selected_faces.add(face_id)
                print(f"   ➕ Added face {face_id} to selection (now {len(self.selected_faces)} selected)")
        else:
            # Replace selection
            self.selected_faces = {face_id}
            print(f"   🔄 New selection: face {face_id}")
        
        # Emit signals
        if self.face_picked is not None:
            self.face_picked.emit(face_id)
        if self.selection_changed is not None:
            self.selection_changed.emit(self.selected_faces.copy())
        
        # Visual feedback
        if self.highlight_callback:
            self.highlight_callback(self.selected_faces)
        
        # Get pick position for debugging
        pos = self.picker.GetPickPosition()
        print(f"   📍 Pick position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
        
        return face_id
    
    def clear_selection(self):
        """Clear all selected faces."""
        self.selected_faces.clear()
        if self.selection_changed is not None:
            self.selection_changed.emit(set())
        
        if self.highlight_callback:
            self.highlight_callback(set())
            
        print(f"🧹 Cleared face selection")
    
    def get_selection(self) -> Set[int]:
        """
        Get current selection.
        
        Returns:
            Set of selected SubD face IDs
        """
        return self.selected_faces.copy()
    
    def set_selection(self, face_ids: Set[int]):
        """
        Set selection programmatically.

        Args:
            face_ids: Set of SubD face IDs to select
        """
        self.selected_faces = set(face_ids)
        if self.selection_changed is not None:
            self.selection_changed.emit(self.selected_faces.copy())
        
        if self.highlight_callback:
            self.highlight_callback(self.selected_faces)
            
        print(f"📝 Set face selection: {len(face_ids)} faces")
    
    def is_face_selected(self, face_id: int) -> bool:
        """
        Check if a face is currently selected.
        
        Args:
            face_id: SubD face ID to check
            
        Returns:
            True if face is selected
        """
        return face_id in self.selected_faces
    
    def get_actor(self) -> Optional[vtk.vtkActor]:
        """
        Get the actor that was picked.
        
        Returns:
            VTK actor at pick position, or None
        """
        return self.picker.GetActor()
