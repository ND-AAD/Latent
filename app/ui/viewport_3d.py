"""
3D Viewport Widget - VTK Implementation with Rhino-Compatible Controls
Displays SubD geometry with control net and limit surface evaluation

Navigation Controls (matching Rhino 8 standard):
- LEFT click/drag: Select objects (window/crossing selection)
- RIGHT drag: Rotate/orbit view
- Shift + RIGHT drag: Pan view
- Ctrl + RIGHT drag: Zoom in/out
- Mouse wheel: Zoom in/out
- Space: Reset camera to default view

This implementation exactly matches Rhino's viewport behavior with left click
reserved for selection and right click for camera manipulation.

Selection Colors (TODO: move to application preferences):
- Faces, Edges, Vertices: Yellow (1.0, 1.0, 0.0) for consistency
- Future: User-configurable via preferences dialog
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction
import sys
import os

# Import VTK types from our bridge - DO NOT import vtk directly
from app import vtk_bridge as vtk

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.geometry.subd_display import SubDDisplayManager


class Viewport3D(QWidget):
    """3D viewport for displaying SubD geometry and regions using VTK"""

    # Signals
    region_clicked = pyqtSignal(str)
    boundary_point_moved = pyqtSignal(int, object)
    debug_message = pyqtSignal(str)  # Signal for debug messages
    view_changed = pyqtSignal(object)  # Signal when view type changes

    def __init__(self):
        super().__init__()

        # VTK components
        self.vtk_widget = None
        self.renderer = None
        self.render_window = None
        self.interactor = None

        # Geometry actors
        self.geometry_actor = None
        self.axes_actor = None
        self.grid_actor = None

        # Region display
        self.region_actors = {}

        # Edit mode support
        self.edit_mode = None
        self.picker = None
        self.highlight_manager = None
        self.current_polydata = None
        self.current_subd = None

        # Selection tracking
        self.selected_faces = set()  # Track multiple selected faces
        self.selected_edges = set()
        self.selected_vertices = set()

        # SubD display manager
        self.subd_display = SubDDisplayManager()
        self.subd_actors = []

        # Viewport info
        self.view_label = None
        self.view_type = None
        self.is_active = False

        self.init_ui()

    def log_debug(self, message):
        """Emit debug message signal"""
        self.debug_message.emit(message)

    def init_ui(self):
        """Initialize the VTK-based UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Add viewport label at the top
        self.view_label = QLabel("Perspective")
        self.view_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 4px;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.view_label)

        # Create VTK widget (from bridge)
        self.vtk_widget = vtk.QVTKWidget(self)
        layout.addWidget(self.vtk_widget)

        # Setup VTK pipeline
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.1, 0.1, 0.15)  # Dark blue-gray background

        self.render_window = self.vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)

        self.interactor = self.render_window.GetInteractor()

        # Add axes helper
        self.add_axes_helper()

        # Add grid plane
        self.add_grid_plane()

        # Initialize the interactor FIRST
        self.interactor.Initialize()

        # CRITICAL: Create and set camera controls AFTER Initialize()
        # because VTK replaces the style with vtkInteractorStyleSwitch during Initialize()
        self.interactor_style = vtk.create_interactor_style(self.renderer, self.interactor)
        self.interactor.SetInteractorStyle(self.interactor_style)

        self.log_debug("✅ Camera controls from vtk_bridge initialized")
        self.log_debug("📍 Controls: LEFT=Select, RIGHT=Rotate, MIDDLE=Pan, Shift+RIGHT=Pan, Wheel=Zoom")

        # Initialize picking system
        self._init_picking_system()

        # Set initial edit mode (SOLID) - this ensures pick callback is set up
        from app.state.edit_mode import EditMode
        self.set_edit_mode(EditMode.SOLID)
        self.log_debug("✅ Initial edit mode set to SOLID")

    def add_axes_helper(self):
        """Add XYZ axes indicator"""
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(1.0, 1.0, 1.0)
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.02)

        # Add axes to corner widget
        widget = vtk.vtkOrientationMarkerWidget()
        widget.SetOrientationMarker(axes)
        widget.SetInteractor(self.interactor)
        widget.SetViewport(0.0, 0.0, 0.2, 0.2)
        widget.EnabledOn()
        widget.InteractiveOff()

        self.axes_actor = axes

    def add_grid_plane(self):
        """Add XY grid plane at Z=0"""
        # Create grid plane
        plane = vtk.vtkPlaneSource()
        plane.SetOrigin(-5.0, -5.0, 0.0)
        plane.SetPoint1(5.0, -5.0, 0.0)
        plane.SetPoint2(-5.0, 5.0, 0.0)
        plane.SetXResolution(10)
        plane.SetYResolution(10)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane.GetOutputPort())

        # Create actor
        self.grid_actor = vtk.vtkActor()
        self.grid_actor.SetMapper(mapper)
        self.grid_actor.GetProperty().SetRepresentationToWireframe()
        self.grid_actor.GetProperty().SetColor(0.3, 0.3, 0.3)
        self.grid_actor.GetProperty().SetOpacity(0.5)

        self.renderer.AddActor(self.grid_actor)

    def create_test_cube(self):
        """Create a test cube for initial testing (Day 2-3 deliverable)"""
        # Create cube
        cube = vtk.vtkCubeSource()
        cube.SetXLength(2.0)
        cube.SetYLength(2.0)
        cube.SetZLength(2.0)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.8, 0.8, 0.9)  # Light blue-gray
        actor.GetProperty().SetOpacity(0.8)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.3)

        # Add to renderer
        if self.geometry_actor:
            self.renderer.RemoveActor(self.geometry_actor)

        self.geometry_actor = actor
        self.renderer.AddActor(actor)

        # Reset camera to view cube
        self.reset_camera()
        self.render_window.Render()

    def create_test_subd_sphere(self):
        """Create and display a test SubD sphere (Day 4 deliverable)"""
        # Create test SubD sphere
        subd = create_test_subd_sphere(radius=5.0, u_count=8, v_count=8)

        if subd is None:
            print("Error: Could not create test SubD (rhino3dm not available)")
            return

        # Set the SubD model
        self.subd_model.set_subd(subd)

        # Clear existing SubD actors
        for actor in self.subd_actors:
            self.renderer.RemoveActor(actor)
        self.subd_actors.clear()

        # Create new actors
        actors = create_vtk_subd_actor(self.subd_model, display_mode="shaded", show_control_net=True)

        # Add to renderer
        for actor in actors:
            self.renderer.AddActor(actor)
            self.subd_actors.append(actor)

        # Reset camera to view geometry
        self.reset_camera()
        self.render_window.Render()

        print(f"Displayed SubD sphere: {subd.Vertices.Count} control vertices, {subd.Faces.Count} control faces")

    def create_test_subd_torus(self):
        """Create and display a test SubD torus (Day 4 deliverable)"""
        # Create test SubD torus
        subd = create_test_subd_torus(major_radius=5.0, minor_radius=2.0, u_count=16, v_count=8)

        if subd is None:
            print("Error: Could not create test SubD (rhino3dm not available)")
            return

        # Set the SubD model
        self.subd_model.set_subd(subd)

        # Clear existing SubD actors
        for actor in self.subd_actors:
            self.renderer.RemoveActor(actor)
        self.subd_actors.clear()

        # Create new actors
        actors = create_vtk_subd_actor(self.subd_model, display_mode="shaded", show_control_net=True)

        # Add to renderer
        for actor in actors:
            self.renderer.AddActor(actor)
            self.subd_actors.append(actor)

        # Reset camera to view geometry
        self.reset_camera()
        self.render_window.Render()

        print(f"Displayed SubD torus: {subd.Vertices.Count} control vertices, {subd.Faces.Count} control faces")

    def display_subd(self, geometry_data):
        """
        Display SubD geometry from Rhino

        Args:
            geometry_data: SubDGeometry with exact SubD representation from Rhino bridge
        """
        if not geometry_data:
            return

        # Check if this is the same geometry we already have (prevent re-rendering)
        if hasattr(self, 'current_subd') and self.current_subd:
            if (geometry_data.vertex_count == self.current_subd.vertex_count and
                geometry_data.face_count == self.current_subd.face_count and
                geometry_data.edge_count == self.current_subd.edge_count):
                # Same geometry, no need to re-render
                return

        # Store reference to SubD
        self.current_subd = geometry_data

        # Debug: Check what we received
        print(f"🔍 Geometry data type: {type(geometry_data)}")
        print(f"🔍 Has mesh_data attr: {hasattr(geometry_data, 'mesh_data')}")
        if hasattr(geometry_data, 'mesh_data'):
            print(f"🔍 mesh_data is None: {geometry_data.mesh_data is None}")
            if geometry_data.mesh_data:
                print(f"🔍 mesh_data keys: {list(geometry_data.mesh_data.keys())}")

        # Check if we have actual mesh data from the server
        polydata = None
        if hasattr(geometry_data, 'mesh_data') and geometry_data.mesh_data:
            print("✅ Using actual mesh data from Rhino")
            polydata = self._create_mesh_from_data(geometry_data.mesh_data)

        # Fallback to placeholder if no mesh data
        if not polydata:
            print("⚠️ Using placeholder geometry (no mesh_data)")
            polydata = self._create_basic_mesh_from_counts(
                geometry_data.vertex_count,
                geometry_data.face_count
            )

        if not polydata:
            print("Warning: Failed to create display geometry")
            return

        print(f"Display mesh ready: {geometry_data.vertex_count} vertices, {geometry_data.face_count} faces")

        # Store polydata for picking
        self.current_polydata = polydata

        # If we're in Edge mode, update the edge picker with new geometry
        from app.state.edit_mode import EditMode
        if self.edit_mode == EditMode.EDGE and self.picker:
            print("🔄 Updating edge picker with new geometry")
            self.picker.setup_edge_extraction(polydata)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        # Create actor
        if self.geometry_actor:
            self.renderer.RemoveActor(self.geometry_actor)

        self.geometry_actor = vtk.vtkActor()
        self.geometry_actor.SetMapper(mapper)
        self.geometry_actor.GetProperty().SetColor(0.8, 0.8, 0.9)
        self.geometry_actor.GetProperty().SetOpacity(0.9)
        self.geometry_actor.GetProperty().EdgeVisibilityOn()
        self.geometry_actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.3)

        self.renderer.AddActor(self.geometry_actor)

        # Reset camera to view geometry
        self.reset_camera()
        self.render_window.Render()

    def _create_control_net_polydata(self, subd_model):
        """
        Create VTK polydata from SubD control net

        Args:
            subd_model: SubDModel with exact SubD representation

        Returns:
            vtkPolyData representing control net
        """
        # TODO: Once rhino3dm is installed, extract control net from SubD
        # For now, create placeholder
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()

        # Add example vertices (will be replaced with actual SubD control vertices)
        for i in range(8):
            x = (i % 2) - 0.5
            y = ((i // 2) % 2) - 0.5
            z = (i // 4) - 0.5
            points.InsertNextPoint(x, y, z)

        # Add example faces (will be replaced with actual SubD control faces)
        # Bottom face
        quad = vtk.vtkQuad()
        quad.GetPointIds().SetId(0, 0)
        quad.GetPointIds().SetId(1, 1)
        quad.GetPointIds().SetId(2, 3)
        quad.GetPointIds().SetId(3, 2)
        polys.InsertNextCell(quad)

        # Top face
        quad = vtk.vtkQuad()
        quad.GetPointIds().SetId(0, 4)
        quad.GetPointIds().SetId(1, 5)
        quad.GetPointIds().SetId(2, 7)
        quad.GetPointIds().SetId(3, 6)
        polys.InsertNextCell(quad)

        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(polys)

        return polydata

    def display_regions(self, regions):
        """
        Display regions with distinct colors on SubD control faces

        Args:
            regions: List of ParametricRegion objects with .faces and .color attributes
        """
        if not regions:
            return

        # Build color map: face_id -> color
        region_colors = {}
        for region in regions:
            color = getattr(region, 'color', (0.8, 0.8, 0.9))  # Default light blue
            for face_id in region.faces:
                region_colors[face_id] = color

        # Update SubD model with colors
        if not hasattr(self, 'subd_model') or self.subd_model is None:
            self.log_debug("⚠️ No SubD model loaded, skipping region display")
            return
        self.subd_model.set_region_colors(region_colors)

        # Clear existing SubD actors
        for actor in self.subd_actors:
            self.renderer.RemoveActor(actor)
        self.subd_actors.clear()

        # Create colored polydata
        polydata = self.subd_model.get_colored_control_net_polydata()

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor(0.2, 0.2, 0.2)

        # Add to renderer
        self.renderer.AddActor(actor)
        self.subd_actors.append(actor)

        # Render
        self.render_window.Render()

        print(f"Displayed {len(regions)} regions with colors")

    def create_test_colored_cube(self):
        """Create a test cube with colored faces (Day 5 deliverable)"""
        # Create cube
        cube = vtk.vtkCubeSource()
        cube.SetXLength(4.0)
        cube.SetYLength(4.0)
        cube.SetZLength(4.0)
        cube.Update()

        polydata = cube.GetOutput()

        # Create colors for each face (6 faces on a cube)
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)
        colors.SetName("Colors")

        # Define distinct colors for each face (simulating regions)
        face_colors = [
            (255, 100, 100),  # Red - Region 1
            (100, 255, 100),  # Green - Region 2
            (100, 100, 255),  # Blue - Region 3
            (255, 255, 100),  # Yellow - Region 4
            (255, 100, 255),  # Magenta - Region 5
            (100, 255, 255),  # Cyan - Region 6
        ]

        for color in face_colors:
            colors.InsertNextTuple3(*color)

        polydata.GetCellData().SetScalars(colors)

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        actor.GetProperty().SetEdgeColor(0.0, 0.0, 0.0)

        # Clear and add
        if self.geometry_actor:
            self.renderer.RemoveActor(self.geometry_actor)

        self.geometry_actor = actor
        self.renderer.AddActor(actor)

        # Reset camera
        self.reset_camera()
        self.render_window.Render()

        print("Displayed colored cube - 6 regions with distinct colors")

    def highlight_region(self, region_id):
        """
        Highlight a region (for selection)

        Args:
            region_id: ID of region to highlight
        """
        # TODO: Implement region highlighting
        # Change color/opacity of selected region
        pass

    def update_region_display(self, region_id, pinned=False):
        """
        Update region display (e.g., when pinned/unpinned)

        Args:
            region_id: ID of region to update
            pinned: Whether region is now pinned
        """
        # TODO: Visual indication of pinned state
        # Could use different color, outline, or icon
        pass

    def enable_boundary_editing(self, region_id):
        """
        Enable boundary editing mode for a region

        Args:
            region_id: ID of region to edit
        """
        # TODO: Implement boundary editing
        # This will be part of Edit Mode system (Week 4)
        pass


    def set_view_type(self, view_type):
        """Set the view type and update the label"""
        self.view_type = view_type
        if self.view_label:
            self.view_label.setText(str(view_type.value if hasattr(view_type, 'value') else view_type))

    def set_active(self, is_active):
        """Set whether this viewport is active"""
        self.is_active = is_active
        if is_active:
            self.setStyleSheet("border: 2px solid #4CAF50;")  # Green border for active
            if self.view_label:
                self.view_label.setStyleSheet("""
                    QLabel {
                        background-color: #4CAF50;
                        color: #ffffff;
                        padding: 4px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)
        else:
            self.setStyleSheet("border: 1px solid #333333;")  # Dark border for inactive
            if self.view_label:
                self.view_label.setStyleSheet("""
                    QLabel {
                        background-color: #2b2b2b;
                        color: #ffffff;
                        padding: 4px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)

    def reset_camera(self):
        """Reset camera to view all geometry"""
        self.renderer.ResetCamera()

        # Set a nice viewing angle
        camera = self.renderer.GetActiveCamera()
        camera.Elevation(30)
        camera.Azimuth(45)
        self.renderer.ResetCameraClippingRange()

        self.render_window.Render()

    def contextMenuEvent(self, event):
        """
        Context menu disabled to prevent conflict with VTK right-click orbit.
        Use View menu in menu bar to change view types instead.
        """
        # Don't show context menu - let VTK handle right-click for camera control
        pass

    def change_view(self, view_name):
        """Request view change (to be handled by layout manager)"""
        self.view_changed.emit(view_name)

    def _convert_rhino3dm_to_vtk(self, subd):
        """
        Convert rhino3dm SubD to VTK polydata

        Args:
            subd: rhino3dm.SubD object

        Returns:
            vtkPolyData
        """
        try:
            import rhino3dm

            points = vtk.vtkPoints()
            polys = vtk.vtkCellArray()

            # Try to get mesh representation from SubD
            # rhino3dm SubD objects have limited API, so we'll create a simple mesh
            # based on the vertex and face counts we know

            # For now, convert SubD to a mesh representation
            # This is a display approximation only - the exact SubD is preserved elsewhere
            if hasattr(subd, 'ToBrep'):
                # Try to convert to Brep then mesh
                brep = subd.ToBrep()
                if brep:
                    # Create mesh from brep
                    mesh_params = rhino3dm.MeshingParameters()
                    meshes = brep.CreateMesh(mesh_params)
                    if meshes and len(meshes) > 0:
                        mesh = meshes[0]

                        # Add vertices
                        for i in range(mesh.Vertices.Count):
                            v = mesh.Vertices[i]
                            points.InsertNextPoint(v.X, v.Y, v.Z)

                        # Add faces
                        for i in range(mesh.Faces.Count):
                            face = mesh.Faces[i]
                            if face.IsQuad:
                                quad = vtk.vtkQuad()
                                quad.GetPointIds().SetId(0, face[0])
                                quad.GetPointIds().SetId(1, face[1])
                                quad.GetPointIds().SetId(2, face[2])
                                quad.GetPointIds().SetId(3, face[3])
                                polys.InsertNextCell(quad)
                            else:
                                tri = vtk.vtkTriangle()
                                tri.GetPointIds().SetId(0, face[0])
                                tri.GetPointIds().SetId(1, face[1])
                                tri.GetPointIds().SetId(2, face[2])
                                polys.InsertNextCell(tri)

                        polydata = vtk.vtkPolyData()
                        polydata.SetPoints(points)
                        polydata.SetPolys(polys)
                        return polydata

            # If conversion fails, return None and we'll use placeholder
            return None

        except Exception as e:
            print(f"Error converting rhino3dm SubD to VTK: {e}")
            return None

    def _create_mesh_from_data(self, mesh_data):
        """
        Create VTK polydata from mesh data received from Rhino

        Args:
            mesh_data: Dictionary with 'vertices' and 'faces' arrays

        Returns:
            vtkPolyData or None if creation fails
        """
        try:
            vertices = mesh_data.get('vertices', [])
            faces = mesh_data.get('faces', [])

            if not vertices or not faces:
                print("No vertex or face data in mesh_data")
                return None

            # Create VTK points
            points = vtk.vtkPoints()
            for vertex in vertices:
                points.InsertNextPoint(vertex[0], vertex[1], vertex[2])

            # Create VTK cells (faces)
            polys = vtk.vtkCellArray()
            for face in faces:
                if len(face) == 4:  # Quad
                    quad = vtk.vtkQuad()
                    for i in range(4):
                        quad.GetPointIds().SetId(i, face[i])
                    polys.InsertNextCell(quad)
                elif len(face) == 3:  # Triangle
                    tri = vtk.vtkTriangle()
                    for i in range(3):
                        tri.GetPointIds().SetId(i, face[i])
                    polys.InsertNextCell(tri)

            # Create polydata
            polydata = vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetPolys(polys)

            # Add normals if provided
            if 'normals' in mesh_data and mesh_data['normals']:
                normals_array = vtk.vtkFloatArray()
                normals_array.SetNumberOfComponents(3)
                normals_array.SetName("Normals")

                for normal in mesh_data['normals']:
                    normals_array.InsertNextTuple3(normal[0], normal[1], normal[2])

                polydata.GetPointData().SetNormals(normals_array)
            else:
                # Compute normals if not provided
                normal_generator = vtk.vtkPolyDataNormals()
                normal_generator.SetInputData(polydata)
                normal_generator.ComputePointNormalsOn()
                normal_generator.ComputeCellNormalsOn()
                normal_generator.Update()
                polydata = normal_generator.GetOutput()

            print(f"Created VTK mesh: {points.GetNumberOfPoints()} vertices, {polys.GetNumberOfCells()} faces")
            return polydata

        except Exception as e:
            print(f"Error creating mesh from data: {e}")
            return None

    def _create_basic_mesh_from_counts(self, vertex_count, face_count):
        """
        Create a display mesh as placeholder when we can't decode the SubD

        This creates a parametric surface that gives a sense of the complexity
        of the actual SubD, even though it's not the exact shape.

        Args:
            vertex_count: Number of vertices (for display)
            face_count: Number of faces (for display)

        Returns:
            vtkPolyData
        """
        # Determine complexity based on vertex count
        if vertex_count < 100:
            # Simple object - use a torus
            source = vtk.vtkParametricTorus()
            source.SetRingRadius(3.0)
            source.SetCrossSectionRadius(1.0)
        elif vertex_count < 500:
            # Medium complexity - use a more complex torus
            source = vtk.vtkParametricTorus()
            source.SetRingRadius(4.0)
            source.SetCrossSectionRadius(1.5)
        else:
            # High complexity - use a Klein bottle or similar
            source = vtk.vtkParametricBoy()

        # Create parametric function source
        param_source = vtk.vtkParametricFunctionSource()
        param_source.SetParametricFunction(source)

        # Set resolution based on face count
        if face_count < 100:
            param_source.SetUResolution(20)
            param_source.SetVResolution(20)
        elif face_count < 500:
            param_source.SetUResolution(30)
            param_source.SetVResolution(30)
        else:
            param_source.SetUResolution(40)
            param_source.SetVResolution(40)

        param_source.Update()

        # Add text annotation showing actual counts
        print(f"📦 Display placeholder for SubD: {vertex_count} vertices, {face_count} faces")
        print(f"   (Exact SubD data preserved for analysis)")

        return param_source.GetOutput()

    def _init_picking_system(self):
        """Initialize the picking system for edit modes"""
        from app.ui.picker import HighlightManager
        self.highlight_manager = HighlightManager(self.renderer)

    def set_edit_mode(self, mode):
        """
        Set the edit mode for this viewport

        Args:
            mode: EditMode enum value
        """
        from app.state.edit_mode import EditMode
        from app.ui.pickers import SubDFacePicker, SubDEdgePicker, SubDVertexPicker

        self.edit_mode = mode

        # Clean up existing picker
        if self.picker:
            if hasattr(self.picker, 'cleanup'):
                self.picker.cleanup()
            self.picker = None

        # Clear highlights
        if self.highlight_manager:
            self.highlight_manager.clear_highlights()

        # Create appropriate picker
        if mode == EditMode.PANEL:
            self.picker = SubDFacePicker(self.renderer, self.render_window)
            # Make main geometry pickable in panel mode
            if self.geometry_actor:
                self.geometry_actor.PickableOn()
            # Connect our custom pick handler to interactor style
            self.interactor_style.SetPickCallback(self._handle_face_pick)
            self.log_debug("✅ Panel selection mode activated (face picking enabled)")

        elif mode == EditMode.EDGE:
            self.picker = SubDEdgePicker(self.renderer, self.render_window)
            if self.current_polydata:
                print(f"🔧 Setting up edge extraction with {self.current_polydata.GetNumberOfPoints()} points")
                self.picker.setup_edge_extraction(self.current_polydata)
            else:
                print("⚠️ No polydata available for edge extraction yet")
            # Make main geometry non-pickable in edge mode
            if self.geometry_actor:
                self.geometry_actor.PickableOff()
            # Connect our custom pick handler to interactor style
            self.interactor_style.SetPickCallback(self._handle_edge_pick)
            self.log_debug("✅ Edge selection mode activated (edge picking enabled)")

        elif mode == EditMode.VERTEX:
            self.picker = SubDVertexPicker(self.renderer, self.render_window)
            # Setup vertex sphere rendering if we have polydata
            if self.current_polydata:
                print(f"🔧 Setting up vertex rendering with {self.current_polydata.GetNumberOfPoints()} vertices")
                self.picker.setup_vertex_rendering(self.current_polydata)
            else:
                print("⚠️ No polydata available for vertex rendering yet")
            # Make main geometry pickable in vertex mode
            if self.geometry_actor:
                self.geometry_actor.PickableOn()
            # Connect our custom pick handler to interactor style
            self.interactor_style.SetPickCallback(self._handle_vertex_pick)
            self.log_debug("✅ Vertex selection mode activated (vertex picking enabled)")

        else:  # SOLID mode
            # Disable picking in solid mode (view-only)
            self.interactor_style.SetPickCallback(None)
            # Make main geometry pickable (even though we won't handle picks)
            if self.geometry_actor:
                self.geometry_actor.PickableOn()
            self.log_debug("✅ Solid mode activated (view-only, no selection)")

        self.render_window.Render()

    def _handle_face_pick(self, x: int, y: int, add_to_selection: bool = False):
        """
        Handle face picking with multi-select support

        Args:
            x, y: Screen coordinates
            add_to_selection: If True (Shift held), add to selection
        """
        if not self.picker:
            return

        # Perform the pick
        face_id = self.picker.pick(x, y, add_to_selection)

        if face_id is not None and face_id >= 0:
            # Update selection set
            if add_to_selection:
                # Toggle face in selection
                if face_id in self.selected_faces:
                    self.selected_faces.remove(face_id)
                    print(f"   ➖ Removed face {face_id} from selection (now {len(self.selected_faces)} selected)")
                else:
                    self.selected_faces.add(face_id)
                    print(f"   ➕ Added face {face_id} to selection (now {len(self.selected_faces)} selected)")
            else:
                # Replace selection
                self.selected_faces = {face_id}
                print(f"   🔄 New selection: face {face_id}")

            # Update highlight to show all selected faces
            if self.highlight_manager and self.current_polydata:
                self.highlight_manager.highlight_faces(
                    self.current_polydata,
                    list(self.selected_faces),
                    color=(1.0, 1.0, 0.0)  # Yellow
                )
                self.highlight_manager.update_display()
                print(f"   ✅ Highlighting {len(self.selected_faces)} faces")

    def _handle_edge_pick(self, x: int, y: int, add_to_selection: bool = False):
        """
        Handle edge picking with multi-select support

        Args:
            x, y: Screen coordinates
            add_to_selection: If True (Shift held), add to selection
        """
        if not self.picker:
            return

        # Perform the pick
        edge_id = self.picker.pick(x, y, add_to_selection)

        if edge_id is not None and edge_id >= 0:
            # Update selection set
            if add_to_selection:
                # Toggle edge in selection
                if edge_id in self.selected_edges:
                    self.selected_edges.remove(edge_id)
                    print(f"   ➖ Removed edge {edge_id} from selection (now {len(self.selected_edges)} selected)")
                else:
                    self.selected_edges.add(edge_id)
                    print(f"   ➕ Added edge {edge_id} to selection (now {len(self.selected_edges)} selected)")
            else:
                # Replace selection
                self.selected_edges = {edge_id}
                print(f"   🔄 New selection: edge {edge_id}")

            # Update highlight to show all selected edges
            if self.highlight_manager and self.current_polydata:
                self.highlight_manager.highlight_edges(
                    self.current_polydata,
                    list(self.selected_edges),
                    color=(1.0, 1.0, 0.0)  # Yellow (matches face selection)
                )
                self.highlight_manager.update_display()
                print(f"   ✅ Highlighting {len(self.selected_edges)} edges")

    def _handle_vertex_pick(self, x: int, y: int, add_to_selection: bool = False):
        """
        Handle vertex picking with multi-select support

        Args:
            x, y: Screen coordinates
            add_to_selection: If True (Shift held), add to selection
        """
        if not self.picker:
            return

        # Perform the pick
        vertex_id = self.picker.pick(x, y, add_to_selection)

        if vertex_id is not None and vertex_id >= 0:
            # Update selection set
            if add_to_selection:
                # Toggle vertex in selection
                if vertex_id in self.selected_vertices:
                    self.selected_vertices.remove(vertex_id)
                    print(f"   ➖ Removed vertex {vertex_id} from selection (now {len(self.selected_vertices)} selected)")
                else:
                    self.selected_vertices.add(vertex_id)
                    print(f"   ➕ Added vertex {vertex_id} to selection (now {len(self.selected_vertices)} selected)")
            else:
                # Replace selection
                self.selected_vertices = {vertex_id}
                print(f"   🔄 New selection: vertex {vertex_id}")

            # Update highlight to show all selected vertices
            if self.highlight_manager and self.current_polydata:
                self.highlight_manager.highlight_vertices(
                    self.current_polydata,
                    list(self.selected_vertices),
                    color=(1.0, 1.0, 0.0)  # Yellow (matches face/edge selection)
                )
                self.highlight_manager.update_display()
                print(f"   ✅ Highlighting {len(self.selected_vertices)} vertices")

    def _on_face_picked(self, face_id):
        """Handle face selection (legacy signal handler - not used anymore)"""
        print(f"🎨 _on_face_picked() called with face_id={face_id}")

        # Highlight the face immediately for visual feedback
        if self.highlight_manager and self.current_polydata:
            print(f"   Highlighting face {face_id}")
            self.highlight_manager.highlight_faces(
                self.current_polydata,
                [face_id],
                color=(1.0, 1.0, 0.0)  # Yellow
            )
            self.highlight_manager.update_display()
            print(f"   ✅ Highlight applied")
        else:
            print(f"   ⚠️ No highlight manager or polydata")

        # Get the application state through parent
        if hasattr(self.parent(), 'parent') and hasattr(self.parent().parent(), 'state'):
            state = self.parent().parent().state
            state.edit_mode_manager.select_face(face_id, add_to_selection=False)
            self.log_debug(f"Selected face {face_id}")
        else:
            print("   ⚠️ Could not access application state")

    def _on_edge_picked(self, edge_id):
        """Handle edge selection"""
        if hasattr(self.parent(), 'parent') and hasattr(self.parent().parent(), 'state'):
            state = self.parent().parent().state
            state.edit_mode_manager.select_edge(edge_id, add_to_selection=False)
            self.log_debug(f"Selected edge {edge_id}")

    def _on_vertex_picked(self, vertex_id):
        """Handle vertex selection"""
        if hasattr(self.parent(), 'parent') and hasattr(self.parent().parent(), 'state'):
            state = self.parent().parent().state
            state.edit_mode_manager.select_vertex(vertex_id, add_to_selection=False)
            self.log_debug(f"Selected vertex {vertex_id}")

    def update_selection(self, selection):
        """
        Update visual representation of selection

        Args:
            selection: Selection object containing selected elements
        """
        if not self.highlight_manager or not self.current_polydata:
            return

        from app.state.edit_mode import EditMode

        self.highlight_manager.clear_highlights()

        if selection.mode == EditMode.PANEL and selection.faces:
            self.highlight_manager.highlight_faces(
                self.current_polydata,
                list(selection.faces),
                color=(1.0, 0.8, 0.0)
            )
        elif selection.mode == EditMode.EDGE and selection.edges:
            self.highlight_manager.highlight_edges(
                self.current_polydata,
                list(selection.edges),
                color=(0.0, 1.0, 0.5)
            )
        elif selection.mode == EditMode.VERTEX and selection.vertices:
            self.highlight_manager.highlight_vertices(
                self.current_polydata,
                list(selection.vertices),
                color=(0.0, 0.5, 1.0)
            )

        self.highlight_manager.update_display()

    def perform_pick(self, x, y):
        """
        Perform picking at the specified screen coordinates
        Called by the interactor style on left click

        Args:
            x, y: Screen coordinates
        """
        if not self.picker or not self.edit_mode:
            return

        # VTK uses bottom-left origin, Qt uses top-left
        # Get render window height to flip Y coordinate
        size = self.render_window.GetSize()
        vtk_y = size[1] - y - 1

        # Perform pick with the current picker
        element_id = self.picker.pick(x, vtk_y)

        if element_id is not None:
            from app.state.edit_mode import EditMode

            # Log the pick
            if self.edit_mode == EditMode.PANEL:
                self.log_debug(f"🎯 Picked face {element_id}")
            elif self.edit_mode == EditMode.EDGE:
                self.log_debug(f"🎯 Picked edge {element_id}")
            elif self.edit_mode == EditMode.VERTEX:
                self.log_debug(f"🎯 Picked vertex {element_id}")

    def enable_picking(self):
        """Enable interactive picking based on current mode"""
        # Picking is now handled through perform_pick called by interactor
        if self.interactor_style:
            self.interactor_style.picking_enabled = True

    def closeEvent(self, event):
        """Clean up VTK resources on close"""
        if self.interactor:
            self.interactor.TerminateApp()
        super().closeEvent(event)
