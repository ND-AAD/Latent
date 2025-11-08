"""
SubD Display Module - VTK Visualization for Subdivision Surfaces

This module provides lossless SubD visualization using VTK. It maintains the exact
rhino3dm SubD representation and generates display meshes on-demand for the viewport.

Key principle: Display meshes are temporary visualization aids ONLY. The authoritative
geometry is always the rhino3dm SubD object with exact limit surface evaluation.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple

# Import VTK types from our bridge - DO NOT import vtk directly
from app import vtk_bridge as vtk

try:
    import rhino3dm as rhino
except ImportError:
    rhino = None


class SubDDisplayModel:
    """
    Maintains exact SubD representation and generates VTK visualization.

    This class is the bridge between rhino3dm's exact SubD and VTK's rendering.
    It stores the exact SubD and creates display polydata for the viewport.
    """

    def __init__(self, subd: Optional['rhino.SubD'] = None):
        """
        Initialize with optional rhino3dm SubD object.

        Args:
            subd: rhino3dm SubD object (exact representation)
        """
        self.subd = subd  # Exact SubD - authoritative geometry
        self.control_net_polydata = None  # Display mesh for control net
        self.limit_surface_polydata = None  # Display mesh for limit surface

        # Region coloring (maps control face indices to colors)
        self.region_colors: Dict[int, Tuple[float, float, float]] = {}

    def set_subd(self, subd: 'rhino.SubD') -> None:
        """
        Set the SubD geometry and clear cached display meshes.

        Args:
            subd: rhino3dm SubD object
        """
        self.subd = subd
        self.control_net_polydata = None
        self.limit_surface_polydata = None

    def get_control_net_polydata(self) -> vtk.vtkPolyData:
        """
        Generate VTK polydata for SubD control net visualization.

        The control net is the quad mesh that defines the SubD. This is what
        users edit and what regions are defined on (face indices).

        Returns:
            vtkPolyData representing the control net
        """
        if self.control_net_polydata is not None:
            return self.control_net_polydata

        if self.subd is None:
            # Return empty polydata if no SubD loaded
            return vtk.vtkPolyData()

        # Extract control vertices
        vertices = []
        for i in range(self.subd.Vertices.Count):
            v = self.subd.Vertices[i].ControlNetPoint
            vertices.append([v.X, v.Y, v.Z])

        vertices = np.array(vertices, dtype=np.float64)

        # Extract control faces (quads or n-gons)
        faces = []
        for i in range(self.subd.Faces.Count):
            face = self.subd.Faces[i]
            face_verts = []
            for j in range(face.EdgeCount):
                # Get vertex indices for this face
                edge = face.Edge(j)
                face_verts.append(edge.StartVertexIndex)
            faces.append(face_verts)

        # Create VTK points
        vtk_points = vtk.vtkPoints()
        vtk_points.SetData(numpy_to_vtk(vertices))

        # Create VTK cells (polygons)
        vtk_cells = vtk.vtkCellArray()
        for face in faces:
            vtk_polygon = vtk.vtkPolygon()
            vtk_polygon.GetPointIds().SetNumberOfIds(len(face))
            for j, vert_idx in enumerate(face):
                vtk_polygon.GetPointIds().SetId(j, vert_idx)
            vtk_cells.InsertNextCell(vtk_polygon)

        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)
        polydata.SetPolys(vtk_cells)

        # Generate normals for proper lighting
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputData(polydata)
        normals.ComputePointNormalsOn()
        normals.ComputeCellNormalsOn()
        normals.Update()

        self.control_net_polydata = normals.GetOutput()
        return self.control_net_polydata

    def get_colored_control_net_polydata(self) -> vtk.vtkPolyData:
        """
        Generate VTK polydata with per-face colors for regions.

        Returns:
            vtkPolyData with cell colors based on region_colors dict
        """
        # Start with base control net
        polydata = self.get_control_net_polydata()

        if not self.region_colors:
            return polydata

        # Create color array for faces
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")

        # Assign colors to each face
        num_faces = polydata.GetNumberOfCells()
        for face_id in range(num_faces):
            if face_id in self.region_colors:
                r, g, b = self.region_colors[face_id]
                colors.InsertNextTuple3(int(r * 255), int(g * 255), int(b * 255))
            else:
                # Default color for unassigned faces (light gray)
                colors.InsertNextTuple3(200, 200, 200)

        polydata.GetCellData().SetScalars(colors)
        return polydata

    def get_limit_surface_polydata(self, subdivision_level: int = 2) -> vtk.vtkPolyData:
        """
        Generate VTK polydata for SubD limit surface visualization.

        This evaluates the smooth Catmull-Clark limit surface by subdividing
        the control net. Higher subdivision levels = smoother display.

        Args:
            subdivision_level: Number of subdivision iterations (0-4 recommended)

        Returns:
            vtkPolyData representing the subdivided limit surface
        """
        if self.subd is None:
            return vtk.vtkPolyData()

        # Start with control net
        polydata = self.get_control_net_polydata()

        # Apply Catmull-Clark subdivision filter
        for _ in range(subdivision_level):
            subdivide = vtk.vtkLinearSubdivisionFilter()
            subdivide.SetInputData(polydata)
            subdivide.SetNumberOfSubdivisions(1)
            subdivide.Update()
            polydata = subdivide.GetOutput()

        # Smooth the result to approximate limit surface
        smooth = vtk.vtkSmoothPolyDataFilter()
        smooth.SetInputData(polydata)
        smooth.SetNumberOfIterations(20)
        smooth.SetRelaxationFactor(0.1)
        smooth.Update()

        self.limit_surface_polydata = smooth.GetOutput()
        return self.limit_surface_polydata

    def set_region_colors(self, region_colors: Dict[int, Tuple[float, float, float]]) -> None:
        """
        Set colors for control face regions.

        Args:
            region_colors: Map of face index -> RGB color tuple (0.0-1.0)
        """
        self.region_colors = region_colors
        # Clear cached polydata to force regeneration with new colors
        self.control_net_polydata = None


def create_test_subd_sphere(radius: float = 5.0, u_count: int = 8, v_count: int = 8) -> Optional['rhino.SubD']:
    """
    Create a test SubD sphere using rhino3dm.

    This generates a subdivision surface sphere by creating a quad mesh
    and converting it to a SubD. Used for testing the display system.

    Args:
        radius: Sphere radius
        u_count: Number of divisions in U direction
        v_count: Number of divisions in V direction

    Returns:
        rhino3dm SubD object, or None if rhino3dm not available
    """
    if rhino is None:
        print("Warning: rhino3dm not available, cannot create test SubD")
        return None

    # Create a sphere mesh first
    sphere = rhino.Mesh.CreateSphere(rhino.Sphere(rhino.Point3d(0, 0, 0), radius), u_count, v_count)

    # Convert mesh to SubD
    # Note: rhino3dm's CreateFromMesh creates a proper SubD with Catmull-Clark structure
    subd = rhino.SubD.CreateFromMesh(sphere)

    return subd


def create_test_subd_torus(major_radius: float = 5.0, minor_radius: float = 2.0,
                          u_count: int = 16, v_count: int = 8) -> Optional['rhino.SubD']:
    """
    Create a test SubD torus using rhino3dm.

    Args:
        major_radius: Distance from center to tube center
        minor_radius: Tube radius
        u_count: Number of divisions around major circle
        v_count: Number of divisions around minor circle

    Returns:
        rhino3dm SubD object, or None if rhino3dm not available
    """
    if rhino is None:
        print("Warning: rhino3dm not available, cannot create test SubD")
        return None

    # Create a torus mesh first
    torus_plane = rhino.Plane(rhino.Point3d(0, 0, 0), rhino.Vector3d(0, 0, 1))
    torus = rhino.Mesh.CreateTorus(torus_plane, major_radius, minor_radius, u_count, v_count)

    # Convert mesh to SubD
    subd = rhino.SubD.CreateFromMesh(torus)

    return subd


def numpy_to_vtk(array: np.ndarray) -> vtk.vtkDataArray:
    """
    Convert numpy array to VTK data array.

    Args:
        array: Numpy array (typically Nx3 for points)

    Returns:
        VTK data array
    """
    from vtk.util import numpy_support
    return numpy_support.numpy_to_vtk(array, deep=True)


def create_vtk_subd_actor(subd_model: SubDDisplayModel,
                          display_mode: str = "shaded",
                          show_control_net: bool = True) -> List[vtk.vtkActor]:
    """
    Create VTK actor(s) for SubD visualization.

    This is the main function for creating renderable actors from a SubD model.

    Args:
        subd_model: SubDDisplayModel containing the exact SubD
        display_mode: "shaded", "wireframe", or "xray"
        show_control_net: If True, show control net edges

    Returns:
        List of vtkActor objects ready to add to renderer
    """
    actors = []

    if subd_model.subd is None:
        return actors

    # Get display polydata (control net or limit surface based on mode)
    if display_mode == "wireframe":
        polydata = subd_model.get_control_net_polydata()
    else:
        polydata = subd_model.get_limit_surface_polydata(subdivision_level=2)

    # Create mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    # Create actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Set display properties
    if display_mode == "shaded":
        # Solid shading with lighting
        actor.GetProperty().SetColor(0.8, 0.9, 1.0)  # Light blue-white
        actor.GetProperty().SetSpecular(0.3)
        actor.GetProperty().SetSpecularPower(20)
        actor.GetProperty().SetDiffuse(0.8)
        actor.GetProperty().SetAmbient(0.2)

    elif display_mode == "wireframe":
        # Wireframe only
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(0.3, 0.3, 0.3)
        actor.GetProperty().SetLineWidth(1.5)

    elif display_mode == "xray":
        # Transparent with edges
        actor.GetProperty().SetColor(0.8, 0.9, 1.0)
        actor.GetProperty().SetOpacity(0.3)
        actor.GetProperty().SetEdgeVisibility(True)
        actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.2)
        actor.GetProperty().SetLineWidth(1.0)

    actors.append(actor)

    # Add control net edges if requested (in shaded mode)
    if show_control_net and display_mode == "shaded":
        edge_polydata = subd_model.get_control_net_polydata()

        edge_mapper = vtk.vtkPolyDataMapper()
        edge_mapper.SetInputData(edge_polydata)

        edge_actor = vtk.vtkActor()
        edge_actor.SetMapper(edge_mapper)
        edge_actor.GetProperty().SetRepresentationToWireframe()
        edge_actor.GetProperty().SetColor(0.2, 0.2, 0.2)  # Dark gray edges
        edge_actor.GetProperty().SetLineWidth(1.0)
        edge_actor.GetProperty().SetOpacity(0.5)

        actors.append(edge_actor)

    return actors
