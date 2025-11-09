"""
VTK-based pickers for SubD element selection.

Provides specialized pickers for:
- Faces (panels) with triangle→face mapping
- Edges with intelligent edge detection and tubular rendering
- Vertices with point picking

All pickers integrate with EditModeManager for state management.
"""

from .face_picker import SubDFacePicker
from .edge_picker import SubDEdgePicker
from .vertex_picker import SubDVertexPicker

__all__ = ['SubDFacePicker', 'SubDEdgePicker', 'SubDVertexPicker']
