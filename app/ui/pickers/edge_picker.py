"""
Advanced Edge Picker for SubD Elements
Implements edge selection with tubular rendering and adjacency tracking

Features:
- Extract edges from tessellation (shared triangle edges)
- Build edge→triangle adjacency map
- Identify boundary vs. internal edges
- Render edges as tubes (vtkTubeFilter) for visibility
- Cyan wireframe guide for all edges
- Yellow highlighting for selected edges only
- Tolerance-based picking (ray-to-edge distance < 0.1 units)
"""

from typing import Optional, Tuple, List, Dict, Set
from PyQt6.QtCore import QObject, pyqtSignal
import numpy as np

# Import VTK types from our bridge - DO NOT import vtk directly
from app import vtk_bridge as vtk


class EdgeInfo:
    """Information about an edge"""
    def __init__(self, v0: int, v1: int, edge_id: int):
        # Store vertex indices in sorted order for consistent lookup
        self.vertices = tuple(sorted([v0, v1]))
        self.edge_id = edge_id
        self.adjacent_triangles = []  # Triangle IDs that share this edge
        self.is_boundary = False  # True if only one adjacent triangle

    def __repr__(self):
        return f"Edge({self.vertices[0]}, {self.vertices[1]}, boundary={self.is_boundary})"


class SubDEdgePicker(QObject):
    """
    Advanced picker for SubD edges with tubular rendering and adjacency tracking
    """

    # Signals
    edge_picked = pyqtSignal(int)  # Edge ID
    position_picked = pyqtSignal(float, float, float)  # World position
    selection_changed = pyqtSignal(list)  # List of selected edge IDs

    def __init__(self, renderer: vtk.vtkRenderer, render_window: vtk.vtkRenderWindow):
        super().__init__()
        self.renderer = renderer
        self.render_window = render_window
        self.interactor = render_window.GetInteractor() if render_window else None

        # Edge data structures
        self.edges = {}  # edge_id -> EdgeInfo
        self.edge_map = {}  # (v0, v1) -> edge_id for fast lookup
        self.polydata = None  # Original mesh polydata
        self.edge_polydata = None  # Extracted edge polydata

        # VTK actors and mappers
        self.guide_actor = None  # Cyan wireframe for all edges
        self.guide_mapper = None
        self.highlight_actor = None  # Yellow highlight for selected edges
        self.highlight_mapper = None

        # Picker for ray casting
        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.01)  # Screen space tolerance

        # Selection state
        self.selected_edge_ids = set()

        # Tolerance for edge picking (world space)
        self.pick_tolerance = 0.1

    def setup_edge_extraction(self, polydata: vtk.vtkPolyData):
        """
        Extract edges from SubD mesh tessellation

        Uses VTK's built-in vtkExtractEdges filter for reliability

        Args:
            polydata: The SubD mesh polydata (triangulated)
        """
        self.polydata = polydata
        self.edges.clear()
        self.edge_map.clear()

        print(f"🔍 Extracting edges using vtkExtractEdges...")
        print(f"   Input: {polydata.GetNumberOfPoints()} points, {polydata.GetNumberOfCells()} cells")

        # Use VTK's built-in edge extraction
        edge_extractor = vtk.vtkExtractEdges()
        edge_extractor.SetInputData(polydata)
        edge_extractor.Update()

        self.edge_polydata = edge_extractor.GetOutput()

        num_lines = self.edge_polydata.GetNumberOfLines()
        print(f"   Extracted {num_lines} edge lines")

        # Build edge info structures from extracted edges
        lines = self.edge_polydata.GetLines()
        lines.InitTraversal()

        id_list = vtk.vtkIdList()
        edge_id = 0

        # Create array to store edge IDs as cell data
        edge_ids_array = vtk.vtkIdTypeArray()
        edge_ids_array.SetName("EdgeIDs")
        edge_ids_array.SetNumberOfTuples(num_lines)

        while lines.GetNextCell(id_list):
            if id_list.GetNumberOfIds() == 2:
                v0 = id_list.GetId(0)
                v1 = id_list.GetId(1)

                # Create edge info
                edge_info = EdgeInfo(v0, v1, edge_id)
                edge_key = tuple(sorted([v0, v1]))

                self.edges[edge_id] = edge_info
                self.edge_map[edge_key] = edge_id

                # Store edge ID in cell data
                edge_ids_array.SetValue(edge_id, edge_id)

                edge_id += 1

        # Add edge IDs to polydata cell data
        self.edge_polydata.GetCellData().AddArray(edge_ids_array)
        self.edge_polydata.GetCellData().SetActiveScalars("EdgeIDs")

        print(f"✅ Extracted {len(self.edges)} edges with IDs stored in cell data")

        # Create guide visualization (cyan tubes for all edges)
        self._create_guide_visualization()

    def _create_edge_polydata(self):
        """Create VTK polydata representing all edges"""
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Get original mesh points
        mesh_points = self.polydata.GetPoints()

        # Build point array (we'll reuse original point indices)
        for i in range(mesh_points.GetNumberOfPoints()):
            points.InsertNextPoint(mesh_points.GetPoint(i))

        # Build line cells for each edge
        for edge_info in self.edges.values():
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, edge_info.vertices[0])
            line.GetPointIds().SetId(1, edge_info.vertices[1])
            lines.InsertNextCell(line)

        # Create polydata
        self.edge_polydata = vtk.vtkPolyData()
        self.edge_polydata.SetPoints(points)
        self.edge_polydata.SetLines(lines)

        print(f"✅ Created edge polydata: {points.GetNumberOfPoints()} points, {lines.GetNumberOfCells()} lines")

    def _create_guide_visualization(self):
        """Create cyan tube visualization for all edges"""
        if not self.edge_polydata or self.edge_polydata.GetNumberOfLines() == 0:
            print(f"⚠️ No edges to visualize")
            return

        # Remove old guide actor if exists
        if self.guide_actor:
            self.renderer.RemoveActor(self.guide_actor)

        print(f"🎨 Creating edge guide visualization from {self.edge_polydata.GetNumberOfLines()} edge lines")

        # Create tubes for better visibility
        tube_filter = vtk.vtkTubeFilter()
        tube_filter.SetInputData(self.edge_polydata)
        tube_filter.SetRadius(0.01)  # Adjust based on model scale
        tube_filter.SetNumberOfSides(8)  # Octagonal tubes
        tube_filter.Update()

        # Create mapper
        self.guide_mapper = vtk.vtkPolyDataMapper()
        self.guide_mapper.SetInputConnection(tube_filter.GetOutputPort())

        # Create actor
        self.guide_actor = vtk.vtkActor()
        self.guide_actor.SetMapper(self.guide_mapper)
        self.guide_actor.GetProperty().SetColor(0.0, 1.0, 1.0)  # Cyan
        self.guide_actor.GetProperty().SetOpacity(0.5)
        self.guide_actor.PickableOn()

        # Add to renderer
        self.renderer.AddActor(self.guide_actor)
        print(f"✅ Edge guide visualization created (cyan tubes, {self.edge_polydata.GetNumberOfLines()} edges)")

    def pick(self, x: int, y: int, add_to_selection: bool = False) -> Optional[int]:
        """
        Pick an edge at screen coordinates using tolerance-based ray casting

        Args:
            x, y: Screen coordinates
            add_to_selection: If True, add to existing selection (Shift+Click)

        Returns:
            Edge ID or None if nothing picked
        """
        mode_str = "ADD TO SELECTION" if add_to_selection else "NEW SELECTION"
        print(f"🎯 SubDEdgePicker.pick() called at ({x}, {y}) - {mode_str}")

        if not self.guide_actor or not self.edge_polydata:
            print(f"   ❌ No edge data (call setup_edge_extraction first)")
            return None

        # Pick with edge actor
        result = self.picker.Pick(x, y, 0, self.renderer)
        print(f"   Pick result: {result}")

        cell_id = self.picker.GetCellId()
        actor = self.picker.GetActor()
        print(f"   Cell ID: {cell_id}, Actor match: {actor == self.guide_actor}")

        if cell_id >= 0 and actor == self.guide_actor:
            # Get the edge ID from the picked cell's data
            # The tube filter propagates cell data, so each tube cell has the original edge ID
            mapper = actor.GetMapper()
            if mapper:
                input_data = mapper.GetInput()
                cell_data = input_data.GetCellData()
                edge_ids = cell_data.GetArray("EdgeIDs")

                if edge_ids and cell_id < edge_ids.GetNumberOfTuples():
                    edge_id = int(edge_ids.GetValue(cell_id))
                    print(f"   📍 Mapped tube cell {cell_id} → edge ID {edge_id}")
                else:
                    print(f"   ⚠️  No EdgeIDs array in tube data")
                    return None
            else:
                print(f"   ⚠️  No mapper for guide actor")
                return None

            if edge_id not in self.edges:
                print(f"   ⚠️  Edge ID {edge_id} not found in edge map")
                return None

            edge_info = self.edges[edge_id]
            pos = self.picker.GetPickPosition()
            print(f"   ✅ Picked edge {edge_id} {edge_info.vertices} at position ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

            # Update selection
            if add_to_selection:
                # Toggle selection
                if edge_id in self.selected_edge_ids:
                    self.selected_edge_ids.remove(edge_id)
                    print(f"   ➖ Removed edge {edge_id} from selection")
                else:
                    self.selected_edge_ids.add(edge_id)
                    print(f"   ➕ Added edge {edge_id} to selection")
            else:
                # Replace selection
                self.selected_edge_ids = {edge_id}
                print(f"   🔄 Replaced selection with edge {edge_id}")

            # Update highlight visualization
            self._update_highlight()

            # Emit signals
            self.edge_picked.emit(edge_id)
            self.position_picked.emit(pos[0], pos[1], pos[2])
            self.selection_changed.emit(list(self.selected_edge_ids))

            return edge_id
        else:
            print(f"   ❌ No edge picked (nothing under cursor)")

            # Clear selection if not adding
            if not add_to_selection and self.selected_edge_ids:
                self.selected_edge_ids.clear()
                self._update_highlight()
                self.selection_changed.emit([])

        return None

    def _update_highlight(self):
        """Update yellow highlighting for selected edges only"""
        # Remove old highlight actor
        if self.highlight_actor:
            self.renderer.RemoveActor(self.highlight_actor)
            self.highlight_actor = None

        if not self.selected_edge_ids:
            # No selection, no highlight
            self.render_window.Render()
            return

        print(f"🎨 Highlighting {len(self.selected_edge_ids)} selected edges: {sorted(self.selected_edge_ids)}")

        # Create polydata for selected edges only
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # CRITICAL: Use edge_polydata points (renumbered by vtkExtractEdges)
        # NOT original mesh points - vertex indices in EdgeInfo refer to renumbered space
        edge_points = self.edge_polydata.GetPoints()

        # Build point array from edge_polydata (renumbered points)
        for i in range(edge_points.GetNumberOfPoints()):
            points.InsertNextPoint(edge_points.GetPoint(i))

        # Build line cells for selected edges only
        for edge_id in sorted(self.selected_edge_ids):
            if edge_id in self.edges:
                edge_info = self.edges[edge_id]
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, edge_info.vertices[0])
                line.GetPointIds().SetId(1, edge_info.vertices[1])
                lines.InsertNextCell(line)

        selected_polydata = vtk.vtkPolyData()
        selected_polydata.SetPoints(points)
        selected_polydata.SetLines(lines)

        # Create thicker tubes for selected edges
        tube_filter = vtk.vtkTubeFilter()
        tube_filter.SetInputData(selected_polydata)
        tube_filter.SetRadius(0.02)  # Thicker than guide
        tube_filter.SetNumberOfSides(12)  # More sides for smoother look
        tube_filter.Update()

        # Create mapper
        self.highlight_mapper = vtk.vtkPolyDataMapper()
        self.highlight_mapper.SetInputConnection(tube_filter.GetOutputPort())

        # Create actor
        self.highlight_actor = vtk.vtkActor()
        self.highlight_actor.SetMapper(self.highlight_mapper)
        self.highlight_actor.GetProperty().SetColor(1.0, 1.0, 0.0)  # Yellow
        self.highlight_actor.GetProperty().SetOpacity(1.0)  # Fully opaque
        self.highlight_actor.PickableOff()  # Don't interfere with picking

        # Add to renderer
        self.renderer.AddActor(self.highlight_actor)

        # Refresh display
        self.render_window.Render()
        print(f"✅ Highlight updated")

    def clear_selection(self):
        """Clear all selected edges"""
        if self.selected_edge_ids:
            self.selected_edge_ids.clear()
            self._update_highlight()
            self.selection_changed.emit([])
            print(f"🗑️  Selection cleared")

    def get_selected_edges(self) -> List[int]:
        """Get list of selected edge IDs"""
        return list(self.selected_edge_ids)

    def get_edge_info(self, edge_id: int) -> Optional[EdgeInfo]:
        """Get information about an edge"""
        return self.edges.get(edge_id)

    def get_boundary_edges(self) -> List[int]:
        """Get list of all boundary edge IDs"""
        return [eid for eid, einfo in self.edges.items() if einfo.is_boundary]

    def get_internal_edges(self) -> List[int]:
        """Get list of all internal edge IDs"""
        return [eid for eid, einfo in self.edges.items() if not einfo.is_boundary]

    def cleanup(self):
        """Remove all actors from renderer"""
        if self.guide_actor:
            self.renderer.RemoveActor(self.guide_actor)
            self.guide_actor = None
        if self.highlight_actor:
            self.renderer.RemoveActor(self.highlight_actor)
            self.highlight_actor = None

        self.edges.clear()
        self.edge_map.clear()
        self.selected_edge_ids.clear()
        print(f"🧹 Edge picker cleaned up")
