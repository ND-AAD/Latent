#!/usr/bin/env python3
"""
Test SubD Display Integration - VTK rendering and viewport functionality.

Tests the complete visualization pipeline from tessellation to screen:
- TessellationResult to VTK conversion
- Display mode switching
- Selection highlighting
- Performance with various mesh sizes
"""

import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import vtk
import numpy as np
from app.geometry.subd_renderer import SubDRenderer, create_test_subd_result


class TestSubDRenderer(unittest.TestCase):
    """Test SubDRenderer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.renderer = SubDRenderer()
        self.vtk_renderer = vtk.vtkRenderer()

    def test_create_subd_actor_basic(self):
        """Test basic actor creation from tessellation result."""
        # Create test tessellation
        result = create_test_subd_result(subdivision_level=1)

        # Create actor
        actor = self.renderer.create_subd_actor(result)

        # Verify actor created
        self.assertIsNotNone(actor)
        self.assertIsInstance(actor, vtk.vtkActor)

        # Verify mapper connected
        mapper = actor.GetMapper()
        self.assertIsNotNone(mapper)

        # Verify polydata has geometry
        polydata = mapper.GetInput()
        self.assertGreater(polydata.GetNumberOfPoints(), 0)
        self.assertGreater(polydata.GetNumberOfCells(), 0)

    def test_tessellation_to_polydata_conversion(self):
        """Test TessellationResult to VTK polydata conversion."""
        result = create_test_subd_result(subdivision_level=2)

        # Create actor (which creates polydata internally)
        actor = self.renderer.create_subd_actor(result)

        # Get polydata
        polydata = self.renderer.current_polydata

        # Verify vertex count matches
        self.assertEqual(
            polydata.GetNumberOfPoints(),
            result.vertex_count()
        )

        # Verify triangle count matches
        self.assertEqual(
            polydata.GetNumberOfCells(),
            result.triangle_count()
        )

        # Verify normals present
        normals = polydata.GetPointData().GetNormals()
        self.assertIsNotNone(normals)
        self.assertEqual(normals.GetNumberOfTuples(), result.vertex_count())

    def test_smooth_shading_normals(self):
        """Test that smooth shading normals are properly computed."""
        result = create_test_subd_result(subdivision_level=2)
        actor = self.renderer.create_subd_actor(result)

        polydata = self.renderer.current_polydata
        normals = polydata.GetPointData().GetNormals()

        # Verify each normal is unit length (or close)
        for i in range(min(10, normals.GetNumberOfTuples())):
            normal = np.array(normals.GetTuple3(i))
            length = np.linalg.norm(normal)
            self.assertAlmostEqual(length, 1.0, places=5,
                                 msg=f"Normal {i} not unit length: {length}")

    def test_display_mode_solid(self):
        """Test solid display mode."""
        result = create_test_subd_result(subdivision_level=1)
        actor = self.renderer.create_subd_actor(result)

        self.renderer.set_display_mode("solid")

        prop = actor.GetProperty()
        self.assertEqual(prop.GetRepresentation(), vtk.VTK_SURFACE)
        self.assertFalse(prop.GetEdgeVisibility())

    def test_display_mode_wireframe(self):
        """Test wireframe display mode."""
        result = create_test_subd_result(subdivision_level=1)
        actor = self.renderer.create_subd_actor(result)

        self.renderer.set_display_mode("wireframe")

        prop = actor.GetProperty()
        self.assertEqual(prop.GetRepresentation(), vtk.VTK_WIREFRAME)

    def test_display_mode_shaded_wireframe(self):
        """Test shaded wireframe display mode."""
        result = create_test_subd_result(subdivision_level=1)
        actor = self.renderer.create_subd_actor(result)

        self.renderer.set_display_mode("shaded_wireframe")

        prop = actor.GetProperty()
        self.assertEqual(prop.GetRepresentation(), vtk.VTK_SURFACE)
        self.assertTrue(prop.GetEdgeVisibility())

    def test_display_mode_points(self):
        """Test points display mode."""
        result = create_test_subd_result(subdivision_level=1)
        actor = self.renderer.create_subd_actor(result)

        self.renderer.set_display_mode("points")

        prop = actor.GetProperty()
        self.assertEqual(prop.GetRepresentation(), vtk.VTK_POINTS)

    def test_invalid_display_mode(self):
        """Test that invalid display mode raises ValueError."""
        with self.assertRaises(ValueError):
            self.renderer.set_display_mode("invalid_mode")

    def test_selection_highlighting(self):
        """Test selection highlighting functionality."""
        result = create_test_subd_result(subdivision_level=2)
        actor = self.renderer.create_subd_actor(result)

        # Add to renderer
        self.vtk_renderer.AddActor(actor)

        # Select some faces
        selected_faces = [0, 1, 5, 10]
        self.renderer.update_selection_highlighting(
            selected_faces,
            self.vtk_renderer
        )

        # Verify highlight actors created
        self.assertGreater(len(self.renderer.highlight_actors), 0)

        # Verify highlight actor in renderer
        actors = self.vtk_renderer.GetActors()
        self.assertIsNotNone(actors)
        self.assertGreater(actors.GetNumberOfItems(), 1)  # Main + highlight

    def test_clear_selection_highlighting(self):
        """Test clearing selection highlighting."""
        result = create_test_subd_result(subdivision_level=1)
        actor = self.renderer.create_subd_actor(result)
        self.vtk_renderer.AddActor(actor)

        # Add highlights
        self.renderer.update_selection_highlighting([0, 1, 2], self.vtk_renderer)
        self.assertGreater(len(self.renderer.highlight_actors), 0)

        # Clear highlights
        self.renderer.update_selection_highlighting([], self.vtk_renderer)
        self.assertEqual(len(self.renderer.highlight_actors), 0)

    def test_performance_small_mesh(self):
        """Test performance stats for small mesh (<1K triangles)."""
        result = create_test_subd_result(subdivision_level=1)
        actor = self.renderer.create_subd_actor(result)

        stats = self.renderer.get_performance_stats()

        self.assertIn("vertices", stats)
        self.assertIn("triangles", stats)
        self.assertIn("has_normals", stats)

        # Small mesh should have < 1000 triangles
        self.assertLess(stats["triangles"], 1000)

    def test_performance_medium_mesh(self):
        """Test performance stats for medium mesh (1K-10K triangles)."""
        result = create_test_subd_result(subdivision_level=3)
        actor = self.renderer.create_subd_actor(result)

        stats = self.renderer.get_performance_stats()

        # Medium mesh should have reasonable size
        self.assertGreater(stats["triangles"], 100)
        self.assertTrue(stats["has_normals"])

    def test_performance_large_mesh(self):
        """Test performance with large mesh (>10K triangles)."""
        result = create_test_subd_result(subdivision_level=4)
        actor = self.renderer.create_subd_actor(result)

        stats = self.renderer.get_performance_stats()

        # Large mesh
        self.assertGreater(stats["triangles"], 1000)

        # Should still maintain >30 FPS target
        # (Actual FPS testing would require rendering loop)
        # Just verify data structures are reasonable
        self.assertIsNotNone(self.renderer.current_polydata)

    def test_color_customization(self):
        """Test custom colors for SubD surface."""
        result = create_test_subd_result(subdivision_level=1)

        # Custom color
        custom_color = (1.0, 0.5, 0.25)
        actor = self.renderer.create_subd_actor(result, color=custom_color)

        # Verify color applied
        color = actor.GetProperty().GetColor()
        np.testing.assert_array_almost_equal(color, custom_color)

    def test_opacity_customization(self):
        """Test custom opacity for SubD surface."""
        result = create_test_subd_result(subdivision_level=1)

        actor = self.renderer.create_subd_actor(result, opacity=0.5)

        # Verify opacity
        self.assertAlmostEqual(actor.GetProperty().GetOpacity(), 0.5)


class TestSubDViewport(unittest.TestCase):
    """Test SubDViewport functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Import here to avoid Qt initialization issues in headless mode
        try:
            from app.ui.subd_viewport import SubDViewport
            self.SubDViewport = SubDViewport
            self.qt_available = True
        except ImportError:
            self.qt_available = False

    def test_viewport_creation(self):
        """Test basic viewport creation."""
        if not self.qt_available:
            self.skipTest("Qt not available in headless mode")

        viewport = self.SubDViewport("Perspective")

        self.assertEqual(viewport.view_name, "Perspective")
        self.assertIsNotNone(viewport.renderer)
        self.assertIsNotNone(viewport.subd_renderer)

    def test_display_mode_switching(self):
        """Test switching display modes."""
        if not self.qt_available:
            self.skipTest("Qt not available in headless mode")

        viewport = self.SubDViewport("Perspective")

        # Test mode switching
        for mode in ["solid", "wireframe", "shaded_wireframe", "points"]:
            viewport.set_display_mode(mode)
            self.assertEqual(viewport.subd_renderer.display_mode, mode)

    def test_performance_stats(self):
        """Test performance statistics reporting."""
        if not self.qt_available:
            self.skipTest("Qt not available in headless mode")

        viewport = self.SubDViewport("Top")
        stats = viewport.get_performance_stats()

        # Verify stats structure
        self.assertIn("view_name", stats)
        self.assertEqual(stats["view_name"], "Top")
        self.assertIn("is_active", stats)
        self.assertIn("display_mode", stats)


def run_visual_test():
    """
    Run a visual test displaying a SubD with various modes.

    This is a manual test that displays a window for verification.
    Not run as part of automated tests.
    """
    from PyQt6.QtWidgets import QApplication
    from app.ui.subd_viewport import SubDViewport

    app = QApplication(sys.argv)

    viewport = SubDViewport("Test Viewport")
    viewport.resize(800, 600)
    viewport.show()

    # Create test geometry
    result = create_test_subd_result(subdivision_level=3)
    viewport.display_subd(result, color=(0.7, 0.8, 0.9))

    # Test display modes
    print("Display modes: solid, wireframe, shaded_wireframe, points")
    print("Press different keys to test modes (manual testing)")

    sys.exit(app.exec())


def main():
    """Run tests."""
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    # Check for visual test flag
    if '--visual' in sys.argv:
        run_visual_test()
    else:
        sys.exit(main())
