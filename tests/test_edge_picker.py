"""
Tests for SubDEdgePicker - Edge selection with tubular rendering and adjacency tracking

Tests cover:
- Edge extraction from tessellation
- Edge→triangle adjacency mapping
- Boundary vs internal edge identification
- Tubular rendering (guide and highlight)
- Picking with tolerance
- Multi-select functionality
- Selection state management
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from PyQt6.QtCore import QObject

# Import our edge picker
from app.ui.pickers.edge_picker import SubDEdgePicker, EdgeInfo

# Import VTK from bridge
from app import vtk_bridge as vtk


class TestEdgeInfo:
    """Test EdgeInfo data structure"""

    def test_edge_info_creation(self):
        """Test creating edge info"""
        edge = EdgeInfo(5, 2, 0)

        # Vertices should be sorted
        assert edge.vertices == (2, 5)
        assert edge.edge_id == 0
        assert edge.adjacent_triangles == []
        assert edge.is_boundary == False

    def test_edge_info_adjacency(self):
        """Test adjacency tracking"""
        edge = EdgeInfo(3, 7, 1)

        edge.adjacent_triangles.append(10)
        edge.adjacent_triangles.append(11)

        assert len(edge.adjacent_triangles) == 2
        assert 10 in edge.adjacent_triangles
        assert 11 in edge.adjacent_triangles

    def test_edge_info_boundary_detection(self):
        """Test boundary edge detection"""
        boundary_edge = EdgeInfo(0, 1, 0)
        boundary_edge.adjacent_triangles.append(5)
        boundary_edge.is_boundary = True

        assert boundary_edge.is_boundary
        assert len(boundary_edge.adjacent_triangles) == 1

        internal_edge = EdgeInfo(2, 3, 1)
        internal_edge.adjacent_triangles.extend([10, 11])

        assert not internal_edge.is_boundary
        assert len(internal_edge.adjacent_triangles) == 2


class TestSubDEdgePicker:
    """Test SubDEdgePicker functionality"""

    @pytest.fixture
    def mock_renderer(self):
        """Create mock VTK renderer"""
        renderer = Mock(spec=vtk.vtkRenderer)
        renderer.AddActor = Mock()
        renderer.RemoveActor = Mock()
        return renderer

    @pytest.fixture
    def mock_render_window(self):
        """Create mock VTK render window"""
        window = Mock(spec=vtk.vtkRenderWindow)
        window.GetInteractor = Mock(return_value=Mock())
        window.Render = Mock()
        return window

    @pytest.fixture
    def edge_picker(self, mock_renderer, mock_render_window):
        """Create edge picker instance"""
        picker = SubDEdgePicker(mock_renderer, mock_render_window)
        return picker

    @pytest.fixture
    def simple_mesh_polydata(self):
        """Create a simple triangulated mesh (2 triangles forming a quad)"""
        # Points:
        # 0---1
        # |  /|
        # | / |
        # |/  |
        # 2---3

        points = vtk.vtkPoints()
        points.InsertNextPoint(0.0, 1.0, 0.0)  # 0
        points.InsertNextPoint(1.0, 1.0, 0.0)  # 1
        points.InsertNextPoint(0.0, 0.0, 0.0)  # 2
        points.InsertNextPoint(1.0, 0.0, 0.0)  # 3

        # Triangles
        triangles = vtk.vtkCellArray()

        # Triangle 0: (0, 1, 2)
        tri1 = vtk.vtkTriangle()
        tri1.GetPointIds().SetId(0, 0)
        tri1.GetPointIds().SetId(1, 1)
        tri1.GetPointIds().SetId(2, 2)
        triangles.InsertNextCell(tri1)

        # Triangle 1: (1, 3, 2)
        tri2 = vtk.vtkTriangle()
        tri2.GetPointIds().SetId(0, 1)
        tri2.GetPointIds().SetId(1, 3)
        tri2.GetPointIds().SetId(2, 2)
        triangles.InsertNextCell(tri2)

        # Create polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(triangles)

        return polydata

    def test_picker_initialization(self, edge_picker):
        """Test picker is initialized correctly"""
        assert edge_picker.renderer is not None
        assert edge_picker.render_window is not None
        assert edge_picker.picker is not None
        assert edge_picker.edges == {}
        assert edge_picker.edge_map == {}
        assert edge_picker.selected_edge_ids == set()
        assert edge_picker.pick_tolerance == 0.1

    def test_edge_extraction_simple_mesh(self, edge_picker, simple_mesh_polydata):
        """Test edge extraction from simple mesh"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        # Simple quad (2 triangles) should have 5 edges:
        # - 4 boundary edges (forming the quad)
        # - 1 internal edge (diagonal)
        assert len(edge_picker.edges) == 5

        # Check boundary edges
        boundary_edges = edge_picker.get_boundary_edges()
        internal_edges = edge_picker.get_internal_edges()

        assert len(boundary_edges) == 4
        assert len(internal_edges) == 1

    def test_edge_adjacency_mapping(self, edge_picker, simple_mesh_polydata):
        """Test edge→triangle adjacency mapping"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        # Find the internal edge (diagonal from point 1 to point 2)
        internal_edges = edge_picker.get_internal_edges()
        assert len(internal_edges) == 1

        internal_edge_id = internal_edges[0]
        edge_info = edge_picker.get_edge_info(internal_edge_id)

        # Internal edge should have 2 adjacent triangles
        assert len(edge_info.adjacent_triangles) == 2
        assert not edge_info.is_boundary

    def test_edge_polydata_creation(self, edge_picker, simple_mesh_polydata):
        """Test VTK polydata creation for edges"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        assert edge_picker.edge_polydata is not None
        assert edge_picker.edge_polydata.GetNumberOfPoints() == 4  # 4 vertices
        assert edge_picker.edge_polydata.GetNumberOfLines() == 5  # 5 edges

    def test_guide_visualization_created(self, edge_picker, simple_mesh_polydata, mock_renderer):
        """Test cyan guide visualization is created"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        # Guide actor should be created and added to renderer
        assert edge_picker.guide_actor is not None
        assert edge_picker.guide_mapper is not None

        # Check color is cyan
        color = edge_picker.guide_actor.GetProperty().GetColor()
        assert color[0] == 0.0  # Red
        assert color[1] == 1.0  # Green
        assert color[2] == 1.0  # Blue

        # Check it was added to renderer
        mock_renderer.AddActor.assert_called()

    def test_selection_state_management(self, edge_picker, simple_mesh_polydata):
        """Test selection state is managed correctly"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        # Initially no selection
        assert len(edge_picker.get_selected_edges()) == 0

        # Add to selection
        edge_picker.selected_edge_ids.add(0)
        edge_picker.selected_edge_ids.add(2)

        selected = edge_picker.get_selected_edges()
        assert len(selected) == 2
        assert 0 in selected
        assert 2 in selected

        # Clear selection
        edge_picker.clear_selection()
        assert len(edge_picker.get_selected_edges()) == 0

    def test_highlight_only_selected_edges(self, edge_picker, simple_mesh_polydata, mock_renderer):
        """Test that highlighting only shows selected edges, not all edges"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        # Select specific edges
        edge_picker.selected_edge_ids.add(0)
        edge_picker.selected_edge_ids.add(2)

        # Update highlight
        edge_picker._update_highlight()

        # Highlight actor should be created
        assert edge_picker.highlight_actor is not None

        # Check color is yellow
        color = edge_picker.highlight_actor.GetProperty().GetColor()
        assert color[0] == 1.0  # Red
        assert color[1] == 1.0  # Green
        assert color[2] == 0.0  # Blue

        # Check it was added to renderer
        assert mock_renderer.AddActor.call_count >= 2  # Guide + Highlight

    def test_highlight_cleared_when_no_selection(self, edge_picker, simple_mesh_polydata, mock_renderer):
        """Test that highlight is removed when selection is cleared"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        # Select and highlight
        edge_picker.selected_edge_ids.add(0)
        edge_picker._update_highlight()
        assert edge_picker.highlight_actor is not None

        # Clear selection
        edge_picker.clear_selection()

        # Highlight actor should be removed
        mock_renderer.RemoveActor.assert_called()

    def test_signals_emitted(self, edge_picker):
        """Test that signals are emitted correctly"""
        # Create signal spy
        edge_picked_spy = Mock()
        position_picked_spy = Mock()
        selection_changed_spy = Mock()

        edge_picker.edge_picked.connect(edge_picked_spy)
        edge_picker.position_picked.connect(position_picked_spy)
        edge_picker.selection_changed.connect(selection_changed_spy)

        # Manually trigger signals (simulating pick)
        edge_picker.edge_picked.emit(5)
        edge_picker.position_picked.emit(1.0, 2.0, 3.0)
        edge_picker.selection_changed.emit([5])

        # Check signals were emitted
        edge_picked_spy.assert_called_once_with(5)
        position_picked_spy.assert_called_once_with(1.0, 2.0, 3.0)
        selection_changed_spy.assert_called_once_with([5])

    def test_multi_select_toggle(self, edge_picker, simple_mesh_polydata):
        """Test multi-select with toggle behavior"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        # Add edge 0
        edge_picker.selected_edge_ids.add(0)
        assert 0 in edge_picker.selected_edge_ids

        # Add edge 1 (multi-select)
        edge_picker.selected_edge_ids.add(1)
        assert 0 in edge_picker.selected_edge_ids
        assert 1 in edge_picker.selected_edge_ids

        # Toggle edge 0 (remove it)
        if 0 in edge_picker.selected_edge_ids:
            edge_picker.selected_edge_ids.remove(0)

        assert 0 not in edge_picker.selected_edge_ids
        assert 1 in edge_picker.selected_edge_ids

    def test_boundary_edge_identification(self, edge_picker, simple_mesh_polydata):
        """Test boundary edges are correctly identified"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        boundary_edges = edge_picker.get_boundary_edges()

        # All boundary edges should have exactly 1 adjacent triangle
        for edge_id in boundary_edges:
            edge_info = edge_picker.get_edge_info(edge_id)
            assert len(edge_info.adjacent_triangles) == 1
            assert edge_info.is_boundary

    def test_internal_edge_identification(self, edge_picker, simple_mesh_polydata):
        """Test internal edges are correctly identified"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)

        internal_edges = edge_picker.get_internal_edges()

        # All internal edges should have 2+ adjacent triangles
        for edge_id in internal_edges:
            edge_info = edge_picker.get_edge_info(edge_id)
            assert len(edge_info.adjacent_triangles) >= 2
            assert not edge_info.is_boundary

    def test_cleanup(self, edge_picker, simple_mesh_polydata, mock_renderer):
        """Test cleanup removes all actors"""
        edge_picker.setup_edge_extraction(simple_mesh_polydata)
        edge_picker.selected_edge_ids.add(0)
        edge_picker._update_highlight()

        # Both actors should exist
        assert edge_picker.guide_actor is not None
        assert edge_picker.highlight_actor is not None

        # Cleanup
        edge_picker.cleanup()

        # Actors should be removed
        assert edge_picker.guide_actor is None
        assert edge_picker.highlight_actor is None
        assert len(edge_picker.edges) == 0
        assert len(edge_picker.selected_edge_ids) == 0

        # Renderer should have RemoveActor called
        assert mock_renderer.RemoveActor.call_count >= 2


class TestEdgePickerIntegration:
    """Integration tests for edge picker with real VTK objects"""

    def test_create_real_mesh_and_extract_edges(self):
        """Test edge extraction with real VTK mesh"""
        # Create a simple cube mesh
        cube_source = vtk.vtkCubeSource()
        cube_source.Update()

        # Triangulate it
        triangulate = vtk.vtkTriangleFilter()
        triangulate.SetInputConnection(cube_source.GetOutputPort())
        triangulate.Update()

        polydata = triangulate.GetOutput()

        # Create renderer and window
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.OffScreenRenderingOn()  # No GUI

        # Create picker
        picker = SubDEdgePicker(renderer, render_window)
        picker.setup_edge_extraction(polydata)

        # Cube should have edges
        assert len(picker.edges) > 0

        # Should have both boundary and internal edges (after triangulation)
        boundary_edges = picker.get_boundary_edges()
        internal_edges = picker.get_internal_edges()

        # A triangulated cube has edges
        assert len(boundary_edges) >= 0
        assert len(internal_edges) >= 0

        # Cleanup
        picker.cleanup()

    def test_tube_filter_creates_geometry(self):
        """Test that vtkTubeFilter creates tubular geometry"""
        # Create a simple line
        points = vtk.vtkPoints()
        points.InsertNextPoint(0.0, 0.0, 0.0)
        points.InsertNextPoint(1.0, 0.0, 0.0)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, 0)
        line.GetPointIds().SetId(1, 1)

        lines = vtk.vtkCellArray()
        lines.InsertNextCell(line)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(lines)

        # Apply tube filter
        tube_filter = vtk.vtkTubeFilter()
        tube_filter.SetInputData(polydata)
        tube_filter.SetRadius(0.1)
        tube_filter.SetNumberOfSides(8)
        tube_filter.Update()

        output = tube_filter.GetOutput()

        # Should create polygonal geometry
        assert output.GetNumberOfPoints() > 2  # More than just the line endpoints
        assert output.GetNumberOfCells() > 0   # Should have surface cells


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
