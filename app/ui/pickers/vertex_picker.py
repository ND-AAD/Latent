"""
Vertex Picker for SubD Vertex Selection
Renders vertices as spheres with proximity-based picking

Vertex Visualization:
- All vertices rendered as spheres (gray by default)
- Selected vertices highlighted in yellow (1.0, 1.0, 0.0)
- Adaptive sphere sizing based on model bounds

Picking Strategy:
- 3D ray from click position
- Find closest vertex to ray within threshold
- Multi-select with Shift+Click
"""

from typing import Optional, List, Tuple
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal

# Import VTK types from our bridge
from app import vtk_bridge as vtk


class SubDVertexPicker(QObject):
    """
    Proximity-based vertex picker with sphere visualization
    
    Features:
    - Renders all vertices as spheres for easy selection
    - Gray spheres for unselected vertices
    - Yellow spheres for selected vertices (Rhino standard)
    - Adaptive sphere sizing based on model bounds
    - Proximity-based picking (closest vertex to ray)
    """
    
    # Signals
    vertex_picked = pyqtSignal(int)  # Vertex ID
    position_picked = pyqtSignal(float, float, float)  # World position
    
    def __init__(self, renderer: vtk.vtkRenderer, render_window: vtk.vtkRenderWindow):
        super().__init__()
        self.renderer = renderer
        self.render_window = render_window
        self.interactor = render_window.GetInteractor() if render_window else None
        
        # Vertex data
        self.polydata = None
        self.vertex_positions = []  # List of (x, y, z) tuples
        self.sphere_radius = 0.05  # Default, will be adaptive
        
        # Visualization actors
        self.vertex_sphere_actors = []  # One actor per vertex
        self.selected_vertices = set()  # Set of selected vertex IDs
        
        # Picking parameters
        self.pick_tolerance = 0.1  # World space tolerance for ray-vertex distance
        
        # Colors
        self.default_color = (0.7, 0.7, 0.7)  # Gray for unselected
        self.selected_color = (1.0, 1.0, 0.0)  # Yellow for selected (Rhino standard)
        
    def setup_vertex_rendering(self, polydata: vtk.vtkPolyData):
        """
        Setup vertex sphere rendering from polydata
        
        Args:
            polydata: VTK polydata containing vertices
        """
        print(f"🎯 Setting up vertex rendering from polydata")
        
        # Store polydata
        self.polydata = polydata
        
        # Clear existing actors
        self.clear_vertex_actors()
        
        # Extract vertex positions
        points = polydata.GetPoints()
        if not points:
            print("⚠️ No points in polydata")
            return
            
        num_vertices = points.GetNumberOfPoints()
        print(f"   Found {num_vertices} vertices")
        
        # Calculate adaptive sphere radius based on model bounds
        bounds = polydata.GetBounds()
        model_size = max(
            bounds[1] - bounds[0],  # X extent
            bounds[3] - bounds[2],  # Y extent
            bounds[5] - bounds[4]   # Z extent
        )
        self.sphere_radius = model_size * 0.015  # 1.5% of model size
        print(f"   Adaptive sphere radius: {self.sphere_radius:.4f}")
        
        # Store vertex positions
        self.vertex_positions = []
        for i in range(num_vertices):
            point = points.GetPoint(i)
            self.vertex_positions.append(point)
        
        # Create sphere actors for all vertices
        self._create_vertex_sphere_actors()
        
        print(f"✅ Vertex rendering setup complete: {len(self.vertex_sphere_actors)} sphere actors")
        
    def _create_vertex_sphere_actors(self):
        """Create sphere actors for all vertices"""
        for i, position in enumerate(self.vertex_positions):
            # Create sphere source
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(position)
            sphere.SetRadius(self.sphere_radius)
            sphere.SetPhiResolution(12)
            sphere.SetThetaResolution(12)
            
            # Create mapper
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())
            
            # Create actor
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            
            # Set color (gray by default)
            color = self.selected_color if i in self.selected_vertices else self.default_color
            actor.GetProperty().SetColor(color)
            
            # Make pickable
            actor.PickableOn()
            
            # Add to renderer
            self.renderer.AddActor(actor)
            self.vertex_sphere_actors.append(actor)
            
    def clear_vertex_actors(self):
        """Remove all vertex sphere actors from renderer"""
        for actor in self.vertex_sphere_actors:
            self.renderer.RemoveActor(actor)
        self.vertex_sphere_actors.clear()
        
    def pick(self, x: int, y: int, add_to_selection: bool = False) -> Optional[int]:
        """
        Pick a vertex using proximity-based ray casting
        
        Strategy:
        1. Cast ray from screen coordinates into 3D scene
        2. Find closest vertex to ray within tolerance
        3. Return vertex ID or None
        
        Args:
            x, y: Screen coordinates (VTK coordinate system)
            add_to_selection: If True, add to existing selection (Shift+Click)
            
        Returns:
            Vertex ID or None if nothing picked
        """
        mode_str = "ADD TO SELECTION" if add_to_selection else "NEW SELECTION"
        print(f"🎯 SubDVertexPicker.pick() called at ({x}, {y}) - {mode_str}")
        
        if not self.vertex_positions:
            print("   ❌ No vertex data available")
            return None
            
        # Get ray in world coordinates
        ray_origin, ray_direction = self._get_picking_ray(x, y)
        if ray_origin is None:
            print("   ❌ Failed to compute picking ray")
            return None
            
        print(f"   Ray origin: {ray_origin}")
        print(f"   Ray direction: {ray_direction}")
        
        # Find closest vertex to ray
        closest_vertex_id = None
        closest_distance = float('inf')
        
        for i, vertex_pos in enumerate(self.vertex_positions):
            # Calculate distance from vertex to ray
            distance = self._point_to_ray_distance(
                np.array(vertex_pos),
                ray_origin,
                ray_direction
            )
            
            if distance < closest_distance:
                closest_distance = distance
                closest_vertex_id = i
                
        print(f"   Closest vertex: {closest_vertex_id} at distance {closest_distance:.4f}")
        
        # Check if within tolerance
        # Tolerance is adaptive based on sphere radius
        effective_tolerance = self.sphere_radius * 3.0
        
        if closest_distance > effective_tolerance:
            print(f"   ❌ No vertex within tolerance ({effective_tolerance:.4f})")
            return None
            
        # Update selection
        if not add_to_selection:
            # Clear previous selection
            old_selected = self.selected_vertices.copy()
            self.selected_vertices.clear()
            # Update colors of previously selected vertices
            for vid in old_selected:
                if vid < len(self.vertex_sphere_actors):
                    self.vertex_sphere_actors[vid].GetProperty().SetColor(self.default_color)
                    
        # Toggle vertex in selection
        if closest_vertex_id in self.selected_vertices:
            self.selected_vertices.remove(closest_vertex_id)
            # Set to default color
            if closest_vertex_id < len(self.vertex_sphere_actors):
                self.vertex_sphere_actors[closest_vertex_id].GetProperty().SetColor(self.default_color)
            print(f"   ➖ Removed vertex {closest_vertex_id} from selection")
        else:
            self.selected_vertices.add(closest_vertex_id)
            # Set to selected color (yellow)
            if closest_vertex_id < len(self.vertex_sphere_actors):
                self.vertex_sphere_actors[closest_vertex_id].GetProperty().SetColor(self.selected_color)
            print(f"   ➕ Added vertex {closest_vertex_id} to selection")
            
        print(f"   ✅ Total selected vertices: {len(self.selected_vertices)}")
        
        # Emit signals
        vertex_pos = self.vertex_positions[closest_vertex_id]
        self.vertex_picked.emit(closest_vertex_id)
        self.position_picked.emit(vertex_pos[0], vertex_pos[1], vertex_pos[2])
        
        # Update display
        self.render_window.Render()
        
        return closest_vertex_id
        
    def _get_picking_ray(self, x: int, y: int) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Compute 3D ray from screen coordinates
        
        Args:
            x, y: Screen coordinates (VTK coordinate system)
            
        Returns:
            Tuple of (ray_origin, ray_direction) as numpy arrays, or (None, None) if failed
        """
        # Get camera
        camera = self.renderer.GetActiveCamera()
        if not camera:
            return None, None
            
        # Get renderer size
        size = self.render_window.GetSize()
        
        # Normalize screen coordinates to [-1, 1]
        # VTK uses bottom-left origin
        norm_x = 2.0 * x / size[0] - 1.0
        norm_y = 2.0 * y / size[1] - 1.0
        
        # Get view properties
        camera_pos = np.array(camera.GetPosition())
        focal_point = np.array(camera.GetFocalPoint())
        view_up = np.array(camera.GetViewUp())
        
        # Compute view direction
        view_dir = focal_point - camera_pos
        view_dir = view_dir / np.linalg.norm(view_dir)
        
        # Compute right vector (cross product of view direction and up)
        right = np.cross(view_dir, view_up)
        right = right / np.linalg.norm(right)
        
        # Recompute up vector to ensure orthogonality
        up = np.cross(right, view_dir)
        up = up / np.linalg.norm(up)
        
        # Get view angle and aspect ratio
        view_angle = camera.GetViewAngle()
        aspect = size[0] / size[1]
        
        # Compute ray direction
        # Account for field of view
        fov_scale = np.tan(np.radians(view_angle / 2.0))
        
        # Offset from center in view space
        offset_right = norm_x * fov_scale * aspect
        offset_up = norm_y * fov_scale
        
        # Compute ray direction in world space
        ray_direction = view_dir + offset_right * right + offset_up * up
        ray_direction = ray_direction / np.linalg.norm(ray_direction)
        
        # Ray origin is camera position
        ray_origin = camera_pos
        
        return ray_origin, ray_direction
        
    def _point_to_ray_distance(self, point: np.ndarray, ray_origin: np.ndarray, 
                               ray_direction: np.ndarray) -> float:
        """
        Calculate minimum distance from point to ray
        
        Uses vector projection formula:
        distance = ||(P - O) - ((P - O) · D) * D||
        where P = point, O = ray origin, D = ray direction (unit vector)
        
        Args:
            point: 3D point coordinates
            ray_origin: Ray origin point
            ray_direction: Ray direction (unit vector)
            
        Returns:
            Minimum distance from point to ray
        """
        # Vector from ray origin to point
        to_point = point - ray_origin
        
        # Project onto ray direction
        projection_length = np.dot(to_point, ray_direction)
        
        # Clamp to positive values (behind camera is invalid)
        if projection_length < 0:
            # Point is behind camera, return distance to origin
            return np.linalg.norm(to_point)
            
        # Closest point on ray
        closest_on_ray = ray_origin + projection_length * ray_direction
        
        # Distance from point to closest point on ray
        distance = np.linalg.norm(point - closest_on_ray)
        
        return distance
        
    def update_selection(self, vertex_ids: List[int]):
        """
        Update visual selection state
        
        Args:
            vertex_ids: List of vertex IDs to select
        """
        # Clear old selection visuals
        for vid in self.selected_vertices:
            if vid < len(self.vertex_sphere_actors):
                self.vertex_sphere_actors[vid].GetProperty().SetColor(self.default_color)
                
        # Update selection set
        self.selected_vertices = set(vertex_ids)
        
        # Apply new selection visuals
        for vid in self.selected_vertices:
            if vid < len(self.vertex_sphere_actors):
                self.vertex_sphere_actors[vid].GetProperty().SetColor(self.selected_color)
                
        # Update display
        self.render_window.Render()
        
    def get_selected_vertices(self) -> List[int]:
        """Get list of currently selected vertex IDs"""
        return list(self.selected_vertices)
        
    def clear_selection(self):
        """Clear all vertex selections"""
        self.update_selection([])
        
    def cleanup(self):
        """Remove all vertex actors from renderer"""
        self.clear_vertex_actors()
        self.vertex_positions.clear()
        self.selected_vertices.clear()
        self.polydata = None
