"""Convert C++ tessellation results to VTK actors for display."""

import vtk
import numpy as np
import cpp_core
from typing import Tuple


class SubDDisplayManager:
    """Manage VTK visualization of SubD geometry."""

    @staticmethod
    def create_mesh_actor(result: cpp_core.TessellationResult,
                         color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
                         show_edges: bool = False) -> vtk.vtkActor:
        """Create VTK actor from tessellation result.

        Args:
            result: Tessellation from SubDEvaluator
            color: RGB color (0-1)
            show_edges: Show edge wireframe

        Returns:
            vtkActor ready for rendering
        """
        # Get numpy arrays (zero-copy!)
        vertices = result.vertices  # (N, 3) array
        normals = result.normals    # (N, 3) array
        triangles = result.triangles  # (M, 3) array

        # Create VTK points
        vtk_points = vtk.vtkPoints()
        for v in vertices:
            vtk_points.InsertNextPoint(v[0], v[1], v[2])

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
            triangle.GetPointIds().SetId(0, tri[0])
            triangle.GetPointIds().SetId(1, tri[1])
            triangle.GetPointIds().SetId(2, tri[2])
            vtk_cells.InsertNextCell(triangle)

        # Create polydata
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(vtk_points)
        poly_data.SetPolys(vtk_cells)
        poly_data.GetPointData().SetNormals(vtk_normals)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)

        if show_edges:
            actor.GetProperty().EdgeVisibilityOn()
            actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.2)

        return actor

    @staticmethod
    def create_control_cage_actor(cage: cpp_core.SubDControlCage,
                                  color: Tuple[float, float, float] = (1.0, 0.0, 0.0),
                                  point_size: float = 5.0) -> vtk.vtkActor:
        """Create VTK actor for control cage wireframe.

        Args:
            cage: SubD control cage
            color: RGB color
            point_size: Control point size

        Returns:
            vtkActor showing control net
        """
        # Create points
        vtk_points = vtk.vtkPoints()
        for v in cage.vertices:
            vtk_points.InsertNextPoint(v.x, v.y, v.z)

        # Create lines for edges
        vtk_lines = vtk.vtkCellArray()

        for face in cage.faces:
            # Draw face edges
            for i in range(len(face)):
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, face[i])
                line.GetPointIds().SetId(1, face[(i + 1) % len(face)])
                vtk_lines.InsertNextCell(line)

        # Create polydata
        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(vtk_points)
        poly_data.SetLines(vtk_lines)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetLineWidth(2.0)
        actor.GetProperty().SetPointSize(point_size)
        actor.GetProperty().SetRenderPointsAsSpheres(True)

        return actor

    @staticmethod
    def compute_bounding_box(result: cpp_core.TessellationResult) -> Tuple[np.ndarray, np.ndarray]:
        """Compute axis-aligned bounding box.

        Returns:
            (min_corner, max_corner) as numpy arrays
        """
        vertices = result.vertices
        min_corner = vertices.min(axis=0)
        max_corner = vertices.max(axis=0)
        return min_corner, max_corner
