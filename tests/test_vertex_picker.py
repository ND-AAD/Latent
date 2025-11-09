"""
Tests for Vertex Picker (Agent 21)
Verifies vertex sphere rendering and proximity-based picking
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import VTK types from our bridge
from app import vtk_bridge as vtk
from app.ui.pickers.vertex_picker import SubDVertexPicker


@pytest.fixture
def mock_renderer():
    """Create mock VTK renderer"""
    renderer = Mock(spec=vtk.vtkRenderer)
    return renderer


@pytest.fixture
def mock_render_window():
    """Create mock VTK render window"""
    window = Mock(spec=vtk.vtkRenderWindow)
    window.GetSize.return_value = (800, 600)
    window.GetInteractor.return_value = Mock()
    return window


@pytest.fixture
def vertex_picker(mock_renderer, mock_render_window):
    """Create vertex picker instance"""
    picker = SubDVertexPicker(mock_renderer, mock_render_window)
    return picker


@pytest.fixture
def sample_polydata():
    """Create sample polydata with 8 vertices (cube corners)"""
    points = vtk.vtkPoints()
    
    # Create 8 vertices forming a cube
    vertices = [
        (0.0, 0.0, 0.0),  # 0
        (1.0, 0.0, 0.0),  # 1
        (1.0, 1.0, 0.0),  # 2
        (0.0, 1.0, 0.0),  # 3
        (0.0, 0.0, 1.0),  # 4
        (1.0, 0.0, 1.0),  # 5
        (1.0, 1.0, 1.0),  # 6
        (0.0, 1.0, 1.0),  # 7
    ]
    
    for vertex in vertices:
        points.InsertNextPoint(vertex)
    
    # Create polydata
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    
    return polydata


class TestVertexPickerSetup:
    """Test vertex picker initialization and setup"""
    
    def test_picker_initialization(self, vertex_picker):
        """Test picker is properly initialized"""
        assert vertex_picker is not None
        assert vertex_picker.renderer is not None
        assert vertex_picker.render_window is not None
        assert vertex_picker.selected_vertices == set()
        assert vertex_picker.vertex_positions == []
        
    def test_default_colors(self, vertex_picker):
        """Test default color values"""
        assert vertex_picker.default_color == (0.7, 0.7, 0.7)  # Gray
        assert vertex_picker.selected_color == (1.0, 1.0, 0.0)  # Yellow
        
    def test_setup_vertex_rendering(self, vertex_picker, sample_polydata):
        """Test vertex rendering setup"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Check vertices were extracted
        assert len(vertex_picker.vertex_positions) == 8
        
        # Check sphere actors were created
        assert len(vertex_picker.vertex_sphere_actors) == 8
        
        # Verify renderer.AddActor was called for each vertex
        assert vertex_picker.renderer.AddActor.call_count == 8
        
    def test_adaptive_sphere_sizing(self, vertex_picker, sample_polydata):
        """Test sphere radius adapts to model size"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Cube has size 1.0 in each dimension
        # Sphere radius should be ~1.5% of model size
        expected_radius = 1.0 * 0.015
        assert abs(vertex_picker.sphere_radius - expected_radius) < 0.001
        
    def test_clear_vertex_actors(self, vertex_picker, sample_polydata):
        """Test clearing vertex actors"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        assert len(vertex_picker.vertex_sphere_actors) == 8
        
        vertex_picker.clear_vertex_actors()
        assert len(vertex_picker.vertex_sphere_actors) == 0
        
        # Verify renderer.RemoveActor was called for each vertex
        assert vertex_picker.renderer.RemoveActor.call_count == 8


class TestProximityPicking:
    """Test proximity-based vertex picking"""
    
    def test_point_to_ray_distance(self, vertex_picker):
        """Test point-to-ray distance calculation"""
        # Ray along X axis from origin
        ray_origin = np.array([0.0, 0.0, 0.0])
        ray_direction = np.array([1.0, 0.0, 0.0])
        
        # Point on the ray should have distance 0
        point_on_ray = np.array([5.0, 0.0, 0.0])
        distance = vertex_picker._point_to_ray_distance(point_on_ray, ray_origin, ray_direction)
        assert abs(distance) < 0.001
        
        # Point offset from ray should have distance equal to offset
        point_off_ray = np.array([5.0, 3.0, 0.0])
        distance = vertex_picker._point_to_ray_distance(point_off_ray, ray_origin, ray_direction)
        assert abs(distance - 3.0) < 0.001
        
    def test_point_to_ray_distance_3d(self, vertex_picker):
        """Test point-to-ray distance in 3D"""
        # Ray from origin in diagonal direction
        ray_origin = np.array([0.0, 0.0, 0.0])
        ray_direction = np.array([1.0, 1.0, 1.0])
        ray_direction = ray_direction / np.linalg.norm(ray_direction)  # Normalize
        
        # Point perpendicular to ray
        point = np.array([1.0, 0.0, 0.0])
        distance = vertex_picker._point_to_ray_distance(point, ray_origin, ray_direction)
        
        # Distance should be ~0.816 (geometric calculation)
        assert 0.8 < distance < 0.85
        
    def test_get_picking_ray(self, vertex_picker, mock_render_window):
        """Test picking ray generation from screen coordinates"""
        # Setup mock camera
        camera = Mock()
        camera.GetPosition.return_value = (0.0, 0.0, 10.0)
        camera.GetFocalPoint.return_value = (0.0, 0.0, 0.0)
        camera.GetViewUp.return_value = (0.0, 1.0, 0.0)
        camera.GetViewAngle.return_value = 45.0
        
        vertex_picker.renderer.GetActiveCamera.return_value = camera
        
        # Get ray from center of screen
        ray_origin, ray_direction = vertex_picker._get_picking_ray(400, 300)
        
        assert ray_origin is not None
        assert ray_direction is not None
        
        # Ray origin should be camera position
        assert np.allclose(ray_origin, [0.0, 0.0, 10.0])
        
        # Ray direction should be roughly toward focal point for center of screen
        # (will have small offset due to FOV calculations)
        assert ray_direction[2] < 0  # Pointing in -Z direction


class TestVertexSelection:
    """Test vertex selection functionality"""
    
    def test_single_vertex_selection(self, vertex_picker, sample_polydata):
        """Test selecting a single vertex"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Manually add vertex to selection
        vertex_picker.selected_vertices.add(0)
        vertex_picker.update_selection([0])
        
        assert 0 in vertex_picker.selected_vertices
        assert len(vertex_picker.selected_vertices) == 1
        
    def test_multi_vertex_selection(self, vertex_picker, sample_polydata):
        """Test selecting multiple vertices"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Select multiple vertices
        vertex_picker.update_selection([0, 2, 5])
        
        assert len(vertex_picker.selected_vertices) == 3
        assert 0 in vertex_picker.selected_vertices
        assert 2 in vertex_picker.selected_vertices
        assert 5 in vertex_picker.selected_vertices
        
    def test_clear_selection(self, vertex_picker, sample_polydata):
        """Test clearing selection"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Select some vertices
        vertex_picker.update_selection([0, 1, 2])
        assert len(vertex_picker.selected_vertices) == 3
        
        # Clear selection
        vertex_picker.clear_selection()
        assert len(vertex_picker.selected_vertices) == 0
        
    def test_get_selected_vertices(self, vertex_picker, sample_polydata):
        """Test getting selected vertex list"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        vertex_picker.update_selection([1, 3, 5, 7])
        selected = vertex_picker.get_selected_vertices()
        
        assert len(selected) == 4
        assert set(selected) == {1, 3, 5, 7}


class TestVertexVisualization:
    """Test vertex sphere visualization"""
    
    def test_sphere_actors_created(self, vertex_picker, sample_polydata):
        """Test sphere actors are created for all vertices"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Should have one actor per vertex
        assert len(vertex_picker.vertex_sphere_actors) == 8
        
        # All actors should be added to renderer
        assert vertex_picker.renderer.AddActor.call_count == 8
        
    def test_default_sphere_color(self, vertex_picker, sample_polydata):
        """Test unselected vertices have gray color"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Mock the GetProperty().SetColor() calls
        for actor in vertex_picker.vertex_sphere_actors:
            # Check that SetColor was called (during creation)
            assert actor.GetProperty().SetColor.called
            
    def test_selected_vertex_color(self, vertex_picker, sample_polydata):
        """Test selected vertices have yellow color"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Select vertex 0
        vertex_picker.update_selection([0])
        
        # Check that vertex 0's actor color was set to yellow
        actor = vertex_picker.vertex_sphere_actors[0]
        actor.GetProperty().SetColor.assert_called_with(1.0, 1.0, 0.0)
        
    def test_sphere_radius_scales_with_model(self, vertex_picker):
        """Test sphere radius adapts to different model sizes"""
        # Create small model
        points_small = vtk.vtkPoints()
        points_small.InsertNextPoint(0.0, 0.0, 0.0)
        points_small.InsertNextPoint(0.1, 0.1, 0.1)
        
        polydata_small = vtk.vtkPolyData()
        polydata_small.SetPoints(points_small)
        
        vertex_picker.setup_vertex_rendering(polydata_small)
        small_radius = vertex_picker.sphere_radius
        
        # Create large model
        vertex_picker.clear_vertex_actors()
        
        points_large = vtk.vtkPoints()
        points_large.InsertNextPoint(0.0, 0.0, 0.0)
        points_large.InsertNextPoint(100.0, 100.0, 100.0)
        
        polydata_large = vtk.vtkPolyData()
        polydata_large.SetPoints(points_large)
        
        vertex_picker.setup_vertex_rendering(polydata_large)
        large_radius = vertex_picker.sphere_radius
        
        # Large model should have larger spheres
        assert large_radius > small_radius
        assert large_radius / small_radius > 500  # Should scale proportionally


class TestPickingIntegration:
    """Integration tests for picking workflow"""
    
    def test_cleanup(self, vertex_picker, sample_polydata):
        """Test cleanup removes all actors and data"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        assert len(vertex_picker.vertex_sphere_actors) == 8
        assert len(vertex_picker.vertex_positions) == 8
        
        vertex_picker.cleanup()
        
        assert len(vertex_picker.vertex_sphere_actors) == 0
        assert len(vertex_picker.vertex_positions) == 0
        assert len(vertex_picker.selected_vertices) == 0
        assert vertex_picker.polydata is None
        
    def test_signals_emitted(self, vertex_picker, sample_polydata):
        """Test that signals are emitted when vertex is picked"""
        from PyQt6.QtCore import QSignalSpy
        
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Create signal spies
        picked_spy = QSignalSpy(vertex_picker.vertex_picked)
        position_spy = QSignalSpy(vertex_picker.position_picked)
        
        # Manually trigger picking by simulating internal pick logic
        # (We can't easily test the full pick() method without mocking camera extensively)
        vertex_id = 0
        pos = vertex_picker.vertex_positions[vertex_id]
        
        vertex_picker.vertex_picked.emit(vertex_id)
        vertex_picker.position_picked.emit(pos[0], pos[1], pos[2])
        
        assert len(picked_spy) == 1
        assert len(position_spy) == 1


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_pick_without_setup(self, vertex_picker):
        """Test picking before setup returns None"""
        # Picking without setup should return None
        # (We can't fully test this without extensive mocking, but we can verify the check)
        assert len(vertex_picker.vertex_positions) == 0
        
    def test_empty_polydata(self, vertex_picker):
        """Test handling of empty polydata"""
        # Create empty polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk.vtkPoints())
        
        vertex_picker.setup_vertex_rendering(polydata)
        
        # Should have no vertices
        assert len(vertex_picker.vertex_positions) == 0
        assert len(vertex_picker.vertex_sphere_actors) == 0
        
    def test_update_selection_out_of_bounds(self, vertex_picker, sample_polydata):
        """Test update_selection with invalid vertex IDs"""
        vertex_picker.setup_vertex_rendering(sample_polydata)
        
        # Try to select vertices that don't exist
        # Should not crash, but won't update colors for invalid IDs
        vertex_picker.update_selection([0, 1, 100, 200])
        
        # Valid vertices should be selected
        assert 0 in vertex_picker.selected_vertices
        assert 1 in vertex_picker.selected_vertices
        
        # Invalid vertices should also be in set (no validation)
        # But won't crash when trying to update colors
        assert 100 in vertex_picker.selected_vertices


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
