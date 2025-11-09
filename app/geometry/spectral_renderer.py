"""
Spectral Renderer - VTK visualization for eigenfunction analysis.

This module provides VTK-based rendering for spectral decomposition results:
- False-color eigenfunction mapping (blue-white-red diverging)
- Nodal line extraction and rendering (zero-crossing curves)
- Multiple eigenmode visualization
- Integration with existing VTK viewport system

Mathematical Background:
- Eigenfunctions are solutions to Laplace-Beltrami eigenvalue problem: Δφ = -λφ
- Nodal lines are zero-level sets: {x | φ(x) = 0}
- Different modes reveal different structural patterns

Author: Ceramic Mold Analyzer - Agent 36
Date: November 2025
"""

import vtk
import numpy as np
from typing import Optional
from app.analysis.spectral_decomposition import EigenMode


class SpectralRenderer:
    """
    VTK renderer for eigenfunction visualization.

    Features:
    - Eigenfunction values mapped as diverging color field
    - Nodal lines (zero crossings) rendered as prominent tubes
    - Multiple visualization modes with transparency blending
    - Customizable color maps and line styles
    """

    def __init__(self, renderer: vtk.vtkRenderer):
        """
        Initialize the spectral renderer.

        Args:
            renderer: VTK renderer to add actors to
        """
        self.renderer = renderer

        # Actors (current visualization state)
        self.surface_actor: Optional[vtk.vtkActor] = None
        self.nodal_line_actor: Optional[vtk.vtkActor] = None

        # Color map configuration
        self.colormap = 'coolwarm'  # Diverging: blue (negative) - white (zero) - red (positive)

        # Nodal line rendering parameters
        self.nodal_line_radius = 0.01
        self.nodal_line_color = (0, 0, 0)  # Black
        self.nodal_line_width = 3

    def render_eigenfunction(self,
                            mesh,
                            mode: EigenMode,
                            show_nodal_lines: bool = True):
        """
        Render eigenfunction as colored surface with optional nodal lines.

        Args:
            mesh: Tessellated mesh (TessellationResult from SubDEvaluator)
            mode: EigenMode to visualize
            show_nodal_lines: If True, draw zero-crossing curves
        """
        # Create polydata from tessellation
        polydata = self._mesh_to_polydata(mesh)

        # Add eigenfunction values as scalar field
        scalars = vtk.vtkFloatArray()
        scalars.SetName("eigenfunction")
        for value in mode.eigenfunction:
            scalars.InsertNextValue(float(value))

        polydata.GetPointData().SetScalars(scalars)

        # Create lookup table (color map)
        lut = self._create_colormap_lut(self.colormap)

        # Create mapper with color mapping
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetScalarRange(float(np.min(mode.eigenfunction)),
                             float(np.max(mode.eigenfunction)))
        mapper.SetLookupTable(lut)

        # Remove old surface actor if exists
        if self.surface_actor:
            self.renderer.RemoveActor(self.surface_actor)

        # Create new surface actor
        self.surface_actor = vtk.vtkActor()
        self.surface_actor.SetMapper(mapper)
        self.surface_actor.GetProperty().SetInterpolationToGouraud()  # Smooth shading
        self.renderer.AddActor(self.surface_actor)

        # Render nodal lines if requested
        if show_nodal_lines:
            self._render_nodal_lines(polydata, mode.eigenfunction)

    def _render_nodal_lines(self,
                           polydata: vtk.vtkPolyData,
                           eigenfunction: np.ndarray):
        """
        Extract and render zero-crossing contours (nodal lines).

        Nodal lines are boundaries between positive and negative eigenfunction regions.
        They represent natural subdivision boundaries revealed by the spectral analysis.

        Args:
            polydata: VTK polydata with eigenfunction scalar field
            eigenfunction: Per-vertex eigenfunction values
        """
        # Use VTK contour filter to extract zero-level set
        contour = vtk.vtkContourFilter()
        contour.SetInputData(polydata)
        contour.SetValue(0, 0.0)  # Extract contour at value = 0
        contour.Update()

        # Check if any contours were extracted
        contour_output = contour.GetOutput()
        if contour_output.GetNumberOfPoints() == 0:
            # No nodal lines (constant eigenfunction or numerical issues)
            if self.nodal_line_actor:
                self.renderer.RemoveActor(self.nodal_line_actor)
                self.nodal_line_actor = None
            return

        # Create tubes around contour lines for visibility
        tubes = vtk.vtkTubeFilter()
        tubes.SetInputConnection(contour.GetOutputPort())
        tubes.SetRadius(self.nodal_line_radius)
        tubes.SetNumberOfSides(8)
        tubes.CappingOn()
        tubes.Update()

        # Create mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tubes.GetOutputPort())

        # Remove old nodal line actor if exists
        if self.nodal_line_actor:
            self.renderer.RemoveActor(self.nodal_line_actor)

        # Create new nodal line actor
        self.nodal_line_actor = vtk.vtkActor()
        self.nodal_line_actor.SetMapper(mapper)
        self.nodal_line_actor.GetProperty().SetColor(*self.nodal_line_color)
        self.nodal_line_actor.GetProperty().SetLineWidth(self.nodal_line_width)

        self.renderer.AddActor(self.nodal_line_actor)

    def _create_colormap_lut(self, name: str) -> vtk.vtkLookupTable:
        """
        Create VTK lookup table for color mapping.

        Args:
            name: Color map name ('coolwarm' for diverging blue-white-red)

        Returns:
            VTK lookup table configured for the color map
        """
        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(256)

        if name == 'coolwarm':
            # Diverging color map: blue (negative) → white (zero) → red (positive)
            # This is ideal for eigenfunction visualization where sign matters
            for i in range(256):
                t = i / 255.0  # Normalized position [0, 1]

                if t < 0.5:
                    # Blue to white (negative to zero)
                    s = 2 * t  # [0, 1]
                    r, g, b = s, s, 1.0
                else:
                    # White to red (zero to positive)
                    s = 2 * (t - 0.5)  # [0, 1]
                    r, g, b = 1.0, 1.0 - s, 1.0 - s

                lut.SetTableValue(i, r, g, b, 1.0)

        lut.Build()
        return lut

    def _mesh_to_polydata(self, mesh) -> vtk.vtkPolyData:
        """
        Convert TessellationResult to vtkPolyData.

        Args:
            mesh: TessellationResult from SubDEvaluator (has vertices, normals, triangles)

        Returns:
            VTK polydata ready for rendering
        """
        # Create VTK points from vertices
        points = vtk.vtkPoints()
        vertices = mesh.vertices
        if isinstance(vertices, np.ndarray):
            # NumPy array (zero-copy from C++)
            if len(vertices.shape) == 1:
                # Flattened array: reshape to (N, 3)
                vertices = vertices.reshape(-1, 3)
            for v in vertices:
                points.InsertNextPoint(float(v[0]), float(v[1]), float(v[2]))
        else:
            # List or other iterable
            for i in range(0, len(vertices), 3):
                points.InsertNextPoint(float(vertices[i]),
                                      float(vertices[i+1]),
                                      float(vertices[i+2]))

        # Create VTK triangles
        triangles = vtk.vtkCellArray()
        tri_data = mesh.triangles
        if isinstance(tri_data, np.ndarray):
            # NumPy array
            if len(tri_data.shape) == 1:
                # Flattened array: reshape to (M, 3)
                tri_data = tri_data.reshape(-1, 3)
            for tri in tri_data:
                triangle = vtk.vtkTriangle()
                triangle.GetPointIds().SetId(0, int(tri[0]))
                triangle.GetPointIds().SetId(1, int(tri[1]))
                triangle.GetPointIds().SetId(2, int(tri[2]))
                triangles.InsertNextCell(triangle)
        else:
            # List or other iterable
            for i in range(0, len(tri_data), 3):
                triangle = vtk.vtkTriangle()
                triangle.GetPointIds().SetId(0, int(tri_data[i]))
                triangle.GetPointIds().SetId(1, int(tri_data[i+1]))
                triangle.GetPointIds().SetId(2, int(tri_data[i+2]))
                triangles.InsertNextCell(triangle)

        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(triangles)

        # Add normals if available
        if hasattr(mesh, 'normals') and mesh.normals is not None:
            normals = vtk.vtkFloatArray()
            normals.SetNumberOfComponents(3)
            normals.SetName("Normals")

            normal_data = mesh.normals
            if isinstance(normal_data, np.ndarray):
                if len(normal_data.shape) == 1:
                    normal_data = normal_data.reshape(-1, 3)
                for n in normal_data:
                    normals.InsertNextTuple3(float(n[0]), float(n[1]), float(n[2]))
            else:
                for i in range(0, len(normal_data), 3):
                    normals.InsertNextTuple3(float(normal_data[i]),
                                            float(normal_data[i+1]),
                                            float(normal_data[i+2]))

            polydata.GetPointData().SetNormals(normals)

        return polydata

    def clear(self):
        """Remove all spectral visualization actors from the renderer."""
        if self.surface_actor:
            self.renderer.RemoveActor(self.surface_actor)
            self.surface_actor = None

        if self.nodal_line_actor:
            self.renderer.RemoveActor(self.nodal_line_actor)
            self.nodal_line_actor = None

    def set_nodal_line_style(self,
                            radius: float = 0.01,
                            color: tuple = (0, 0, 0),
                            width: float = 3):
        """
        Configure nodal line rendering style.

        Args:
            radius: Tube radius for nodal lines
            color: RGB color tuple (0-1 range)
            width: Line width
        """
        self.nodal_line_radius = radius
        self.nodal_line_color = color
        self.nodal_line_width = width

    def set_colormap(self, name: str):
        """
        Change the color map.

        Args:
            name: Color map name (currently only 'coolwarm' supported)
        """
        self.colormap = name

    def get_stats(self, mode: EigenMode) -> dict:
        """
        Get statistics about the eigenfunction.

        Args:
            mode: EigenMode to analyze

        Returns:
            Dictionary with statistics
        """
        ef = mode.eigenfunction
        return {
            'eigenvalue': float(mode.eigenvalue),
            'index': mode.index,
            'multiplicity': mode.multiplicity,
            'min': float(np.min(ef)),
            'max': float(np.max(ef)),
            'mean': float(np.mean(ef)),
            'std': float(np.std(ef)),
            'zero_crossings': int(np.sum(np.diff(np.sign(ef)) != 0)),
            'num_vertices': len(ef)
        }
