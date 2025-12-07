"""
EvaluatorRenderer - Renders directly from SubDEvaluator

This is the SINGLE SOURCE OF TRUTH for visualization.
All display comes from evaluator queries - no disconnected meshes.

Architecture:
    SubDEvaluator → Analysis → EvaluatorRenderer → VTK Display

Pre-analysis: Samples exact SubD surface, colors by face
Post-analysis: Samples exact SubD surface, colors by region

The display IS the geometry. What you see = what was analyzed.
"""

from typing import List, Dict, Optional, Tuple, Set
import numpy as np

try:
    import cpp_core
except ImportError:
    cpp_core = None

# VTK imports through bridge
from app import vtk_bridge as vtk

from app.state.parametric_region import ParametricRegion


class EvaluatorRenderer:
    """
    Renders SubD surfaces directly from the evaluator.

    This replaces the old mesh-based display that was disconnected
    from the analysis. Now display = analysis = truth.

    Usage:
        renderer = EvaluatorRenderer(evaluator)

        # Pre-analysis: show SubD colored by face
        actors = renderer.render_subd()

        # Post-analysis: show regions
        actors = renderer.render_regions(analysis_results)

        # Picking
        region_id, face_id, u, v = renderer.pick(screen_x, screen_y, renderer_vtk)
    """

    # Default sampling density per face (samples_u x samples_v)
    DEFAULT_SAMPLES_PER_EDGE = 4

    def __init__(self, evaluator: 'cpp_core.SubDEvaluator'):
        """
        Initialize renderer with evaluator.

        Args:
            evaluator: Initialized SubDEvaluator (the source of truth)
        """
        if cpp_core is None:
            raise RuntimeError("cpp_core not available")

        if not evaluator.is_initialized():
            raise ValueError("Evaluator must be initialized")

        self.evaluator = evaluator
        self.current_regions: Optional[List[ParametricRegion]] = None

        # Cache for picking (maps VTK cell_id → (face_id, u, v))
        self._cell_to_param: Dict[int, Tuple[int, float, float]] = {}

        # Region lookup (maps face_id → region)
        self._face_to_region: Dict[int, ParametricRegion] = {}

    def render_subd(self,
                    samples_per_edge: int = DEFAULT_SAMPLES_PER_EDGE,
                    show_control_cage: bool = True) -> List:
        """
        Render exact SubD surface (pre-analysis mode).

        Samples the limit surface directly from evaluator.
        Colors faces by face_id for visual distinction.

        Args:
            samples_per_edge: Sample density per face edge
            show_control_cage: Include control cage wireframe

        Returns:
            List of VTK actors for rendering
        """
        self.current_regions = None
        self._face_to_region.clear()

        actors = []

        # Sample the exact surface
        polydata, self._cell_to_param = self._sample_surface(
            samples_per_edge=samples_per_edge,
            color_by='face'
        )

        # Create surface actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetScalarModeToUseCellData()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetInterpolationToFlat()
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.2)
        actor.GetProperty().SetLineWidth(0.5)

        actors.append(actor)

        # Add control cage wireframe
        if show_control_cage:
            cage_actor = self._create_control_cage_actor()
            if cage_actor:
                actors.append(cage_actor)

        return actors

    def render_regions(self,
                       regions: List[ParametricRegion],
                       samples_per_edge: int = DEFAULT_SAMPLES_PER_EDGE,
                       show_boundaries: bool = True) -> List:
        """
        Render analysis results (post-analysis mode).

        Samples the limit surface directly from evaluator.
        Colors by region membership - what you see IS the analysis.

        Args:
            regions: Analysis results (ParametricRegion objects)
            samples_per_edge: Sample density per face edge
            show_boundaries: Draw region boundaries

        Returns:
            List of VTK actors for rendering
        """
        self.current_regions = regions

        # Build face → region lookup
        self._face_to_region.clear()
        for region in regions:
            for face_id in region.faces:
                self._face_to_region[face_id] = region

        actors = []

        # Assign colors to regions
        region_colors = self._assign_region_colors(regions)

        # Sample the exact surface with region coloring
        polydata, self._cell_to_param = self._sample_surface(
            samples_per_edge=samples_per_edge,
            color_by='region',
            region_colors=region_colors
        )

        # Create surface actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetScalarModeToUseCellData()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetInterpolationToFlat()
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor(0.15, 0.15, 0.15)
        actor.GetProperty().SetLineWidth(0.5)

        actors.append(actor)

        # Add region boundaries
        if show_boundaries:
            boundary_actors = self._create_boundary_actors(regions)
            actors.extend(boundary_actors)

        return actors

    def _sample_surface(self,
                        samples_per_edge: int,
                        color_by: str = 'face',
                        region_colors: Optional[Dict[str, Tuple[int, int, int]]] = None
                        ) -> Tuple['vtk.vtkPolyData', Dict[int, Tuple[int, float, float]]]:
        """
        Sample exact limit surface from evaluator.

        Args:
            samples_per_edge: Samples per parametric edge
            color_by: 'face' or 'region'
            region_colors: Region ID → RGB color (0-255)

        Returns:
            (vtkPolyData, cell_to_param mapping)
        """
        num_faces = self.evaluator.get_control_face_count()

        # Generate (u, v) sample grid
        u_samples = np.linspace(0.0, 1.0, samples_per_edge + 1)
        v_samples = np.linspace(0.0, 1.0, samples_per_edge + 1)

        # Collect all sample points
        all_points = []
        all_normals = []
        all_quads = []  # (p0, p1, p2, p3) vertex indices
        all_colors = []  # RGB per cell
        cell_to_param = {}

        vertex_idx = 0
        cell_idx = 0

        for face_id in range(num_faces):
            # Determine color for this face
            if color_by == 'region' and face_id in self._face_to_region:
                region = self._face_to_region[face_id]
                color = region_colors.get(region.id, (200, 200, 200)) if region_colors else (200, 200, 200)
            else:
                # Color by face_id (hue rotation)
                hue = (face_id * 137.5) % 360  # Golden angle for good distribution
                color = self._hsv_to_rgb(hue / 360.0, 0.6, 0.85)

            # Sample grid on this face
            face_vertices = {}  # (i, j) → vertex index

            for i, u in enumerate(u_samples):
                for j, v in enumerate(v_samples):
                    # Evaluate exact limit surface
                    point, normal = self.evaluator.evaluate_limit(face_id, float(u), float(v))

                    all_points.append((point.x, point.y, point.z))
                    all_normals.append((normal.x, normal.y, normal.z))
                    face_vertices[(i, j)] = vertex_idx
                    vertex_idx += 1

            # Create quads from sample grid
            for i in range(samples_per_edge):
                for j in range(samples_per_edge):
                    # Quad corners
                    p0 = face_vertices[(i, j)]
                    p1 = face_vertices[(i + 1, j)]
                    p2 = face_vertices[(i + 1, j + 1)]
                    p3 = face_vertices[(i, j + 1)]

                    all_quads.append((p0, p1, p2, p3))
                    all_colors.append(color)

                    # Store parametric mapping for picking
                    # Use center of quad as representative point
                    u_center = (u_samples[i] + u_samples[i + 1]) / 2
                    v_center = (v_samples[j] + v_samples[j + 1]) / 2
                    cell_to_param[cell_idx] = (face_id, u_center, v_center)
                    cell_idx += 1

        # Build VTK polydata
        points = vtk.vtkPoints()
        for p in all_points:
            points.InsertNextPoint(*p)

        normals = vtk.vtkFloatArray()
        normals.SetNumberOfComponents(3)
        normals.SetName("Normals")
        for n in all_normals:
            normals.InsertNextTuple3(*n)

        cells = vtk.vtkCellArray()
        for quad in all_quads:
            q = vtk.vtkQuad()
            q.GetPointIds().SetId(0, quad[0])
            q.GetPointIds().SetId(1, quad[1])
            q.GetPointIds().SetId(2, quad[2])
            q.GetPointIds().SetId(3, quad[3])
            cells.InsertNextCell(q)

        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")
        for c in all_colors:
            colors.InsertNextTuple3(*c)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(cells)
        polydata.GetPointData().SetNormals(normals)
        polydata.GetCellData().SetScalars(colors)

        return polydata, cell_to_param

    def _create_control_cage_actor(self) -> Optional['vtk.vtkActor']:
        """Create wireframe actor for control cage."""
        # This would need access to the original control cage
        # For now, return None - can be added when we have cage access
        return None

    def _create_boundary_actors(self, regions: List[ParametricRegion]) -> List:
        """
        Create actors for region boundaries.

        Evaluates boundary curves on exact surface.
        """
        actors = []

        for region in regions:
            if not region.boundary:
                continue

            # Evaluate boundary curve on exact surface
            for curve in region.boundary:
                if not curve.points:
                    continue

                points = vtk.vtkPoints()
                for face_id, u, v in curve.points:
                    point = self.evaluator.evaluate_limit_point(face_id, float(u), float(v))
                    points.InsertNextPoint(point.x, point.y, point.z)

                # Create line
                lines = vtk.vtkCellArray()
                line = vtk.vtkPolyLine()
                line.GetPointIds().SetNumberOfIds(points.GetNumberOfPoints())
                for i in range(points.GetNumberOfPoints()):
                    line.GetPointIds().SetId(i, i)
                lines.InsertNextCell(line)

                polydata = vtk.vtkPolyData()
                polydata.SetPoints(points)
                polydata.SetLines(lines)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(polydata)

                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # White boundaries
                actor.GetProperty().SetLineWidth(2.0)

                actors.append(actor)

        return actors

    def _assign_region_colors(self, regions: List[ParametricRegion]) -> Dict[str, Tuple[int, int, int]]:
        """
        Assign distinct colors to regions.

        Uses curvature type metadata if available for semantic coloring.
        """
        colors = {}

        # Semantic colors by curvature type
        type_colors = {
            'elliptic': (100, 149, 237),    # Cornflower blue (bowl-like)
            'hyperbolic': (255, 127, 80),   # Coral (saddle-like)
            'parabolic': (144, 238, 144),   # Light green (cylindrical)
            'planar': (211, 211, 211),      # Light gray (flat)
        }

        # Count regions per type for shade variation
        type_counts: Dict[str, int] = {}

        for region in regions:
            curv_type = region.metadata.get('curvature_type', 'unknown')

            if curv_type in type_colors:
                # Use semantic color with slight variation
                base_color = type_colors[curv_type]
                count = type_counts.get(curv_type, 0)
                type_counts[curv_type] = count + 1

                # Vary brightness slightly for multiple regions of same type
                factor = 1.0 - (count * 0.1)
                factor = max(0.6, min(1.0, factor))

                color = tuple(int(c * factor) for c in base_color)
            else:
                # Fallback: hue rotation
                idx = len(colors)
                hue = (idx * 137.5) % 360
                color = self._hsv_to_rgb(hue / 360.0, 0.7, 0.8)

            colors[region.id] = color

        return colors

    def pick(self,
             screen_x: int,
             screen_y: int,
             renderer: 'vtk.vtkRenderer') -> Optional[Tuple[Optional[str], int, float, float]]:
        """
        Pick at screen coordinates, return parametric location.

        Args:
            screen_x, screen_y: Screen coordinates
            renderer: VTK renderer for picking

        Returns:
            (region_id, face_id, u, v) or None if no hit
            region_id is None in pre-analysis mode
        """
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.005)

        if picker.Pick(screen_x, screen_y, 0, renderer):
            cell_id = picker.GetCellId()

            if cell_id >= 0 and cell_id in self._cell_to_param:
                face_id, u, v = self._cell_to_param[cell_id]

                # Look up region if in post-analysis mode
                region_id = None
                if face_id in self._face_to_region:
                    region_id = self._face_to_region[face_id].id

                return (region_id, face_id, u, v)

        return None

    def get_region_at_face(self, face_id: int) -> Optional[ParametricRegion]:
        """Get region containing face_id, or None if pre-analysis."""
        return self._face_to_region.get(face_id)

    @staticmethod
    def _hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """Convert HSV to RGB (0-255)."""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))
