"""
Tests for Region Visualization and Coloring

Tests RegionColorManager and RegionRenderer functionality:
- Color assignment and generation
- Region visualization with coloring
- Boundary rendering
- Highlighting (hover and selection)
- Color persistence and export
"""

import pytest
import numpy as np
import vtk
from app.ui.region_color_manager import RegionColorManager
from app.geometry.region_renderer import RegionRenderer
from app.state.parametric_region import ParametricRegion


class TestRegionColorManager:
    """Test RegionColorManager color assignment."""

    def test_initialization(self):
        """Test color manager initialization."""
        cm = RegionColorManager()

        assert cm.region_colors == {}
        assert cm.user_overrides == {}
        assert cm.saturation == 0.75
        assert cm.value == 0.85
        assert cm.default_color == (0.7, 0.7, 0.8)

    def test_generate_distinct_colors(self):
        """Test generation of visually distinct colors."""
        cm = RegionColorManager()

        # Generate 5 colors
        colors = cm._generate_distinct_colors(5)

        assert len(colors) == 5
        for color in colors:
            assert len(color) == 3
            assert all(0.0 <= c <= 1.0 for c in color)

        # Colors should be distinct (check hue differences)
        # Since we use golden ratio, hues should be well-separated
        hues = []
        for r, g, b in colors:
            import colorsys
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hues.append(h)

        # Check that we have good hue distribution
        # With golden ratio, minimum spacing should be reasonable
        for i in range(len(hues) - 1):
            diff = abs(hues[i+1] - hues[i])
            # Due to modulo, differences can wrap around
            if diff > 0.5:
                diff = 1.0 - diff
            # Should have some separation (not too close)
            assert diff > 0.1

    def test_assign_colors(self):
        """Test color assignment to regions."""
        cm = RegionColorManager()

        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2]),
            ParametricRegion(id="r2", faces=[3, 4, 5]),
            ParametricRegion(id="r3", faces=[6, 7, 8])
        ]

        cm.assign_colors(regions)

        # All regions should have colors
        assert len(cm.region_colors) == 3
        assert "r1" in cm.region_colors
        assert "r2" in cm.region_colors
        assert "r3" in cm.region_colors

        # Colors should be valid RGB tuples
        for region_id, color in cm.region_colors.items():
            assert len(color) == 3
            assert all(0.0 <= c <= 1.0 for c in color)

    def test_preserve_existing_colors(self):
        """Test that existing colors are preserved when preserve_existing=True."""
        cm = RegionColorManager()

        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2]),
            ParametricRegion(id="r2", faces=[3, 4, 5])
        ]

        # Assign initial colors
        cm.assign_colors(regions)
        r1_color = cm.get_color("r1")

        # Add new region and reassign with preserve_existing=True
        regions.append(ParametricRegion(id="r3", faces=[6, 7, 8]))
        cm.assign_colors(regions, preserve_existing=True)

        # r1 should keep same color
        assert cm.get_color("r1") == r1_color

        # r3 should have a color assigned
        assert "r3" in cm.region_colors
        # Note: With golden ratio and small numbers, colors may coincidentally match
        # The important thing is that r3 has a color assigned

    def test_get_color(self):
        """Test color retrieval with priority system."""
        cm = RegionColorManager()

        # Default color for unknown region
        assert cm.get_color("unknown") == cm.default_color

        # Assigned color
        region = ParametricRegion(id="r1", faces=[0, 1, 2])
        cm.assign_colors([region])
        assigned_color = cm.get_color("r1")
        assert assigned_color != cm.default_color

        # User override takes precedence
        override_color = (1.0, 0.0, 0.0)
        cm.set_color("r1", override_color)
        assert cm.get_color("r1") == override_color

    def test_set_color_override(self):
        """Test user color override."""
        cm = RegionColorManager()

        custom_color = (0.5, 0.3, 0.8)
        cm.set_color("r1", custom_color)

        assert "r1" in cm.user_overrides
        assert cm.user_overrides["r1"] == custom_color
        assert cm.get_color("r1") == custom_color

    def test_clear_override(self):
        """Test clearing user override."""
        cm = RegionColorManager()

        # Set override
        cm.set_color("r1", (1.0, 0.0, 0.0))
        assert "r1" in cm.user_overrides

        # Clear override
        cm.clear_override("r1")
        assert "r1" not in cm.user_overrides

    def test_get_highlight_color(self):
        """Test highlight color generation (lighter shade)."""
        cm = RegionColorManager()

        region = ParametricRegion(id="r1", faces=[0, 1, 2])
        cm.assign_colors([region])

        base_color = cm.get_color("r1")
        highlight_color = cm.get_highlight_color("r1")

        # Highlight should be lighter (higher value in HSV)
        import colorsys
        h1, s1, v1 = colorsys.rgb_to_hsv(*base_color)
        h2, s2, v2 = colorsys.rgb_to_hsv(*highlight_color)

        assert v2 >= v1  # Lighter or same
        assert s2 <= s1  # Less saturated or same

    def test_get_boundary_color(self):
        """Test boundary color generation (darker shade)."""
        cm = RegionColorManager()

        region = ParametricRegion(id="r1", faces=[0, 1, 2])
        cm.assign_colors([region])

        base_color = cm.get_color("r1")
        boundary_color = cm.get_boundary_color("r1")

        # Boundary should be darker (lower value in HSV)
        import colorsys
        h1, s1, v1 = colorsys.rgb_to_hsv(*base_color)
        h2, s2, v2 = colorsys.rgb_to_hsv(*boundary_color)

        assert v2 < v1  # Darker

    def test_remove_region(self):
        """Test removing region colors."""
        cm = RegionColorManager()

        region = ParametricRegion(id="r1", faces=[0, 1, 2])
        cm.assign_colors([region])
        cm.set_color("r1", (1.0, 0.0, 0.0))

        assert "r1" in cm.region_colors
        assert "r1" in cm.user_overrides

        cm.remove_region("r1")

        assert "r1" not in cm.region_colors
        assert "r1" not in cm.user_overrides

    def test_clear_all(self):
        """Test clearing all color assignments."""
        cm = RegionColorManager()

        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2]),
            ParametricRegion(id="r2", faces=[3, 4, 5])
        ]
        cm.assign_colors(regions)
        cm.set_color("r1", (1.0, 0.0, 0.0))

        assert len(cm.region_colors) > 0
        assert len(cm.user_overrides) > 0

        cm.clear_all()

        assert len(cm.region_colors) == 0
        assert len(cm.user_overrides) == 0

    def test_to_dict(self):
        """Test serialization to dictionary."""
        cm = RegionColorManager()

        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2]),
            ParametricRegion(id="r2", faces=[3, 4, 5])
        ]
        cm.assign_colors(regions)
        cm.set_color("r1", (1.0, 0.0, 0.0))

        data = cm.to_dict()

        assert 'region_colors' in data
        assert 'user_overrides' in data
        assert 'saturation' in data
        assert 'value' in data
        assert 'default_color' in data

        assert 'r1' in data['region_colors']
        assert 'r2' in data['region_colors']
        assert 'r1' in data['user_overrides']

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        cm = RegionColorManager()

        data = {
            'region_colors': {
                'r1': [0.5, 0.3, 0.8],
                'r2': [0.2, 0.7, 0.4]
            },
            'user_overrides': {
                'r1': [1.0, 0.0, 0.0]
            },
            'saturation': 0.8,
            'value': 0.9,
            'default_color': [0.6, 0.6, 0.7]
        }

        cm.from_dict(data)

        assert cm.get_color("r1") == (1.0, 0.0, 0.0)  # User override
        assert cm.get_color("r2") == (0.2, 0.7, 0.4)
        assert cm.saturation == 0.8
        assert cm.value == 0.9
        assert cm.default_color == (0.6, 0.6, 0.7)

    def test_get_all_colors(self):
        """Test getting all colors including overrides."""
        cm = RegionColorManager()

        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2]),
            ParametricRegion(id="r2", faces=[3, 4, 5])
        ]
        cm.assign_colors(regions)

        # Set override for r1
        override_color = (1.0, 0.0, 0.0)
        cm.set_color("r1", override_color)

        all_colors = cm.get_all_colors()

        assert len(all_colors) == 2
        assert all_colors["r1"] == override_color  # Override takes precedence
        assert "r2" in all_colors


class TestRegionRenderer:
    """Test RegionRenderer visualization."""

    def setup_method(self):
        """Setup for each test."""
        self.color_manager = RegionColorManager()
        self.renderer = RegionRenderer(self.color_manager)
        self.vtk_renderer = vtk.vtkRenderer()

    def create_mock_tessellation_result(self):
        """Create mock TessellationResult for testing."""
        # Simple cube tessellation
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Bottom
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],  # Top
        ], dtype=np.float32)

        normals = np.array([
            [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],  # Bottom normals
            [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],      # Top normals
        ], dtype=np.float32)

        # Two triangles per face
        triangles = np.array([
            [0, 1, 2], [0, 2, 3],  # Bottom (face 0)
            [4, 5, 6], [4, 6, 7],  # Top (face 1)
        ], dtype=np.int32)

        # Face parents (which SubD face each triangle came from)
        face_parents = [0, 0, 1, 1]  # 2 triangles from face 0, 2 from face 1

        class MockTessellationResult:
            def __init__(self, verts, norms, tris, parents):
                self.vertices = verts
                self.normals = norms
                self.triangles = tris
                self.face_parents = parents

        return MockTessellationResult(vertices, normals, triangles, face_parents)

    def test_initialization(self):
        """Test renderer initialization."""
        assert self.renderer.color_manager is self.color_manager
        assert self.renderer.region_actors == []
        assert self.renderer.boundary_actors == []
        assert self.renderer.highlight_actors == []
        assert self.renderer.current_polydata is None

    def test_create_polydata_from_tessellation(self):
        """Test conversion of TessellationResult to VTK polydata."""
        result = self.create_mock_tessellation_result()

        polydata = self.renderer._create_polydata_from_tessellation(result)

        assert polydata.GetNumberOfPoints() == 8
        assert polydata.GetNumberOfCells() == 4  # 4 triangles

        # Check normals
        normals = polydata.GetPointData().GetNormals()
        assert normals is not None
        assert normals.GetNumberOfTuples() == 8

    def test_create_face_to_region_map(self):
        """Test creation of face-to-region mapping."""
        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2]),
            ParametricRegion(id="r2", faces=[3, 4, 5])
        ]

        face_map = self.renderer._create_face_to_region_map(regions)

        assert face_map[0] == "r1"
        assert face_map[1] == "r1"
        assert face_map[2] == "r1"
        assert face_map[3] == "r2"
        assert face_map[4] == "r2"
        assert face_map[5] == "r2"

    def test_render_regions(self):
        """Test rendering regions with colors."""
        regions = [
            ParametricRegion(id="r1", faces=[0]),
            ParametricRegion(id="r2", faces=[1])
        ]

        result = self.create_mock_tessellation_result()

        self.renderer.render_regions(regions, result, self.vtk_renderer)

        # Should have created region actors
        assert len(self.renderer.region_actors) > 0

        # Should have assigned colors
        assert "r1" in self.color_manager.region_colors
        assert "r2" in self.color_manager.region_colors

    def test_clear_all(self):
        """Test clearing all visualization actors."""
        regions = [
            ParametricRegion(id="r1", faces=[0]),
            ParametricRegion(id="r2", faces=[1])
        ]

        result = self.create_mock_tessellation_result()

        # Render regions
        self.renderer.render_regions(regions, result, self.vtk_renderer)

        # Verify actors exist
        assert len(self.renderer.region_actors) > 0
        assert self.renderer.current_polydata is not None

        # Clear all
        self.renderer.clear_all(self.vtk_renderer)

        # Verify cleared
        assert len(self.renderer.region_actors) == 0
        assert len(self.renderer.boundary_actors) == 0
        assert len(self.renderer.highlight_actors) == 0
        assert self.renderer.current_polydata is None

    def test_highlight_region_hover(self):
        """Test hover highlighting."""
        regions = [
            ParametricRegion(id="r1", faces=[0])
        ]

        result = self.create_mock_tessellation_result()
        self.renderer.render_regions(regions, result, self.vtk_renderer)

        # Highlight region
        self.renderer.highlight_region(regions[0], self.vtk_renderer, hover=True)

        # Should have created highlight actor
        assert len(self.renderer.highlight_actors) > 0

    def test_highlight_region_selection(self):
        """Test selection highlighting."""
        regions = [
            ParametricRegion(id="r1", faces=[0])
        ]

        result = self.create_mock_tessellation_result()
        self.renderer.render_regions(regions, result, self.vtk_renderer)

        # Highlight region
        self.renderer.highlight_region(regions[0], self.vtk_renderer, hover=False)

        # Should have created highlight actor
        assert len(self.renderer.highlight_actors) > 0

    def test_highlight_clear(self):
        """Test clearing highlights."""
        regions = [
            ParametricRegion(id="r1", faces=[0])
        ]

        result = self.create_mock_tessellation_result()
        self.renderer.render_regions(regions, result, self.vtk_renderer)

        # Add highlight
        self.renderer.highlight_region(regions[0], self.vtk_renderer, hover=True)
        assert len(self.renderer.highlight_actors) > 0

        # Clear highlight
        self.renderer.highlight_region(None, self.vtk_renderer)
        assert len(self.renderer.highlight_actors) == 0

    def test_extract_region_faces(self):
        """Test extraction of region faces."""
        regions = [
            ParametricRegion(id="r1", faces=[0]),
            ParametricRegion(id="r2", faces=[1])
        ]

        result = self.create_mock_tessellation_result()
        self.renderer.render_regions(regions, result, self.vtk_renderer)

        # Extract r1 faces
        r1_polydata = self.renderer._extract_region_faces(regions[0])

        # Should have 2 triangles (face 0 has 2 triangles in mock data)
        assert r1_polydata.GetNumberOfCells() == 2

    def test_calculate_region_centroid(self):
        """Test centroid calculation."""
        regions = [
            ParametricRegion(id="r1", faces=[0])
        ]

        result = self.create_mock_tessellation_result()
        self.renderer.render_regions(regions, result, self.vtk_renderer)

        # Calculate centroid
        centroid = self.renderer._calculate_region_centroid(regions[0])

        assert centroid is not None
        assert len(centroid) == 3

        # Should be somewhere in the bottom face region
        x, y, z = centroid
        assert 0 <= x <= 1
        assert 0 <= y <= 1
        # Bottom face is at z=0
        assert z >= 0 and z <= 0.5  # Should be in lower half

    def test_add_pin_marker(self):
        """Test adding pin marker to region."""
        regions = [
            ParametricRegion(id="r1", faces=[0], pinned=True)
        ]

        result = self.create_mock_tessellation_result()
        self.renderer.render_regions(regions, result, self.vtk_renderer)

        # Add pin marker
        self.renderer.add_pin_marker(regions[0], self.vtk_renderer)

        # Should have created pin marker actor
        assert len(self.renderer.pin_markers) > 0


class TestIntegration:
    """Integration tests for color manager and renderer."""

    def test_color_persistence_workflow(self):
        """Test complete workflow with color persistence."""
        cm = RegionColorManager()

        # Create initial regions
        regions = [
            ParametricRegion(id="r1", faces=[0, 1, 2]),
            ParametricRegion(id="r2", faces=[3, 4, 5])
        ]

        # Assign colors
        cm.assign_colors(regions)
        r1_color = cm.get_color("r1")

        # User customizes r1 color
        custom_color = (1.0, 0.0, 0.0)
        cm.set_color("r1", custom_color)

        # Export to dict
        data = cm.to_dict()

        # Create new color manager and load
        cm2 = RegionColorManager()
        cm2.from_dict(data)

        # Verify persistence
        assert cm2.get_color("r1") == custom_color  # Custom color preserved
        assert cm2.get_color("r2") == cm.get_color("r2")  # Auto-assigned color preserved

    def test_rendering_with_pinned_regions(self):
        """Test rendering with pinned and unpinned regions."""
        cm = RegionColorManager()
        renderer = RegionRenderer(cm)
        vtk_renderer = vtk.vtkRenderer()

        # Create regions with different pinned states
        regions = [
            ParametricRegion(id="r1", faces=[0], pinned=True),
            ParametricRegion(id="r2", faces=[1], pinned=False)
        ]

        # Create mock tessellation
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
        ], dtype=np.float32)

        normals = np.array([
            [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],
            [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],
        ], dtype=np.float32)

        triangles = np.array([
            [0, 1, 2], [0, 2, 3],
            [4, 5, 6], [4, 6, 7],
        ], dtype=np.int32)

        face_parents = [0, 0, 1, 1]

        class MockTessellationResult:
            def __init__(self, verts, norms, tris, parents):
                self.vertices = verts
                self.normals = norms
                self.triangles = tris
                self.face_parents = parents

        result = MockTessellationResult(vertices, normals, triangles, face_parents)

        # Render regions
        renderer.render_regions(regions, result, vtk_renderer)

        # Add pin marker to pinned region
        renderer.add_pin_marker(regions[0], vtk_renderer)

        # Verify rendering succeeded
        assert len(renderer.region_actors) > 0
        assert len(renderer.pin_markers) > 0

    def test_color_distinctiveness(self):
        """Test that generated colors are sufficiently distinct."""
        cm = RegionColorManager()

        # Create many regions
        regions = [
            ParametricRegion(id=f"r{i}", faces=[i])
            for i in range(20)
        ]

        cm.assign_colors(regions)

        # Get all colors
        colors = [cm.get_color(f"r{i}") for i in range(20)]

        # Check pairwise distinctiveness
        # Colors should have minimum perceptual distance
        import colorsys

        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                c1 = colors[i]
                c2 = colors[j]

                # Calculate simple color distance in RGB space
                distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

                # Should have reasonable separation (empirical threshold)
                # With 20 colors on HSV wheel using golden ratio, some colors
                # will be closer than others. 0.05 is a reasonable minimum.
                assert distance > 0.05, f"Colors {i} and {j} too similar: {c1} vs {c2}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
