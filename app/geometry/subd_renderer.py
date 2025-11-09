"""
SubD Renderer - Convert C++ tessellation results to VTK actors with display modes.

This module provides rendering capabilities for subdivision surfaces, converting
TessellationResult from C++ into VTK actors with support for:
- Multiple display modes (solid, wireframe, shaded_wireframe, points)
- Selection highlighting (yellow for selected faces/edges/vertices)
- Performance optimization for large meshes
"""

import vtk
import numpy as np
from typing import List, Tuple, Optional

try:
    import cpp_core
except ImportError:
    # cpp_core not built yet - will be available after Day 0 setup
    cpp_core = None


class SubDRenderer:
    """Renders subdivision surfaces using VTK with various display modes."""

    def __init__(self):
        """Initialize the SubD renderer."""
        self.current_actor = None
        self.current_polydata = None
        self.display_mode = "solid"  # solid, wireframe, shaded_wireframe, points
        self.selected_faces = []
        self.highlight_actors = []

    def create_subd_actor(
        self,
        result,  # cpp_core.TessellationResult
        color: Tuple[float, float, float] = (0.8, 0.8, 0.9),
        opacity: float = 1.0
    ) -> vtk.vtkActor:
        """
        Create VTK actor from C++ tessellation result.

        Args:
            result: TessellationResult from SubDEvaluator
            color: RGB color tuple (0-1 range)
            opacity: Opacity value (0-1 range)

        Returns:
            vtkActor ready for rendering with current display mode applied
        """
        # Create VTK polydata from tessellation result
        polydata = self._create_polydata_from_tessellation(result)
        self.current_polydata = polydata

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetOpacity(opacity)

        # Apply current display mode
        self._apply_display_mode(actor)

        self.current_actor = actor
        return actor

    def _create_polydata_from_tessellation(self, result) -> vtk.vtkPolyData:
        """
        Convert TessellationResult to VTK polydata.

        Uses zero-copy numpy arrays for optimal performance.

        Args:
            result: TessellationResult with vertices, normals, triangles

        Returns:
            vtkPolyData with geometry and normals
        """
        # Get numpy arrays (zero-copy from C++)
        vertices = result.vertices  # (N, 3) array
        normals = result.normals    # (N, 3) array
        triangles = result.triangles  # (M, 3) array

        # Create VTK points
        vtk_points = vtk.vtkPoints()
        vtk_points.SetNumberOfPoints(vertices.shape[0])
        for i, v in enumerate(vertices):
            vtk_points.SetPoint(i, v[0], v[1], v[2])

        # Create VTK normals
        vtk_normals = vtk.vtkFloatArray()
        vtk_normals.SetNumberOfComponents(3)
        vtk_normals.SetName("Normals")
        for n in normals:
            vtk_normals.InsertNextTuple3(n[0], n[1], n[2])

        # Create VTK triangles
        vtk_cells = vtk.vtkCellArray()
        for tri in triangles:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, int(tri[0]))
            triangle.GetPointIds().SetId(1, int(tri[1]))
            triangle.GetPointIds().SetId(2, int(tri[2]))
            vtk_cells.InsertNextCell(triangle)

        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)
        polydata.SetPolys(vtk_cells)
        polydata.GetPointData().SetNormals(vtk_normals)

        return polydata

    def set_display_mode(self, mode: str):
        """
        Set the display mode for the SubD surface.

        Args:
            mode: One of "solid", "wireframe", "shaded_wireframe", "points"

        Raises:
            ValueError: If mode is not recognized
        """
        valid_modes = ["solid", "wireframe", "shaded_wireframe", "points"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid display mode '{mode}'. Must be one of {valid_modes}")

        self.display_mode = mode

        # Apply to current actor if exists
        if self.current_actor:
            self._apply_display_mode(self.current_actor)

    def _apply_display_mode(self, actor: vtk.vtkActor):
        """Apply the current display mode to an actor."""
        prop = actor.GetProperty()

        if self.display_mode == "solid":
            prop.SetRepresentationToSurface()
            prop.EdgeVisibilityOff()
            prop.SetInterpolationToGouraud()  # Smooth shading

        elif self.display_mode == "wireframe":
            prop.SetRepresentationToWireframe()
            prop.EdgeVisibilityOff()
            prop.SetLineWidth(1.5)

        elif self.display_mode == "shaded_wireframe":
            prop.SetRepresentationToSurface()
            prop.EdgeVisibilityOn()
            prop.SetEdgeColor(0.2, 0.2, 0.3)
            prop.SetInterpolationToGouraud()

        elif self.display_mode == "points":
            prop.SetRepresentationToPoints()
            prop.SetPointSize(3.0)
            prop.SetRenderPointsAsSpheres(True)

    def update_selection_highlighting(
        self,
        selected_faces: List[int],
        renderer: vtk.vtkRenderer,
        highlight_color: Tuple[float, float, float] = (1.0, 1.0, 0.0)
    ):
        """
        Update selection highlighting for specified faces.

        Creates overlay actors that highlight selected faces in yellow.

        Args:
            selected_faces: List of face (triangle) indices to highlight
            renderer: VTK renderer to add highlight actors to
            highlight_color: RGB color for highlights (default yellow)
        """
        # Clear existing highlights
        self._clear_highlights(renderer)

        if not selected_faces or not self.current_polydata:
            return

        # Store selected faces
        self.selected_faces = selected_faces

        # Create highlight geometry
        highlight_polydata = self._extract_faces(self.current_polydata, selected_faces)

        if highlight_polydata.GetNumberOfCells() == 0:
            return

        # Create highlight mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(highlight_polydata)

        # Create highlight actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*highlight_color)
        actor.GetProperty().SetOpacity(0.8)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor(1.0, 0.8, 0.0)  # Slightly darker yellow
        actor.GetProperty().SetLineWidth(3.0)

        # Offset slightly to prevent z-fighting
        actor.GetProperty().SetRepresentationToSurface()
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-1, -1)

        # Add to renderer
        renderer.AddActor(actor)
        self.highlight_actors.append(actor)

    def _extract_faces(
        self,
        polydata: vtk.vtkPolyData,
        face_indices: List[int]
    ) -> vtk.vtkPolyData:
        """
        Extract specified faces from polydata.

        Args:
            polydata: Source polydata
            face_indices: List of cell indices to extract

        Returns:
            New polydata containing only specified faces
        """
        # Create selection for specified cells
        selection = vtk.vtkSelectionNode()
        selection.SetFieldType(vtk.vtkSelectionNode.CELL)
        selection.SetContentType(vtk.vtkSelectionNode.INDICES)

        # Create ID array
        id_array = vtk.vtkIdTypeArray()
        for face_id in face_indices:
            id_array.InsertNextValue(face_id)
        selection.SetSelectionList(id_array)

        # Create selection object
        selection_obj = vtk.vtkSelection()
        selection_obj.AddNode(selection)

        # Extract selection
        extract = vtk.vtkExtractSelection()
        extract.SetInputData(0, polydata)
        extract.SetInputData(1, selection_obj)
        extract.Update()

        # Convert to polydata
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputData(extract.GetOutput())
        geometry_filter.Update()

        return geometry_filter.GetOutput()

    def _clear_highlights(self, renderer: vtk.vtkRenderer):
        """Remove all highlight actors from the renderer."""
        for actor in self.highlight_actors:
            renderer.RemoveActor(actor)
        self.highlight_actors.clear()

    def create_control_cage_actor(
        self,
        cage,  # cpp_core.SubDControlCage
        color: Tuple[float, float, float] = (1.0, 0.5, 0.0),
        point_size: float = 6.0,
        line_width: float = 2.0
    ) -> vtk.vtkActor:
        """
        Create VTK actor for control cage visualization.

        Shows control vertices and edges as a wireframe overlay.

        Args:
            cage: SubDControlCage from C++
            color: RGB color for cage (default orange)
            point_size: Size of control points
            line_width: Width of control edges

        Returns:
            vtkActor showing control cage
        """
        # Create points
        vtk_points = vtk.vtkPoints()
        for v in cage.vertices:
            vtk_points.InsertNextPoint(v.x, v.y, v.z)

        # Create lines for edges (infer from faces)
        vtk_lines = vtk.vtkCellArray()
        edges_added = set()  # Track edges to avoid duplicates

        for face in cage.faces:
            # Draw edges around face perimeter
            for i in range(len(face)):
                v1 = face[i]
                v2 = face[(i + 1) % len(face)]

                # Create canonical edge (smaller index first)
                edge = (min(v1, v2), max(v1, v2))

                if edge not in edges_added:
                    line = vtk.vtkLine()
                    line.GetPointIds().SetId(0, v1)
                    line.GetPointIds().SetId(1, v2)
                    vtk_lines.InsertNextCell(line)
                    edges_added.add(edge)

        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)
        polydata.SetLines(vtk_lines)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetLineWidth(line_width)
        actor.GetProperty().SetPointSize(point_size)
        actor.GetProperty().SetRenderPointsAsSpheres(True)
        actor.GetProperty().SetRenderLinesAsTubes(True)
        actor.GetProperty().VertexVisibilityOn()

        return actor

    def get_performance_stats(self) -> dict:
        """
        Get performance statistics for current geometry.

        Returns:
            Dictionary with vertex count, triangle count, etc.
        """
        if not self.current_polydata:
            return {
                "vertices": 0,
                "triangles": 0,
                "has_normals": False
            }

        return {
            "vertices": self.current_polydata.GetNumberOfPoints(),
            "triangles": self.current_polydata.GetNumberOfCells(),
            "has_normals": self.current_polydata.GetPointData().GetNormals() is not None,
            "memory_kb": self.current_polydata.GetActualMemorySize()
        }


def create_test_subd_result(subdivision_level: int = 2):
    """
    Create a test TessellationResult for development/testing.

    Generates a simple subdivided cube for testing the renderer
    without requiring Grasshopper or full C++ setup.

    Args:
        subdivision_level: Level of subdivision (0-4)

    Returns:
        Mock object mimicking cpp_core.TessellationResult
    """
    # Create a simple subdivided cube
    cube_source = vtk.vtkCubeSource()
    cube_source.SetXLength(2.0)
    cube_source.SetYLength(2.0)
    cube_source.SetZLength(2.0)
    cube_source.Update()

    # Triangulate first (LinearSubdivisionFilter requires triangles)
    triangulate = vtk.vtkTriangleFilter()
    triangulate.SetInputData(cube_source.GetOutput())
    triangulate.Update()

    # Subdivide
    subdivider = vtk.vtkLinearSubdivisionFilter()
    subdivider.SetInputData(triangulate.GetOutput())
    subdivider.SetNumberOfSubdivisions(subdivision_level)
    subdivider.Update()

    # Compute normals
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(subdivider.GetOutput())
    normals.ComputePointNormalsOn()
    normals.Update()

    polydata = normals.GetOutput()

    # Convert to numpy arrays
    points = polydata.GetPoints()
    num_points = points.GetNumberOfPoints()

    vertices = np.zeros((num_points, 3), dtype=np.float32)
    normals_array = np.zeros((num_points, 3), dtype=np.float32)

    for i in range(num_points):
        vertices[i] = points.GetPoint(i)

    vtk_normals = polydata.GetPointData().GetNormals()
    if vtk_normals:
        for i in range(num_points):
            normals_array[i] = vtk_normals.GetTuple3(i)

    # Extract triangles
    num_cells = polydata.GetNumberOfCells()
    triangles = np.zeros((num_cells, 3), dtype=np.int32)

    for i in range(num_cells):
        cell = polydata.GetCell(i)
        if cell.GetNumberOfPoints() == 3:
            for j in range(3):
                triangles[i, j] = cell.GetPointId(j)

    # Create mock TessellationResult
    class MockTessellationResult:
        def __init__(self, verts, norms, tris):
            self.vertices = verts
            self.normals = norms
            self.triangles = tris
            self.face_parents = list(range(len(tris)))

        def vertex_count(self):
            return len(self.vertices)

        def triangle_count(self):
            return len(self.triangles)

    return MockTessellationResult(vertices, normals_array, triangles)
