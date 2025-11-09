"""Viewport helper utilities (axes, grid, etc)."""

import vtk


class ViewportHelpers:
    """Factory for common viewport visual aids."""

    @staticmethod
    def create_axes_actor(length: float = 1.0) -> vtk.vtkAxesActor:
        """Create RGB axes helper (X=Red, Y=Green, Z=Blue).

        Args:
            length: Axis length

        Returns:
            vtkAxesActor
        """
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(length, length, length)
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.02)
        axes.SetConeRadius(0.1)
        axes.SetNormalizedShaftLength(0.8, 0.8, 0.8)
        axes.SetNormalizedTipLength(0.2, 0.2, 0.2)

        # Labels
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()

        return axes

    @staticmethod
    def create_grid_plane(size: float = 10.0,
                          divisions: int = 10,
                          color: tuple = (0.3, 0.3, 0.3)) -> vtk.vtkActor:
        """Create ground plane grid.

        Args:
            size: Grid size
            divisions: Number of grid divisions
            color: Grid line color (R,G,B)

        Returns:
            vtkActor for grid
        """
        # Create grid points
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        step = size / divisions
        half_size = size / 2.0

        # Horizontal lines
        for i in range(divisions + 1):
            y = -half_size + i * step

            p1_id = points.InsertNextPoint(-half_size, y, 0)
            p2_id = points.InsertNextPoint(half_size, y, 0)

            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, p1_id)
            line.GetPointIds().SetId(1, p2_id)
            lines.InsertNextCell(line)

        # Vertical lines
        for i in range(divisions + 1):
            x = -half_size + i * step

            p1_id = points.InsertNextPoint(x, -half_size, 0)
            p2_id = points.InsertNextPoint(x, half_size, 0)

            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, p1_id)
            line.GetPointIds().SetId(1, p2_id)
            lines.InsertNextCell(line)

        # Create polydata
        grid = vtk.vtkPolyData()
        grid.SetPoints(points)
        grid.SetLines(lines)

        # Mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(grid)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetLineWidth(1.0)
        actor.GetProperty().SetOpacity(0.5)

        return actor

    @staticmethod
    def create_bounding_box(bounds: tuple) -> vtk.vtkActor:
        """Create wireframe bounding box.

        Args:
            bounds: (xmin, xmax, ymin, ymax, zmin, zmax)

        Returns:
            vtkActor for bounding box
        """
        outline = vtk.vtkOutlineSource()
        outline.SetBounds(bounds)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outline.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        actor.GetProperty().SetLineWidth(1.5)

        return actor
