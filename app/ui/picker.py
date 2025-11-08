"""
VTK Picking System for SubD Elements
Provides interactive selection of faces, edges, and vertices

Future: Will integrate with OpenSubdiv for exact limit surface picking
"""

from typing import Optional, Tuple, Callable
from PyQt6.QtCore import QObject, pyqtSignal

# Import VTK types from our bridge - DO NOT import vtk directly
from app import vtk_bridge as vtk


class SubDPicker(QObject):
    """Base class for picking SubD elements"""

    # Signals
    element_picked = pyqtSignal(int)  # Element ID
    position_picked = pyqtSignal(float, float, float)  # World position

    def __init__(self, renderer: vtk.vtkRenderer, render_window: vtk.vtkRenderWindow):
        super().__init__()
        self.renderer = renderer
        self.render_window = render_window
        self.interactor = render_window.GetInteractor()

        # Store callback for highlighting
        self.highlight_callback = None

    def set_highlight_callback(self, callback: Callable[[int], None]):
        """Set callback for highlighting picked elements"""
        self.highlight_callback = callback


class SubDFacePicker(SubDPicker):
    """Picker for SubD faces/panels"""

    def __init__(self, renderer: vtk.vtkRenderer, render_window: vtk.vtkRenderWindow):
        super().__init__(renderer, render_window)

        # Create cell picker for faces
        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.005)

    def pick(self, x: int, y: int, add_to_selection: bool = False) -> Optional[int]:
        """
        Pick a face at screen coordinates

        Args:
            x, y: Screen coordinates
            add_to_selection: If True, add to existing selection (Shift+Click)

        Returns:
            Face ID or None if nothing picked
        """
        mode_str = "ADD TO SELECTION" if add_to_selection else "NEW SELECTION"
        print(f"🎯 SubDFacePicker.pick() called at ({x}, {y}) - {mode_str}")

        # Perform pick
        result = self.picker.Pick(x, y, 0, self.renderer)
        print(f"   Pick result: {result}")

        cell_id = self.picker.GetCellId()
        print(f"   Cell ID: {cell_id}")

        if cell_id >= 0:
            pos = self.picker.GetPickPosition()
            print(f"   ✅ Picked face {cell_id} at position {pos}")

            # Emit signals
            self.element_picked.emit(cell_id)
            self.position_picked.emit(pos[0], pos[1], pos[2])

            # Highlight if callback set
            if self.highlight_callback:
                self.highlight_callback(cell_id)

            return cell_id
        else:
            print(f"   ❌ No face picked (nothing under cursor)")

        return None

    def get_actor(self) -> Optional[vtk.vtkActor]:
        """Get the actor that was picked"""
        return self.picker.GetActor()


class SubDEdgePicker(SubDPicker):
    """Picker for SubD edges"""

    def __init__(self, renderer: vtk.vtkRenderer, render_window: vtk.vtkRenderWindow):
        super().__init__(renderer, render_window)

        # For edges, we'll use a custom approach
        # Extract edges from the mesh and pick them
        self.edge_actor = None
        self.edge_mapper = None
        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.01)  # Slightly higher tolerance for edges

    def setup_edge_extraction(self, polydata: vtk.vtkPolyData):
        """
        Extract edges from SubD mesh for picking

        Args:
            polydata: The SubD mesh polydata
        """
        # Extract edges
        edge_filter = vtk.vtkExtractEdges()
        edge_filter.SetInputData(polydata)
        edge_filter.Update()

        # Create mapper for edges
        self.edge_mapper = vtk.vtkPolyDataMapper()
        self.edge_mapper.SetInputConnection(edge_filter.GetOutputPort())

        # Create actor for edges (visible for picking)
        self.edge_actor = vtk.vtkActor()
        self.edge_actor.SetMapper(self.edge_mapper)
        self.edge_actor.GetProperty().SetColor(0.0, 1.0, 1.0)  # Cyan
        self.edge_actor.GetProperty().SetLineWidth(3.0)  # Thick lines
        self.edge_actor.GetProperty().SetOpacity(1.0)  # Fully visible
        self.edge_actor.PickableOn()

        # Add to renderer
        self.renderer.AddActor(self.edge_actor)
        print(f"✅ Edge actor created and added to renderer")

    def pick(self, x: int, y: int, add_to_selection: bool = False) -> Optional[int]:
        """
        Pick an edge at screen coordinates

        Args:
            x, y: Screen coordinates
            add_to_selection: If True, add to existing selection (Shift+Click)

        Returns:
            Edge ID or None if nothing picked
        """
        mode_str = "ADD TO SELECTION" if add_to_selection else "NEW SELECTION"
        print(f"🎯 SubDEdgePicker.pick() called at ({x}, {y}) - {mode_str}")

        if not self.edge_actor:
            print(f"   ❌ No edge actor (call setup_edge_extraction first)")
            return None

        # Pick with edge actor
        result = self.picker.Pick(x, y, 0, self.renderer)
        print(f"   Pick result: {result}")

        cell_id = self.picker.GetCellId()
        actor = self.picker.GetActor()
        print(f"   Cell ID: {cell_id}, Actor match: {actor == self.edge_actor}")

        if cell_id >= 0 and actor == self.edge_actor:
            edge_id = cell_id
            pos = self.picker.GetPickPosition()
            print(f"   ✅ Picked edge {edge_id} at position {pos}")

            # Emit signals
            self.element_picked.emit(edge_id)
            self.position_picked.emit(pos[0], pos[1], pos[2])

            # Highlight if callback set
            if self.highlight_callback:
                self.highlight_callback(edge_id)

            return edge_id
        else:
            print(f"   ❌ No edge picked (nothing under cursor)")

        return None

    def cleanup(self):
        """Remove edge actor from renderer"""
        if self.edge_actor:
            self.renderer.RemoveActor(self.edge_actor)
            self.edge_actor = None


class SubDVertexPicker(SubDPicker):
    """Picker for SubD vertices"""

    def __init__(self, renderer: vtk.vtkRenderer, render_window: vtk.vtkRenderWindow):
        super().__init__(renderer, render_window)

        # Create point picker for vertices
        self.picker = vtk.vtkPointPicker()
        self.picker.SetTolerance(0.02)  # Higher tolerance for points

    def pick(self, x: int, y: int, add_to_selection: bool = False) -> Optional[int]:
        """
        Pick a vertex at screen coordinates

        Args:
            x, y: Screen coordinates
            add_to_selection: If True, add to existing selection (Shift+Click)

        Returns:
            Vertex ID or None if nothing picked
        """
        mode_str = "ADD TO SELECTION" if add_to_selection else "NEW SELECTION"
        print(f"🎯 SubDVertexPicker.pick() called at ({x}, {y}) - {mode_str}")

        # Perform pick
        result = self.picker.Pick(x, y, 0, self.renderer)
        print(f"   Pick result: {result}")

        point_id = self.picker.GetPointId()
        print(f"   Point ID: {point_id}")

        if point_id >= 0:
            pos = self.picker.GetPickPosition()
            print(f"   ✅ Picked vertex {point_id} at position {pos}")

            # Emit signals
            self.element_picked.emit(point_id)
            self.position_picked.emit(pos[0], pos[1], pos[2])

            # Highlight if callback set
            if self.highlight_callback:
                self.highlight_callback(point_id)

            return point_id
        else:
            print(f"   ❌ No vertex picked (nothing under cursor)")

        return None


class HighlightManager:
    """Manages visual highlighting of selected elements"""

    def __init__(self, renderer: vtk.vtkRenderer):
        self.renderer = renderer
        self.highlight_actors = []

    def highlight_faces(self, polydata: vtk.vtkPolyData, face_ids: list, color=(1.0, 1.0, 0.0)):
        """
        Highlight selected faces

        Args:
            polydata: The mesh data
            face_ids: List of face IDs to highlight
            color: RGB color for highlighting
        """
        self.clear_highlights()

        if not face_ids:
            return

        # Create selection
        selection = vtk.vtkSelection()
        selection_node = vtk.vtkSelectionNode()
        selection_node.SetFieldType(vtk.vtkSelectionNode.CELL)
        selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)

        # Add face IDs
        id_array = vtk.vtkIdTypeArray()
        for face_id in face_ids:
            id_array.InsertNextValue(face_id)
        selection_node.SetSelectionList(id_array)
        selection.AddNode(selection_node)

        # Extract selection
        extract_selection = vtk.vtkExtractSelection()
        extract_selection.SetInputData(0, polydata)
        extract_selection.SetInputData(1, selection)
        extract_selection.Update()

        # Convert to polydata
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputConnection(extract_selection.GetOutputPort())
        geometry_filter.Update()

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(geometry_filter.GetOutputPort())

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(0.5)
        actor.GetProperty().SetLineWidth(3)
        actor.GetProperty().EdgeVisibilityOn()

        self.renderer.AddActor(actor)
        self.highlight_actors.append(actor)

    def highlight_edges(self, polydata: vtk.vtkPolyData, edge_ids: list, color=(0.0, 1.0, 0.0)):
        """
        Highlight selected edges

        Args:
            polydata: The mesh data (or edge polydata from edge filter)
            edge_ids: List of edge IDs to highlight
            color: RGB color for highlighting
        """
        self.clear_highlights()

        if not edge_ids:
            return

        # Extract all edges first
        edge_filter = vtk.vtkExtractEdges()
        edge_filter.SetInputData(polydata)
        edge_filter.Update()

        edge_polydata = edge_filter.GetOutput()

        # Create selection for specific edges
        selection = vtk.vtkSelection()
        selection_node = vtk.vtkSelectionNode()
        selection_node.SetFieldType(vtk.vtkSelectionNode.CELL)
        selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)

        # Add edge IDs
        id_array = vtk.vtkIdTypeArray()
        for edge_id in edge_ids:
            id_array.InsertNextValue(edge_id)
        selection_node.SetSelectionList(id_array)
        selection.AddNode(selection_node)

        # Extract selected edges only
        extract_selection = vtk.vtkExtractSelection()
        extract_selection.SetInputData(0, edge_polydata)
        extract_selection.SetInputData(1, selection)
        extract_selection.Update()

        # Convert to polydata
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputConnection(extract_selection.GetOutputPort())
        geometry_filter.Update()

        # Create mapper for selected edges only
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(geometry_filter.GetOutputPort())

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(8)  # Thick lines
        actor.GetProperty().SetOpacity(1.0)  # Fully visible
        actor.GetProperty().RenderLinesAsTubesOn()  # Make lines round/tubular

        self.renderer.AddActor(actor)
        self.highlight_actors.append(actor)

    def highlight_vertices(self, polydata: vtk.vtkPolyData, vertex_ids: list, color=(0.0, 0.0, 1.0)):
        """
        Highlight selected vertices with spheres

        Args:
            polydata: The mesh data
            vertex_ids: List of vertex IDs to highlight
            color: RGB color for highlighting
        """
        self.clear_highlights()

        if not vertex_ids:
            return

        points = polydata.GetPoints()

        for vertex_id in vertex_ids:
            if vertex_id < points.GetNumberOfPoints():
                point = points.GetPoint(vertex_id)

                # Create sphere at vertex
                sphere = vtk.vtkSphereSource()
                sphere.SetCenter(point)
                sphere.SetRadius(0.05)  # Adjust based on model scale
                sphere.SetPhiResolution(16)
                sphere.SetThetaResolution(16)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(sphere.GetOutputPort())

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(color)

                self.renderer.AddActor(actor)
                self.highlight_actors.append(actor)

    def clear_highlights(self):
        """Remove all highlight actors"""
        for actor in self.highlight_actors:
            self.renderer.RemoveActor(actor)
        self.highlight_actors.clear()

    def update_display(self):
        """Refresh the renderer"""
        if self.renderer.GetRenderWindow():
            self.renderer.GetRenderWindow().Render()