"""
Tests for ConstraintRenderer - VTK constraint visualization

Tests constraint visualization including undercuts, draft angles,
and demolding direction arrows.
"""

import pytest
import vtk
import numpy as np
from app.geometry.constraint_renderer import ConstraintRenderer, create_test_constraint_visualization


@pytest.fixture
def renderer():
    """Create a VTK renderer for testing."""
    return vtk.vtkRenderer()


@pytest.fixture
def test_mesh():
    """Create a simple test mesh (sphere)."""
    sphere = vtk.vtkSphereSource()
    sphere.SetRadius(2.0)
    sphere.SetThetaResolution(20)
    sphere.SetPhiResolution(20)
    sphere.Update()
    return sphere.GetOutput()


@pytest.fixture
def constraint_renderer(renderer):
    """Create a ConstraintRenderer instance."""
    return ConstraintRenderer(renderer)


class TestConstraintRendererInit:
    """Test ConstraintRenderer initialization."""

    def test_init(self, renderer):
        """Test basic initialization."""
        cr = ConstraintRenderer(renderer)
        assert cr.renderer == renderer
        assert cr.undercut_actor is None
        assert cr.draft_actor is None
        assert cr.demold_arrow is None
        assert cr.current_mesh is None

    def test_default_thresholds(self, constraint_renderer):
        """Test default draft angle thresholds."""
        assert constraint_renderer.draft_insufficient == 0.5
        assert constraint_renderer.draft_marginal == 2.0


class TestUndercutVisualization:
    """Test undercut highlighting."""

    def test_show_undercuts_empty_list(self, constraint_renderer, test_mesh, renderer):
        """Test with empty undercut list."""
        constraint_renderer.show_undercuts([], test_mesh)
        assert constraint_renderer.undercut_actor is None

    def test_show_undercuts_valid(self, constraint_renderer, test_mesh, renderer):
        """Test showing undercuts on valid faces."""
        num_cells = test_mesh.GetNumberOfCells()
        undercut_faces = [0, 1, 2, 3, 4]  # First 5 faces

        constraint_renderer.show_undercuts(undercut_faces, test_mesh)

        # Check actor was created
        assert constraint_renderer.undercut_actor is not None
        assert constraint_renderer.current_mesh is not None

        # Check actor properties
        actor = constraint_renderer.undercut_actor
        color = actor.GetProperty().GetColor()
        assert color[0] == 1.0  # Red
        assert color[1] == 0.0
        assert color[2] == 0.0

        opacity = actor.GetProperty().GetOpacity()
        assert opacity == 0.7

        # Check actor is in renderer
        actors = renderer.GetActors()
        actors.InitTraversal()
        found = False
        for _ in range(actors.GetNumberOfItems()):
            if actors.GetNextActor() == actor:
                found = True
                break
        assert found

    def test_show_undercuts_all_faces(self, constraint_renderer, test_mesh, renderer):
        """Test highlighting all faces as undercuts."""
        num_cells = test_mesh.GetNumberOfCells()
        all_faces = list(range(num_cells))

        constraint_renderer.show_undercuts(all_faces, test_mesh)
        assert constraint_renderer.undercut_actor is not None

    def test_clear_undercuts(self, constraint_renderer, test_mesh, renderer):
        """Test clearing undercut visualization."""
        undercut_faces = [0, 1, 2]
        constraint_renderer.show_undercuts(undercut_faces, test_mesh)
        assert constraint_renderer.undercut_actor is not None

        constraint_renderer.clear_undercuts()
        assert constraint_renderer.undercut_actor is None

    def test_show_undercuts_replaces_previous(self, constraint_renderer, test_mesh, renderer):
        """Test that showing new undercuts replaces previous visualization."""
        constraint_renderer.show_undercuts([0, 1], test_mesh)
        first_actor = constraint_renderer.undercut_actor

        constraint_renderer.show_undercuts([5, 6, 7], test_mesh)
        second_actor = constraint_renderer.undercut_actor

        # Should be different actors
        assert second_actor != first_actor


class TestDraftAngleVisualization:
    """Test draft angle color-coding."""

    def test_show_draft_angles_empty_map(self, constraint_renderer, test_mesh, renderer):
        """Test with empty draft map."""
        constraint_renderer.show_draft_angles({}, test_mesh)
        assert constraint_renderer.draft_actor is None

    def test_show_draft_angles_valid(self, constraint_renderer, test_mesh, renderer):
        """Test showing draft angles with valid data."""
        num_cells = test_mesh.GetNumberOfCells()

        # Create draft map with various angles
        draft_map = {}
        for i in range(num_cells):
            draft_map[i] = float(i % 5)  # 0-4 degrees

        constraint_renderer.show_draft_angles(draft_map, test_mesh)

        # Check actor was created
        assert constraint_renderer.draft_actor is not None
        assert constraint_renderer.current_mesh is not None

        # Check actor is in renderer
        actor = constraint_renderer.draft_actor
        actors = renderer.GetActors()
        actors.InitTraversal()
        found = False
        for _ in range(actors.GetNumberOfItems()):
            if actors.GetNextActor() == actor:
                found = True
                break
        assert found

    def test_draft_angle_color_mapping(self, constraint_renderer, test_mesh, renderer):
        """Test that draft angle LUT is created correctly."""
        draft_map = {0: 0.3, 1: 1.0, 2: 3.0}  # Insufficient, marginal, good

        constraint_renderer.show_draft_angles(draft_map, test_mesh)

        # Get the lookup table
        mapper = constraint_renderer.draft_actor.GetMapper()
        lut = mapper.GetLookupTable()

        # Verify LUT exists and has correct range
        assert lut is not None
        range_min, range_max = lut.GetTableRange()
        assert range_min == 0.0
        assert range_max == 5.0

    def test_clear_draft(self, constraint_renderer, test_mesh, renderer):
        """Test clearing draft angle visualization."""
        draft_map = {0: 1.5, 1: 2.5}
        constraint_renderer.show_draft_angles(draft_map, test_mesh)
        assert constraint_renderer.draft_actor is not None

        constraint_renderer.clear_draft()
        assert constraint_renderer.draft_actor is None

    def test_draft_lut_color_ranges(self, constraint_renderer):
        """Test that LUT produces correct colors for different draft angles."""
        lut = constraint_renderer._create_draft_lut()

        # Test insufficient draft (< 0.5°) -> should be red
        color_insufficient = [0, 0, 0, 0]
        lut.GetTableValue(int((0.2 / 5.0) * 255), color_insufficient)
        assert color_insufficient[0] == 1.0  # Red
        assert color_insufficient[1] == 0.0  # No green
        assert color_insufficient[2] == 0.0  # No blue

        # Test good draft (> 2.0°) -> should be green
        color_good = [0, 0, 0, 0]
        lut.GetTableValue(int((3.0 / 5.0) * 255), color_good)
        assert color_good[0] == 0.0  # No red
        assert color_good[1] == 1.0  # Green
        assert color_good[2] == 0.0  # No blue

    def test_update_draft_thresholds(self, constraint_renderer, test_mesh, renderer):
        """Test updating draft angle thresholds."""
        # Create initial visualization
        draft_map = {0: 1.0, 1: 2.0}
        constraint_renderer.show_draft_angles(draft_map, test_mesh)

        # Update thresholds
        constraint_renderer.update_draft_thresholds(1.0, 3.0)

        assert constraint_renderer.draft_insufficient == 1.0
        assert constraint_renderer.draft_marginal == 3.0


class TestDemoldingDirection:
    """Test demolding direction arrow visualization."""

    def test_show_demolding_direction_basic(self, constraint_renderer, renderer):
        """Test showing demolding direction arrow."""
        direction = (0.0, 0.0, 1.0)  # Upward Z
        constraint_renderer.show_demolding_direction(direction)

        assert constraint_renderer.demold_arrow is not None

        # Check color is blue
        actor = constraint_renderer.demold_arrow
        color = actor.GetProperty().GetColor()
        assert color[0] == 0.0  # No red
        assert color[1] == 0.5  # Half green
        assert color[2] == 1.0  # Full blue

        opacity = actor.GetProperty().GetOpacity()
        assert opacity == 0.8

    def test_show_demolding_direction_with_origin(self, constraint_renderer, renderer):
        """Test arrow with custom origin point."""
        direction = (1.0, 0.0, 0.0)
        origin = (5.0, 5.0, 5.0)

        constraint_renderer.show_demolding_direction(direction, origin=origin, scale=1.5)
        assert constraint_renderer.demold_arrow is not None

    def test_show_demolding_direction_normalization(self, constraint_renderer, renderer):
        """Test that direction vector is normalized."""
        # Non-unit vector
        direction = (3.0, 4.0, 0.0)  # Length = 5

        constraint_renderer.show_demolding_direction(direction)
        assert constraint_renderer.demold_arrow is not None

    def test_show_demolding_direction_invalid(self, constraint_renderer, renderer):
        """Test with invalid (zero-length) direction."""
        direction = (0.0, 0.0, 0.0)

        constraint_renderer.show_demolding_direction(direction)
        # Should not create arrow for zero-length vector
        assert constraint_renderer.demold_arrow is None

    def test_clear_demold_arrow(self, constraint_renderer, renderer):
        """Test clearing demolding arrow."""
        direction = (0.0, 1.0, 0.0)
        constraint_renderer.show_demolding_direction(direction)
        assert constraint_renderer.demold_arrow is not None

        constraint_renderer.clear_demold_arrow()
        assert constraint_renderer.demold_arrow is None

    def test_demold_arrow_auto_origin(self, constraint_renderer, test_mesh, renderer):
        """Test arrow with automatic origin from mesh bounds."""
        constraint_renderer.current_mesh = test_mesh

        direction = (0.0, 0.0, 1.0)
        constraint_renderer.show_demolding_direction(direction)

        # Arrow should be created at mesh center
        assert constraint_renderer.demold_arrow is not None


class TestClearAll:
    """Test clearing all visualizations."""

    def test_clear_all(self, constraint_renderer, test_mesh, renderer):
        """Test clearing all constraint visualizations."""
        # Add all visualizations
        undercut_faces = [0, 1, 2]
        draft_map = {0: 1.0, 1: 2.0, 2: 3.0}
        direction = (0.0, 0.0, 1.0)

        constraint_renderer.show_undercuts(undercut_faces, test_mesh)
        constraint_renderer.show_draft_angles(draft_map, test_mesh)
        constraint_renderer.show_demolding_direction(direction)

        assert constraint_renderer.undercut_actor is not None
        assert constraint_renderer.draft_actor is not None
        assert constraint_renderer.demold_arrow is not None

        # Clear all
        constraint_renderer.clear_all()

        assert constraint_renderer.undercut_actor is None
        assert constraint_renderer.draft_actor is None
        assert constraint_renderer.demold_arrow is None
        assert constraint_renderer.current_mesh is None


class TestDraftStatistics:
    """Test draft angle statistics calculation."""

    def test_get_draft_statistics_empty(self, constraint_renderer):
        """Test statistics with empty draft map."""
        stats = constraint_renderer.get_draft_statistics({})

        assert stats["min"] == 0.0
        assert stats["max"] == 0.0
        assert stats["mean"] == 0.0
        assert stats["std"] == 0.0
        assert stats["total_faces"] == 0
        assert stats["count_insufficient"] == 0
        assert stats["count_marginal"] == 0
        assert stats["count_good"] == 0

    def test_get_draft_statistics_valid(self, constraint_renderer):
        """Test statistics with valid draft data."""
        draft_map = {
            0: 0.2,   # Insufficient
            1: 0.3,   # Insufficient
            2: 1.0,   # Marginal
            3: 1.5,   # Marginal
            4: 2.5,   # Good
            5: 3.0,   # Good
            6: 4.0,   # Good
        }

        stats = constraint_renderer.get_draft_statistics(draft_map)

        assert stats["total_faces"] == 7
        assert stats["count_insufficient"] == 2
        assert stats["count_marginal"] == 2
        assert stats["count_good"] == 3
        assert stats["min"] == 0.2
        assert stats["max"] == 4.0
        assert stats["mean"] == pytest.approx(1.7857, rel=0.01)
        assert "median" in stats

    def test_get_draft_statistics_all_good(self, constraint_renderer):
        """Test statistics with all good draft angles."""
        draft_map = {i: 3.0 + i * 0.1 for i in range(10)}

        stats = constraint_renderer.get_draft_statistics(draft_map)

        assert stats["count_insufficient"] == 0
        assert stats["count_marginal"] == 0
        assert stats["count_good"] == 10

    def test_get_draft_statistics_all_insufficient(self, constraint_renderer):
        """Test statistics with all insufficient draft angles."""
        draft_map = {i: 0.1 + i * 0.01 for i in range(10)}

        stats = constraint_renderer.get_draft_statistics(draft_map)

        assert stats["count_insufficient"] == 10
        assert stats["count_marginal"] == 0
        assert stats["count_good"] == 0


class TestConstraintVisualizationIntegration:
    """Integration tests for complete constraint visualization."""

    def test_multiple_visualizations_coexist(self, constraint_renderer, test_mesh, renderer):
        """Test that all three visualizations can coexist."""
        undercut_faces = [0, 1, 2]
        draft_map = {i: float(i % 4) for i in range(test_mesh.GetNumberOfCells())}
        direction = (0.0, 1.0, 0.0)

        constraint_renderer.show_undercuts(undercut_faces, test_mesh)
        constraint_renderer.show_draft_angles(draft_map, test_mesh)
        constraint_renderer.show_demolding_direction(direction)

        # All three should be present
        assert constraint_renderer.undercut_actor is not None
        assert constraint_renderer.draft_actor is not None
        assert constraint_renderer.demold_arrow is not None

        # All should be in renderer
        num_actors = renderer.GetActors().GetNumberOfItems()
        assert num_actors >= 3

    def test_sequential_updates(self, constraint_renderer, test_mesh, renderer):
        """Test updating visualizations sequentially."""
        # First update
        constraint_renderer.show_undercuts([0, 1], test_mesh)
        first_undercut = constraint_renderer.undercut_actor

        # Second update with different data
        constraint_renderer.show_undercuts([5, 6, 7, 8], test_mesh)
        second_undercut = constraint_renderer.undercut_actor

        # Should replace, not accumulate
        assert second_undercut != first_undercut


class TestConstraintRendererTestUtility:
    """Test the test utility function."""

    def test_create_test_constraint_visualization(self, renderer):
        """Test creating test constraint visualization."""
        cr = create_test_constraint_visualization(renderer)

        assert cr is not None
        assert isinstance(cr, ConstraintRenderer)

        # Should have created all three visualizations
        assert cr.undercut_actor is not None
        assert cr.draft_actor is not None
        assert cr.demold_arrow is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_none_mesh(self, constraint_renderer):
        """Test with None mesh."""
        constraint_renderer.show_undercuts([0, 1], None)
        assert constraint_renderer.undercut_actor is None

        constraint_renderer.show_draft_angles({0: 1.0}, None)
        assert constraint_renderer.draft_actor is None

    def test_none_direction(self, constraint_renderer, renderer):
        """Test with None direction."""
        constraint_renderer.show_demolding_direction(None)
        assert constraint_renderer.demold_arrow is None

    def test_out_of_bounds_face_ids(self, constraint_renderer, test_mesh, renderer):
        """Test with face IDs that are out of bounds."""
        num_cells = test_mesh.GetNumberOfCells()

        # Use invalid face IDs
        invalid_faces = [num_cells + 10, num_cells + 20]

        # Should not crash, but may not create actor
        constraint_renderer.show_undercuts(invalid_faces, test_mesh)
        # Behavior is implementation-defined, just ensure no crash

    def test_negative_face_ids(self, constraint_renderer, test_mesh, renderer):
        """Test with negative face IDs."""
        # Should handle gracefully
        constraint_renderer.show_undercuts([-1, -2], test_mesh)
        # Should not crash

    def test_draft_map_sparse(self, constraint_renderer, test_mesh, renderer):
        """Test draft map with only some faces mapped."""
        num_cells = test_mesh.GetNumberOfCells()

        # Only map a few faces
        draft_map = {0: 1.0, 5: 2.0, 10: 3.0}

        # Should work, unmapped faces get 0.0
        constraint_renderer.show_draft_angles(draft_map, test_mesh)
        assert constraint_renderer.draft_actor is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
