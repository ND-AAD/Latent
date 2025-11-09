"""
Region Renderer - Visualization of parametric regions with coloring.

Provides per-region coloring, boundary rendering, and highlighting for regions.

CRITICAL: This renderer uses display meshes generated from exact limit surface
evaluation. Display meshes are for rendering ONLY - they do not replace the
parametric region definitions which remain exact until fabrication.
"""

import vtk
import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from app.state.parametric_region import ParametricRegion
from app.ui.region_color_manager import RegionColorManager

try:
    import cpp_core
except ImportError:
    # cpp_core not built yet - will be available after Day 0 setup
    cpp_core = None


class RegionRenderer:
    """
    Renders regions with per-region coloring, boundaries, and highlighting.

    Features:
    - Per-region coloring using VTK scalar arrays
    - Boundary rendering as tubes
    - Hover highlighting (lighter shade)
    - Selection highlighting (thick boundary)
    - Pinned region marking
    """

    def __init__(self, color_manager: RegionColorManager):
        """
        Initialize the region renderer.

        Args:
            color_manager: RegionColorManager for color assignment
        """
        self.color_manager = color_manager

        # VTK actors
        self.region_actors: List[vtk.vtkActor] = []
        self.boundary_actors: List[vtk.vtkActor] = []
        self.highlight_actors: List[vtk.vtkActor] = []
        self.pin_markers: List[vtk.vtkActor] = []

        # State
        self.current_polydata = None
        self.tessellation_result = None
        self.hovered_region_id: Optional[str] = None
        self.selected_region_id: Optional[str] = None

    def render_regions(
        self,
        regions: List[ParametricRegion],
        tessellation_result,  # cpp_core.TessellationResult
        renderer: vtk.vtkRenderer
    ):
        """
        Render all regions with per-region coloring.

        Creates a single colored mesh actor with per-face colors applied
        using VTK scalar arrays.

        Args:
            regions: List of ParametricRegion to render
            tessellation_result: TessellationResult from SubDEvaluator
            renderer: VTK renderer to add actors to
        """
        # Clear existing actors
        self.clear_all(renderer)

        if not regions or tessellation_result is None:
            return

        # Store for later use
        self.tessellation_result = tessellation_result

        # Assign colors to regions
        self.color_manager.assign_colors(regions)

        # Create polydata from tessellation
        polydata = self._create_polydata_from_tessellation(tessellation_result)
        self.current_polydata = polydata

        # Create face-to-region mapping
        face_to_region = self._create_face_to_region_map(regions)

        # Apply per-face colors
        colored_polydata = self._apply_region_colors(polydata, face_to_region, tessellation_result)

        # Create mapper with scalar coloring
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(colored_polydata)
        mapper.SetScalarModeToUseCellData()
        mapper.ScalarVisibilityOn()

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetInterpolationToGouraud()  # Smooth shading

        # Add to renderer
        renderer.AddActor(actor)
        self.region_actors.append(actor)

        # Render boundaries
        self._render_boundaries(regions, renderer)

    def _create_polydata_from_tessellation(self, result) -> vtk.vtkPolyData:
        """
        Convert TessellationResult to VTK polydata.

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

    def _create_face_to_region_map(self, regions: List[ParametricRegion]) -> Dict[int, str]:
        """
        Create mapping from SubD face index to region ID.

        Args:
            regions: List of regions

        Returns:
            Dictionary mapping face_id -> region_id
        """
        face_to_region = {}

        for region in regions:
            for face_id in region.faces:
                face_to_region[face_id] = region.id

        return face_to_region

    def _apply_region_colors(
        self,
        polydata: vtk.vtkPolyData,
        face_to_region: Dict[int, str],
        tessellation_result
    ) -> vtk.vtkPolyData:
        """
        Apply per-region colors to polydata using cell scalars.

        Args:
            polydata: Input polydata
            face_to_region: Mapping from face ID to region ID
            tessellation_result: TessellationResult with face_parents

        Returns:
            New polydata with color scalars applied
        """
        # Create color lookup table
        num_cells = polydata.GetNumberOfCells()

        # Create RGB color array for cells
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("RegionColors")
        colors.SetNumberOfTuples(num_cells)

        # Get face parent information (which SubD face each triangle came from)
        face_parents = tessellation_result.face_parents

        # Apply colors based on region
        for cell_id in range(num_cells):
            # Get parent face for this triangle
            parent_face = face_parents[cell_id] if cell_id < len(face_parents) else -1

            if parent_face in face_to_region:
                # Get region color
                region_id = face_to_region[parent_face]
                color = self.color_manager.get_color(region_id)

                # Convert to 0-255 range
                r = int(color[0] * 255)
                g = int(color[1] * 255)
                b = int(color[2] * 255)
            else:
                # Unassigned face - use default gray
                r, g, b = 180, 180, 200

            colors.SetTuple3(cell_id, r, g, b)

        # Add colors to polydata
        polydata.GetCellData().SetScalars(colors)

        return polydata

    def _render_boundaries(self, regions: List[ParametricRegion], renderer: vtk.vtkRenderer):
        """
        Render region boundaries as tubes.

        Extracts boundary edges between regions and renders them as
        colored tubes for clear visual separation.

        Args:
            regions: List of regions
            renderer: VTK renderer to add boundary actors to
        """
        # Build face adjacency for boundary detection
        face_to_region = self._create_face_to_region_map(regions)

        # Extract boundary edges (edges between different regions)
        boundary_edges = self._extract_boundary_edges(face_to_region)

        if not boundary_edges:
            return

        # Create boundary geometry for each region
        for region in regions:
            region_boundaries = [
                edge for edge, (r1, r2) in boundary_edges.items()
                if r1 == region.id or r2 == region.id
            ]

            if not region_boundaries:
                continue

            # Create tube actor for region boundaries
            boundary_actor = self._create_boundary_actor(
                region_boundaries,
                self.color_manager.get_boundary_color(region.id)
            )

            renderer.AddActor(boundary_actor)
            self.boundary_actors.append(boundary_actor)

    def _extract_boundary_edges(
        self,
        face_to_region: Dict[int, str]
    ) -> Dict[Tuple[int, int], Tuple[str, str]]:
        """
        Extract boundary edges between regions.

        An edge is a boundary if it's shared by faces belonging to different regions.

        Args:
            face_to_region: Mapping from face ID to region ID

        Returns:
            Dictionary mapping edge (v1, v2) -> (region1_id, region2_id)
        """
        if not self.current_polydata:
            return {}

        # Build edge to faces mapping
        edge_to_faces: Dict[Tuple[int, int], List[int]] = {}

        num_cells = self.current_polydata.GetNumberOfCells()
        for cell_id in range(num_cells):
            cell = self.current_polydata.GetCell(cell_id)

            if cell.GetNumberOfPoints() != 3:
                continue

            # Get triangle vertices
            v0 = cell.GetPointId(0)
            v1 = cell.GetPointId(1)
            v2 = cell.GetPointId(2)

            # Add edges (canonical ordering: smaller index first)
            edges = [
                (min(v0, v1), max(v0, v1)),
                (min(v1, v2), max(v1, v2)),
                (min(v2, v0), max(v2, v0))
            ]

            for edge in edges:
                if edge not in edge_to_faces:
                    edge_to_faces[edge] = []
                edge_to_faces[edge].append(cell_id)

        # Find boundary edges (between different regions)
        boundary_edges = {}

        if not self.tessellation_result:
            return {}

        face_parents = self.tessellation_result.face_parents

        for edge, face_cells in edge_to_faces.items():
            if len(face_cells) < 2:
                continue  # Border edge, not between regions

            # Get parent faces for cells sharing this edge
            parent_faces = [
                face_parents[cell_id] if cell_id < len(face_parents) else -1
                for cell_id in face_cells
            ]

            # Get regions for parent faces
            regions_at_edge = set()
            for parent_face in parent_faces:
                if parent_face in face_to_region:
                    regions_at_edge.add(face_to_region[parent_face])

            # If edge is shared by multiple regions, it's a boundary
            if len(regions_at_edge) >= 2:
                region_list = list(regions_at_edge)
                boundary_edges[edge] = (region_list[0], region_list[1])

        return boundary_edges

    def _create_boundary_actor(
        self,
        edges: List[Tuple[int, int]],
        color: Tuple[float, float, float],
        line_width: float = 3.0
    ) -> vtk.vtkActor:
        """
        Create VTK actor for boundary edges rendered as tubes.

        Args:
            edges: List of edge tuples (v1, v2)
            color: RGB color for boundary
            line_width: Width of boundary lines

        Returns:
            vtkActor for boundary visualization
        """
        if not edges or not self.current_polydata:
            # Return empty actor
            actor = vtk.vtkActor()
            return actor

        # Create polyline from edges
        points = self.current_polydata.GetPoints()

        vtk_lines = vtk.vtkCellArray()
        for v1, v2 in edges:
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, v1)
            line.GetPointIds().SetId(1, v2)
            vtk_lines.InsertNextCell(line)

        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(vtk_lines)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetLineWidth(line_width)
        actor.GetProperty().SetRenderLinesAsTubes(True)

        # Offset slightly to prevent z-fighting
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-2, -2)

        return actor

    def highlight_region(
        self,
        region: Optional[ParametricRegion],
        renderer: vtk.vtkRenderer,
        hover: bool = True
    ):
        """
        Highlight a region (for hover or selection).

        Args:
            region: Region to highlight (None to clear)
            renderer: VTK renderer
            hover: If True, use hover highlighting (lighter shade).
                   If False, use selection highlighting (thick boundary)
        """
        # Clear existing highlights
        self._clear_highlight_actors(renderer)

        if not region or not self.current_polydata or not self.tessellation_result:
            return

        if hover:
            # Hover highlighting - lighter shade overlay
            self._create_hover_highlight(region, renderer)
        else:
            # Selection highlighting - thick boundary
            self._create_selection_highlight(region, renderer)

    def _create_hover_highlight(self, region: ParametricRegion, renderer: vtk.vtkRenderer):
        """
        Create hover highlight overlay (lighter shade).

        Args:
            region: Region to highlight
            renderer: VTK renderer
        """
        # Get lighter color for region
        highlight_color = self.color_manager.get_highlight_color(region.id)

        # Extract region faces
        region_faces = self._extract_region_faces(region)

        if region_faces.GetNumberOfCells() == 0:
            return

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(region_faces)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*highlight_color)
        actor.GetProperty().SetOpacity(0.6)
        actor.GetProperty().SetInterpolationToGouraud()

        # Offset to prevent z-fighting
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-1, -1)

        renderer.AddActor(actor)
        self.highlight_actors.append(actor)

    def _create_selection_highlight(self, region: ParametricRegion, renderer: vtk.vtkRenderer):
        """
        Create selection highlight (thick boundary).

        Args:
            region: Region to highlight
            renderer: VTK renderer
        """
        # Extract boundary of selected region
        boundary_edges = self._extract_region_boundary(region)

        if not boundary_edges:
            return

        # Create thick boundary actor
        boundary_color = self.color_manager.get_boundary_color(region.id)
        actor = self._create_boundary_actor(
            boundary_edges,
            boundary_color,
            line_width=5.0  # Thicker for selection
        )

        renderer.AddActor(actor)
        self.highlight_actors.append(actor)

    def _extract_region_faces(self, region: ParametricRegion) -> vtk.vtkPolyData:
        """
        Extract faces belonging to a region.

        Args:
            region: Region to extract

        Returns:
            vtkPolyData containing only region's faces
        """
        if not self.current_polydata or not self.tessellation_result:
            return vtk.vtkPolyData()

        # Get face parents
        face_parents = self.tessellation_result.face_parents

        # Find cells that belong to this region
        region_cells = []
        num_cells = self.current_polydata.GetNumberOfCells()

        for cell_id in range(num_cells):
            parent_face = face_parents[cell_id] if cell_id < len(face_parents) else -1

            if parent_face in region.faces:
                region_cells.append(cell_id)

        # Extract cells
        if not region_cells:
            return vtk.vtkPolyData()

        # Create selection
        selection = vtk.vtkSelectionNode()
        selection.SetFieldType(vtk.vtkSelectionNode.CELL)
        selection.SetContentType(vtk.vtkSelectionNode.INDICES)

        id_array = vtk.vtkIdTypeArray()
        for cell_id in region_cells:
            id_array.InsertNextValue(cell_id)
        selection.SetSelectionList(id_array)

        selection_obj = vtk.vtkSelection()
        selection_obj.AddNode(selection)

        # Extract
        extract = vtk.vtkExtractSelection()
        extract.SetInputData(0, self.current_polydata)
        extract.SetInputData(1, selection_obj)
        extract.Update()

        # Convert to polydata
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputData(extract.GetOutput())
        geometry_filter.Update()

        return geometry_filter.GetOutput()

    def _extract_region_boundary(self, region: ParametricRegion) -> List[Tuple[int, int]]:
        """
        Extract boundary edges of a region.

        Args:
            region: Region to extract boundary from

        Returns:
            List of edge tuples (v1, v2)
        """
        if not self.current_polydata or not self.tessellation_result:
            return []

        face_parents = self.tessellation_result.face_parents

        # Build edge to cells mapping for region faces only
        edge_to_cells: Dict[Tuple[int, int], List[int]] = {}

        num_cells = self.current_polydata.GetNumberOfCells()
        for cell_id in range(num_cells):
            parent_face = face_parents[cell_id] if cell_id < len(face_parents) else -1

            if parent_face not in region.faces:
                continue

            cell = self.current_polydata.GetCell(cell_id)
            if cell.GetNumberOfPoints() != 3:
                continue

            # Get triangle vertices
            v0 = cell.GetPointId(0)
            v1 = cell.GetPointId(1)
            v2 = cell.GetPointId(2)

            # Add edges
            edges = [
                (min(v0, v1), max(v0, v1)),
                (min(v1, v2), max(v1, v2)),
                (min(v2, v0), max(v2, v0))
            ]

            for edge in edges:
                if edge not in edge_to_cells:
                    edge_to_cells[edge] = []
                edge_to_cells[edge].append(cell_id)

        # Boundary edges are those with only one adjacent cell in the region
        boundary_edges = [
            edge for edge, cells in edge_to_cells.items()
            if len(cells) == 1
        ]

        return boundary_edges

    def add_pin_marker(
        self,
        region: ParametricRegion,
        renderer: vtk.vtkRenderer
    ):
        """
        Add visual marker for pinned regions.

        Creates a small cone/marker at the region centroid.

        Args:
            region: Pinned region
            renderer: VTK renderer
        """
        # Calculate region centroid
        centroid = self._calculate_region_centroid(region)

        if centroid is None:
            return

        # Create cone marker
        cone = vtk.vtkConeSource()
        cone.SetHeight(0.3)
        cone.SetRadius(0.15)
        cone.SetResolution(16)
        cone.SetDirection(0, 0, 1)  # Point upward

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cone.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.SetPosition(centroid[0], centroid[1], centroid[2] + 0.2)
        actor.GetProperty().SetColor(1.0, 0.8, 0.0)  # Gold color

        renderer.AddActor(actor)
        self.pin_markers.append(actor)

    def _calculate_region_centroid(self, region: ParametricRegion) -> Optional[Tuple[float, float, float]]:
        """
        Calculate centroid of region faces.

        Args:
            region: Region to calculate centroid for

        Returns:
            (x, y, z) centroid or None if failed
        """
        if not self.current_polydata or not self.tessellation_result:
            return None

        face_parents = self.tessellation_result.face_parents

        # Collect all points in region
        points_in_region = []

        num_cells = self.current_polydata.GetNumberOfCells()
        for cell_id in range(num_cells):
            parent_face = face_parents[cell_id] if cell_id < len(face_parents) else -1

            if parent_face not in region.faces:
                continue

            cell = self.current_polydata.GetCell(cell_id)
            for i in range(cell.GetNumberOfPoints()):
                pt = self.current_polydata.GetPoint(cell.GetPointId(i))
                points_in_region.append(pt)

        if not points_in_region:
            return None

        # Calculate average
        centroid = np.mean(points_in_region, axis=0)
        return tuple(centroid)

    def _clear_highlight_actors(self, renderer: vtk.vtkRenderer):
        """Remove highlight actors from renderer."""
        for actor in self.highlight_actors:
            renderer.RemoveActor(actor)
        self.highlight_actors.clear()

    def clear_all(self, renderer: vtk.vtkRenderer):
        """
        Clear all region visualization actors.

        Args:
            renderer: VTK renderer to remove actors from
        """
        # Clear region actors
        for actor in self.region_actors:
            renderer.RemoveActor(actor)
        self.region_actors.clear()

        # Clear boundary actors
        for actor in self.boundary_actors:
            renderer.RemoveActor(actor)
        self.boundary_actors.clear()

        # Clear highlights
        self._clear_highlight_actors(renderer)

        # Clear pin markers
        for actor in self.pin_markers:
            renderer.RemoveActor(actor)
        self.pin_markers.clear()

        # Clear state
        self.current_polydata = None
        self.tessellation_result = None
        self.hovered_region_id = None
        self.selected_region_id = None
