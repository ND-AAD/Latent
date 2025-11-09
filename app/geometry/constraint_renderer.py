"""
Constraint Renderer - VTK visualization of undercuts and draft angles.

This module provides visualization for manufacturing constraint validation,
displaying undercuts, draft angle color-coding, and demolding direction vectors.

Features:
- Red highlighting of undercut faces (Tier 1: hard constraint)
- Color-coded draft angle visualization (Tier 2: manufacturing challenge)
  - Red: <0.5° (insufficient draft)
  - Yellow: 0.5-2.0° (marginal draft)
  - Green: >2.0° (good draft)
- 3D arrow visualization of demolding direction vector
- Support for both face-based and vertex-based constraint data

Constraint Tiers (v5.0 spec):
- **Tier 1 (Physical)**: Undercuts, slip access, air traps - MUST pass
- **Tier 2 (Manufacturing)**: Draft angles, wall thickness - warnings
- **Tier 3 (Mathematical)**: Unity strength, resonance - suggestions

Author: Ceramic Mold Analyzer - Agent 45
Date: November 2025
"""

import vtk
import numpy as np
from typing import List, Dict, Optional, Tuple


class ConstraintRenderer:
    """
    Render constraint violations in VTK viewport.

    Provides visual feedback for manufacturing constraints including:
    - Undercuts: Red highlighting for faces that cannot be demolded
    - Draft angles: Color gradient showing draft quality
    - Demolding vector: Blue arrow showing pull direction

    This renderer works with polydata (display mesh) generated from exact
    SubD limit surface evaluation. The visualization is for user feedback;
    the underlying parametric regions remain exact.
    """

    def __init__(self, renderer: vtk.vtkRenderer):
        """
        Initialize the constraint renderer.

        Args:
            renderer: VTK renderer to add constraint visualization actors to
        """
        self.renderer = renderer

        # VTK actors for constraint visualization
        self.undercut_actor: Optional[vtk.vtkActor] = None
        self.draft_actor: Optional[vtk.vtkActor] = None
        self.demold_arrow: Optional[vtk.vtkActor] = None

        # Cached polydata for updates
        self.current_mesh: Optional[vtk.vtkPolyData] = None

        # Draft angle thresholds (degrees)
        self.draft_insufficient = 0.5   # Below this: red (insufficient)
        self.draft_marginal = 2.0       # Below this: yellow (marginal), above: green (good)

    def show_undercuts(
        self,
        face_ids: List[int],
        mesh: vtk.vtkPolyData
    ):
        """
        Highlight undercut faces in red.

        Undercuts are Tier 1 physical constraints - they prevent demolding
        and must be resolved before mold generation.

        Args:
            face_ids: List of face indices (cells) that have undercuts
            mesh: VTK polydata representing the surface
        """
        # Clear existing undercut visualization
        self.clear_undercuts()

        if not face_ids or mesh is None:
            return

        # Store mesh reference
        self.current_mesh = mesh

        # Create selection of undercut faces
        selection = vtk.vtkSelectionNode()
        selection.SetFieldType(vtk.vtkSelectionNode.CELL)
        selection.SetContentType(vtk.vtkSelectionNode.INDICES)

        # Add face IDs to selection
        id_array = vtk.vtkIdTypeArray()
        for face_id in face_ids:
            id_array.InsertNextValue(face_id)
        selection.SetSelectionList(id_array)

        selection_obj = vtk.vtkSelection()
        selection_obj.AddNode(selection)

        # Extract undercut faces
        extract = vtk.vtkExtractSelection()
        extract.SetInputData(0, mesh)
        extract.SetInputData(1, selection_obj)
        extract.Update()

        # Convert to polydata
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputData(extract.GetOutput())
        geometry_filter.Update()

        undercut_polydata = geometry_filter.GetOutput()

        if undercut_polydata.GetNumberOfCells() == 0:
            return

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(undercut_polydata)

        # Create actor with red highlighting
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # Red
        actor.GetProperty().SetOpacity(0.7)  # Semi-transparent overlay
        actor.GetProperty().SetInterpolationToFlat()  # Flat shading for emphasis

        # Offset to prevent z-fighting with underlying mesh
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-1, -1)

        # Add to renderer
        self.renderer.AddActor(actor)
        self.undercut_actor = actor

    def show_draft_angles(
        self,
        draft_map: Dict[int, float],
        mesh: vtk.vtkPolyData
    ):
        """
        Color faces by draft angle.

        Draft angles are Tier 2 manufacturing constraints - they affect
        demolding ease but don't prevent it entirely.

        Color scheme:
        - Red: <0.5° (insufficient - very difficult to demold)
        - Yellow: 0.5-2.0° (marginal - requires care)
        - Green: >2.0° (good - easy demolding)

        Args:
            draft_map: Dictionary mapping face_id -> draft_angle (degrees)
            mesh: VTK polydata representing the surface
        """
        # Clear existing draft visualization
        self.clear_draft()

        if not draft_map or mesh is None:
            return

        # Store mesh reference
        self.current_mesh = mesh

        # Create a copy of mesh to avoid modifying original
        mesh_copy = vtk.vtkPolyData()
        mesh_copy.DeepCopy(mesh)

        # Create scalar array for draft angles
        num_cells = mesh_copy.GetNumberOfCells()
        draft_scalars = vtk.vtkFloatArray()
        draft_scalars.SetName("DraftAngle")
        draft_scalars.SetNumberOfTuples(num_cells)

        # Fill draft angle values (use 0.0 for unmapped faces)
        for cell_id in range(num_cells):
            draft_angle = draft_map.get(cell_id, 0.0)
            draft_scalars.SetValue(cell_id, draft_angle)

        # Add scalars to mesh
        mesh_copy.GetCellData().SetScalars(draft_scalars)

        # Create lookup table for draft angle color mapping
        lut = self._create_draft_lut()

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(mesh_copy)
        mapper.SetLookupTable(lut)
        mapper.SetScalarModeToUseCellData()
        mapper.SetScalarRange(0.0, 5.0)  # 0-5 degree range

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetInterpolationToGouraud()  # Smooth shading

        # Add to renderer
        self.renderer.AddActor(actor)
        self.draft_actor = actor

    def show_demolding_direction(
        self,
        direction: Tuple[float, float, float],
        origin: Optional[Tuple[float, float, float]] = None,
        scale: float = 2.0
    ):
        """
        Display demolding vector as 3D arrow.

        The demolding direction indicates the pull direction for mold separation.
        This is typically the primary constraint direction for draft angle validation.

        Args:
            direction: Unit vector (x, y, z) for demolding direction
            origin: Starting point for arrow (uses scene center if None)
            scale: Scale factor for arrow length (default: 2.0)
        """
        # Clear existing arrow
        self.clear_demold_arrow()

        if direction is None:
            return

        # Normalize direction vector
        dir_array = np.array(direction, dtype=float)
        length = np.linalg.norm(dir_array)
        if length < 1e-6:
            return  # Invalid direction
        dir_normalized = dir_array / length

        # Determine origin (use scene center if not provided)
        if origin is None:
            if self.current_mesh:
                bounds = self.current_mesh.GetBounds()
                origin = (
                    (bounds[0] + bounds[1]) / 2,
                    (bounds[2] + bounds[3]) / 2,
                    (bounds[4] + bounds[5]) / 2
                )
            else:
                origin = (0.0, 0.0, 0.0)

        # Create arrow source
        arrow_source = vtk.vtkArrowSource()
        arrow_source.SetTipResolution(16)
        arrow_source.SetShaftResolution(16)
        arrow_source.SetTipRadius(0.15)
        arrow_source.SetTipLength(0.35)
        arrow_source.SetShaftRadius(0.05)

        # Create transformation matrix for arrow orientation
        # VTK arrow points along +X by default
        transform = vtk.vtkTransform()
        transform.Translate(origin[0], origin[1], origin[2])

        # Calculate rotation to align +X with direction vector
        # Using angle-axis rotation
        default_dir = np.array([1.0, 0.0, 0.0])
        rotation_axis = np.cross(default_dir, dir_normalized)
        rotation_axis_length = np.linalg.norm(rotation_axis)

        if rotation_axis_length > 1e-6:
            # Non-parallel vectors - rotate
            rotation_axis /= rotation_axis_length
            angle = np.arccos(np.clip(np.dot(default_dir, dir_normalized), -1.0, 1.0))
            angle_deg = np.degrees(angle)
            transform.RotateWXYZ(angle_deg, rotation_axis[0], rotation_axis[1], rotation_axis[2])
        elif np.dot(default_dir, dir_normalized) < 0:
            # Opposite direction - rotate 180°
            transform.RotateWXYZ(180.0, 0.0, 1.0, 0.0)

        # Scale arrow
        transform.Scale(scale, scale, scale)

        # Apply transformation
        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputConnection(arrow_source.GetOutputPort())
        transform_filter.SetTransform(transform)
        transform_filter.Update()

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transform_filter.GetOutputPort())

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.0, 0.5, 1.0)  # Blue
        actor.GetProperty().SetOpacity(0.8)

        # Add to renderer
        self.renderer.AddActor(actor)
        self.demold_arrow = actor

    def _create_draft_lut(self) -> vtk.vtkLookupTable:
        """
        Create lookup table for draft angle color mapping.

        Color scheme:
        - Red (1.0, 0.0, 0.0): 0.0 to 0.5° (insufficient)
        - Yellow (1.0, 1.0, 0.0): 0.5 to 2.0° (marginal)
        - Green (0.0, 1.0, 0.0): 2.0° and above (good)

        Returns:
            vtkLookupTable configured for draft angle visualization
        """
        lut = vtk.vtkLookupTable()
        lut.SetTableRange(0.0, 5.0)  # 0-5 degree range
        lut.SetNumberOfTableValues(256)

        for i in range(256):
            # Map table index to draft angle
            draft_angle = (i / 255.0) * 5.0

            if draft_angle < self.draft_insufficient:
                # Red: insufficient draft
                r, g, b = 1.0, 0.0, 0.0
            elif draft_angle < self.draft_marginal:
                # Gradient from red to yellow to green
                # Interpolate between red (0.5°) and green (2.0°)
                t = (draft_angle - self.draft_insufficient) / (self.draft_marginal - self.draft_insufficient)

                # Red -> Yellow -> Green
                if t < 0.5:
                    # Red to yellow (add green component)
                    t_local = t * 2.0
                    r, g, b = 1.0, t_local, 0.0
                else:
                    # Yellow to green (remove red component)
                    t_local = (t - 0.5) * 2.0
                    r, g, b = 1.0 - t_local, 1.0, 0.0
            else:
                # Green: good draft
                r, g, b = 0.0, 1.0, 0.0

            lut.SetTableValue(i, r, g, b, 1.0)

        lut.Build()
        return lut

    def clear_undercuts(self):
        """Clear undercut visualization from renderer."""
        if self.undercut_actor:
            self.renderer.RemoveActor(self.undercut_actor)
            self.undercut_actor = None

    def clear_draft(self):
        """Clear draft angle visualization from renderer."""
        if self.draft_actor:
            self.renderer.RemoveActor(self.draft_actor)
            self.draft_actor = None

    def clear_demold_arrow(self):
        """Clear demolding arrow from renderer."""
        if self.demold_arrow:
            self.renderer.RemoveActor(self.demold_arrow)
            self.demold_arrow = None

    def clear_all(self):
        """Clear all constraint visualizations from renderer."""
        self.clear_undercuts()
        self.clear_draft()
        self.clear_demold_arrow()
        self.current_mesh = None

    def update_draft_thresholds(
        self,
        insufficient: float,
        marginal: float
    ):
        """
        Update draft angle threshold values.

        Allows customization of color breakpoints based on material
        properties and manufacturing capabilities.

        Args:
            insufficient: Angle below which draft is insufficient (degrees)
            marginal: Angle below which draft is marginal (degrees)
        """
        self.draft_insufficient = insufficient
        self.draft_marginal = marginal

        # If draft visualization is active, update it
        if self.draft_actor:
            # Recreate LUT with new thresholds
            mapper = self.draft_actor.GetMapper()
            lut = self._create_draft_lut()
            mapper.SetLookupTable(lut)

    def get_draft_statistics(
        self,
        draft_map: Dict[int, float]
    ) -> Dict[str, any]:
        """
        Calculate statistics for draft angle distribution.

        Args:
            draft_map: Dictionary mapping face_id -> draft_angle (degrees)

        Returns:
            Dictionary with min, max, mean, std, and counts per category
        """
        if not draft_map:
            return {
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "std": 0.0,
                "count_insufficient": 0,
                "count_marginal": 0,
                "count_good": 0,
                "total_faces": 0
            }

        draft_values = np.array(list(draft_map.values()))

        # Count faces by category
        insufficient = np.sum(draft_values < self.draft_insufficient)
        marginal = np.sum((draft_values >= self.draft_insufficient) &
                         (draft_values < self.draft_marginal))
        good = np.sum(draft_values >= self.draft_marginal)

        return {
            "min": float(np.min(draft_values)),
            "max": float(np.max(draft_values)),
            "mean": float(np.mean(draft_values)),
            "std": float(np.std(draft_values)),
            "median": float(np.median(draft_values)),
            "count_insufficient": int(insufficient),
            "count_marginal": int(marginal),
            "count_good": int(good),
            "total_faces": len(draft_map)
        }


def create_test_constraint_visualization(
    renderer: vtk.vtkRenderer
) -> ConstraintRenderer:
    """
    Create test constraint visualization on a simple mesh.

    Demonstrates undercut highlighting, draft angle coloring, and
    demolding direction arrow.

    Args:
        renderer: VTK renderer to add visualization to

    Returns:
        ConstraintRenderer with test visualization active
    """
    # Create test cylinder (simulates mold surface)
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetHeight(4.0)
    cylinder.SetRadius(1.5)
    cylinder.SetResolution(32)
    cylinder.Update()

    mesh = cylinder.GetOutput()
    num_cells = mesh.GetNumberOfCells()

    # Create constraint renderer
    constraint_renderer = ConstraintRenderer(renderer)

    # Simulate undercuts (bottom 20% of faces)
    undercut_faces = list(range(int(num_cells * 0.8), num_cells))
    constraint_renderer.show_undercuts(undercut_faces, mesh)

    # Simulate draft angles (gradient along height)
    draft_map = {}
    for i in range(num_cells):
        # Top faces have good draft, bottom faces have poor draft
        draft_angle = 3.0 - (i / num_cells) * 2.8  # 3.0° to 0.2°
        draft_map[i] = draft_angle

    constraint_renderer.show_draft_angles(draft_map, mesh)

    # Show demolding direction (upward +Z)
    constraint_renderer.show_demolding_direction(
        direction=(0.0, 1.0, 0.0),  # Cylinder's Y-axis
        scale=3.0
    )

    return constraint_renderer
